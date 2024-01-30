#from picarx_improved import Picarx
# class picture taker is from example code in canvas 
import time

from picamera import PiCamera
from io import BytesIO
import cv2 as cv
from matplotlib import pyplot as plt
import numpy as np
#Class to handle repeated picture taking using Raspberry Pi
class PictureTaker():
    #Initialize camera and data stream
    def __init__(self):
        self.camera = PiCamera()
        self.camera.resolution = (400,300)
        self.camStream = BytesIO()
        self.camera.start_preview()
        time.sleep(2)
        #Take a picture, do some small preprocessing, and return picture data
    def takePicture(self):
        #Snag picture and write to stream
        self.camera.capture(self.camStream,format='jpeg')
        #Rewind stream to start of picture
        self.camStream.seek(0)
        #Convert stream data to numpy uint8 array
        file_bytes = np.asarray(bytearray(self.camStream.read()),dtype=np.uint8)
        #Convert numpy array to OpenCV structure
        img = cv.imdecode(file_bytes,cv.IMREAD_COLOR)
        #Rewind back to start of stream for writing new pic
        self.camStream.seek(0)
        #Crop image to bottom half and middle half where line probably is
        croppedImg = img[150:300,100:300]
        self.lastCrop = croppedImg
        #To grayscale
        grayImg = cv.cvtColor(croppedImg,cv.COLOR_BGR2GRAY)
        #Find edges (might have to mess with min/max thresholds)
        self.lastEdges = cv.Canny(grayImg,25,125)
        return self.lastEdges
'''
picture = PictureTaker()
class Sensors():
    def __init__(self):
        self.readings = picture.takePicture()
    
    def readings():
        return self.readings 

class Interpreter():
    def __init__(self, sensitivity_given:float = 0.5, 
                 polarity_given:int = 1):
        self.sensitivity= sensitivity_given
        self.polarity = polarity_given
        

'''
if __name__ == "__main__":
    picTaker = PictureTaker()
    while True:
        edge = picTaker.takePicture()
        crop = picTaker.lastCrop
        plt.subplot(211)
        plt.imshow(crop,cmap='gray')
        plt.subplot(212)
        plt.imshow(edge,cmap='gray')
        #Plot images, then pause for 3 seconds
        plt.show(block=False)
        plt.pause(3)
        plt.close()
