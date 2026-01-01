
try:
    #  Preferred, correct file
    from .custom_logger import CustomLogger
except ImportError:
    # Backward compatibility only
    from .custom_logger import CustomLogger

# Expose a single global logger across the codebase
GLOBAL_LOGGER = CustomLogger().get_logger(__name__)