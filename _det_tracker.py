
import config


"""
A Class To Track Instances Between Frames
"""
class _det_tracker:

    
    """
    Creates A Tracker object
    """
    def __init__(self):

        self.continuation = {}

    """
    Updates The Tracked Instances, With The Most Recent Set of Predictions, And Their Corrasponding Colors

    Args:
        predictions (list): the list of prediction keypoints, for each valid prediction
        c (list): the list of colors given to each prediction
    """
    def apply_update(self, predictions, c):

        for key in self.continuation:
            self.continuation[key].reset_satisfaction()

        kp = predictions._fields['pred_keypoints'].numpy()
        b = predictions._fields['pred_boxes'].tensor.numpy()
        c = [tuple(v) for v in c]

        #print("NEW:")
        #For Every NEW prediction
        for index, c_index in enumerate(c):

            #Determine If Continuation
            match = self.continuation.get(c_index)

            #If So, Update According Match
            if not match is None:
                #print(f" -- UPDATING: {c[index]}")
                match.apply(kp[index], b[index])
            #Otherwise, Create New
            else:
                #print(f" -- CREATING: {c[index]}")

                self.continuation[c_index] = _det_tracker.tracker(kp[index], b[index], config.DB_FRAGMENT_ID)
                config.DB_FRAGMENT_ID += 1

        for key, value in self.continuation.items():
            #If Not Satisfied: Fill Blank
            if not value.satisfied == True:
                value.apply_not()

    """
    Obtains A List Of The Most Recent State Of The Tracked Predictions

    Returns:
        list: a list containing the color and keypoints for each prediction
    """
    def get_tracked(self):
        return [(value,key) 
                for key, value in self.continuation.items()
                if value.satisfied == True]


    """
    A Class Representing A Single Tracked Prediction
    """
    class tracker:

        """
        Creating An Instance Representing A Single Prediction

        Args:
            point (list): the list of keypoints on a prediction
            box (list): the box keypoints around a prediction
            id (int): the database id given to this prediction
        """
        def __init__(self, point, box, id):
            self.points = [point]
            self.boxs = [box]
            self.satisfied = True
            self.id = id
            self.time_since = 0


        """
        Updating The Prediction Using Most Recent Frame Information

        Args:
            points (list): the list of most recent keypoints
            box (list): the box keypoints around a prediction
        """
        def apply(self, point, box):
            self.points.append(point)
            self.boxs.append(box)
            self.satisfied = True
            self.time_since = 0

        """
        Updating The Prediction For A Prediction Not Found In Most Recent Frame
        """
        def apply_not(self):
            self.points.append(None)
            self.boxs.append(None)
            self.time_since += 1

        """
        Resets Prediction For Next Frame
        """
        def reset_satisfaction(self):
            self.satisfied = False
