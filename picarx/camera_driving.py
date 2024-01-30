#from picarx_improved import Picarx
# class picture taker is from example code in canvas 
import time

from picamera import PiCamera
from io import BytesIO
import cv2 as cv
from matplotlib import pyplot as plt
import numpy as np
import sys
import math
import os
import logging
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
class Geom():
    def calc_line(self, x1, y1, x2, y2):
        a = float(y2 - y1) / (x2 - x1) if x2 != x1 else 0
        b = y1 - a * x1
        return a, b

    def calc_line_length(self, p1, p2):
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        return math.sqrt(dx * dx + dy * dy)

    def get_horz_shift(self,x, w):
        hw = w / 2
        return 100 * (x - hw) / hw


    def calc_rect_area(self,rect_points):
        a = self.calc_line_length(rect_points[0], rect_points[1])
        b = self.calc_line_length(rect_points[1], rect_points[2])
        return a * b

    def get_vert_angle(self,p1, p2, w, h):
        px1 = p1[0] - w/2
        px2 = p2[0] - w/2
        
        py1 = h - p1[1]
        py2 = h - p2[1]

        angle = 90
        if px1 != px2:
            a, b = self.calc_line(px1, py1, px2, py2)
            angle = 0
            if a != 0:
                x0 = -b/a
                y1 = 1.0
                x1 = (y1 - b) / a
                dx = x1 - x0
                tg = y1 * y1 / dx / dx
                angle = 180 * np.arctan(tg) / np.pi
                if a < 0:
                    angle = 180 - angle
        return angle


    def order_box(self,box):
        srt = np.argsort(box[:, 1])
        btm1 = box[srt[0]]
        btm2 = box[srt[1]]

        top1 = box[srt[2]]
        top2 = box[srt[3]]

        bc = btm1[0] < btm2[0]
        btm_l = btm1 if bc else btm2
        btm_r = btm2 if bc else btm1

        tc = top1[0] < top2[0]
        top_l = top1 if tc else top2
        top_r = top2 if tc else top1

        return np.array([top_l, top_r, btm_r, btm_l])

    def shift_box(self,box, w, h):
        return np.array([[box[0][0] + w,box[0][1] + h],[box[1][0] + w,box[1][1] + h], [box[2][0] + w,box[2][1] + h],[box[3][0] + w,box[3][1] + h]])


    def calc_box_vector(box):
        v_side = self.calc_line_length(box[0], box[3])
        h_side = self.calc_line_length(box[0], box[1])
        idx = [0, 1, 2, 3]
        if v_side < h_side:
            idx = [0, 3, 1, 2]
        return ((box[idx[0]][0] + box[idx[1]][0]) / 2, (box[idx[0]][1] + box[idx[1]][1]) / 2), ((box[idx[2]][0] + box[idx[3]][0]) / 2, (box[idx[2]][1]  +box[idx[3]][1]) / 2)

geom = Geom()

class ROI():
    area = 0
    vertices = None


    def init_roi(self, width, height):
        print(width,height)
        #vertices = [(0, height), (width / 4, 3 * height / 4),(3 * width / 4, 3 * height / 4), (width, height)]
        vertices = [(0, height), (width / 5, 1 * height / 2),(4 * width / 5, 1 * height / 2), (width, height)]
        self.vertices = np.array([vertices], np.int32)
        
        blank = np.zeros((height, width, 3), np.uint8)
        blank[:] = (255, 255, 255)
        blank_gray = cv.cvtColor(blank, cv.COLOR_BGR2GRAY)
        blank_cropped = self.crop_roi(blank_gray)
        self.area = cv.countNonZero(blank_cropped)


    def crop_roi(self, img):
        #cv.imshow("Image", img)
        mask = np.zeros_like(img)
        match_mask_color = 255
        
        cv.fillPoly(mask, self.vertices, match_mask_color)
        masked_image = cv.bitwise_and(img, mask)
        return masked_image

    def get_area(self):
        return self.area

    def get_vertices(self):
        return self.vertices

Roi = ROI()

class Track_Conf:
    ## Picture settings

    # initial grayscale threshold
    threshold = 120

    # max grayscale threshold
    threshold_max = 180

    #min grayscale threshold
    threshold_min = 40

    # iterations to find balanced threshold
    th_iterations = 10

    # min % of white in roi
    white_min=3

    # max % of white in roi
    white_max=20

    ## Driving settings

    # line angle to make a turn
    turn_angle = 45

    # line shift to make an adjustment
    shift_max = 20

    # turning time of shift adjustment
    shift_step = 0.125

    # turning time of turn
    turn_step = 0.25

    # time of straight run
    straight_run = 0.5

    # attempts to find the line if lost
    find_turn_attempts = 5

    # turn step to find the line if lost
    find_turn_step = 0.2

    # max # of iterations of the whole tracking
    max_steps = 40

    # target brightness level
    brightness = 100

tconf = Track_Conf

class Track():
    T = tconf.threshold
    #Roi = roi.ROI()
    def __init__(self):
        pass
    def balance_pic(self, image, inv_polarity=False, threshold=50):
        polarity = 0

        if(inv_polarity):
            polarity = cv.THRESH_BINARY_INV_, gray = cv.threshold(image, threshold, 255, polarity)
        return Roi.crop_roi(gray)  


    def adjust_brightness(self,img, level):
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        b = np.mean(img[:,:,2])
        if b == 0:
            return img
        r = level / b
        c = img.copy()
        c[:,:,2] = c[:,:,2] * r
        return cv.cvtColor(c, cv.COLOR_HSV2BGR)

    

    def prepare_pic(self,image, inv_polarity=False, threshold=50):
        global Roi
        global T
        height, width = image.shape[:2]

        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        blurred = cv.GaussianBlur(gray, (9, 9), 0)

        if Roi.get_area() == 0:
            Roi.init_roi(width, height)

        return self.balance_pic(blurred, inv_polarity, threshold), width, height


    def find_main_countour(self,image):

        cnts, hierarchy = cv.findContours(image, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)

        C = None
        if cnts is not None and len(cnts) > 0:
            C = max(cnts, key = cv.contourArea)


        if C is None:
            return None, None

        rect = cv.minAreaRect(C)
        box = cv.boxPoints(rect)
        box = np.int0(box)
        box = geom.order_box(box)
        return C, box

    def handle_pic(self,image, draw=False, inv_polarity=False, threshold=50):
        
        cropped, w, h = self.prepare_pic(image, inv_polarity, threshold)
        if cropped is None:
            return None, None
        
        cont, box = self.find_main_countour(cropped)
        if cont is None:
            return None, None
        
        p1, p2 = geom.calc_box_vector(box)
        if p1 is None:
            return None, None
        
        angle = geom.get_vert_angle(p1, p2, w, h)
        shift = geom.get_horz_shift(p1[0], w)

        if draw:
            cv.drawContours(image, [cont], -1, (0,0,255), 3)
            cv.drawContours(image,[box],0,(255,0,0),2)
            cv.line(image, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), (0, 255, 0), 3)
            
            cv.circle(image,(int(p1[0]), int(p1[1])), 10, (255,0, 0), -1)
            cv.circle(image,(int(p2[0]), int(p2[1])), 10, (255,255, 0), -1)

            msg_a = "Angle {0}".format(int(angle))
            msg_s = "Shift {0}".format(int(shift))

            cv.putText(image, msg_a, (10, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
            cv.putText(image, msg_s, (10, 40), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
            
        return angle, shift
    
    def prepare_pic2(self,image):
        height, width = image.shape[:2]
        crop = image[3 * height / 4: height, width / 4:3 * width/ 4]
        crop = self.adjust_brightness(crop, tconf.brightness)

        gray = cv.cvtColor(crop, cv.COLOR_BGR2GRAY)
        blurred = cv.GaussianBlur(gray, (9, 9), 0)

        rc, gray = cv.threshold(blurred, tconf.threshold, 255, 0)
        return gray, width / 2, height / 4



    def handle_pic2(self,path, fout = None, show = False):
        image = cv.imread(path)
        if image is None:
            logging.warning(("File not found", path))
            return None, None
        height, width = image.shape[:2]
        cropped, w, h = self.prepare_pic2(image)
        if cropped is None:
            return None, None
        cont, box = self.find_main_countour(cropped)
        if cont is None:
            return None, None
        
        p1, p2 = geom.calc_box_vector(box)
        if p1 is None:
            return None, None

        angle = geom.get_vert_angle(p1, p2, w, h)
        shift = geom.get_horz_shift(p1[0], w)

        draw = fout is not None or show

        if draw:
            w_offset = (width - w) / 2
            h_offset = (height - h)
            dbox = geom.shift_box(box, w_offset, h_offset)

            cv.drawContours(image,[dbox],0,(255,0,0),2)
            dp1 = (p1[0] + w_offset, p1[1] + h_offset)
            dp2 = (p2[0] + w_offset, p2[1] + h_offset)
            cv.line(image, dp1, dp2, (0, 255, 0), 3)
            msg_a = "Angle {0}".format(int(angle))
            msg_s = "Shift {0}".format(int(shift))

            cv.putText(image, msg_a, (10, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
            cv.putText(image, msg_s, (10, 40), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

        if fout is not None:
            cv.imwrite(fout, image)

        if show:    
            cv.imshow("Image", image)
            cv.waitKey(0)
        return angle, shift

track= Track()

class Sensors():
    def __init__(self):
        pass 
    
    def readings(self):
        readings = picTaker.takePicture()
        return readings 

sensor=Sensors()

class Interpreter():
    def __init__(self, sensitivity_given:float = 0.5, 
                 polarity_given:int = 1):
        self.sensitivity= sensitivity_given
        self.polarity = polarity_given

# help from https://docs.opencv.org/3.4/d6/d10/tutorial_py_houghlines.html for the hough line transformation 
    def process (self, frame, draw=False):
        
        angle,shift = track.handle_pic(frame = frame, draw=draw, inv_polarity = True, threshold= 80)
        return angle, shift 
        
interpret = Interpreter()

if __name__ == "__main__":
    sensor=Sensors()
    
    while True:
        
        edge = picTaker.takePicture()
        crop = picTaker.lastCrop
        '''
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
        angle, shift = interpret.process(crop, draw= True)
        
        
