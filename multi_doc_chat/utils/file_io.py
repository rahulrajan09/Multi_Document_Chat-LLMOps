from __future__ import annotations
import os
from pathlib import Path
import uuid
import re
from typing import List,Iterable

from multi_doc_chat.logger import GLOBAL_LOGGER as log
from multi_doc_chat.exception.custom_exception import DocumentPortalException

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".pptx", ".md", ".csv", ".xlsx", ".xls", ".db", ".sqlite", ".sqlite3"}

def save_uploaded_file(uploaded_files:Iterable,target_dir:Path)->List[Path]:
    #saving uploaded files to return as local file
    try:
        target_dir.mkdir(parents=True,exist_ok=True)            #creating target folder 
        saved:List[Path]=[]                                     #defining name for output 
        
        #extracting extention from uploaded files
        for uf in uploaded_files:
            
            name=getattr(uf,"filename",getattr(uf,"name","file"))
            ext=Path(name).suffix.lower()                   #e.g abcfile.pdf -> .pdf
            
            if ext not in SUPPORTED_EXTENSIONS:
                log.warning("unsupported file format skipped",filename=name)
                continue
            
            #cleaning file name without extension(e.g abc.pdf -> abc and removing unnecesary words,numbers,symbols)
            safe_name=re.sub(r'[^a-zA-Z0-9_\-]',"_",Path(name).stem).lower() #substitute unnecesary words
            f_name=f"{safe_name}_{uuid.uuid4().hex[:8]}{ext}"                  #assign unique id
            #f_name=f"{uuid.uuid4().hex[:8]}{ext}"
            out=target_dir/f_name                                   #link of new file
            
            #writing inside this link to create the file-writing file to disk
            with open(out,"wb") as f:
                
                #is fastapi /starlette uploadfile
                if hasattr(uf,"file") and hasattr(uf.file,"read"):
                    f.write(uf.file.read())
                    
                #generic file object
                elif hasattr(uf,"read"):
                    data=uf.read()
                    #if data returns memoryview convert to bytes else assume bytes
                    if isinstance(data,memoryview):
                        data=data.tobytes()
                    f.write(data)
                    
                else:
                    #fallback
                    buf=getattr(uf,"getbuffer",None)
                    if callable(buf):
                        data=buf()
                        if isinstance(data,memoryview):
                            data=data.tobytes()
                        f.write(data)
                    else:
                        raise ValueError("Unsupported uploaded file object; no readable interface")
            saved.append(out)
            log.info("file saved for ingestion",uploaded=name,saved_as=str(out))
        return saved
            
    except Exception as e:
        log.error(f"failed to save uploaded file",error=str(e),dir=str(target_dir))
        raise DocumentPortalException("failed to save uploaded file",e) from e
    