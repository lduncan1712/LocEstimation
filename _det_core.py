import math
from random import random
import numpy as np

from torchvision.ops import box_convert, box_area

from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.data import MetadataCatalog
from detectron2.utils.video_visualizer import VideoVisualizer
from detectron2.utils.visualizer import ColorMode, Visualizer
from detectron2 import model_zoo
from detectron2.layers import interpolate
import os
import imutils
from scipy import ndimage
from shapely.geometry import Point, Polygon
from shapely.geometry import Polygon
import cv2
import torch
import random

import config


"""
    The Core Image (Video) Detection
"""
class _det_core:

    """
    Setup Detection Model

    Args:
        det (detection_step): the class handling the detection of the images
    """
    def set_up(det):
        cfg = get_cfg()
        cfg.INPUT.MASK_FORMAT = "polygons"  # ??
        cfg.MODEL.DEVICE = "cpu"

        cfg.merge_from_file(model_zoo.get_config_file(config.INSTANCE_CONFIG))
        cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(config.CHECKPOINT_URL)

        cfg.merge_from_file(model_zoo.get_config_file(config.KEYPOINT_CONFIG))
        cfg.MODEL.WEIGHTS = os.path.join("./model", config.MODEL)
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = config.ERROR_TOLERANCE
        cfg.MODEL.ROI_KEYPOINT_HEAD.NUM_KEYPOINTS = 5
        global predictor
        predictor = DefaultPredictor(cfg)

        global tree_metadata
        tree_metadata = MetadataCatalog.get("my_tree_dataset").set(thing_classes=["Tree"],
                                                                   keypoint_names=["kpCP", "kpL", "kpR", "AX1", "AX2"])
        
        global vid_vis
        vid_vis =  VideoVisualizer(metadata=tree_metadata)

    """
    Apply Predictor On Image To Obtain Predictions

    Args:
        frame (Image): the image to have predictions applied on
        corners (List): a list of corners in the image

    """
    def apply_detection(frame,corners):

        predictions = predictor(frame)

        predictions["instances"].remove("scores")

        valid_predictions = _det_core.remove_select_predictions(predictions,corners)

        predictions = predictions["instances"][valid_predictions]

        image, c = vid_vis.draw_instance_predictions(frame,predictions.to("cpu"))

        return image, predictions, c
    
    """
    Remove Select Predictions Outside Of Corners 

    Args:
        predictions (dict): a dictionary containing a set of predictions
        corners (List): a list of corners in the image
    """
    def remove_select_predictions(predictions, corners):

        polygon = Polygon(corners)
        predictions_to_keep = []
        key_points = predictions["instances"]._fields['pred_keypoints'].numpy()

        for index, point in enumerate(key_points):

            middle = Point(point[2][0], point[2][1])

            if polygon.contains(middle):
                predictions_to_keep.append(index)

        return torch.tensor(predictions_to_keep, dtype=torch.long)


    
