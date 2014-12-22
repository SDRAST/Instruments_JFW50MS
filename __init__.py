"""
module JFW50MS for JFW Industries microwave switch M&C
"""
import telnetlib
import logging
import re

from MonitorControl import ObservatoryError, Device, Switch, show_port_sources

module_logger = logging.getLogger(__name__)

class MS287(Device):
  switch_type = "Nx1"
  host = "192.168.100.50"
  port = 3001
  connection = None

  def __init__(self, parent, name, inputs=None, output_names=[], active=True):
    mylogger = logging.getLogger(module_logger.name+".MS287")
    self.name = name # needed by the next statement
    mylogger.debug(" initializing %s", self)
    show_port_sources(inputs, " Inputs to MS287:", mylogger.level)
    Device.__init__(self, name, inputs=inputs, output_names=output_names,
                    active=active)
    self.logger = mylogger
    show_port_sources(inputs, " MS287 inputs redefined:", mylogger.level)
    self.name = name
    self.parent = parent
    self._connect()
    self.channel = {}
    for name in output_names:
      self.channel[name] = self.Channel(self, name, inputs=self.inputs,
                                        output_names = [name], active=active)
    self.logger.debug(" %s outputs: %s", self.name, self.outputs)

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

  class Channel(Switch):
    def __init__(self, parent, name, inputs=None, output_names=None,
                 active=True):
      self.type = MS287.switch_type
      self.parent = parent
      self.name = name
      self.ID = int(name[-1])-1
      mylogger = logging.getLogger(self.parent.logger.name+".Channel")
      show_port_sources(inputs, " Inputs to %s:" % self, mylogger.level)
      Switch.__init__(self, parent, name, inputs=inputs,
                      output_names=[name], stype = self.type,
                      active=active)
      self.logger = mylogger
      show_port_sources(self.inputs, " %s inputs redefined:" % str(self),
                         self.logger.level)
      self.parent.outputs[name] = self.outputs[name]
                      
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
      self.logger.debug("set_input: Command sent: %s", command)
      response = self.parent.send_request(command)
      inport_str = response.strip().split()[-1]
      inport = int(inport_str.lstrip("#"))
      self.logger.debug("set_input: Response: %s", inport)
      self.state = int(inport)-1
      return self.state
