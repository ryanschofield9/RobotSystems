#import picarx_improved as improved
from picarx_improved import Picarx

import time

import logging 
logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO,
datefmt="%H:%M:%S")
logging.getLogger().setLevel(logging.DEBUG)

if __name__ == "__main__":
    car = Picarx()
    logging.debug("Starting program")
    car.forward(50, 0)
    time.sleep(2)
    car.stop() 
