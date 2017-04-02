import telnetlib
import logging
import re

module_logger = logging.getLogger(__name__)

class MS287(object):
  """
  This is a 24 input by 4 output full matrix switch.

  The switch numbers its ports 1...N.  For Python we convert it to (0...N-1).
  We can treat it logically as four 24x1 switches.  Some functions apply to the
  entire physical switch. To avoid repeating them we have a class variable
  'connection'.  For now, this limits us to one switch of this type in a
  configuration but we can change it to a dict to support multiple JFW50MS287
  switches.

  Class Variable
  ==============
  connection  - a Telnet instance for the session with the physical switch.
  host        - assigned by sys admin
  port        - manufacture's default
  switch_type - apply as Switch().sw_type.
  
  Public attributes
  =================
  These additional attributes are added to the Switch() atrributes of sw_type,
  sources and destinations::
    - name   - identifier text for switch
    - switch - switch number = outport number - 1
    - state  - index into multiports[] to active input port
  """
  switch_type = "Nx1"
  host = "192.168.100.50"
  port = 3001
  connection = None

  def __init__(self, name="IFswitch", output_names=["1", "2", "3", "4"],
               active=True):
    """
    In most Device types, the first argument is the device providing the
    signal source.  In the case of a Switch it is the instance which "owns" the
    switch, which may be an observatory or a telescope.  Use the attribute
    'sources' to see where the signal comes from.
    
    @param observatory : argument to pass to Switch() as the parent
    @type  observatory : Observatory() instance

    @param swID : logical switch in the matrix, keyed to output port
    @type  swID : int
    """
    self.logger = logging.getLogger(module_logger.name+".MS287")
    self.name = name # needed by the next statement
    self.logger.debug(" initializing %s", self)
    self._connect()
    self.channel = {}
    for name in output_names:
      self.channel[name] = self.Channel(self, name, active=active)
    self.states = {}
    
  def _connect(self):
    """
    """
    try:
      MS287.connection = telnetlib.Telnet(host=MS287.host,
                                               port=MS287.port)
    except Exception, details:
      self.logger.error("_connect: Could not connect to MS287: %s",
                     str(details))
      raise ObservatoryError(MS287.host,"did not respond. IF switch is down.")
    else:
      received = MS287.connection.read_until('something',0.5)
      self.logger.debug("_connect: MS287 replied: %s",received.strip())

  def send_request(self,request):
    """
    Send a command and get the response.

    The read_all() method doesn't work because the switch does not send an
    EOF at the end of a response.

    @param request : command to be sent to the switch
    @type  request : str

    @return: response from switch (str)
    """
    MS287.connection.write(request+'\r')
    response = MS287.connection.read_until('something',0.5)
    self.logger.debug("send_request: returned: %s",response.strip() )
    if re.search("Error", response):
      raise ObservatoryError(response,"returned by MS287")
    return response

  def get_states(self):
    """
    """
    for ch in self.channel.keys():
      self.states[ch] = self.channel[ch]._get_state()
    return self.states
    
  class Channel(object):
    """
    """
    def __init__(self, parent, name, active=True):
      """
      """
      self.type = MS287.switch_type
      self.name = name
      self.parent = parent
      self.ID = int(name[-1])-1
      self.logger = logging.getLogger(self.parent.logger.name+".Channel")
                      
    def _get_state(self):
      """
      Returns the state of the switch channel

      The switch state is the 0-based number of the input which is connected to
      the output, e.g., 0 means input #1.

      A typical response from the MS287 is "Output #1 set to Input #4".  An
      input of #0 means the output is set to its self-terminating state. This
      results in a state of -1.
      """
      command = "RO"+str(self.ID+1)
      self.logger.debug("_get_state: command sent: %s", command)
      response = self.parent.send_request(command).strip()
      self.logger.debug("_get_state: response received: %s", response)
      # Parse the last word for the number
      inport_str = response.split()[-1]
      inport = int(inport_str.lstrip("#"))
      self.logger.debug("_get_state: inport = %s", inport)
      self.state = int(inport)-1
      return self.state

    def _set_state(self,inport):
      """
      Sets the state of the switch channel
      """
      command = "SOR%1d %2d" % (self.ID+1,inport)
      self.logger.debug("_set_state: Command sent: %s", command)
      response = self.parent.send_request(command)
      inport_str = response.strip().split()[-1]
      inport = int(inport_str.lstrip("#"))
      self.logger.debug("_set_state: Response: %s", inport)
      self.state = int(inport)-1
      return self.state
