import yaml


def get_configuration(filename):
    """
    得到配置文件
    :param filename: 配置文件路径
    :return: 字典
    """
    with open(filename, 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)

    return result
