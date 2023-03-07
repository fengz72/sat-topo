import time
from skyfield.api import load
from sgp4.api import jday
from datetime import datetime

epochTimeStr = '2023-2-24 11:30:00'  # 输入仿真的时间格式


def get_filename_time(std_str_time):
    """得到2023-02-24_14-00-00形式的时间字符串"""
    struct_time = get_struct_time_from_std_str_time(std_str_time)
    filename_time = time.strftime('%Y-%m-%d_%H-%M-%S', struct_time)
    return filename_time


def get_struct_time_from_std_str_time(std_str_time):
    """输出格式化时间元组"""
    return time.strptime(std_str_time, "%Y-%m-%d %H:%M:%S")


def get_skyfield_time(std_str_time):
    """得到skyfield库中的时间"""
    struct_time = get_struct_time_from_std_str_time(std_str_time)
    ts = load.timescale()
    t = ts.utc(struct_time.tm_year,
               struct_time.tm_mon,
               struct_time.tm_mday,
               struct_time.tm_hour,
               struct_time.tm_min,
               struct_time.tm_sec)
    return t


def get_jd_and_fr(std_str_time):
    """得到julian的JDN+0.5和分数, JD = jd + fr"""
    struct_time = get_struct_time_from_std_str_time(std_str_time)
    jd, fr = jday(struct_time.tm_year,
                  struct_time.tm_mon,
                  struct_time.tm_mday,
                  struct_time.tm_hour,
                  struct_time.tm_min,
                  struct_time.tm_sec)
    return jd, fr


def get_datetime_from_time_str(time_str):
    return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")


def get_julian_from_time_str(time_str):
    """
    得到julian时间
    :param time_str:
    :return: jd, fr
    """
    date_time = get_datetime_from_time_str(time_str)
    jd, fr = get_julian_from_datetime(date_time)
    return jd, fr


def get_julian_from_datetime(date_time):
    """
    得到julian时间
    :param date_time:
    :return: jd, fr
    """
    t = get_skyfield_time_from_datetime(date_time)
    jd = t.whole
    fr = t.tt_fraction
    return jd, fr


def get_skyfield_time_from_datetime(date_time):
    ts = load.timescale()
    t = ts.utc(date_time.year, date_time.month,
               date_time.day, date_time.hour,
               date_time.minute, date_time.second)
    return t
