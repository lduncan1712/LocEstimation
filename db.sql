CREATE EXTENSION postgis;

"""
A Table Representing A Single Photo Taken
"""
CREATE TABLE frame(
    id INT,
    tilt REAL,
    roll REAL,
    direction REAL,
    time BIGINT,
    location GEOGRAPHY(Point, 4326),
    width INT,
    height INT,
    dop INT
);

"""
A Table Representing A Prediction Associated Within A Photo Taken
"""
CREATE TABLE fragment(
    id INT,
    frame INT,
    
    bp0x REAL,
    bp0y REAL,
    bp1x REAL,
    bp1y REAL,
 
    kp0x REAL,
    kp0y REAL,
    kp1x REAL,
    kp1y REAL,
    kp2x REAL,
    kp2y REAL,
    kp3x REAL,
    kp3y REAL,
    kp4x REAL,
    kp4y REAL
);