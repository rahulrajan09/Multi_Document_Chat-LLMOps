import os
from pathlib import Path
import yaml

def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]
    """_getting the root folder where the project is situated.
        path(__file__)-gives the path of current file
        resolve()-gives absolute path
        .parents[1]-moves 2 level up from current file
    """

def load_config(config_path:str| None = None) -> dict:
    #if given in .env file load the path
    env_path=os.getenv("CONFIG_PATH")
    
    if config_path is None:                 #if config_path given use it not given then take from env file if not present use manual one
        config_path=env_path or str(_project_root()/"config"/"config.yaml")
    
    path=Path(config_path)  #converting to path object
    
    if not path.is_absolute():          #checking for absolute path if not use the provided path
        path=_project_root()/path
        
    if not path.exists():               #after confirming the path checking file exists or not in that path
        raise FileNotFoundError(f"config file not found:{path}")
    
    with open(path,"r",encoding="utf-8") as f:
        yaml.safe_load(f) or {}         # opening yaml file in safe mode if nothing present provide empty dict
    