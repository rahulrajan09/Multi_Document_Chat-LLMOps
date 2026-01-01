import os
import sys
import json
from multi_doc_chat.logger import GLOBAL_LOGGER as log
from multi_doc_chat.exception.custom_exception import DocumentPortalException
from multi_doc_chat.utils.config_loader import load_config

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama,OllamaEmbeddings
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

class ApiKeyManager:
    REQUIRED_KEYS=["GROQ_API_KEY","OPENROUTER_MODEL_KEY"]       #must have api keys
    
    def __init__(self):                             #load + validate + prepare
        self.api_keys:dict[str,str] = {}            #initialaise an empty dict for apikeys
        raw=os.getenv("APIKEY_LIVE_CLASS")          #json env file
        
        #access from json file
        if raw:
            try:
                parsed=json.loads(raw)
                if not isinstance(parsed,dict):
                    raise ValueError("API_KEYS is not a valid object")
                self.api_keys=parsed
                log.info("loaded api keys from json ecs secret")
                
            except Exception as e:
                log.warnings("Failed to pass API KEY from JSON",error=str(e))
                
        #checking required keys in loaded json if not present load individually from .env
        for key in self.REQUIRED_KEYS:
            if not self.api_keys.get(key):
                env_val=os.getenv(key)
                if env_val:
                    self.api_keys[key]=env_val          #assiging to json new api key
                    log.info(f"loaded {key} from individual env")
                    
        #check for missing values 
        missing =[k for k in self.REQUIRED_KEYS if not self.api_keys.get(k)]
        if missing:
            log.error("missing required API_key",missing_keys=missing)
            raise DocumentPortalException("Missing API Key",error_details=sys.exc_info())
        log.info("API keys loaded", keys=sorted(self.api_keys.keys()))

    def get(self,key:str) ->str:                #safe, read-only access
        val=self.api_keys.get(key)
        if not val:
            raise KeyError(f"api key for {key} is missing")
        return val
    
class ModelLoader():
    def __init__(self):
        #checking which mode operating
        VALID_ENVS = {"local", "production"}
        env_val=os.getenv("ENV","local").lower()
        if env_val not in VALID_ENVS:
            raise ValueError(f"invalid ENV value:{env_val}.Must be local or production")
        elif env_val == "local":
            load_dotenv()
            log.info("running in local mode:.env loaded")
        else:
            log.info("running in production mode")
        
        self.api_key_mgr=ApiKeyManager()
        self.config=load_config()
        log.info("Yaml config loaded",config_keys=list(self.config.keys()))
        
    def get_provider(self,env_keys:str,default_key:str,current_block:dict) -> str:
        """checks configuration in .env file with config file if not matched raise error

        Args:
            env_keys (str): Value mentioned in .env file e.g llm
            default (str): if no value in .env file then use this
            current_block (dict): current config block we are in e.g embedding block/llm block

        Returns:
            str: env file or default value or error
        """
        provider_key=os.getenv(env_keys,default_key)
        if provider_key not in current_block:
            log.error(f"{provider_key} not found in config file")
            raise ValueError(f"{provider_key} not found in config file")
        else:
            if provider_key==default_key:
                log.info(f"loaded default value {default_key}")
            else:
                log.info(f"loaded env value {provider_key}")
        
        return provider_key
        
        
    def load_embeddings(self):
        """loads and returns embedding models
        """
        try:
            
            embedding_block =self.config["embedding_model"]   #current block in config file
            provider_key=self.get_provider(env_keys="EMBEDDING_PROVIDER",default_key="ollama",current_block=embedding_block)
            
            #loading from config yaml
            emb_config = embedding_block[provider_key]              #e.g embedding_model[google]
            provider=emb_config.get("provider")                     #e.g embedding_model[google][provider]
            model_name=emb_config.get("model_name")                 #e.g embedding_model[google][model_name]
            
            log.info("Loading embedding model",provider=provider_key,model=model_name)
            
            #loading as per langchain schema using above config 
            if provider == "google":
                return GoogleGenerativeAIEmbeddings(model=model_name,
                                                    api_key=self.api_key_mgr.get("GOOGLE_API_KEY"))
            
            elif provider == "ollama":
                return OllamaEmbeddings(model=model_name,base_url=os.getenv("OLLAMA_BASE_URL"))  
        
        except Exception as e:
            log.error("failed loading embeding models")
            raise DocumentPortalException("failed to load embedding models",sys)      
        
        
    def load_llms(self):
        
        """loads and returns llm models
        """
        try:
            
            llm_block =self.config["llm"]   #current block in config file
            provider_key=self.get_provider(env_keys="LLM_PROVIDER",default_key="ollama",current_block=llm_block)
            
            #loading from config yaml
            llm_config = llm_block[provider_key]              #e.g llm_model[google]
            provider=llm_config.get("provider")                     #e.g llm_model[google][provider]
            model_name=llm_config.get("model_name")                 #e.g llm_model[google][model_name]
            temperature=llm_config.get("temperature")
            max_output_tokens=llm_config.get("max_output_tokens")
            
            log.info("Loading llm model",provider=provider_key,model=model_name)
            
            #loading as per langchain schema using above config 
            if provider == "groq":
                return ChatGroq(model=model_name,
                                api_key=self.api_key_mgr.get("GROQ_API_KEY"),
                                temperature=temperature,
                                max_tokens=max_output_tokens)
            elif provider == "openrouter":
                return ChatOpenAI(model=model_name,
                                api_key=self.api_key_mgr.get("OPENROUTER_MODEL_KEY"),
                                base_url=os.getenv("OPENROUTER_BASE_URL"),
                                temperature=temperature,
                                max_tokens=max_output_tokens)
            elif provider == "ollama_cloud":
                return ChatOllama(model=model_name,
                                api_key=self.api_key_mgr.get("OLLAMA_API_KEY"),
                                base_url=os.getenv("OLLAMA_CD_BASE_URL"),
                                temperature=temperature,
                                max_tokens=max_output_tokens)
            elif provider == "ollama":
                return ChatOllama(model=model_name,
                                base_url=os.getenv("OLLAMA_BASE_URL"),
                                temperature=temperature,
                                max_tokens=max_output_tokens)
                
        
        except Exception as e:
            log.error("failed loading embeding models")
            raise DocumentPortalException("failed to load embedding models",sys)
        
if __name__=="__main__":
    loader=ModelLoader()
    #test embedding models
    embedding=loader.load_embeddings()
    print(f"Embedding Model Loaded: {embedding}")
    result = embedding.embed_query("Hello, how are you?")
    print(f"Embedding Result: {result}")
    
    #test llm model
    llm = loader.load_llms()
    print(f"LLM Loaded: {llm}")
    result = llm.invoke("explain blackhole in 1 line.")
    print(f"LLM Result: {result.content}")
    
        
        