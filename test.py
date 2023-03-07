import networkx
from skyfield.api import load, EarthSatellite
from sgp4.api import Satrec, WGS72
import time
import math

from sgp4.api import Satrec, WGS72, jday, SatrecArray
from skyfield.api import EarthSatellite, load
import numpy as np
from earth_satellite import get_one_satrec_from_scratch


def test():
    # 得到skyfield的time对象
    ts = load.timescale()
    t = ts.now()
    # ts.utc(2022, 10, 24, 16, 46, 10)

    # stations_url = 'http://celestrak.com/NORAD/elements/stations.txt'
    stations_url = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle'
    groupName = 'starlink-all'  # 星座名称
    epochTimeStr = '2023-2-24 11:30:00'  # 输入仿真的时间格式

    now = int(time.time())
    timeArr = time.localtime(now)
    timeStr = time.strftime("%Y-%m-%d_%H-%M-%S", )

    tleFileName = './data/' + timeStr + '_' + groupName + ".txt"
    print(tleFileName)
    satellites = load.tle_file(stations_url, filename=tleFileName)  # list<EarthSatellite>

    # by_name = {sat.name for sat in satellites}
    # satellite = by_name

    oneSat = satellites[0]
    geocentric = oneSat.at(t)

import yaml
from tool.file_tools import get_configuration
def test_yaml():
    # with open('configuration.yaml', 'r', encoding='utf-8') as f:
    #     result = yaml.load(f.read(), Loader=yaml.FullLoader)

    # a = result['test']
    # print(a)
    result = get_configuration()
    print(result['epoch'])
    print(result['startTime'])
    if result['tle_save']:
        print(result['tle_save'])


def test_earth():
    jd_list = []
    fr_list = []
    for sec in range(0, 30):
        jd, fr = jday(2023, 2, 27, 11, 3, sec)
        jd_list.append(jd)
        fr_list.append(fr)

    num_orbits = 72
    num_sats_per_orbits = 22
    sat_list = []
    for i in range(1, num_orbits+1):
        for j in range(1, num_sats_per_orbits+1):
            num_sat = i * num_orbits + j
            sat = get_one_satrec_from_scratch(num_orbits, num_sats_per_orbits, num_sat, 45,
                                          jd_list[0], fr_list[0], 0.0001, 90, 53, 15.06)
            sat_list.append(sat)

    np.set_printoptions(precision=2)
    a = SatrecArray(sat_list)
    jd_np = np.array(jd_list)
    fr_np = np.array(fr_list)
    e, r, v = a.sgp4(jd_np, fr_np)

    # with open("./data/distance.txt", 'w') as f:
    #     f.write(r)

    print(r.shape)
    print(type(r[0][0]))
    print(r)

def get_position_on_teme(sat_dict, start_time, end_time, timescale):

    sat_dict.values()
    ts = load.timescale()
    ts.linspace()





if __name__ == '__main__':
    test_yaml()