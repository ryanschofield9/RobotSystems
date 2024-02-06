from picarx_improved import Picarx, Sensor, Interpreter, Controller
import rossros as rr 
import logging
import time

logging.getLogger().setLevel(logging.INFO)

#initiate buses 

grySensor = Sensor()
gryInt = Interpreter()
gryControl = Controller()

grayscale_sensor = rr.Bus(grySensor.sensor_reading(), "grayscale_bus")
interpreter_gray = rr.Bus(gryInt.processing(Sensor.sensor_reading()), "interpreter gray bus") 
control_grey = rr.Bus(gryControl.control_car(Interpreter.processing(Sensor.sensor_reading())), "controller_gray_bus")
terminate = rr.Bus(0, "Terminate Bus")

produceSignal = rr.Producer(Sensor.sensor_reading(), grayscale_sensor, 0.05, terminate, "Produce grapyscale sensor signal")
prodConIntGray = rr.ConsumerProducer(Interpreter.processing(), grayscale_sensor, interpreter_gray, 0.1, terminate, "Producer Consumer Interpreter gray scale")
consumerControl = rr.Consumer(Controller.control_car(), interpreter_gray, 0.1, terminate, "Consumer grayscale controler" )

printBuses = rr.Printer(
    (grayscale_sensor, interpreter_gray, control_grey, terminate),
    1,  # delay between printing cycles
    terminate,  # bus to watch for termination signal
    "Print bus data",  # Name of printer
    "Bus readings are: ")  # Prefix for output

terminationTimer = rr.Timer(
    terminate,  # Output data bus
    3,  # Duration
    0.01,  # Delay between checking for termination time
    terminate,  # Bus to check for termination signal
    "Termination timer")  # Name of this timer

producer_consumer_list = [produceSignal, 
                          prodConIntGray, 
                          consumerControl,
                          printBuses,
                          terminationTimer]

# Execute the list of producer-consumers concurrently
rr.runConcurrently(producer_consumer_list)
