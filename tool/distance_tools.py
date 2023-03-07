import math


def get_distance_from_xyz(x, y, z):
    return math.sqrt(x**2+y**2+z**2)


def get_distance_from_array(distance_array):
    return get_distance_from_xyz(distance_array[0], distance_array[1], distance_array[2])
