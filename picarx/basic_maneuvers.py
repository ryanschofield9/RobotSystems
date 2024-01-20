#import picarx_improved as improved
from picarx_improved import Picarx

import time

import logging 
logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO,
datefmt="%H:%M:%S")
logging.getLogger().setLevel(logging.DEBUG)
car = Picarx()

class Maneuvers ():
    def parallel_park():
        logging.debug("Backing up at 70 degree angle for 2 seconds")
        car.backward(100, 70)
        time.sleep(2)
        
        logging.debug("Backing up at 50 degree angle for 1 second")
        car.backward(100, 50)
        time.sleep(1)

        logging.debug("Backing up at 0 degree angle for 1 second")
        car.backward(100,0)
        time.sleep(1)

        car.stop() 
        time.sleep(1)

        logging.debug("Going forward at 10 degree angle for 1 second")
        car.forward(100, 10)
        time.sleep(1)

        logging.debug("Going forward at 0 degree angle for 1 second")
        car.forward(100, 0)
        time.sleep(1)

        car.stop()

    def three_turn():
        
        logging.debug("Going forward at 100 degree angle for 1 second")
        car.forward(100,100)
        time.sleep(1)

        car.stop()
        time.sleep(0.5)

        logging.debug("Backing up at 45 degree angle for 1 second")
        car.backward(100, 45)
        time.sleep(1)

        car.stop()
        time.sleep(0.5)

        logging.debug("Going forward at 10 degree angle for 1 second")
        car.forward(100,10)
        time.sleep(1)

        logging.debug("Going forward at 0 degree angle for 2 seconds")
        car.forward(100,0)
        time.sleep(2)
    
    def choose_move ():
        choice = input("What maneuver would you like to do? Press a for moving forwards and backwards at an angle of your choice. Press b for parallel parking. Press c for 3 point turn." )
        logging.debug("The choice is ")
        logging.debug(choice)

if __name__ == "__main__":
    time.sleep(2)
    manuevers = Maneuvers()
    logging.debug("Starting program")
    manuevers.choose_move()
    manuevers.three_turn()
    logging.debug("Finished program")
