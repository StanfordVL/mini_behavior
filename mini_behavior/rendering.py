from PIL import Image
from gym_minigrid.rendering import *


def img_to_array(img_path):
    """
    given a path to image, return array
    """
    img = Image.open(img_path)
    array = np.asarray(img)
    return array


def point_in_icon(img, img_array):
    def fn(x, y):
        x = x * img.shape[1] - 0.5
        y = y * img.shape[0] - 0.5
        x = int(x / np.shape(img)[1] * np.shape(img_array)[1])
        y = int(y / np.shape(img)[0] * np.shape(img_array)[0])

        return np.all(img_array[y, x] != 255)

    return fn
