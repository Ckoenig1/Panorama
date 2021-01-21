import sys
import os
import pickle as pkl
import argparse

# Christopher Koenig
# this script runs the other three scripts so you dont have to run them one at a time
# i run this script like so
# python ./panorama_creator.py --left_img_path C:\Users\Chris\Pictures\panoramas\goldengate-02.png --right_img_path C:\Users\Chris\Pictures\panoramas\goldengate-03.png --final_panorama_path C:\Users\Chris\Pictures

def main():
    parser = argparse.ArgumentParser(description='code')
    parser.add_argument('--left_img_path', type=str, default=None,
                        help='path of the left img')
    parser.add_argument('--right_img_path', type=str, default=None,
                        help='path of the right img')
    parser.add_argument('--output_path', type=str, default=None,
                        help='path to folder where all output imgs will be saved')
    args = parser.parse_args()
    # this call runs my corner detector script on the left image and outputs a pkl file along with an image that shows
    # all the corners detected
    os.system("python harris_corner_detector.py --img_path " + args.left_img_path + " --pickle_name harris_window_left.pkl --output_path " + args.output_path + "\\visualized_corners.png")
    # this calls the same script for the right image
    os.system("python harris_corner_detector.py --img_path " + args.right_img_path + " --pickle_name harris_window_right.pkl --output_path " + args.output_path + "\\visualized_corners2.png")
    # this calls my corner matching script and produces an image showing the corners that were matched side by side and
    # a pkl file to be used in ransac
    os.system("python corner_matcher.py --pickle_name1 harris_window_left.pkl --pickle_name2 harris_window_right.pkl --img1_path "+args.left_img_path+" --img2_path "+args.right_img_path+" --img_output_path " +args.output_path+"\\paired_matches.png --output_pickle raw_candidates.pkl" )
    # this is the final call that runs my ransac algorithm and panorama creation code it saves the transformation matrix
    # as a txt file using np.savetxt
    os.system("python ransac_matcher.py --pickle_name raw_candidates.pkl --output_path " +args.output_path+"\\final_panorama.png --img_path "+args.left_img_path+" --img2_path "+args.right_img_path)

if __name__ == "__main__":
    main()