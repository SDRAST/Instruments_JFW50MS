"""
module JFW50MS for JFW Industries microwave switch M&C
"""
import telnetlib
import logging
import re

from MonitorControl import ObservatoryError, Device, Switch, show_port_sources
from Electronics.Instruments.JFW50MS.hwif import MS287
from support.pyro import get_device_server

module_logger = logging.getLogger(__name__)

class MS287client(Device):
  """
  This is the client class for a 24 input by 4 output full matrix switch.

  The actual switch is controlled by a server through the class MS287server 
  which is defined in the server app MS287_server.py.  The switch itself is a
  sub-class of class MS287 in the module 'hwif'.
  
  The purpose of this module is to manage the signal flow.
  """
  switch_type = "Nx1"

  def __init__(self, name, inputs=None, output_names=[], active=True):
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
    mylogger = logging.getLogger(module_logger.name+".MS287")
    self.name = name # needed by the next statement
    mylogger.debug(" initializing %s", self)
    show_port_sources(inputs, " Inputs to MS287:", mylogger.level)
    Device.__init__(self, name, inputs=inputs, output_names=output_names,
                    active=active)
    self.logger = mylogger
    show_port_sources(inputs, " MS287 inputs redefined:", mylogger.level)
    self.name = name
    self.hw = get_device_server("MS287server")
    
    self.channel = {}
    for name in output_names:
      self.channel[name] = self.Channel(self, name, inputs=self.inputs,
                                        output_names = [name], active=active)
    self.logger.debug(" %s outputs: %s", self.name, self.outputs)

  def get_states(self):
    """
    """
    return self.hw.get_states()
  
  def help(self):
    """
    """
    return self.hw.help()
    
  def set_state(self, switch, source):
    """
    """
    self.hw.set_state(switch, source)
  
  def get_state(self, switch):
    """
    """
    self.hw.get_state(switch)
    
  class Channel(Switch):
    """
    (I think the only role this plays is to trace signals.
    """
    def __init__(self, parent, name, inputs=None, output_names=None,
                 active=True):
      self.type = MS287.switch_type
      self.parent = parent
      self.name = name
      self.ID = int(name[-1])-1
      mylogger = logging.getLogger(self.parent.logger.name+".Channel")
      show_port_sources(inputs, " Inputs to %s:" % self, mylogger.level)
      Switch.__init__(self, name, inputs=inputs,
                      output_names=[name], stype = self.type,
                      active=active)
      self.logger = mylogger
      show_port_sources(self.inputs, " %s inputs redefined:" % str(self),
                         self.logger.level)
      self.parent.outputs[name] = self.outputs[name]
                      
