from .Jackbord import Jackbord
from .credLoader import CredLoader
import softserve

def importCreds():
    cl = CredLoader()
    cl.importCreds()

setattr(softserve, "importCreds", importCreds)

__version__ = "12.2.0"
