import os
from detectron2.utils.video_visualizer import VideoVisualizer
import cv2
import random

from _det_core import _det_core
from _det_photo import _det_photo
from _det_tracker import _det_tracker
from _det_db import _det_db

import config

"""
A Class To Implement Image Detection For Our Given Data
"""
class detection_step:

    """
    Create An Object  
    """
    def __init__(self):

        #Determining Inter-Photo Ranges
        self.between_black = _det_photo.frames_between_black()
        print(self.between_black)

        #Configuring The Size Of This Data
        _det_photo.photo_macro()
        self.vcap, self.out = _det_photo.video_macro()

        #Building Photos
        self.photos = _det_photo.construct_images()
            
        #Model
        _det_core.set_up(self)

        #Detection
        self.detection_sequence()

    """
    Begin Detection One Frame At A Time
    """
    def detection_sequence(self):

        #Storing Tracks
        self.frame_index = 0
        self.major_index = 0
        self.tracker = _det_tracker()

        self.visual_store = []

        while(self.vcap.isOpened()):
            ret, frame = self.vcap.read()
            if not ret: 
                break

            move, roll = self.determine_detection_related()

            #Determine Action To Do

            #Skip
            if move == "BEFORE" or move == "BLACK" or move == "SKIPPED" or move == "BLACK":
                pass

            #Last Black (Could Be Last)
            elif move == "LAST-BLACK":
                    self.major_index += 1
                    if self.major_index == len(self.photos): return

            #An Image (Major or Minor)
            else:
                    #Database Upload (using Photo)
                    if move == "MAJOR":
                        major = self.photos[self.major_index]
                        frame = major.full_path
                        
                    #Prepare Photo
                    prepped, corners = _det_photo.modify_photo(frame, roll)

                    #Add Predictions
                    image, predictions, c = _det_core.apply_detection(prepped,corners)
                    self.tracker.apply_update(predictions, c)
                    

                    #If Photo is Used: Upload to Database
                    if move == "MAJOR":
                        perspectives = self.tracker.get_tracked()
                        visuals = _det_db.upload_fragments(perspectives, major)

                        self.visual_store.extend(visuals)

                    #Print Image 
                    vi = image.get_image()

                    #Display Past Predictions (To Show Change In Directions)
                    for item in self.visual_store:
                        print(item)

                        for col,width in zip([(0,0,0), (round(item[0][0]*255),round(item[0][1]*255),round(item[0][2]*255))],
                                             [20,12]):

                            cv2.line(vi, 
                                (round(item[1]), round(item[2])), 
                                (round(item[3]), round(item[4])), 
                                col,
                                 width)

                    cv2.imwrite(f"\\Downloads\\sample_det_photoNEW{self.frame_index}.jpg", vi)

                    
            self.frame_index+=1
        self.vcap.release()
        cv2.destroyAllWindows()
        

    """
    Determine What To Do With The Next Frame Given The Past Frame

    Returns:
        list(str,int): name of action to do, and roll to apply to it
    """
    def determine_detection_related(self):

        #Means Before First Image
        if self.major_index == 0 and self.between_black[self.major_index][0] > self.frame_index:
            print("BEFORE")
            return "BEFORE", None
        
        #Means First Within Black (Major)
        elif self.between_black[self.major_index][0] == self.frame_index:
            print("MAJOR")
            return "MAJOR", self.photos[self.major_index].roll
        
        #Means Last Within Black
        elif self.between_black[self.major_index][1] == self.frame_index:
            print("LAST BLACK")
            return "LAST-BLACK", None

        #Means One Of The Other Blacks
        elif self.between_black[self.major_index][0] <= self.frame_index <= self.between_black[self.major_index][1]:
            print("BLACK")
            return "BLACK", None
        #Means Valid Non Black Cell
        else:
            #Cell Skipped
            if self.frame_index % config.N_FRAME != 0:
                print("SKIPPED")
                return "SKIPPED", None

            #Prepare Cell For Full Processing
            else:
                print("MINOR")

                start = self.photos[self.major_index - 1].roll
                end = self.photos[self.major_index].roll

                delta = end - start

                time_delta = self.between_black[self.major_index][0] - \
                             self.between_black[self.major_index - 1][1]
        
                step = self.frame_index - self.between_black[self.major_index-1][1]

                roll = start + (delta*(step/time_delta))
                print(f"MINOR ROW: {roll}")

                return "MINOR", roll

        


if __name__ == "__main__":
    detection_step()

    

