import json
import iterm2.api_pb2
import iterm2.rpc
import iterm2.session
import iterm2.tab
import iterm2.util

class CreateTabException(Exception):
  pass

class SetPropertyException(Exception):
  pass

class GetPropertyException(Exception):
  pass

class Window:
  """Represents an iTerm2 window."""
  def __init__(self, connection, window_id, tabs, frame):
    self.connection = connection
    self.window_id = window_id
    self.tabs = tabs
    self.frame = frame

  def __repr__(self):
    return "<Window id=%s tabs=%s frame=%s>" % (self.window_id, self.tabs, iterm2.util.frame_str(self.frame))

  def pretty_str(self, indent=""):
    """
    Returns: A nicely formatted string describing the window, its tabs, and their sessions.
    """
    s = indent + "Window id=%s frame=%s\n" % (self.get_window_id(), iterm2.util.frame_str(self.frame))
    for t in self.tabs:
      s += t.pretty_str(indent=indent + "  ")
    return s

  @staticmethod
  async def create(connection, profile=None, command=None):
    """
    Creates a new window.

    profile: The profile name to use or None for the default profile.
    command: The command to run in the new session, or None for the default for the profile.

    Returns: A session_id

    Raises: CreateTabException if something goes wrong.
    """
    result = await iterm2.rpc.create_tab(connection, profile=profile, command=command)
    if result.create_tab_response.status == iterm2.api_pb2.CreateTabResponse.Status.Value("OK"):
      return result.create_tab_response.session_id
    else:
      raise CreateTabException(iterm2.api_pb2.CreateTabResponse.Status.Name(result.create_tab_response.status))

  def get_window_id(self):
    """
    Returns: the window's unique identifier.
    """
    return self.window_id

  def get_tabs(self):
    """
    Returns: a list of iterm2.tab.Tab objects.
    """
    return self.tabs

  async def create_tab(self, profile=None, command=None, index=None):
    """
    Creates a new tab in this window.

    profile: The profile name to use or None for the default profile.
    command: The command to run in the new session, or None for the default for the profile.
    index: The index in the window where the new tab should go (0=first position, etc.)

    Returns: A session_id

    Raises: CreateTabException if something goes wrong.
    """
    result = await iterm2.rpc.create_tab(self.connection, profile=profile, window=self.window_id, index=index, command=command)
    if result.create_tab_response.status == iterm2.api_pb2.CreateTabResponse.Status.Value("OK"):
      return result.create_tab_response.session_id
    else:
      raise CreateTabException(iterm2.api_pb2.CreateTabResponse.Status.Name(result.create_tab_response.status))

  async def get_frame(self, connection):
    """
    Gets the window's frame.

    0,0 is the *bottom* right of the main screen.

    connection: A connected iterm2.Connection.

    Returns: api_pb2.Frame

    Raises: GetPropertyException if something goes wrong.
    """

    response = await iterm2.rpc.get_property(connection, "frame", self.window_id)
    if response.get_property_response.status == iterm2.api_pb2.GetPropertyResponse.Status.Value("OK"):
      d = json.loads(response.get_property_response.json_value)
      frame = iterm2.api_pb2.Frame()
      frame.origin.x = d["origin"]["x"]
      frame.origin.y = d["origin"]["y"]
      frame.size.width = d["size"]["width"]
      frame.size.height = d["size"]["height"]
      return frame
    else:
      raise GetPropertyException(response.get_property_response.status)

  async def set_frame(self, connection, frame):
    """
    Sets the window's frame.

    connection: A connected iterm2.Connection.
    frame: api_pb2.Frame

    Raises: SetPropertyException if something goes wrong.
    """
    dict = { "origin": { "x": frame.origin.x,
                         "y": frame.origin.y },
             "size": { "width": frame.size.width,
                       "height": frame.size.height } }
    json_value = json.dumps(dict)
    response = await iterm2.rpc.set_property(connection, "frame", json_value, window_id=self.window_id)
    if response.set_property_response.status != iterm2.api_pb2.SetPropertyResponse.Status.Value("OK"):
      raise SetPropertyException(response.get_property_response.status)

  async def get_fullscreen(self, connection):
    """
    Checks if the window is full-screen.

    connection: A connected iterm2.Connection.

    Returns: True (fullscreen) or False (not fullscreen)

    Raises: GetPropertyException if something goes wrong.
    """
    response = await iterm2.rpc.get_property(connection, "fullscreen", self.window_id)
    if response.get_property_response.status == iterm2.api_pb2.GetPropertyResponse.Status.Value("OK"):
      return json.loads(response.get_property_response.json_value)
    else:
      raise GetPropertyException(response.get_property_response.status)


  async def set_fullscreen(self, connection, fullscreen):
    """
    Changes the window's full-screen status.

    connection: A connected iterm2.Connection.
    fullscreen: True to make fullscreen, False to make not-fullscreen

    Raises: SetPropertyException if something goes wrong.
    """
    json_value = json.dumps(fullscreen)
    response = await iterm2.rpc.set_property(connection, "fullscreen", json_value, window_id=self.window_id)
    if response.get_property_response.status != iterm2.api_pb2.SetPropertyResponse.Status.Value("OK"):
      raise SetPropertyException(response.get_property_response.status)

