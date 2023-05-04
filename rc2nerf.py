import argparse
import csv
import json
import math
import numpy as np
import pandas as pd
import os
import cv2
from copy import deepcopy as dc

from tqdm import tqdm
from pathlib import Path

from utils import sharpness, Mat2Nerf, central_point, plot, _PLT
from mat_utils import matrix_from_euler

from concurrent.futures import ThreadPoolExecutor


def parse_args():
    parser = argparse.ArgumentParser(description="convert Reality Capture csv export to nerf format transforms.json")

    parser.add_argument("--csv_in", help="specify csv file location") #TODO: Chang to positional argument
    parser.add_argument("--out", dest="path", default="transforms.json", help="output path")
    parser.add_argument("--imgfolder", default="./images/", help="location of folder with images")
    parser.add_argument("--imgtype", default="jpg", help="type of images (ex. jpg, png, ...)")
    parser.add_argument("--aabb_scale", default=16, type=int, help="size of the aabb, default is 16")
    parser.add_argument("--plot", action="store_true", help="plot the cameras and the bounding region in 3D")
    parser.add_argument("--scale", default=1.0, type=float, help="scale the scene by a factor")
    parser.add_argument("--no_scale", action="store_true", help="DISABLES the scaling of the cameras to the bounding region")
    parser.add_argument("--no_center", action="store_true", help="DISABLES the centering of the cameras around the computed central point")
    parser.add_argument("--camera_size", default=0.1, type=float, help="size of the camera in the 3D plot. Does not affect the output.")

    parser.add_argument("--debug_ignore_images", action="store_true", help="IGNORES the images in the xml file. For debugging purposes only.")

    parser.add_argument("--threads", default=8, type=int, help="number of threads to use for processing")

    args = parser.parse_args()
    return args


def build_sensor(resolution, focal_length, intrinsics:dict):
    out = dict()

    width, height = resolution

    out["w"] = width
    out["h"] = height
    out["fl_x"] = focal_length
    out["fl_y"] = focal_length

    # # Given the w, h, pixel_width, pixel_height, and focal_length
    # # Calculate the focal length in pixels
    # fl_pxl = (w * focal_length) / (w * pixel_width)

    camera_angle_x = math.atan(float(width) / (float(focal_length) * 2)) * 2
    camera_angle_y = math.atan(float(height) / (float(focal_length) * 2)) * 2

    out["camera_angle_x"] = camera_angle_x
    out["camera_angle_y"] = camera_angle_y

    intrinsics_keys = ['cx', 'cy', 'b1', 'b2',
                       'k1', 'k2', 'k3', 'k4',
                       'p1', 'p2', 'p3', 'p4']
    
    for intrinsic in intrinsics_keys:
        if intrinsic not in intrinsics.keys():
            continue

        out[intrinsic] = intrinsics[intrinsic]
        
    return out


def build_transform_matrix(position, rotation):
    # mat = np.eye(4)
    mat = matrix_from_euler(rotation, order='yxz')

    mat[:3,3] = position
    
    return mat


if __name__ == "__main__":
    args = parse_args()
    CSV_PATH = args.csv_in
    IMGTYPE = args.imgtype
    IMGFOLDER = args.imgfolder

    files = list(Path(IMGFOLDER).glob('*.{}'.format(IMGTYPE)))
    stems = list([f.stem for f in files])

    # Check if the files path has images in it
    if(len(files)==0) & (args.debug_ignore_images==False):
        print('No images found in folder: {}'.format(IMGFOLDER))
        exit()

    out = dict()

    out['aabb_scale'] = args.aabb_scale


    def read_img(row):
        i, row = row
        img_file_path = os.path.join(IMGFOLDER, row['#name'])
        if os.path.exists(img_file_path):
            img = cv2.imread(os.path.join(IMGFOLDER, row['#name']))
        else:
            img = None
        return row, img


    frames = []

    df = pd.read_csv(CSV_PATH, sep=',')
    pbar = tqdm(total=len(df))

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
         for row, img in executor.map(read_img, df.iterrows()):
            pbar.update(1)

            if img is None:
                print( f'{row["#name"]} image found' )
                continue
        
            # f, px, py, k1, k2, k3, k4, t1, t2

            width, height, *_ = img.shape

            focal = row['f'] * np.maximum(width, height) / 36

            intrinsics = dict(
                cx=row['px'] / 36.0 + width / 2.0,
                cy=row['py'] / 36.0 + height / 2.0,
                k1=row['k1'],
                k2=row['k2'],
                k3=row['k3'],
                k4=row['k4'],
                p1=row['t1'],
                p2=row['t2'],
                )
            
            camera = build_sensor((width, height), focal, row.to_dict())

            mat = np.eye(4)

            mat[:3, :3] = matrix_from_euler([row['pitch'], row['heading'], row['roll']], 'yxz', True)

            mat[:3,3] = [row['x'], row['y'], row['alt']]

            camera['transform_matrix'] = Mat2Nerf(mat)

            camera['sharpness'] = sharpness(img)

            frames.append(camera)

    out['frames'] = frames

    if args.no_center:
        center = np.zeros(3)
    else:
        # Compute the center of attention
        center = central_point(out)

    # Set the offset and convert to list
    for f in out["frames"]:
        f["transform_matrix"][0:3,3] -= center
        f["transform_matrix"] = f["transform_matrix"].tolist()

    with open(args.path, "w") as f:
        json.dump(out, f, indent=4)

    if _PLT & args.plot:
        plot(out, center, args.camera_size)