import argparse
from mini_behavior.utils.scene_to_grid import gen_grid_from_img
import os

# run this to convert iGibson floor plan image to grid image
# takes in img paths as args (default: process all imgs in scenes dir)

dir_path = os.path.dirname('mini_behavior')
img_dir = os.path.join(dir_path, 'mini_behavior/scenes')
list_scenes = os.listdir(img_dir)
grids_dir = os.path.join(dir_path, 'mini_behavior/floorplans')

parser = argparse.ArgumentParser()
parser.add_argument("--imgs", nargs='+', default=list_scenes,
                    help="path of the floor plan image (REQUIRED)")

args = parser.parse_args()

for img in args.imgs:
    grid_img_path = os.path.join(grids_dir, img)

    if os.path.exists(grid_img_path):
        print('grid for {} already generated'.format(img))
    else:
        grid = gen_grid_from_img(img=img, img_dir=img_dir, save_dir=grids_dir)




