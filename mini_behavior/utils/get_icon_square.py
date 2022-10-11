import os
from PIL import Image
from mini_behavior.mini_behavior.rendering import img_to_array
import numpy as np


def square_img_array(img_path):
    img_array = img_to_array(img_path)

    # 0 = black, 255 = white
    num_dims = np.ndim(img_array)
    array = img_array[:, :]

    height, width = np.shape(array)
    start_row, start_col = 0, 0
    end_row, end_col = height - 1, width - 1

    while np.all(array[start_row, :] == 255):
        start_row += 1

    while np.all(array[end_row, :] == 255):
        end_row -= 1

    while np.all(array[:, start_col] == 255):
        start_col += 1

    while np.all(array[:, end_col] == 255):
        end_col -= 1

    assert start_row <= end_row, 'incorrect start/end row'
    assert start_col <= end_col, 'incorrect start/end col'

    new_size = max(end_row - start_row, end_col - start_col)
    start = int((height - new_size) / 2)
    end = int((height + new_size) / 2)

    square = img_array[start: end, start: end]

    return square


# dir with all icon images
# img_dir = '/Users/emilyjin/Downloads/icons'
img_dir = '/Users/emilyjin/Downloads/untitled folder'
# dir to save cropped icons as square
crop_dir = '/mini_behavior/mini_behavior/utils/state_icons'

imgs = os.listdir(img_dir)
for img in imgs:
    if img[0] == '.':
        continue
    print(img)
    img_path = os.path.join(img_dir, img)
    square = square_img_array(img_path)
    square_img = Image.fromarray(square)
    # square_img.show()
    save_path = os.path.join(crop_dir, img)
    square_img.save(img)
