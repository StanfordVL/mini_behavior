# MODIFIED FROM MINIGRID REPO

import math
import numpy as np
from PIL import Image


def downsample(img, factor):
    """
    Downsample an image along both dimensions by some factor
    """
    # print(img.shape)
    # print(factor)
    assert img.shape[0] % factor == 0
    assert img.shape[1] % factor == 0

    img = img.reshape([img.shape[0]//factor, factor, img.shape[1]//factor, factor, 3])
    img = img.mean(axis=3)
    img = img.mean(axis=1)

    return img


def fill_coords(img, fn, color):
    """
    Fill pixels of an image with coordinates matching a filter function
    """

    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            yf = (y + 0.5) / img.shape[0]
            xf = (x + 0.5) / img.shape[1]
            if fn(xf, yf):
                img[y, x] = color

    return img


def rotate_fn(fin, cx, cy, theta):
    def fout(x, y):
        x = x - cx
        y = y - cy

        x2 = cx + x * math.cos(-theta) - y * math.sin(-theta)
        y2 = cy + y * math.cos(-theta) + x * math.sin(-theta)

        return fin(x2, y2)

    return fout


def point_in_line(x0, y0, x1, y1, r):
    p0 = np.array([x0, y0])
    p1 = np.array([x1, y1])
    dir = p1 - p0
    dist = np.linalg.norm(dir)
    dir = dir / dist

    xmin = min(x0, x1) - r
    xmax = max(x0, x1) + r
    ymin = min(y0, y1) - r
    ymax = max(y0, y1) + r

    def fn(x, y):
        # Fast, early escape test
        if x < xmin or x > xmax or y < ymin or y > ymax:
            return False

        q = np.array([x, y])
        pq = q - p0

        # Closest point on line
        a = np.dot(pq, dir)
        a = np.clip(a, 0, dist)
        p = p0 + a * dir

        dist_to_line = np.linalg.norm(q - p)
        return dist_to_line <= r

    return fn


def point_in_circle(cx, cy, r):
    def fn(x, y):
        return (x-cx)*(x-cx) + (y-cy)*(y-cy) <= r * r
    return fn


def point_in_rect(xmin, xmax, ymin, ymax):
    def fn(x, y):
        return x >= xmin and x <= xmax and y >= ymin and y <= ymax
    return fn


def point_in_triangle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    def fn(x, y):
        v0 = c - a
        v1 = b - a
        v2 = np.array((x, y)) - a

        # Compute dot products
        dot00 = np.dot(v0, v0)
        dot01 = np.dot(v0, v1)
        dot02 = np.dot(v0, v2)
        dot11 = np.dot(v1, v1)
        dot12 = np.dot(v1, v2)

        # Compute barycentric coordinates
        inv_denom = 1 / (dot00 * dot11 - dot01 * dot01)
        u = (dot11 * dot02 - dot01 * dot12) * inv_denom
        v = (dot00 * dot12 - dot01 * dot02) * inv_denom

        # Check if point is in triangle
        return (u >= 0) and (v >= 0) and (u + v) < 1

    return fn


def highlight_img(img, color=(255, 255, 255), alpha=0.30):
    """
    Add highlighting to an image
    """

    blend_img = img + alpha * (np.array(color, dtype=np.uint8) - img)
    blend_img = blend_img.clip(0, 255).astype(np.uint8)
    img[:, :, :] = blend_img


def img_to_array(img_path):
    """
    given a path to image, return array
    """
    img = Image.open(img_path)
    array = np.asarray(img)
    return array


def square_img(img_path):
    img_array = img_to_array(img_path)

    # 0 = black, 255 = white
    img_array = img_array[:, :, 0]
    height, width = np.shape(img_array)
    start_row = 0
    end_row = height - 1
    start_col = 0
    end_col = width - 1

    while np.all(img_array[start_row, :] == 255):
        start_row += 1

    while np.all(img_array[end_row, :] == 255):
        end_row -= 1

    while np.all(img_array[:, start_col] == 255):
        start_col += 1

    while np.all(img_array[:, end_col] == 255):
        end_col -= 1

    assert start_row <= end_row, 'incorrect start/end row'
    assert start_col <= end_col, 'incorrect start/end col'

    crop = img_array[start_row: end_row, start_col: end_col]

    new_height, new_width = np.shape(crop)
    expand_first = abs(new_height - new_width) // 2
    expand_sec = abs(new_height - new_width) - expand_first

    if new_height > new_width:
        # expand the width by expand_by on both sides
        expand_first = np.full((new_height, expand_first), 255)
        expand_sec = np.full((new_height, expand_sec), 255)
        square = np.hstack((expand_first, crop, expand_sec))
        print(np.shape(square))
    elif new_height < new_width:
        expand_first = np.full((expand_first, new_width), 255)
        expand_sec = np.full((expand_sec, new_width), 255)
        square = np.vstack((expand_first, crop, expand_sec))
        print(np.shape(square))
    else:
        square = crop

    return square.astype(np.uint8)
