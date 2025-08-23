# fantasio/__init__.py
import sys
sys.modules['fantasio'] = sys.modules[__name__]

version = "0.1.2"

from . import automatic
from . import interactive
from . import fantasio
from . import auto
from . import inter
from . import GUI_functions
from . import fitting_GUI_functions as ff


