"""
module JFW50MS for JFW Industries microwave switch M&C
"""
import telnetlib
from MonitorControl import ObservatoryError, Device, Switch

class MS287(Device):
  switch_type = "Nx1"
  host = "192.168.100.50"
  port = 3001
  connection = None

  def __init__(self, parent, name, inputs=None, output_names=[], active=True):
    Device.__init__(self, name, inputs=inputs, output_names=output_names,
                    active=active)
    self.parent = parent
    self._connect()
    self.channel = {}
    for name in output_names:
      self.channel[name] = self.Channel(self, name, inputs=inputs,
                                        output_names = [name], active=active)

  def _connect(self):
    """
    """
    try:
      MS287.connection = telnetlib.Telnet(host=MS287.host,
                                               port=MS287.port)
    except Exception, details:
      self.logger.error("__init__: Could not connect to MS287: %s",
                     str(details))
      raise ObservatoryError(MS287.host,"did not respond. IF switch is down.")
    else:
      received = MS287.connection.read_until('something',0.5)
      self.logger.debug("__init__: MS287 replied: %s",received.strip())

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
    return response

  class Channel(Switch):
    def __init__(self, parent, name, inputs=None, output_names=None,
                 active=True):
      self.type = MS287.switch_type
      self.parent = parent
      self.ID = int(name[-1])-1
      Switch.__init__(self, parent, name, inputs=inputs,
                      output_names=output_names,stype = self.type, active=active)

    def _get_state(self):
      command = "RO"+str(self.ID+1)
      self.logger.debug("get_input: Command sent: %s", command)
      self.parent.send_request(command)
      response = self.parent.send_request(command)
      inport_str = response.strip().split()[-1]
      inport = int(inport_str.lstrip("#"))
      self.logger.debug("get_input: Response: %s", inport)
      if inport:
        self.state = int(inport)-1
      else:
        self.state = None
      return self.state

    def _set_state(self,inport):
      command = "SOR%1d %2d" % (self.ID+1,inport)
      self.logger.debug("set_input: Command sent: %s", command)
      response = self.parent.send_request(command)
      inport_str = response.strip().split()[-1]
      inport = int(inport_str.lstrip("#"))
      self.logger.debug("set_input: Response: %s", inport)
      self.state = int(inport)-1
      return self.state
