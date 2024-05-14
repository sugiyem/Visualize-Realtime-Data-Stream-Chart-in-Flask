# Example random_nr data stream
from data_stream import Config
from random import random
from random import randrange

def random_loc():
    x = randrange(0, 100) / 100
    y = x ** 2
    return [x, y] + [round(random() * 10, 3) for _ in range(6)]

random_loc_config = Config(_name = "Location Stream")