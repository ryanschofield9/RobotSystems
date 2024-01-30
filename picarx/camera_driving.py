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

picTaker = PictureTaker()

class Sensors():
    def __init__(self):
        self.readings = picTaker.takePicture()
    
    def readings(self):
        self.readings = picTaker.takePicture()
        return self.readings 

sensor=Sensors()

class Interpreter():
    def __init__(self, sensitivity_given:float = 0.5, 
                 polarity_given:int = 1):
        self.sensitivity= sensitivity_given
        self.polarity = polarity_given

# help from https://docs.opencv.org/3.4/d6/d10/tutorial_py_houghlines.html for the hough line transformation 
    def process (self):
        '''
        edge = picTaker.takePicture()
        lines = cv.HoughLinesP(edge, 1, np.pi/180, 100, minLineLength= 100, maxLineGap =10)
        crop = picTaker.lastCrop
        for line in lines: 
            x1,y1,x2,y2 = line[0]
            cv.line(crop, (x1, y1), (x2, y2), (0,255,0),2)
        '''
        img = cv.imread(cv.samples.findFile('sudoku.png'))
        gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
        edges = cv.Canny(gray,50,150,apertureSize = 3)
        lines = cv.HoughLinesP(edges,1,np.pi/180,100,minLineLength=100,maxLineGap=10)
        for line in lines:
            x1,y1,x2,y2 = line[0]
            cv.line(img,(x1,y1),(x2,y2),(0,255,0),2)
        plt.imshow(crop,cmap='gray')
        plt.show(block=False)
        plt.pause(3)
        plt.close()
        
interpret = Interpreter()

if __name__ == "__main__":
    sensor=Sensors()
    
    while True:
        '''
        edge = picTaker.takePicture()
        crop = picTaker.lastCrop
        #reading = sensor.readings()
        plt.subplot(211)
        plt.imshow(crop,cmap='gray')
        plt.subplot(212)
        plt.imshow(edge,cmap='gray')
        #Plot images, then pause for 3 seconds
        plt.show(block=False)
        plt.pause(3)
        plt.close()
        '''
        interpret.process()
        
