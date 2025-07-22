import os
import random
import logging

logger = logging.getLogger(__name__) 

def get_image_names(directory):
    """
    Get the names of images from a directory.
    """
    image_names = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webm', '.gif')):
                image_names.append(os.path.join(root, file))
    return image_names

def randomize_image_order(image_names):
    """
    Randomize the order of image names.
    """
    random.shuffle(image_names)
    return image_names
