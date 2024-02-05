from picarx_improved import Picarx, Sensor, Interpreter, Controller
import time
import concurrent.futures
from readerwriterlock import rwlock
class Bus():
    def __init__(self):
        self.msg = "None"
        self.lock = rwlock.RWLockWriteD()
    def write(self,data ):
        with self.lock.gen_wlock():
            self.msg= data 
    def read (self):
        with self.lock.gen_rlock():
            msg = self.msg
        return msg

class Sensor_Bus():
    #producer
    def __init__(self):
        self.data = "NONE"
        self.sen = Sensor()
    
    def producer(self,sensor_bus, delay ):

        while (True):
            self.data = self.sen.sensor_reading()
            sensor_bus.write(self.data)
            time.sleep(delay)

class Interpreter_Bus():
    def __init__(self):
        self.data = "NONE"
        self.interpret = Interpreter()
    
    def consumer_producer(self, sensor_bus, interpreter_bus, delay):
        while(True):
            readings = sensor_bus.read()
            self.data = self.interpret.processing(readings)
            interpreter_bus.write(self.data)
            time.sleep(delay)

class Controller_Bus():
    def __init__(self):
        self.data = "NONE"
        self.control = Controller()
        self.px= Picarx()
    
    def consumer(self, interpreter_bus, delay):
        while(True): 
            result = interpreter_bus.read()
            angle = self.control.control_car(result)
            self.px.set_dir_servo_angle(angle)
            self.px.forward(30)
            time.sleep(delay)
             

    


if __name__ == "__main__":
    px = Picarx()
    sensor = Sensor_Bus()
    interpret = Interpreter_Bus()
    control = Controller_Bus()
    sensor_bus = Bus()
    interpreter_bus = Bus()
    control_bus = Bus()
    sensor_delay = 0.1
    interpret_delay = 0.1
    control_delay = 0.1
    start_time = time.time()
    run_time = 5
    px.set_dir_servo_angle(0)

    while(True):
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            eSensor = executor.submit(sensor.producer, sensor_bus,sensor_delay)
            eInterpreter = executor.submit(interpret.consumer_producer,sensor_bus, interpreter_bus,interpret_delay)
            eControl = executor.submit(control.consumer, interpreter_bus, control_delay)
        eSensor.result()
        eInterpreter.result()
        eControl.result()
    px.stop()
        