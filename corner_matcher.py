import numpy as np
import copy
from PIL import Image
from PIL import ImageDraw
import argparse
import math
import pickle as pkl
# Christopher Koenig
# This script takes 6 arguments. --pickle_name1 and --pickle_name2 refer to the pkls created after running my
# harris_corner_detector for the left and right image respectively. --img1_path and  --img2_path refer to the paths
# of the left and right images respectively. The left and right orientation is important because my code does not handle
# the revere orientation. If you input the right image as pickle_name1/img1_path the code will likely crash
# --img_output_path refers to the path of the match visualization image that will be saved
# --output_pickle refers to the name you would like the candidate data to be saved as.



def main():


    def compute_distance(x1,y1,x2,y2):
        distance = 0
        for i in range(0,25):
            distance += (x1[i] - x2[i])**2 + (y1[i] - y2[i])**2
        return distance



    def get_candidates(c1,c2):
        c1_matches = []
        c1_corners = []
        for (x,y,Gx,Gy)  in c1:
            distance = 100000000000
            for (x2,y2,Gx2,Gy2) in c2:
                comp_dist = compute_distance(Gx,Gy,Gx2,Gy2)
                if comp_dist < distance:
                    distance = comp_dist
                    closest_match = (x2,y2)
            c1_matches.append(((x,y),closest_match,distance))
        c1_matches.sort(key=sortingfunc)
        matches = c1_matches[0:int(len(c1_matches) / 2)]
        return matches


    def sortingfunc(e):
        (x,y,distance) = e
        return distance


    parser = argparse.ArgumentParser(description='code')
    parser.add_argument('--pickle_name1', type=str, default=None,
                        help='file name of the left images pkl file including .pkl')
    parser.add_argument('--pickle_name2', type=str, default=None,
                        help='file name of the right images pkl file including .pkl')
    parser.add_argument('--img1_path', type=str, default=None,
                        help='path to the left img')
    parser.add_argument('--img2_path', type=str, default=None,
                        help='path to the right img')
    parser.add_argument('--img_output_path', type=str, default=None,
                        help='path to the output comparison image')
    parser.add_argument('--output_pickle', type=str, default=None,
                        help='file name for the candidate data to be saved under including .pkl')
    args = parser.parse_args()

    with open(args.pickle_name1,"rb") as f:
        img1 = pkl.load(f)

    with open(args.pickle_name2,"rb") as f:
        img2 = pkl.load(f)
    # here i get a tuple of two lists of matching corners that have been sorted by distance and then cut in half
    candidates = get_candidates(img1,img2)
    # now i visualize both lists of corners with their respective images
    im1 = Image.open(args.img1_path)
    im2 = Image.open(args.img2_path)
    im1 = im1.convert('RGB')
    im2 = im2.convert('RGB')
    draw = ImageDraw.Draw(im1)
    draw2 = ImageDraw.Draw(im2)
    for (c1,c2,distance) in candidates:
        (x,y) = c1
        draw.rectangle((x-2, y-2, x+2, y+2), fill=(0, 255, 0))
        (x2,y2) = c2
        draw2.rectangle((x2 - 2, y2 - 2, x2 + 2, y2 + 2), fill=(0, 255, 0))
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    dst.save(args.img_output_path)
    with open(args.output_pickle, 'wb') as f:
        pkl.dump(candidates, f)
    # save modified image


if __name__== "__main__":
    main()