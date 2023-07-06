import logging
from enum import Enum

_LOGGER = logging.getLogger(__name__)

class Namespace(Enum):
    # Common abilities
    SYSTEM_ALL = 'Appliance.System.All'
    SYSTEM_ABILITY = 'Appliance.System.Ability'


    CONTROL_TOGGLEX = 'Appliance.Control.ToggleX'

