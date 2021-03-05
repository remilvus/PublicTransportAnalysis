from utilities import constants as const


# time formatting
def fix_time(t):
    """
    :param t: time of day in seconds
    :return: `t` in interval [0, 24*60*60)
    """
    return t % const.SEC_IN_DAY


def human_time(t):
    """
    :param t: time of day in seconds
    :return: time in human-readable format
    """
    hour = t // 3600
    minute = int(t / 60) % 60
    if hour < 10:
        hour = f"0{hour}"
    if minute < 10:
        minute = f"0{minute}"
    return f"{hour}:{minute}"
