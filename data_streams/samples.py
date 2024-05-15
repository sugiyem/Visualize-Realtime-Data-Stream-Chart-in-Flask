# Example random_nr data stream
from data_stream import Config
import random
import math 

count = 0

def random_loc():
    global count 
    count += 1
    x = math.sin(math.pi * count / 20) + random.normalvariate(0., 1e-2)
    y = x ** 2 + random.normalvariate(0., 1e-2)
    return [x, y] + [round(random.random() * 10, 3) for _ in range(6)]

random_loc_config = Config(_name = "Location Stream", xmin = -2.0, xmax = 2.0, ymin = -2.0, ymax = 2.0)