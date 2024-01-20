#import picarx_improved as improved
from picarx_improved import Picarx

import time

import logging 
logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO,
datefmt="%H:%M:%S")
logging.getLogger().setLevel(logging.DEBUG)
car = Picarx()

def parallel_park():
    car.backward(100, 70)
    time.sleep(2)
    
    car.backward(100, 50)
    time.sleep(1)

    car.backward(100,0)
    time.sleep(1)

    car.stop() 
    time.sleep(1)
    
    car.forward(100, 10)
    time.sleep(1)
    car.forward(100, 0)
    time.sleep(1)
    car.stop()

def three_turn():
    car.forward(100,100)
    time.sleep(1)

    car.stop()
    time.sleep(0.5)

    car.backward(100, 45)
    time.sleep(1)

    car.stop()
    time.sleep(0.5)

    car.forward(100,10)
    time.sleep(1)

    car.forward(100,0)
    time.sleep(2)

if __name__ == "__main__":
    time.sleep(2)
    logging.debug("Starting program")
    
    logging.debug("Finished program")
