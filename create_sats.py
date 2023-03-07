import math

from sgp4.api import Satrec, WGS72, jday, SatrecArray
from sgp4 import exporter
from skyfield.api import EarthSatellite, load

from tool.file_tools import get_configuration

def create_sats(file_path = 'configuration.yaml'):
    result = get_configuration(file_path)

