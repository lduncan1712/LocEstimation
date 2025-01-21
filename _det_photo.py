import cv2
import os
import exif
import re
import math
from datetime import datetime
from scipy import ndimage


from _det_db import _det_db

import config

"""
    A Class With Methods For Extracting Image Information
"""

class _det_photo:

    """
    Creates A Det Photo:
    
    Args:
        name (str): the file name to make image from
        id (int): the database id for the frame this will become
    """
    def __init__(self, name, id):
        self.db_id = id

        self.full_path = config.PHOTO_PATH + "\\" + name
        
        try:
            metadata =  exif.Image(self.full_path).get_all()
        except:
            print("No Metadata Found")


        #Platform Specific
        tilt_roll = metadata.get('image_description', 'F')
        slices = re.split('=|/', tilt_roll)
        self.tilt, self.roll = float(slices[1].strip()), float(slices[3].strip())

        rads = math.radians(abs(self.roll))

        self.new_x = abs(config.PHOTO_X*math.cos(rads)) + abs(config.PHOTO_Y*math.sin(rads))
        self.new_y = abs(config.PHOTO_X*math.sin(rads)) + abs(config.PHOTO_Y*math.cos(rads))

        self.longitude = 1*_det_photo.convert_dms_to_dd(metadata.get('gps_longitude', 'F'))
        self.latitude = -1*_det_photo.convert_dms_to_dd(metadata.get('gps_latitude', 'F'))
        self.altitude = metadata.get('gps_altitude', 'F')
        self.dop = metadata.get('gps_dop', 'F')
        self.direction = metadata.get('gps_img_direction', 'F')  # ANOUTHERTAG???????????

        self.HAOV = config.HAOV
        self.VAOV = config.VAOV

        date_time = metadata.get('datetime', 'F')
        date_time = datetime.strptime(date_time, '%Y:%m:%d %H:%M:%S')
        self.date_time = int(date_time.timestamp())

        _det_db.upload_frame(self)
    

    """
    Converts A Pixel Y In An Image Into Its Corraspnding Geospatial Y Degree

    Args:
        y (double): the y pixel number
    """
    def y_to_angle(self, y):
        location = self.tilt + -1*(y - self.new_y/2)*config.DEGREE_PER_PIXEL_Y
        return location

    """
    Converts A Pixel X In An Image Into Its Corrasponding Geospatial X Degree

    Args:
        x (double): the x pixel number
    """
    def x_to_angle(self, x):
        return (self.direction + (x - self.new_x/2)*config.DEGREE_PER_PIXEL_X) % 360



    """
    A Method To Determine Which Frames Within The Video Are Black (where images were taken)

    Return:
        list(list): list of ranges of frames between black
    """
    @staticmethod
    def frames_between_black():

        distance = []
        between = []
        
        vcap = cv2.VideoCapture(config.VIDEO_PATH)

        position = 0
        time_since_black = 0
        number_of_black = 0

        b = 0
        w = 0
        t = 0

        prev_was_black = False
        pos1 = 0
        pos2 = 0
        current_pos = 0

        while (vcap.isOpened()):
            ret, frame = vcap.read()
            # if frame is read correctly ret is True
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break

            # BLACK
            if cv2.mean(frame)[0] < 40:

                # Continue Black
                if prev_was_black:
                    b += 1
                # Starting Black
                else:
                    b += 1
                    pos1 = t
                    prev_was_black = True
            # WHITE
            else:
                # MEANS END OF SNAP
                if prev_was_black:
                    pos2 = t
                    distance.append((pos1, pos2 - 1))
                    prev_was_black = False
                    w += 1

                # Continuing White
                else:
                    w += 1
            t += 1

        del distance[0]  #No need Componenet Before First Photo
        return distance
    
    """
    Obtaining Metadata To Create Ratios Of Image Size Within Photos Vs Video

    Return 
        bool: whether method success
    """
    @staticmethod
    def photo_macro():
        for name in os.listdir(config.PHOTO_PATH):
            try:
                metadata =  exif.Image(config.PHOTO_PATH + "\\" + name).get_all()

                x = metadata.get('pixel_x_dimension', 'F')
                y = metadata.get('pixel_y_dimension', 'F')

                
                
                if not x == 'F' or not y == 'F':
                    config.PHOTO_X, config.PHOTO_Y = x,y
                    config.DEGREE_PER_PIXEL_X = config.HAOV/config.PHOTO_X
                    config.DEGREE_PER_PIXEL_Y = config.VAOV/config.PHOTO_Y
                    return 1
                else:
                    print("Metadata Found - No Dimension Found")
            except:
                print("Metadata Not Found - Attempting Other Photo")
        return 0

    """
    Opens The Video, Stores Its Information

    Returns:
        VideoCapture: the video to apply predictions to
    """
    @staticmethod
    def video_macro():

        vcap = cv2.VideoCapture(config.VIDEO_PATH)

        w = int(vcap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(vcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(vcap.get(cv2.CAP_PROP_FPS))

        return vcap
    
    """
    Converts Coordinate Degree 

    Args:
        dms (list): a coordinate in the form days, minutes, seconds

    Returns (double): a coordinate in the form degrees
    """
    @staticmethod
    def convert_dms_to_dd(dms):
        return (dms[2]/3600 + dms[1]/60 + dms[0])
    
    """
    Resizes And Rotates An Image So Its Oriented With No Roll, And Scaled To Dimension Of Photos

    Args:
        individual (Image): the image to modify
        roll (double): the number of degrees this image needs to be roll

    Returns:
        Image: the modified image
    """
    @staticmethod
    def modify_photo(individual, roll):

        #Main
        if isinstance(individual, str):
            print(f"MAJOR: {individual}")
            frame = cv2.imread(individual)
        #Minor
        else:
            print(f"MINOR X: {config.PHOTO_X} Y: {config.PHOTO_Y} {type(individual)}")
            frame = cv2.resize(individual, (config.PHOTO_X, config.PHOTO_Y))
    
        frame = ndimage.rotate(frame, float(roll), mode='constant', cval=0)

        
        corners = _det_photo.get_old_corners(frame.shape, roll)

        return frame, corners
    
    """
    Builds A List Of Det photo objects corrasponding to unique photos

    Returns:
        list(_det_photo): each photos corrasponding _det_photo object
    """
    def construct_images():
        photos = []
        for name in os.listdir(config.PHOTO_PATH):
            photos.append(_det_photo(name, config.DB_FRAME_ID))
            config.DB_FRAME_ID+=1
        return photos
    

    """
    Obtains The Location Of Image Corners Given The Roll of the image

    Args:
        shape: (list) the shape of an image
        roll: (double) the roll in degrees applied to rectangle

    Return:
        list: the corners of image with given roll
    """
    def get_old_corners(shape,roll):
        x,y,_ = shape
        rad = math.radians(abs(roll))

        p1 = int((y * math.sin(rad)))
        p2 = int((x * math.cos(rad)))  
        p3 = int((math.cos(rad) * y))  
        p4 = int((math.sin(rad) * x))  

        if roll >= 0:
            return [(0, p4), (p2, 0), (x, p3), (p1, y)]
        else:
            return [(x - p1, y), (x, p4), (p1, 0), (0, y - p4)]