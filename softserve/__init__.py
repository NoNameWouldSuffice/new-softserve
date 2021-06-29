from .Jackbord import Jackbord
from .credLoader import CredLoader
import softserve

def importCreds(username, password):
    cl = CredLoader()
    cl.importCreds(username, password)

setattr(softserve, "importCreds", importCreds)

__version__ = "12.2.0"
