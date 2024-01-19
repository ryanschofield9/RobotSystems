import picarx_improved as improved

import time

import logging 
logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO,
datefmt="%H:%M:%S")
logging.getLogger().setLevel(logging.DEBUG)

if __name__ == "__main__":
    logging.debug("Starting program")
    improved.forward(50, 0)
    time.sleep(2)
    improved.stop 
