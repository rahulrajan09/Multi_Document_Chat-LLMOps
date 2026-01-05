from __future__ import annotations
import os
from pathlib import Path
from typing import List,Iterable

from multi_doc_chat.logger import GLOBAL_LOGGER as log
from multi_doc_chat.exception.custom_exception import DocumentPortalException

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader,Docx2txtLoader,TextLoader
from fastapi import UploadFile

SUPPORTED_EXTENSIONS={".pdf",".txt",".docx"}

def load_documents(paths:Iterable[Path]) -> List[Document]:
    """LOad documents using apprpriate loader

    Args:
        paths (Iterable[Path]): the path of file which we want to load


    Returns:
        List[Document]: convertes to langchain document objects 
    """
    
    docs:List[Document]=[]
    
    try:
        for p in paths:
            ext=p.suffix.lower()
            if ext==".pdf":
                loader=PyPDFLoader(str(p))
            elif ext== ".docx":
                loader=Docx2txtLoader(str(p))
            elif ext== ".txt":
                loader=TextLoader(str(p),encoding="utf-8")
            else:
                log.warning("Unsupported extension skipped",path=str(p))
                continue
            
            docs.extend(loader.load())
        
        log.info("Documents loaded successfully",count=len(docs))
        return docs
    
    except Exception as e:
        log.error("failed to load documents",error =str(e))
        raise DocumentPortalException("Failed loading documents",e) from e
    
class FastAPIFileAdapter:
    """Wraps one object and makes it look like another.
    adapts fastapifile UploadFile tp simple object with .name and .getbuffer
    why helpful?-
    - many libraries dont know about Fastapi uploadfile.They just want name filename(.name) and raw data(.getbuffer)
    - this adapter makes it look like that kind of object
    """
    def __init__(self,uf:UploadFile):
        """ 
        -Keeps original UploadFile internally
        - Exposes .name like a normal file objec
        """
        self._uf=uf
        self.name=uf.filename or "file"
        
    def getbuffer(self)-> bytes:
        """YOU will get contents of the file
        """
        self._uf.file.seek(0)               #moves the pointer back to beginning.ITS imp becoz file may have been read partially.
        return self._uf.file.read()        #reads entire file into memory as raw bytes