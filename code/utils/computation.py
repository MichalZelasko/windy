from math import floor

def extract_time(filename):
    filename_splits = filename.split("_")
    hours = int(filename_splits[-2])
    last_split = filename_splits[-1]
    minutes_string = last_split.split(".")[0]
    if minutes_string[0] == "0":
        minutes_string = minutes_string[1:]
    minutes = int(minutes_string)
    return 60 * hours + minutes

def hash_position(x, y):
    return 1500 * x + y
    # return int(hash(1500 * x + y)) % 1000

def time_to_titles(t):
    if t >= 100:
        retval = str(t)
    elif t >= 10:
        retval = "0" + str(t)
    else:
        retval = "00" + str(t)
    return retval

def time_to_minutes(t):
    if t >= 10:
        retval = str(t)
    else:
        retval = "0" + str(t)
    return retval

def time_to_filename(t):
    h = floor(t / 61)
    m = t - 60 * h
    return "Map_" + str(h) + "_" + time_to_minutes(m) + ".png"