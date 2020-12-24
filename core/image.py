import cv2
import numpy as np


def thumbnail(inbytes):
    nparray = np.frombuffer(inbytes, dtype='uint8')
    image = cv2.imdecode(nparray, cv2.IMREAD_UNCHANGED)
    r = 300 / float(image.shape[0])
    thumb = cv2.resize(image, (0, 0), fx=r, fy=r)
    img_bytes = cv2.imencode(".png", thumb)[1].tostring()
    return img_bytes


def resize(inbytes, max):
    nparray = np.frombuffer(inbytes, dtype='uint8')
    image = cv2.imdecode(nparray, cv2.IMREAD_UNCHANGED)
    r = max / float(image.shape[0])
    thumb = cv2.resize(image, (0, 0), fx=r, fy=r)
    img_bytes = cv2.imencode(".png", thumb)[1].tostring()
    return img_bytes


def size(inbytes):
    nparray = np.frombuffer(inbytes, dtype='uint8')
    image = cv2.imdecode(nparray, cv2.IMREAD_UNCHANGED)
    height, width, channels = image.shape
    return height, width
