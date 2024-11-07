import pandas as pd
import cv2
import os
from PIL import Image
import requests
from io import BytesIO


dict1 = {
    'name1': 'Alice',
    'age1': 30,
    'city1': 'New York'
}

dict2 = {
    'name': 'Bob',
    'age': 25,
    'city': 'Los Angeles'
}

dict2.update(dict1)

print(dict2)