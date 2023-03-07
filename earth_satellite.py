import math
import os.path
import time

from sgp4.api import Satrec, WGS72, jday, SatrecArray
from sgp4 import exporter
from skyfield.api import EarthSatellite, load
import numpy as np

from tool.file_tools import get_configuration
from tool.time_tools import get_julian_from_time_str, get_datetime_from_time_str, get_julian_from_datetime, \
    get_skyfield_time_from_datetime

# jd从公历的公元前4714年11月24日12:00计算
# epoch从1949 December 31 00:00 UT计算
time_diff = 2433281.5


# https://rhodesmill.org/skyfield/earth-satellites.html#build-a-satellite-from-orbital-elements


def get_one_satrec_from_scratch(num_orbits,
                                num_sats_per_orbits,
                                num_orbit,
                                num_sat_on_orbit,
                                f,
                                jd,
                                fr,
                                ecco,
                                argpo,
                                inclo,
                                mean_motion_loop_per_day):
    """
    通过sgp4的WGS74库来初始化卫星

    :param num_orbits: 轨道数
    :param num_sats_per_orbits: 每轨卫星数
    :param num_orbit: 当前卫星的轨道, 从1开始
    :param num_sat_on_orbit: 当前卫星在轨道的编号, 从1开始
    :param f: 相位因子
    :param jd: julian day
    :param fr: jd的小数部分
    :param ecco: 偏心率
    :param argpo: 近地点辐角
    :param inclo: 轨道倾角
    :param mean_motion_loop_per_day: 卫星每天运动的天数
    """

    num_sat = (num_orbit - 1) * num_sats_per_orbits + num_sat_on_orbit

    mean_anomaly_degree = (360.0 / num_sats_per_orbits) * num_sat_on_orbit * (1 + f / num_orbits) % 360
    mean_motion_degree_minute = mean_motion_loop_per_day * 360 / (24 * 60)
    raan_degree = 360.0 / num_orbits * num_orbit

    satrec = Satrec()
    satrec.sgp4init(
        WGS72,  # gravity model
        'i',  # 'a' = old AFSPC mode, 'i' = improved mode
        num_sat,  # num_sat: Satellite number
        (jd + fr) - time_diff,  # epoch: days since 1949 December 31 00:00 UT
        0.0,  # bstar:   drag coefficient (kg/m2er)
        0.0,  # ndot: ballistic coefficient (revs/day)
        0.0,  # nndot:   second derivative of mean motion (revs/day^3)
        ecco,  # ecco: eccentricity, 偏心率
        math.radians(argpo),  # argpo: argument of perigee (radians), 近地点辐角
        math.radians(inclo),  # inclo: inclination (radians), 轨道与赤道的夹角
        math.radians(mean_anomaly_degree),  # mo: mean anomaly (radians), 平近点角
        math.radians(mean_motion_degree_minute),  # no_kozai: mean motion (radians/minute), 每分钟的弧度
        math.radians(raan_degree)  # nodeo: R.A. of ascending node (radians) RAAN: 升交点赤经
    )

    return satrec


def get_all_satrec_from_scratch(constellation_name,
                                num_orbits,
                                num_sats_per_orbits,
                                f,
                                jd,
                                fr,
                                ecco,
                                argpo,
                                inclo,
                                mean_motion_loop_per_day):
    """
    得到所有的卫星对象, 以字典返回. key: (constellation_name)_(num_orbit)_(num_sat_on_orbit)
    :param constellation_name: 星座名称
    :param num_orbits:
    :param num_sats_per_orbits:
    :param f: 相位
    :param jd: julian日期
    :param fr: julian日期小数部分
    :param ecco: 离心率
    :param argpo: 近地点辐角
    :param inclo: 轨道倾角
    :param mean_motion_loop_per_day: 卫星每天运动圈数
    :return: sat_dict, key: (constellation_name)_(num_orbit)_(num_sat_on_orbit), value: sgp4::satRec
    """
    sat_dict = {}
    for i in range(1, num_orbits + 1):
        for j in range(1, num_sats_per_orbits + 1):
            name_sat = constellation_name + '_' + str(i) + '_' + str(j)
            sat = get_one_satrec_from_scratch(num_orbits, num_sats_per_orbits, i, j, f,
                                              jd, fr, ecco, argpo, inclo, mean_motion_loop_per_day)
            sat_dict[name_sat] = sat
    return sat_dict


def get_all_skyfield_sat_from_scratch(sat_dict):
    """
    将得到的satRec对象包装为skyfield::EarthSatellite
    :param sat_dict: 存储satRec的字典
    :return: 返回字典
    """
    sat_skyfield_dict = {}
    ts = load.timescale()
    for key, value in sat_dict.items():
        sat = EarthSatellite.from_satrec(value, ts)
        sat_skyfield_dict[key] = sat

    return sat_skyfield_dict


def save_tles_to_file(sat_dict, file_name=''):
    """
    生成tle文件并保存.
    :param sat_dict: 字典, <starlink_name, satrec>
    :param file_name: 保存的文件名称, 默认为'./data/tles/当前时间(%Y-%m-%d_%H-%M-%S)_(file_name).txt
    :return:
    """
    time_str = time.strftime('%Y-%m-%d_%H-%M-%S')
    if file_name is None or '':
        file_name = 'test'
    dir_path = './data/tles/'
    file_path = dir_path + time_str + '_' + file_name + '.txt'

    file = ''
    for key, value in sat_dict.items():
        line1, line2 = exporter.export_tle(value)
        tle_line1, tle_line2 = set_right_tle(line1, line2)
        file += key + '\n' + tle_line1 + '\n' + tle_line2 + '\n'

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(file)


def set_right_tle(line1, line2):
    """
    手动矫正tle
    代码来自于https://github.com/snkas/hypatia/blob/master/satgenpy/satgen/tles/generate_tles_from_scratch.py
    :param line1:
    :param line2:
    :return:
    """
    tle_line1 = line1[:7] + "U 00000ABC " + line1[18:]
    tle_line1 = tle_line1[:68] + str(calculate_tle_line_checksum(tle_line1[:68]))
    tle_line2 = line2
    # Check that the checksum is correct
    if len(tle_line1) != 69 or calculate_tle_line_checksum(tle_line1[:68]) != int(tle_line1[68]):
        raise ValueError("TLE line 1 checksum failed")
    if len(tle_line2) != 69 or calculate_tle_line_checksum(tle_line2[:68]) != int(tle_line2[68]):
        raise ValueError("TLE line 2 checksum failed")
    return tle_line1, tle_line2


def calculate_tle_line_checksum(tle_line_without_checksum):
    if len(tle_line_without_checksum) != 68:
        raise ValueError("Must have exactly 68 characters")
    s = 0
    for i in range(len(tle_line_without_checksum)):
        if tle_line_without_checksum[i].isnumeric():
            s += int(tle_line_without_checksum[i])
        if tle_line_without_checksum[i] == "-":
            s += 1
    return s % 10



from skyfield.framelib import itrs
def save_itrs_position_to_file(skyfield_dict, start_time, end_time, timescale):
    """
    将每个时刻的坐标写入文件
    :param skyfield_dict: skyfield库卫星字典
    :param start_time: 开始时间
    :param end_time: 结束时间
    :param timescale: 时间间隔， 以ms为单位
    :return:
    """
    dir_path = './data/positions/' + time.strftime('%Y-%m-%d_%H-%M-%S')
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(dir_path + "/position.txt", 'w', encoding='utf-8') as f:
        ts = load.timescale()
        diff_sec = (end_time - start_time).total_seconds()  # 总秒数
        num = int(diff_sec * 1000 / timescale)

        t1 = get_skyfield_time_from_datetime(start_time)
        t2 = get_skyfield_time_from_datetime(end_time)
        t_array = ts.linspace(t1, t2, num)

        for tt in t_array: # 将时间间隔写入文件，[jd, fr]
            str = f'[{tt.whole}, {tt.tt_fraction}] '
            f.write(str)

        for key, value in skyfield_dict.items(): # 将坐标写入文件，[x, y, z]
            gcrs_position = value.at(t_array)
            itrs_xyz = gcrs_position.frame_xyz(itrs).km
            f.write(key + '\n')
            length = itrs_xyz[0].shape[0]
            for i in range(length):
                str = f'[{itrs_xyz[0][i]}, {itrs_xyz[1][i]}, {itrs_xyz[2][i]}] '
                f.write(str)
            f.write('\n')



def auto_create_sats(file_path='configuration.yaml'):
    result = get_configuration(file_path)
    if result['epoch'] is None:
        result['epoch'] = result['startTime']

    jd, fr = get_julian_from_datetime(result['epoch'])
    satrec_dict = get_all_satrec_from_scratch(result['name'],
                                              result['num_orbits'],
                                              result['num_sats_per_orbits'],
                                              result['f'],
                                              jd,
                                              fr,
                                              result['ecco'],
                                              result['argpo'],
                                              result['inclo'],
                                              result['mean_motion_loop_per_day'])
    skyfield_dict = get_all_skyfield_sat_from_scratch(satrec_dict)

    if result['tle_save']:
        save_tles_to_file(satrec_dict, result['name'])

    if result['position_save']:
        save_itrs_position_to_file(skyfield_dict, result['startTime'], result['endTime'], result['timescale'])

import math
if __name__ == '__main__':
     auto_create_sats()


