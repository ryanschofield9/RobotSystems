import os 
from time import sleep
import logging
import subprocess

class ADC:
    ADDR = 0x14  # 扩展板的地址为0x14

    def __init__(self, chn):  # 参数，通道数，树莓派扩展板上有8个adc通道分别为"A0, A1, A2, A3, A4, A5, A6, A7"
        if isinstance(chn, str):
            if chn.startswith("A"):  # 判断传递来的参数是否为A开头，如果是，取A后面的数字出来
                chn = int(chn[1:])
            else:
                raise ValueError("ADC channel should be between [A0, A7], not {0}".format(chn))
        if chn < 0 or chn > 7:  # 判断取出来的数字是否在0~7的范围内
            self._error('Incorrect channel range')
        chn = 7 - chn
        self.chn = chn | 0x10  # 给从机地址
        self.reg = 0x40 + self.chn
        
    def send(self, data, address):
        # Implement the logic to send data to the specified address
        pass

    def recv(self, length, address):
        # Implement the logic to receive data of the specified length from the address
        pass

    def _debug(self, message):
        # Implement the debug logic
        pass

    def _error(self, message):
        # Implement the error handling logic
        pass

    def read(self):  # adc通道读取数---写一次数据，读取两次数据 （读取的数据范围是0~4095）
        self._debug("Write 0x%02X to 0x%02X" % (self.chn, self.ADDR))
        self.send([self.chn, 0, 0], self.ADDR)

        self._debug("Read from 0x%02X" % (self.ADDR))
        value_h = self.recv(1, self.ADDR)[0]  # 读取数据

        self._debug("Read from 0x%02X" % (self.ADDR))
        value_l = self.recv(1, self.ADDR)[0]  # 读取数据（读两次）

        value = (value_h << 8) + value_l
        self._debug("Read value: %s" % value)
        return value

    def read_voltage(self):  # 将读取的数据转化为电压值（0~3.3V）
        return self.read * 3.3 / 4095

class fileDB(object):
    """A file based database.

    A file based database, read and write arguments in the specific file.
    """
    def __init__(self, db: str, mode: str = None, owner: str = None):  
        '''Init the db_file is a file to save the datas.'''

        self.db = db
        # Check if db_file exists, otherwise create one
        if self.db is not None:    
            self.file_check_create(db, mode, owner)
        else:
            raise ValueError('db: Missing file path parameter.')

    def file_check_create(self, file_path: str, mode: str = None, owner: str = None):
        dir = file_path.rsplit('/', 1)[0]
        try:
            if os.path.exists(file_path):
                if not os.path.isfile(file_path):
                    print('Could not create file, there is a folder with the same name')
                    return
            else:
                if os.path.exists(dir):
                    if not os.path.isdir(dir):
                        print('Could not create directory, there is a file with the same name')
                        return
                else:
                    os.makedirs(file_path.rsplit('/', 1)[0], mode=0o754)
                    sleep(0.001)

                with open(file_path, 'w') as f:
                    f.write("# robot-hat config and calibration value of robots\n\n")

            if mode is not None:
                os.popen('sudo chmod %s %s' % (mode, file_path))
            if owner is not None:
                os.popen('sudo chown -R %s:%s %s' % (owner, owner, file_path.rsplit('/', 1)[0]))
        except Exception as e:
            raise(e) 

    def get(self, name, default_value=None):
        """Get value by data's name. Default value is for the arguments do not exist"""
        try:
            conf = open(self.db, 'r')
            lines = conf.readlines()
            conf.close()
            file_len = len(lines) - 1
            flag = False
            # Find the argument and set the value
            for i in range(file_len):
                if lines[i][0] != '#':
                    if lines[i].split('=')[0].strip() == name:
                        value = lines[i].split('=')[1].replace(' ', '').strip()
                        flag = True
            if flag:
                return value
            else:
                return default_value
        except FileNotFoundError:
            conf = open(self.db, 'w')
            conf.write("")
            conf.close()
            return default_value
        except:
            return default_value

    def set(self, name, value):
        """Set value by data's name. Or create one if the argument does not exist"""

        # Read the file
        conf = open(self.db, 'r')
        lines = conf.readlines()
        conf.close()
        file_len = len(lines) - 1
        flag = False
        # Find the argument and set the value
        for i in range(file_len):
            if lines[i][0] != '#':
                if lines[i].split('=')[0].strip() == name:
                    lines[i] = '%s = %s\n' % (name, value)
                    flag = True
        # If argument does not exist, create one
        if not flag:
            lines.append('%s = %s\n\n' % (name, value))

        # Save the file
        conf = open(self.db, 'w')
        conf.writelines(lines)
        conf.close()


class _BasicClass(object):
    _class_name = '_BasicClass'
    DEBUG_LEVELS = {'debug': logging.DEBUG,
                    'info': logging.INFO,
                    'warning': logging.WARNING,
                    'error': logging.ERROR,
                    'critical': logging.CRITICAL,
                    }
    DEBUG_NAMES = ['critical', 'error', 'warning', 'info', 'debug']

    def __init__(self):
        self._debug_level = 0
        self.logger = logging.getLogger(self._class_name)
        self.ch = logging.StreamHandler()
        form = "%(asctime)s	[%(levelname)s]	%(message)s"
        self.formatter = logging.Formatter(form)
        self.ch.setFormatter(self.formatter)
        self.logger.addHandler(self.ch)
        self._debug = self.logger.debug
        self._info = self.logger.info
        self._warning = self.logger.warning
        self._error = self.logger.error
        self._critical = self.logger.critical

    @property
    def debug(self):
        return self._debug_level

    @debug.setter
    def debug(self, debug):
        if debug in range(5):
            self._debug_level = self.DEBUG_NAMES[debug]
        elif debug in self.DEBUG_NAMES:
            self._debug_level = debug
        else:
            raise ValueError('Debug value must be 0(critical), 1(error), 2(warning), 3(info) or 4(debug), not \"{0}\".'.format(debug))
        self.logger.setLevel(self.DEBUG_LEVELS[self._debug_level])
        self.ch.setLevel(self.DEBUG_LEVELS[self._debug_level])
        self._debug('Set logging level to [%s]' % self._debug_level)

    def run_command(self, cmd):
        p = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = p.stdout.read().decode('utf-8')
        status = p.poll()
        # print(result)
        # print(status)
        return status, result

    def map(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

class Servo(_BasicClass):
    MAX_PW = 2500
    MIN_PW = 500
    _freq = 50

    def __init__(self, pwm):
        super().__init__()
        self.pwm = pwm
        self.pwm.period(4095)
        prescaler = int(float(self.pwm.CLOCK) / self.pwm._freq / self.pwm.period())
        self.pwm.prescaler(prescaler)
        # self.angle(90)

    # angle ranges -90 to 90 degrees
    def angle(self, angle):
        if not (isinstance(angle, int) or isinstance(angle, float)):
            raise ValueError("Angle value should be int or float value, not %s" % type(angle))
        if angle < -90:
            angle = -90
        if angle > 90:
            angle = 90
        High_level_time = self.map(angle, -90, 90, self.MIN_PW, self.MAX_PW)
        self._debug("High_level_time: %f" % High_level_time)
        pwr = High_level_time / 20000
        self._debug("pulse width rate: %f" % pwr)
        value = int(pwr * self.pwm.period())
        self._debug("pulse width value: %d" % value)
        self.pwm.pulse_width(value)

    # pwm_value ranges MIN_PW 500 to MAX_PW 2500 degrees
    def set_pwm(self, pwm_value):
        if pwm_value > self.MAX_PW:
            pwm_value = self.MAX_PW
        if pwm_value < self.MIN_PW:
            pwm_value = self.MIN_PW

        self.pwm.pulse_width(pwm_value)
