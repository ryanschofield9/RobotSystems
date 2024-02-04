from picarx_improved import Picarx

px = Picarx()

class Bus():
    def __init__(self):
        self.msg = "None"
    def write(self,data ):
        self.msg = data 
    def read (self):
        return self.msg

class Sensor():
    #producer
    def __init__(self):
        self.data = "NONE"
        self.sensor_bus = Bus()

    def send_data(self, data):
       
        return self.sensor_bus

class interpretation():
    def __init__(self):
        pass

if __name__ == "__main__":
    sensor_bus = Bus()
    sensor_bus.write("hello")
    control_bus = Bus()
    control_bus.write(6)
    print(sensor_bus.read())
    print(control_bus.read())
        