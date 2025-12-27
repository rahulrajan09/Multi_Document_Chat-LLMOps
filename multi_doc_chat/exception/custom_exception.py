import sys
import traceback
from typing import cast, Optional

class DocumentPortalException(Exception):
    
    def __init__(self,error_message,error_details:Optional[object]=None):
        # normalise error message
        if isinstance(error_message,BaseException):
            norm_msg=str(error_message)
        else:
            norm_msg=str(error_message)
        
        # fetching error details
        exc_type = exc_value = exc_tb = None
        if error_details is None:                               #first check if error details none then extract from sys.exc_info()
            exc_type,exc_value,exc_tb=sys.exc_info()
        else:                                                  #check for 3 conditions:
            if hasattr(error_details,"exc_info"):                               # 1)errordetails has any name exc info in it 
                exc_info_obj=cast(sys,error_details)                            #if it has then converting it to sys to do sys.exc_info()
                exc_type,exc_value,exc_tb=exc_info_obj.exc_info()
                
            elif isinstance(error_details,BaseException):
                exc_type,exc_value,exc_tb=type(error_details),error_details,error_details.__traceback__
            
            else:
                exc_type,exc_value,exc_tb=sys.exc_info()
                
        #fetch last traceback
        last_tb=exc_tb                                  #fetching last traceback
        while last_tb and last_tb.tb_next:
            last_tb = last_tb.tb_next
            
        self.file_name= last_tb.tb_frame.f_code.co_filename if last_tb else "<unknown>"      #extracting filename for traceback
        self.lineno=last_tb.tb_lineno if last_tb else -1                               #extracting linenumber fro traceback
        self.error_message=norm_msg                                                  #assigning error message from earlier received norm msg
        
        #pretty traceback-writing in better way(if its available)
        if exc_type and exc_tb:
            self.traceback_str=''.join(traceback.format_exception(exc_type,exc_value,exc_tb))
        else:
            self.traceback_str= ""
                
        super().__init__(self.__str__())
        
        
    #compact logger friendly message-personalised
    def __str__(self):
        base = f"Error in filename [{self.file_name}] at line number [{self.lineno}] | Message : [{self.error_message}]"
        if self.traceback_str:
            return f"{base} \n Traceback: \n {self.traceback_str} "
        return base
        
    #for terminal debugging
    def __repr__(self):
        return f" DocumentPortalException(file={self.file_name!r} ,line= {self.lineno},message= {self.error_message!r})"
    
