#import picarx_improved as improved
from picarx_improved import Picarx

import time

import logging 
logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO,
datefmt="%H:%M:%S")
logging.getLogger().setLevel(logging.INFO)
car = Picarx()

class Maneuvers ():
    def parallel_park(self):
        logging.debug("Backing up at 70 degree angle for 2 seconds")
        car.backward(100, 85)
        time.sleep(2)
        
        logging.debug("Backing up at 50 degree angle for 1 second")
        car.backward(100, 55)
        time.sleep(1)
        '''
        logging.debug("Backing up at 0 degree angle for 1 second")
        car.backward(100,0)
        time.sleep(1)
        '''
        car.stop() 
        time.sleep(1)

        logging.debug("Going forward at 10 degree angle for 1 second")
        car.forward(100, 10)
        time.sleep(0.5)

        logging.debug("Going forward at 0 degree angle for 1 second")
        car.forward(100, 0)
        time.sleep(0.5)
        
        car.stop()

    def three_turn(self):
        
        logging.debug("Going forward at 90 degree angle for 3 second")
        car.forward(100,90)
        time.sleep(3)
        
        car.stop()
        time.sleep(0.5)

        logging.debug("Backing up at 0 degree angle for 2 second")
        car.backward(100, 0)
        time.sleep(2)

        car.stop()
        time.sleep(0.5)
        
        logging.debug("Going forward at 90 degree angle for 2.5 seconds")
        car.forward(100,90)
        time.sleep(3)
           
        logging.debug("Going forward at 0 degree angle for 1 second")
        car.forward(100,0)
        time.sleep(1)
        
        car.stop()
        
        
    
    def choose_move (self):
        choice = input("What maneuver would you like to do? Press a for moving forwards and backwards at an angle of your choice. Press b for parallel parking. Press c for 3 point turn. Press x to cancel: " )
        while (choice != 'x'): 
            if choice == 'a':
                angle = input("What angle (degrees): ")
                car.forward(100,int(angle))
                time.sleep(1)
                car.stop()
                car.backward(100, int(angle))
                time.sleep(1)
                car.stop()
            elif choice == 'b':
                self.parallel_park()
            elif choice == 'c':
                self.three_turn()
            else: 
                car.stop()
                exit()
            choice = input("What maneuver would you like to do? Press a for moving forwards and backwards at an angle of your choice. Press b for parallel parking. Press c for 3 point turn. Press x to cancel: " )
        logging.debug("out of while")

if __name__ == "__main__":
    manuevers = Maneuvers()
    logging.debug("Starting program")
    #manuevers.choose_move()
    car.forward(100,0)
    car.backward(100,0)
    logging.debug("Finished program")
