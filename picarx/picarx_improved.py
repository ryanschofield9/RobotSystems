
#from robot_hat import Pin, ADC, PWM, Servo, fileDB
import time
try:
    from robot_hat import *
    from robot_hat import reset_mcu
    reset_mcu()
    time.sleep(0.01)
except ImportError:
    print("This computer does not appear to be a PiCar-X system (robot_hat is not present). Shadowing hardware calls with substitute functions")
    from sim_robot_hat import *
#from robot_hat import Grayscale_Module, Ultrasonic
#from robot_hat.utils import reset_mcu, run_command
import os
import atexit
import logging 
logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO,
datefmt="%H:%M:%S")
logging.getLogger().setLevel(logging.DEBUG)

#from camera_driving import Controller_Cam
# reset robot_hat
#reset_mcu()
#time.sleep(0.2)
import numpy

def constrain(x, min_val, max_val):
    '''
    Constrains value to be within a range.
    '''
    return max(min_val, min(max_val, x))

class Picarx(object):
    CONFIG = '/opt/picar-x/picar-x.conf'

    DEFAULT_LINE_REF = [1000, 1000, 1000]
    DEFAULT_CLIFF_REF = [500, 500, 500]

    DIR_MIN = -30
    DIR_MAX = 30
    CAM_PAN_MIN = -90
    CAM_PAN_MAX = 90
    CAM_TILT_MIN = -35
    CAM_TILT_MAX = 65

    PERIOD = 4095
    PRESCALER = 10
    TIMEOUT = 0.02

    # servo_pins: camera_pan_servo, camera_tilt_servo, direction_servo
    # motor_pins: left_swicth, right_swicth, left_pwm, right_pwm
    # grayscale_pins: 3 adc channels
    # ultrasonic_pins: tring, echo2
    # config: path of config file
    def __init__(self, 
                servo_pins:list=['P0', 'P1', 'P2'], 
                motor_pins:list=['D4', 'D5', 'P12', 'P13'],
                grayscale_pins:list=['A0', 'A1', 'A2'],
                ultrasonic_pins:list=['D2','D3'],
                config:str=CONFIG,
                ):

        # --------- config_flie ---------
        self.config_flie = fileDB(config, 774, os.getlogin())

        # --------- servos init ---------
        self.cam_pan = Servo(servo_pins[0])
        self.cam_tilt = Servo(servo_pins[1])   
        self.dir_servo_pin = Servo(servo_pins[2])
        # get calibration values
        self.dir_cali_val = float(self.config_flie.get("picarx_dir_servo", default_value=0))
        self.cam_pan_cali_val = float(self.config_flie.get("picarx_cam_pan_servo", default_value=0))
        self.cam_tilt_cali_val = float(self.config_flie.get("picarx_cam_tilt_servo", default_value=0))
        # set servos to init angle
        self.dir_servo_pin.angle(self.dir_cali_val)
        self.cam_pan.angle(self.cam_pan_cali_val)
        self.cam_tilt.angle(self.cam_tilt_cali_val)

        # --------- motors init ---------
        self.left_rear_dir_pin = Pin(motor_pins[0])
        self.right_rear_dir_pin = Pin(motor_pins[1])
        self.left_rear_pwm_pin = PWM(motor_pins[2])
        self.right_rear_pwm_pin = PWM(motor_pins[3])
        self.motor_direction_pins = [self.left_rear_dir_pin, self.right_rear_dir_pin]
        self.motor_speed_pins = [self.left_rear_pwm_pin, self.right_rear_pwm_pin]
        # get calibration values
        self.cali_dir_value = self.config_flie.get("picarx_dir_motor", default_value="[1, 1]")
        self.cali_dir_value = [int(i.strip()) for i in self.cali_dir_value.strip().strip("[]").split(",")]
        self.cali_speed_value = [0, 0]
        self.dir_current_angle = 0
        # init pwm
        for pin in self.motor_speed_pins:
            pin.period(self.PERIOD)
            pin.prescaler(self.PRESCALER)

        # --------- grayscale module init ---------
        adc0, adc1, adc2 = [ADC(pin) for pin in grayscale_pins]
        self.grayscale = Grayscale_Module(adc0, adc1, adc2, reference=None)
        # get reference
        self.line_reference = self.config_flie.get("line_reference", default_value=str(self.DEFAULT_LINE_REF))
        self.line_reference = [float(i) for i in self.line_reference.strip().strip('[]').split(',')]
        self.cliff_reference = self.config_flie.get("cliff_reference", default_value=str(self.DEFAULT_CLIFF_REF))
        self.cliff_reference = [float(i) for i in self.cliff_reference.strip().strip('[]').split(',')]
        # transfer reference
        #self.grayscale.reference(self.line_reference)

        # --------- ultrasonic init ---------
        tring, echo= ultrasonic_pins
        self.ultrasonic = Ultrasonic(Pin(tring), Pin(echo))
        
         # --------- atexit registering ---------
        atexit.register(self.stop)
        
    def set_motor_speed(self, motor, speed):
        ''' set motor speed
        
        param motor: motor index, 1 means left motor, 2 means right motor
        type motor: int
        param speed: speed
        type speed: int      
        '''
        speed = constrain(speed, -100, 100)
        motor -= 1
        if speed >= 0:
            direction = 1 * self.cali_dir_value[motor]
        elif speed < 0:
            direction = -1 * self.cali_dir_value[motor]
        speed = abs(speed)
        #if speed != 0:
            #speed = int(speed /2 ) + 50
        #speed = speed - self.cali_speed_value[motor]
        if direction < 0:
            self.motor_direction_pins[motor].high()
            self.motor_speed_pins[motor].pulse_width_percent(speed)
        else:
            self.motor_direction_pins[motor].low()
            self.motor_speed_pins[motor].pulse_width_percent(speed)

    def motor_speed_calibration(self, value):
        self.cali_speed_value = value
        if value < 0:
            self.cali_speed_value[0] = 0
            self.cali_speed_value[1] = abs(self.cali_speed_value)
        else:
            self.cali_speed_value[0] = abs(self.cali_speed_value)
            self.cali_speed_value[1] = 0

    def motor_direction_calibrate(self, motor, value):
        ''' set motor direction calibration value
        
        param motor: motor index, 1 means left motor, 2 means right motor
        type motor: int
        param value: speed
        type value: int
        '''      
        motor -= 1
        if value == 1:
            self.cali_dir_value[motor] = 1
        elif value == -1:
            self.cali_dir_value[motor] = -1
        self.config_flie.set("picarx_dir_motor", self.cali_dir_value)

    def dir_servo_calibrate(self, value):
        self.dir_cali_val = value
        self.config_flie.set("picarx_dir_servo", "%s"%value)
        self.dir_servo_pin.angle(value)

    def set_dir_servo_angle(self, value):
        self.dir_current_angle = constrain(value, self.DIR_MIN, self.DIR_MAX)
        angle_value  = self.dir_current_angle + self.dir_cali_val
        self.dir_servo_pin.angle(angle_value)

    def cam_pan_servo_calibrate(self, value):
        self.cam_pan_cali_val = value
        self.config_flie.set("picarx_cam_pan_servo", "%s"%value)
        self.cam_pan.angle(value)

    def cam_tilt_servo_calibrate(self, value):
        self.cam_tilt_cali_val = value
        self.config_flie.set("picarx_cam_tilt_servo", "%s"%value)
        self.cam_tilt.angle(value)

    def set_cam_pan_angle(self, value):
        value = constrain(value, self.CAM_PAN_MIN, self.CAM_PAN_MAX)
        self.cam_pan.angle(-1*(value + -1*self.cam_pan_cali_val))

    def set_cam_tilt_angle(self,value):
        value = constrain(value, self.CAM_TILT_MIN, self.CAM_TILT_MAX)
        self.cam_tilt.angle(-1*(value + -1*self.cam_tilt_cali_val))

    def set_power(self, speed):
        self.set_motor_speed(1, speed)
        self.set_motor_speed(2, speed)

    def backward(self, speed): 
        current_angle = self.dir_current_angle
        if current_angle != 0:
            abs_current_angle = abs(current_angle)
            if abs_current_angle > self.DIR_MAX:
                abs_current_angle = self.DIR_MAX
            power_scale = (100 - abs_current_angle) / 100.0 
            #power_scale = numpy.arctan(4*numpy.tan(current_angle)/(4+0.5*6 *numpy.tan(current_angle )))
            if (current_angle / abs_current_angle) > 0:
                self.set_motor_speed(1, -1*speed)
                self.set_motor_speed(2, speed * power_scale)
            else:
                self.set_motor_speed(1, -1*speed * power_scale)
                self.set_motor_speed(2, speed )
        else:
            self.set_motor_speed(1, -1*speed)
            self.set_motor_speed(2, speed)  
            

    def forward(self, speed):
        current_angle = self.dir_current_angle
        if current_angle != 0:
            abs_current_angle = abs(current_angle)
            if abs_current_angle > self.DIR_MAX:
                abs_current_angle = self.DIR_MAX
            #power_scale = (100 - abs_current_angle) / 100.0
            power_scale = numpy.arctan(4*numpy.tan(current_angle)/(4+0.5*6 *numpy.tan(current_angle )))
            
            if (current_angle / abs_current_angle) > 0:
                self.set_motor_speed(1, 1*speed * power_scale)
                self.set_motor_speed(2, -speed) 
            else:
                self.set_motor_speed(1, speed)
                self.set_motor_speed(2, -1*speed * power_scale)
        else:
            self.set_motor_speed(1, speed)
            self.set_motor_speed(2, -1*speed)                  

    def stop(self):
        '''
        Execute twice to make sure it stops
        '''
        for _ in range(2):
            self.motor_speed_pins[0].pulse_width_percent(0)
            self.motor_speed_pins[1].pulse_width_percent(0)
            time.sleep(0.002)

    def get_distance(self):
        return self.ultrasonic.read()

    def set_grayscale_reference(self, value):
        if isinstance(value, list) and len(value) == 3:
            self.line_reference = value
            self.grayscale.reference(self.line_reference)
            self.config_flie.set("line_reference", self.line_reference)
        else:
            raise ValueError("grayscale reference must be a 1*3 list")

    def get_grayscale_data(self):
        return list.copy(self.grayscale.read())

    def get_line_status(self,gm_val_list):
        return self.grayscale.read_status(gm_val_list)

    def set_line_reference(self, value):
        self.set_grayscale_reference(value)

    def get_cliff_status(self,gm_val_list):
        for i in range(0,3):
            if gm_val_list[i]<=self.cliff_reference[i]:
                return True
        return False

    def set_cliff_reference(self, value):
        if isinstance(value, list) and len(value) == 3:
            self.cliff_reference = value
            self.config_flie.set("cliff_reference", self.cliff_reference)
        else:
            raise ValueError("grayscale reference must be a 1*3 list")

#controller_cam = Controller_Cam()

class Sensor():
    def __init__(self):
       self.grayscale_pin_r = ADC('A0')
       self.grayscale_pin_m = ADC('A1')
       self.grayscale_pin_l = ADC('A2')
       self.grayscale = Grayscale_Module(self.grayscale_pin_r, self.grayscale_pin_m, self.grayscale_pin_l, reference=None)
    
    def sensor_reading(self):
        #print("in sensor")
        return (self.grayscale.read())


class Interpreter():
    def __init__(self, sensitivity_given:float = 0.25, 
                 polarity_given:int = 1):
        self.sensitivity= sensitivity_given
        self.polarity = polarity_given
        self.dif = [0, 0, 0]
        self.norm = [0, 0, 0]
        self.significant = [0, 0, 0] 
    
    def processing(self,values): 
        #print("in interpreter")
        self.val_l = values[0]
        self.val_m = values[1]
        self.val_r = values[2]
        
        #self.val_l = 800
        #self.val_m = 800
        #self.val_r = 800

        self.avg = (self.val_l + self.val_m + self.val_r)/3
        self.dif[0] = self.val_l - self.avg
        self.dif[1] = self.val_m - self.avg 
        self.dif[2] = self.val_r - self.avg 

        self.norm[0]= abs(self.dif[0]/ self.avg)
        self.norm[1] = abs(self.dif[1]/self.avg)
        self.norm[2] = abs(self.dif[2]/self.avg)
    
        self.is_significant()
        #print(self.significant)
        #logging.DEBUG(self.significant)
        self.changes()
        self.get_results() 
        #print(self.significant)
        #logging.DEBUG(self.significant)
        
        return self.result 
    
    def is_significant (self):
        self.significant = [0, 0, 0] 
        for i, x in enumerate (self.norm):
            if x > self.sensitivity:
                self.significant[i] = 1


    def changes (self):
        
        self.changed = False
        if self.significant == [0, 0, 0]:
            pass 
        elif self.significant == [0, 1, 0]:
            pass 
        elif self.polarity == 1: # The line is darker than the floor (lighter == higher readings)
            for i,x in enumerate(self.significant): 
                if x == 1 and self.changed == False:
                    if self.dif[i] > 0: 
                        self.switch()
                        self.changed == True
        else: # The line is lighter than the floor (darker == lower )
            for i,x in enumerate(self.significant): 
                if x == 1 and self.changed == False:
                    if self.dif[i] < 0: 
                        self.switch()
                        self.changed == True 

    def switch(self):
        for i,x in enumerate(self.significant):
            if x == 0: 
                self.significant[i] = 1
            else: 
                self.significant[i] = 0 

    def get_results(self):
        self.add = 0
        if self.significant == [0, 1, 0]:
            self.result = 0 
        else: 
            for i,x in enumerate(self.significant):
                if x == 1: 
                    self.add = self.add + 1
            if self.add == 0: 
                self.result = 0 
            elif self.add == 1: 
                if self.significant[0] == 1:
                    self.result = -0.5 # just left side is off 
                else: 
                    self.result = 0.5 # just right side is off 
            else: 
                if self.significant[0] == 1:
                    self.result = -1 # left side and middle is off 
                else: 
                    self.result = 1 # right side and middle is off 


class Controller(): 
    def __init__(self, scaling_factor_given:float = 1.0):
         self.scaling_factor = scaling_factor_given
         self.px = Picarx()
         
    def control_car(self, result):
        #print("in controller")
        #result = value in range [-1, 1] 
        # -1 means really far left from line 
        # -0.5 means a little left from line 
        # 0 means straight on line 
        # 0.5 means a little right from line 
        # 1 means really far right from line 
        if result == -1: 
            angle = self.scaling_factor * 40
        elif result == -0.5: 
            angle = self.scaling_factor * 20
        elif result == 0: 
            angle = 0
        elif result == 0.5: 
            angle = self.scaling_factor * -40
        else: 
            angle = self.scaling_factor * -20

        self.px.set_dir_servo_angle(angle)
        self.px.forward(25)
        
        return angle 


class SensorUltra():
    def __init__(self):
        tring, echo= ['D2','D3']
        self.ultrasonic = Ultrasonic(Pin(tring), Pin(echo))

    def sensor_reading(self):
        #print("in ultra_sonic_sensor")
        #print(self.ultrasonic.read())
        return self.ultrasonic.read()


class InterpreterUltra():
    def __init__(self):
        self.distance = 0
        self.result = 0 
    def processing(self, distance):
        #print("in processing ultra")
        self.distance = distance 
        if self.distance < 8: 
            self.result = 0
        elif self.distance < 15: 
            self.result = 0.5 
        else: 
            self.result = 1 
        
        return self.result 

class ControllerUltra():
    def __init__(self, scaling_factor_given:float = 1.0):
        self.scaling_factor = scaling_factor_given
        self.px = Picarx()
        self.result = 0 
        self.speed = 40 
    
    def control_car(self, result):
        print("in ultrasonic control")
        self.result = result 
        self.px.forward(self.speed*result)

class ControllerCombined (): 
    def __init__(self):
        self.px = Picarx()
        self.result = 0 
        self.speed = 30 
    
    def control_car(self, result_gry, result_ult):
        print("in controller combined")
        print (result_ult)
        print(result_ult*self.speed)
        if result_gry == -1: 
            angle =  40
        elif result_gry == -0.5: 
            angle =  20
        elif result_gry == 0: 
            angle = 0
        elif result_gry == 0.5: 
            angle =  -40
        else: 
            angle =  -20

        self.px.set_dir_servo_angle(angle)
        self.px.forward(result_ult*self.speed)
        print("end")

        return angle


        



def follow_line(px, sensor, interpret, controller):
    reading = sensor.sensor_reading()
    #logging.DEBUG( f"reading:{reading}")
    result = interpret.processing(reading)
    angle = controller.control_car(result)
    #logging.DEBUG(angle)
    px.set_dir_servo_angle(angle) 
    px.forward(30)
    time.sleep(0.0)

'''
def follow_line_cam():
    angle = controller_cam.control_car()
    px.set_dir_servo_angle(angle)
    px.forward(25)
    time.sleep(0.05)
''' 

if __name__ == "__main__":

    px=Picarx()
    sensor = Sensor()
    interpret = Interpreter()
    controller = Controller()
    sensorUlt = SensorUltra()
    #while True:
        #reading = sensor.sensor_reading()
        #print(reading)
        #result = interpret.processing(reading)
        #print(result)
        #time.sleep(2)
    
    while True: 
        reading = sensorUlt.sensor_reading()
        time.sleep(1) 
    start_time = time.time()
    run_time = 2
    px.set_dir_servo_angle(0)
    #while (time.time() - start_time < run_time):
        #follow_line(px, sensor, interpret, controller)
        #px.set_dir_servo_angle(0)
        #px.forward(-35)
        
    
    px.stop()
    print("stop")
 
