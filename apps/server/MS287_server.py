import logging
import sys

from support.logs import set_module_loggers, initiate_option_parser
from support.logs import init_logging, get_loglevel, set_loglevel
from support.pyro import PyroServer, PyroServerLauncher

from Electronics.Instruments.JFW50MS.hwif import MS287
       
examples = '''
help         - returns this text
set_state    - selects the input (1-24) for a switch; returns get_state()
get_state    - returns the state of the switch = input port number-1
send_request - process a MS287 command; returns MS287 response
quit         - stops the Pyro server
'''

# Set up Python logging
logging.basicConfig(level=logging.WARNING)
module_logger = logging.getLogger(__name__)

class MS287_Server(PyroServer, MS287):
  """
  """
  def __init__(self):
    """
    """
    self.logger = logging.getLogger(module_logger.name+".MS287_Server")
    PyroServer.__init__(self)
    self.logger.debug(" superclass initialized")
    MS287.__init__(self)
    self.logger.debug(" server instantiated")
    self.run = True

  def set_state(self, number, inp):
    """
    Selects the input for a switch.
    
    Returns the state of the switch which is the input port number - 1
    
    @param number : number of the switch, 1-4
    @type  number : int or str
    
    @return: int
    """
    state = int(inp)
    self.channel[str(number)]._set_state(state)
    return self.get_state(number)
    
  def get_state(self, number):
    """
    """
    self.channel[str(number)]._get_state()
    return self.channel[str(number)].state
    
  def quit(self):
      """
      """
      self.logger.info("quit: stopping daemon")
      self.run = False
      self.halt()

  def help(self):
    """
    """
    return examples
    
def main():
    """
    """
    name = "MS287server"
    
    p = initiate_option_parser("""Pyro server for MS287 IF switch.""",
                               examples)
    # Add other options here
  
    args = p.parse_args(sys.argv[1:])
  
    # This cannot be delegated to another module or class
    mylogger = init_logging(logging.getLogger(),
                            loglevel   = get_loglevel(args.file_loglevel),
                            consolevel = get_loglevel(args.console_loglevel),
                            logname    = args.logpath+name+".log")
    mylogger.debug(" Handlers: %s", mylogger.handlers)
    loggers = set_module_loggers(eval(args.modloglevels))

    psl = PyroServerLauncher(name, nameserver_host='dto')
    IFsw = MS287_Server()
    psl.start(IFsw)
  
    psl.finish()
  
main()
