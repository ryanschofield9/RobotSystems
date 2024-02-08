from picarx_improved import Picarx, Sensor, Interpreter, Controller, SensorUltra, InterpreterUltra, ControllerUltra, ControllerCombined
import rossros as rr 
import logging
import time

logging.getLogger().setLevel(logging.INFO)

#initiate buses 

grySensor = Sensor()
gryInt = Interpreter()
gryControl = Controller()

ultSensor = SensorUltra()
ultInt = InterpreterUltra()
ultControl = ControllerUltra()

controlCom = ControllerCombined()

grayscale_sensor = rr.Bus(grySensor.sensor_reading(), "grayscale_bus")
interpreter_gray = rr.Bus(gryInt.processing(grySensor.sensor_reading()), "interpreter gray bus") 
control_grey = rr.Bus(gryControl.control_car(gryInt.processing(grySensor.sensor_reading())), "controller_gray_bus")
ultra_sensor = rr.Bus(ultSensor.sensor_reading(), "ultra_bus")
interpreter_ultra = rr.Bus(ultInt.processing(ultSensor.sensor_reading()), "interpreter ultra bus")
control_ultra = rr.Bus(ultControl.control_car(ultInt.processing(ultSensor.sensor_reading())), "controller_ult_bus")
control = rr.Bus(controlCom.control_car(gryInt.processing(grySensor.sensor_reading()), ultInt.processing(ultSensor.sensor_reading())))
terminate = rr.Bus(0, "Terminate Bus")

produceSignal = rr.Producer(grySensor.sensor_reading, grayscale_sensor, 0.05, terminate, "Produce grapyscale sensor signal")
prodConIntGray = rr.ConsumerProducer(gryInt.processing, grayscale_sensor, interpreter_gray, 0.1, terminate, "Producer Consumer Interpreter gray scale")
consumerControl = rr.Consumer(gryControl.control_car, interpreter_gray, 0.1, terminate, "Consumer grayscale controler" )
produceSignalUlt = rr.Producer(ultSensor.sensor_reading, ultra_sensor, 0.05, terminate, "Produce ultra sensor signal" )
prodConIntUlt = rr.ConsumerProducer(ultInt.processing, ultra_sensor, interpreter_ultra, 0.1,terminate, "Produce Consumer Interpreter ultra" )
contCombined = rr.Consumer (controlCom.control_car,[interpreter_gray, interpreter_ultra], 0.1, terminate, "Consumer Combined Control" )
consuControlUlt = rr.Consumer(ultControl.control_car,interpreter_ultra, 0.1, terminate, "consumer ultra bus" )

# (grayscale_sensor, interpreter_gray, ultra_sensor, interpreter_ultra, control, terminate)

printBuses = rr.Printer(
    (grayscale_sensor, interpreter_gray, ultra_sensor, interpreter_ultra, terminate), 
    1,  # delay between printing cycles
    terminate,  # bus to watch for termination signal
    "Print bus data",  # Name of printer
    "Bus readings are: ")  # Prefix for output

terminationTimer = rr.Timer(
    terminate,  # Output data bus
    5,  # Duration
    0.01,  # Delay between checking for termination time
    terminate,  # Bus to check for termination signal
    "Termination timer")  # Name of this timer

producer_consumer_list = [produceSignal, 
                          prodConIntGray, 
                          produceSignalUlt, 
                          prodConIntUlt, 
                          consuControlUlt,
                          terminationTimer]

# Execute the list of producer-consumers concurrently
rr.runConcurrently(producer_consumer_list)
