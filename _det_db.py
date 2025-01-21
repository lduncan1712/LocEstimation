import psycopg2
import json


with open("db_creds.json", 'r') as creds:
    creds = json.load(creds)
    myConn = psycopg2.connect(
        dbname= creds["dbname"],
        user= creds["user"],
        host= creds["host"],
        password= creds["password"],
        port= creds["port"]
    )
cursor = myConn.cursor()

#Insert Into Frame
frame_query = """
    INSERT INTO frame(
        id, tilt, roll, direction, time, 
        location, width, height, dop
    )
    VALUES (%s, %s, %s, %s, %s, 
            ST_GeographyFromText('SRID=4326;POINT(%s %s)'), %s, %s, %s)
"""

#Obtain A Select Range Of Frames
frame_get_query = """
    SELECT id from frame where id between 10000 and 99999;
"""

#Insert Into Fragments
fragment_query = """
    INSERT INTO fragment(id, frame, 
                          bp0x,bp0y,bp1x,bp1y,
                          kp0x,kp0y,kp1x,kp1y,kp2x,kp2y,kp3x,kp3y,kp4x,kp4y)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

#Obtain A Select Range Of Fragments
fragment_get_query = """
    SELECT * from fragment where id between 10000 and 99999;
"""


"""
    Handles The Integration Between Detected Predictions, Metadata and The database
"""
class _det_db:

    """
    Uploads A Set Of Fragments (predictions) into the database

    Args:
        perspectives (List): the prediction keypoints and boxs
        det_photo (_det_photo): a class instance used to calculate pixels to skew 
    """
    def upload_fragments(perspectives, det_photo):

        visuals = []

        for perspective in perspectives:
            per = perspective[0]
            lbp = per.boxs[-1]
            lkp = per.points[-1]

            data=(per.id, det_photo.db_id,
                            det_photo.x_to_angle(lbp[0]), det_photo.y_to_angle(lbp[1]),
                            det_photo.x_to_angle(lbp[2]), det_photo.y_to_angle(lbp[3]),
                            
                            
                            det_photo.x_to_angle(lkp[0][0]), det_photo.y_to_angle(lkp[0][1]),
                            det_photo.x_to_angle(lkp[1][0]), det_photo.y_to_angle(lkp[1][1]),
                            det_photo.x_to_angle(lkp[2][0]), det_photo.y_to_angle(lkp[2][1]),
                            det_photo.x_to_angle(lkp[3][0]), det_photo.y_to_angle(lkp[3][1]),
                            det_photo.x_to_angle(lkp[4][0]), det_photo.y_to_angle(lkp[4][1]),
                            )

            cursor.execute(fragment_query, 
                           data)
            
            visuals.append([perspective[1], lkp[0][0], lkp[0][1], lkp[4][0], lkp[4][1]])
        myConn.commit()

        return visuals
        

    """
    Uploads A Frame (image) into the database

    Args:
        frame (_det_photo): information from the photo which we are uploading
    """
    def upload_frame(frame):

        data = [frame.db_id, frame.tilt, frame.roll, frame.direction, frame.date_time,
                frame.longitude, frame.latitude, frame.HAOV, frame.VAOV, frame.dop]
        
        cursor.execute(frame_query,data)
        myConn.commit()

    """
    Obtains A Summary Of Data (Used For Gradient Descent Step)
    """
    def get_data():
        cursor.execute(frame_get_query)
        frames = cursor.fetchall()
        cursor.execute(fragment_get_query)
        fragments = cursor.fetchall()
        return frames, fragments
        

    