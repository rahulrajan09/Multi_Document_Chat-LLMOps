import os
import logging
from datetime import datetime
import structlog

class CustomLogger:
    def __init__(self,log_dir="logs"):
        
        self.logs_dir=os.path.join(os.getcwd(),log_dir)                         #create a log folder path
        os.makedirs(self.logs_dir,exist_ok=True)                                #create actual folder from path
        log_file=f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"          #create log file name
        self.log_file_path=os.path.join(self.logs_dir,log_file)                 #create a log file path
    
    def get_logger(self,name=__file__):
        # creating a logger name of the file which we are currently in
        logger_name=os.path.basename(name)               #fetches only name from the entire filepath e.g main.py from path c:\\scripts\main.py
        
        #filehandler-writes logs to the file
        filehandler=logging.FileHandler(self.log_file_path)
        filehandler.setLevel(logging.INFO)
        filehandler.setFormatter(logging.Formatter("%(message)s"))
        
        #consolehandler-writes logs to the console
        consolehandler=logging.StreamHandler()
        consolehandler.setLevel(logging.INFO)
        consolehandler.setFormatter(logging.Formatter("%(message)s"))
        
        #logging config
        
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            handlers=[consolehandler,filehandler]
        )
        
        #giving structure using structlog
        
        structlog.configure(
            
            processors=[
                structlog.processors.TimeStamper(fmt="iso",utc=True,key="timestamp"),
                structlog.processors.add_log_level,
                structlog.processors.EventRenamer(to="event"),
                structlog.processors.JSONRenderer()
            ],
            
            #loggerfactory and cache
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True   
        )
        
        return structlog.get_logger(logger_name)