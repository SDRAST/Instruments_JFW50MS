import logging
import sys

from support.logs import set_module_loggers, initiate_option_parser
from support.logs import init_logging, get_loglevel, set_loglevel
from support.pyro import PyroServer, PyroServerLauncher

from Electronics.Instruments.JFW50MS.hwif import MS287

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
      #super(MS287_Server,self).__init__()
      PyroServer.__init__(self)
      self.logger.debug(" superclass initialized")
      MS287.__init__(self)
      self.logger.debug(" server instantiated")
      self.run = True
 
    def answer(self):
      return "got it"
       
examples = ''
  
def main():
    """
    """
    p = initiate_option_parser(
     """Pyro server for MS287 IF switch.""",
     examples)
    # Add other options here
  
    opts, args = p.parse_args(sys.argv[1:])
  
    # This cannot be delegated to another module or class
    mylogger = init_logging(logging.getLogger(),
                            loglevel   = get_loglevel(opts.file_loglevel),
                            consolevel = get_loglevel(opts.stderr_loglevel),
                            logname    = opts.logpath+__name__+".log")
    mylogger.debug(" Handlers: %s", mylogger.handlers)
    loggers = set_module_loggers(eval(opts.modloglevels))

    psl = PyroServerLauncher("MS287server", nameserver_host='dto')
    IFsw = MS287_Server()
    psl.start(IFsw)
  
    psl.finish()
  
main()
