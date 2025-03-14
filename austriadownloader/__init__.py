from austriadownloader.download import download

__all__ = ["download"]

# Dynamic version import
import importlib.metadata

__version__ = importlib.metadata.version("austriadownloader")