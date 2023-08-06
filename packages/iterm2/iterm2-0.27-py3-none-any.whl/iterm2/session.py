import asyncio

import iterm2.app
import iterm2.connection
import iterm2.notifications
import iterm2.profile
import iterm2.rpc
import iterm2.util

class SplitPaneException(Exception):
  """Something went wrong when trying to split a pane."""
  pass

class Splitter:
  """A container of split pane sessions where the dividers are all aligned the same way.
  
  :ivar vertical: Whether the split pane dividers in this Splitter are vertical
    or horizontal.
  """
  def __init__(self, vertical=False):
    """
    :param vertical: Bool. If true, the divider is vertical, else horizontal.
    """
    self.vertical = vertical
    # Elements are either Splitter or Session
    self.children = []
    # Elements are Session
    self.sessions = []

  @staticmethod
  def from_node(node, connection):
    """Creates a new Splitter from a node.

    node: iterm2.api_pb2.ListSessionsResponse.SplitTreeNode
    connection: iterm2.connection.Connection

    :returns: A new Splitter.
    """
    splitter = Splitter(node.vertical)
    for link in node.links:
      if link.HasField("session"):
        session = Session(connection, link)
        splitter.add_child(session)
      else:
        subsplit = Splitter.from_node(link.node, connection)
        splitter.add_child(subsplit)
    return splitter

  def add_child(self, child):
    """
    Adds one or more new sessions to a splitter.

    child: A Session or a Splitter.
    """
    self.children.append(child)
    if type(child) is Session:
      self.sessions.append(child)
    else:
      self.sessions.extend(child.all_sessions())

  def get_children(self):
    """
    :returns: This splitter's children. A list of iterm2.session.Session objects.
    """
    return self.children

  def all_sessions(self):
    """
    :returns: All sessions in this splitter and all nested splitters. A list of
      iterm2.session.Session objects.
    """
    return self.sessions

  def pretty_str(self, indent=""):
    """
    :returns: A string describing this splitter. Has newlines.
    """
    s = indent + "Splitter %s\n" % (
        "|" if self.vertical else "-")
    for child in self.children:
      s += child.pretty_str("  " + indent)
    return s

  def update_session(self, s):
    """
    Finds a session with the same ID as s. If it exists, replace the reference with s.

    :returns: True if the update occurred.
    """
    i = 0
    for c in self.children:
      if type(c) is Session and c.session_id == s.session_id:
        self.children[i] = s

        # Update the entry in self.sessions
        for j in range(len(self.sessions)):
          if self.sessions[j].session_id == s.session_id:
            self.sessions[j] = s
            break

        return True
      elif type(c) is Splitter:
        if c.update_session(s):
          return True
      i += 1

class Session:
  """
  Represents an iTerm2 session.
  """

  @staticmethod
  def active_proxy(connection):
    """
    Use this to register notifications against the currently active session.

    :returns: A proxy for the currently active session.
    """
    return ProxySession(connection, "active")

  @staticmethod
  def all_proxy(connection):
    """
    Use this to register notifications against all sessions, including those
    not yet created.

    :returns: A proxy for all sessions.
    """
    return ProxySession(connection, "all")

  def __init__(self, connection, link):
    """
    connection: iterm2.connection.Connection
    link: iterm2.api_pb2.ListSessionsResponse.SplitTreeNode.SplitTreeLink
    """
    self.connection = connection

    self.session_id = link.session.unique_identifier
    self.frame = link.session.frame
    self.grid_size = link.session.grid_size
    self.name = link.session.title

  def __repr__(self):
    return "<Session name=%s id=%s>" % (self.name, self.session_id)

  def update_from(self, s):
    """Replace internal state with that of another session."""
    self.frame = s.frame
    self.grid_size = s.grid_size
    self.name = s.name

  def pretty_str(self, indent=""):
    """
    :returns: A string describing the session.
    """
    return indent + "Session \"%s\" id=%s %s frame=%s\n" % (
        self.name,
        self.session_id,
        iterm2.util.size_str(self.grid_size),
        iterm2.util.frame_str(self.frame))

  def get_session_id(self):
    """
    :returns: the globally unique identifier for this session.
    """
    return self.session_id

  def get_keystroke_reader(self):
    """
    Provides a nice interface for observing a sequence of keystrokes.

    :returns: a keystroke reader, an iterm2.session.Session.KeystrokeReader.

    :Example:

      async with session.get_keystroke_reader() as reader:
        while condition():
          handle_keystrokes(reader.get())

    .. note:: Each call to reader.get() returns an array of new keystrokes.
    """
    return self.KeystrokeReader(self.connection, self.session_id)

  def get_screen_streamer(self, want_contents=True):
    """
    Provides a nice interface for receiving updates to the screne.

    The screen is the mutable part of a session (its last lines, excluding
    scrollback history).

    :returns: An iterm2.session.Session.ScreenStreamer
    """
    return self.ScreenStreamer(self.connection, self.session_id, want_contents=want_contents)

  async def send_text(self, text):
    """
    Send text as though the user had typed it.

    :param text: The text to send.
    """
    await iterm2.rpc.send_text(self.connection, self.session_id, text)

  async def split_pane(self, vertical=False, before=False, profile=None):
    """
    Splits the pane, creating a new session.

    :param vertical: Bool. If true, the divider is vertical, else horizontal.
    :param before: Bool, whether the new session should be left/above the existing one.
    :param profile: The profile name to use. None for the default profile.

    :returns: New iterm.session.Session.

    :throws: SplitPaneException if something goes wrong.
    """
    result = await iterm2.rpc.split_pane(self.connection, self.session_id, vertical, before, profile)
    if result.split_pane_response.status == iterm2.api_pb2.SplitPaneResponse.Status.Value("OK"):
      new_session_id = result.split_pane_response.session_id[0]
      app = await iterm2.app.get_app(self.connection)
      await app.refresh()
      return await app.get_session_by_id(new_session_id)
    else:
      raise SplitPaneException(iterm2.api_pb2.SplitPaneResponse.Status.Name(result.split_pane_response.status))

  async def read_keystroke(self):
    """
    Blocks until a keystroke is received. Returns a KeystrokeNotification.

    See also get_keystroke_reader().

    :returns: iterm2.api_pb2.KeystrokeNotification
    """
    future = asyncio.Future()
    async def on_keystroke(connection, message):
      future.set_result(message)

    token = await iterm2.notifications.subscribe_to_keystroke_notification(self.connection, on_keystroke, self.session_id)
    await self.connection.dispatch_until_future(future)
    await iterm2.notifications.unsubscribe(self.connection, token)
    return future.result()

  async def wait_for_screen_update(self):
    """
    Blocks until the screen contents change.

    :returns: iterm2.api_pb2.ScreenUpdateNotification
    """
    future = asyncio.Future()
    async def on_update(connection, message):
      future.set_result(message)

    token = await iterm2.notifications.subscribe_to_screen_update_notification(self.connection, on_update, self.session_id)
    await self.connection.dispatch_until_future(future)
    await iterm2.notifications.unsubscribe(self.connection, token)
    return future.result

  async def get_screen_contents(self):
    """
    :returns: The screen contents, an iterm2.api_pb2.GetBufferResponse

    :throws: iterm2.rpc.RPCException if something goes wrong.
    """
    response = await iterm2.rpc.get_buffer_with_screen_contents(self.connection, self.session_id)
    status = response.get_buffer_response.status
    if status == iterm2.api_pb2.GetBufferResponse.Status.Value("OK"):
      return response.get_buffer_response
    else:
      raise iterm2.rpc.RPCException(iterm2.api_pb2.GetBufferResponse.Status.Name(status))

  async def get_buffer_lines(self, trailing_lines):
    """
    Fetches the last lines of the session, reaching into history if needed.

    :param trailing_lines: The number of lines to fetch.

    :returns: The buffer contents, an iterm2.api_pb2.GetBufferResponse

    :throws: iterm2.rpc.RPCException if something goes wrong.
    """
    response = await iterm2.rpc.get_buffer_lines(self.connection, trailing_lines, self.session_id)
    status = response.get_buffer_response.status
    if status == iterm2.api_pb2.GetBufferResponse.Status.Value("OK"):
      return response.get_buffer_response
    else:
      raise iterm2.rpc.RPCException(iterm2.api_pb2.GetBufferResponse.Status.Name(status))

  async def get_prompt(self):
    """
    Fetches info about the last prompt in this session.

    :returns: iterm2.api_pb2.GetPromptResponse

    :throws: iterm2.rpc.RPCException if something goes wrong.
    """
    response = await iterm2.rpc.get_prompt(self.connection, self.session_id)
    status = response.get_prompt_response.status
    if status == iterm2.api_pb2.GetPromptResponse.Status.Value("OK"):
      return response.get_prompt_response
    elif status == iterm2.api_pb2.GetPromptResponse.Status.Value("PROMPT_UNAVAILABLE"):
      return None
    else:
      raise iterm2.rpc.RPCException(iterm2.api_pb2.GetPromptResponse.Status.Name(status))

  async def set_profile_property(self, key, json_value):
    """
    Sets the value of a property in this session.

    :param key: The name of the property
    :param json_value: The json-encoded value to set

    :returns: iterm2.api_pb2.SetProfilePropertyResponse

    :throws: iterm2.rpc.RPCException if something goes wrong.
    """
    response = await iterm2.rpc.set_profile_property(self.connection, key, json_value)
    status = response.set_profile_property_response.status
    if status == iterm2.api_pb2.SetProfilePropertyResponse.Status.Value("OK"):
      return response.set_profile_property_response
    else:
      raise iterm2.rpc.RPCException(iterm2.api_pb2.GetPromptResponse.Status.Name(status))

  async def get_profile(self):
    """
    Fetches the profile of this session

    :returns: iterm2.profile.Profile

    :throws: iterm2.rpc.RPCException if something goes wrong.
    """
    response = await iterm2.rpc.get_profile(self.connection, self.session_id)
    status = response.get_profile_property_response.status
    if status == iterm2.api_pb2.GetProfilePropertyResponse.Status.Value("OK"):
      return iterm2.profile.Profile(self.session_id, self.connection, response.get_profile_property_response)
    else:
      raise iterm2.rpc.RPCException(iterm2.api_pb2.GetProfilePropertyResponse.Status.Name(status))

  async def inject(self, data):
    """
    Injects data as though it were program output.

    :param data: A byte array to inject.
    """
    response = await iterm2.rpc.inject(self.connection, data, [self.session_id])
    status = response.inject_response.status[0]
    if status != iterm2.api_pb2.InjectResponse.Status.Value("OK"):
      raise iterm2.rpc.RPCException(iterm2.api_pb2.InjectResponse.Status.Name(status))

  async def activate(self, select_tab=True, order_window_front=True):
     """
     Makes the session the active session in its tab.

     :param select_tab: Whether the tab this session is in should be selected.
     :param order_window_front: Whether the window this session is in should be
       brought to the front and given keyboard focus.
     """
     await iterm2.rpc.activate(self.connection, True, select_tab, order_window_front, session_id=self.session_id)

  async def set_variable(self, name, value):
      """
      Sets a user-defined variable in the session.

      See Badges documentation for more information on user-defined variables.

      :param name: The variable's name.
      :param value: The new value to assign.
      """
      result = await iterm2.rpc.variable(self.connection, self.session_id, [(name, value)], [])
      status = result.variable_response.status
      if status != iterm2.api_pb2.VariableResponse.Status.Value("OK"):
        raise iterm2.rpc.RPCException(iterm2.api_pb2.VariableResponse.Status.Name(status))

  async def get_variable(self, name):
      """
      Fetches a session variable.

      See Badges documentation for more information on user-defined variables.

      :param name: The variable's name.

      :returns: The variable's value or empty string if it is undefined.
      """
      result = await iterm2.rpc.variable(self.connection, self.session_id, [], [name])
      status = result.variable_response.status
      if status != iterm2.api_pb2.VariableResponse.Status.Value("OK"):
        raise iterm2.rpc.RPCException(iterm2.api_pb2.VariableResponse.Status.Name(status))
      else:
        return result.variable_response.values[0]

  class KeystrokeReader:
    """An asyncio context manager for reading keystrokes.

    Don't create this yourself. Use Session.get_keystroke_reader() instead. See
    its docstring for more info."""
    def __init__(self, connection, session_id):
      self.connection = connection
      self.session_id = session_id
      self.buffer = []

    async def __aenter__(self):
      async def on_keystroke(connection, message):
        self.buffer.append(message)
        if self.future is not None:
          temp = self.buffer
          self.buffer = []
          self.future.set_result(temp)

      self.token = await iterm2.notifications.subscribe_to_keystroke_notification(self.connection, on_keystroke, self.session_id)
      return self

    async def get(self):
      """
      Get the next keystroke.

      :returns: An iterm2.api_pb2.KeystrokeNotification.
      """
      self.future = asyncio.Future()
      await self.connection.dispatch_until_future(self.future)
      result = self.future.result()
      self.future = None
      return result

    async def __aexit__(self, exc_type, exc, tb):
      await iterm2.notifications.unsubscribe(self.connection, self.token)
      return self.buffer

  class ScreenStreamer:
    """An asyncio context manager for monitoring the screen contents.

    Don't create this yourself. Use Session.get_screen_streamer() instead. See
    its docstring for more info."""
    def __init__(self, connection, session_id, want_contents=True):
      self.connection = connection
      self.session_id = session_id
      self.want_contents = want_contents

    async def __aenter__(self):
      async def on_update(connection, message):
        future = self.future
        if future is None:
          # Ignore reentrant calls
          return

        self.future = None
        if future is not None and not future.done():
          future.set_result(message)

      self.token = await iterm2.notifications.subscribe_to_screen_update_notification(self.connection, on_update, self.session_id)
      return self

    async def __aexit__(self, exc_type, exc, tb):
      await iterm2.notifications.unsubscribe(self.connection, self.token)

    async def get(self):
      """
      Gets the screen contents, waiting until they change if needed.

      :returns: An iterm2.api_pb2.GetBufferResponse.
      """
      future = asyncio.Future()
      self.future = future
      await self.connection.dispatch_until_future(self.future)
      self.future = None

      if self.want_contents:
        result = await iterm2.rpc.get_buffer_with_screen_contents(self.connection, self.session_id)
        return result

class InvalidSessionId(Exception):
  """The specified session ID is not allowed in this method."""
  pass

class ProxySession(Session):
  """A proxy for a Session.

  This is used when you specify an abstract session ID like "all" or "active".
  Since the session or set of sessions that refers to is ever-changing, this
  proxy stands in for the real thing. It may limit functionality since it
  doesn't make sense to, for example, get the screen contents of "all"
  sessions.
  """
  def __init__(self, connection, session_id):
    self.connection = connection
    self.session_id = session_id

  def __repr__(self):
    return "<ProxySession %s>" % self.session_id

  def pretty_str(self, indent=""):
    return indent + "ProxySession %s" % self.session_id

  async def get_screen_contents(self):
    if self.session_id == "all":
      raise InvalidSessionId()
    return await super(ProxySession, self).get_screen_contents()

  async def get_buffer_lines(self, trailing_lines):
    if self.session_id == "all":
      raise InvalidSessionId()
    return await super(ProxySession, self).get_buffer_lines(trailing_lines)

  async def get_prompt(self):
    if self.session_id == "all":
      raise InvalidSessionId()
    return await super(ProxySession, self).get_prompt()

  async def get_profile(self):
    if self.session_id == "all":
      return iterm2.profile.WriteOnlyProfile(self.session_id, self.connection)
    else:
      return await super(ProxySession, self).get_profile()

