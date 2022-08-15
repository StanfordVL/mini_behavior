from PIL import Image
import numpy as np
import math
import os

FLOORPLANS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "floorplans")

def img_to_array(img_path):
    img = Image.open(img_path)
    array = np.asarray(img)
    return array

def get_floorplan(scene_id) :
    return os.path.join(FLOORPLANS_DIR, f"{scene_id}_floor_trav_no_obj_0.png")

def crop_img(img_array):
    # 0 = black, 255 = white
    height, width = np.shape(img_array)
    start_row = 0
    end_row = height - 1
    start_col = 0
    end_col = width - 1

    while np.all(img_array[start_row, :] == 0):
        start_row += 1

    while np.all(img_array[end_row, :] == 0):
        end_row -= 1

    while np.all(img_array[:, start_col] == 0):
        start_col += 1

    while np.all(img_array[:, end_col] == 0):
        end_col -= 1

    assert start_row <= end_row, 'incorrect start/end row'
    assert start_col <= end_col, 'incorrect start/end col'

    return img_array[start_row: end_row, start_col: end_col]


def get_pix_per_grid(img_array):
    # get pixels per grid
    def iter_rows(array, cur_min=math.inf):
        for row in array:
            count = 0
            for i in range(np.shape(array)[1]):
                if row[i] == 0:
                    count += 1
                else:
                    if count != 0:
                        cur_min = max(min(cur_min, count), 8)
                    count = 0
        return cur_min

    pix_per_grid = iter_rows(img_array)
    pix_per_grid = iter_rows(np.transpose(img_array), pix_per_grid)

    return pix_per_grid


def gen_grid_from_array(img_array):
    pix_per_grid = get_pix_per_grid(img_array)

    height, width = np.shape(img_array)
    grid_rows = math.ceil(height / pix_per_grid)
    grid_cols = math.ceil(width / pix_per_grid)

    # create grid with outer layer of walls
    grid = np.zeros((grid_rows + 2, grid_cols + 2))
    grid[0, :] = 0
    grid[-1, :] = 0
    grid[:, 0] = 0
    grid[:, -1] = 0

    # convert img to grid
    for i in range(grid_rows):
        for j in range(grid_cols):
            start_row = i * pix_per_grid
            end_row = (i+1) * pix_per_grid if (i+1) * pix_per_grid <= height else height
            start_col = j * pix_per_grid
            end_col = (j + 1) * pix_per_grid if (j+1) * pix_per_grid <= width else width

            sub_img = img_array[start_row: end_row, start_col: end_col]
            num_black = sub_img[np.where(sub_img == 0)].size
            num_white = sub_img[np.where(sub_img == 255)].size

            # set grid color to majority color in the subimg
            if num_black > num_white:
                grid[i + 1, j + 1] = 0
            else:
                grid[i + 1, j + 1] = 255

    return grid


def gen_grid_from_img(img='rs_int_floor_trav_no_obj_0.png', img_dir='scenes', save_dir='floorplans'):
    # load and process img into grid
    img_path = os.path.join(img_dir, img)
    img_array = img_to_array(img_path)
    img_array = crop_img(img_array)
    grid = gen_grid_from_array(img_array)

    # show grid
    grid = grid.astype(np.uint8)
    grid_img = Image.fromarray(grid)
    grid_img.show()

    # save grid in save_dir
    save_path = os.path.join(save_dir, img)
    print('saving grid to: {}'.format(save_path))
    grid_img.save(save_path)

    return grid
