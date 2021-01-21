import numpy as np
import copy
from PIL import Image
from PIL import ImageDraw
import argparse
import math
import pickle as pkl
import random

# Christopher Koenig

# this code is a combination of questions 4 and 5 since 5 could be completed with little addition to this script i did
# not deem it necessary to create a whole separate script

# the success of this script is dependant on the number of iterations(k) the number of
# also inliers (d) the margin of error (t) and the number of points sampled to make the model (n)
# if the code doesnt work it is likely because the algorithm didnt find a model that fit the data and
# therefore best_model is never set to a value. You can try changing the variables around to fix this issue
# but if your two images only share content on the far left and right side of the image changing these values
# will not magically make it work. To fix this issue steps would need to be taken in the previous scripts.
# one example would be searching for corners only in the left and right half of each image so that less
# non shared features are included in the data. Or you could simply use two pictures that have more overlap


def main():
    def estimate_transformation(matches):
        # This function computes a transformation that maps the locations in pointsb
        # to the locations in pointsa using least squares
        matrix = []
        pointsa = []
        pointsb = []
        for (p1,p2,distance) in matches:
            pointsa.append(p1)
            pointsb.append(p2)
            matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0] * p1[0], -p2[0] * p1[1]])
            matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1] * p1[0], -p2[1] * p1[1]])

        A = np.matrix(matrix, dtype=np.float)
        B = np.array(pointsb).reshape(2 * len(pointsa))

        res = np.dot(np.linalg.inv(A.T * A) * A.T, B)
        return np.array(res).reshape(8)

    def compute_error(pointsa, transformation, pointsb):
        # transform all point in pointsb according to transformation, and compute
        # the total error made by the transformation

        m = [[transformation[0], transformation[1], transformation[2]],
             [transformation[3], transformation[4], transformation[5]],
             [transformation[6], transformation[7], 1]]
        T = np.matrix(m)
        T = np.linalg.inv(T)

        transb = []
        for (x, y) in pointsb:
            p = np.matrix([[x], [y], [1]])
            tp = np.matmul(T, p)
            tpo = (tp[0, 0] / tp[2, 0], tp[1, 0] / tp[2, 0])
            transb.append(tpo)

        err = 0
        for p1, p2 in zip(pointsa, transb):
            err = err + math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

        return err / len(pointsb)




    parser = argparse.ArgumentParser(description='code')
    parser.add_argument('--pickle_name', type=str, default=None,
                        help='name of the pickle file that will be created including the .pkl')
    parser.add_argument('--output_path', type=str, default=None,
                        help='path of the output panorama img')
    parser.add_argument('--img_path', type=str, default=None,
                        help='path of the left img')
    parser.add_argument('--img2_path', type=str, default=None,
                        help='path of the right img')
    args = parser.parse_args()
    with open(args.pickle_name, "rb") as f:
        matches = pkl.load(f)
    k = 400
    iter = 0
    n = 4
    t = 2
    d = 15
    best_error = 1000000000000000000000
    while(iter < k):
        maybe_inliers = random.sample(matches,n)
        maybe_model = estimate_transformation(maybe_inliers)
        also_inliers = []
        for correspondence in matches:
            if not(correspondence in maybe_inliers):
                (pointsa,pointsb,distance) = correspondence
                error = compute_error([pointsa],maybe_model,[pointsb])
                print(error)
                if error < t:
                    also_inliers.append(correspondence)
        if len(also_inliers) > d:
            new_set = maybe_inliers + also_inliers
            better_model = estimate_transformation(new_set)
            pointsa = []
            pointsb = []
            for (pointa,pointb,distance) in new_set:
                pointsa.append(pointa)
                pointsb.append(pointb)
            this_error = compute_error(pointsa,better_model,pointsb)
            if this_error < best_error:
                best_model = better_model
                best_error = this_error
        iter = iter + 1
        print("iter: ",iter,"/",k)

    # with ransac complete i now begin question 5 by stitching together the two images after transforming the right image
    im = Image.open(args.img_path)
    im2 = Image.open(args.img2_path)
    im2 = im2.transform((int(im.width * 1.5), im.height), Image.PERSPECTIVE, best_model,
                 Image.BILINEAR)
    img2_matrix = np.asarray(im2.convert('L'))
    img1_matrix = np.asarray(im.convert('L'))
    stitch_matrix = np.zeros(img2_matrix.shape)
    # this does not account for the case where my previous scripts were run with the right image as img1 and the
    # left img as img2. In other words this (and likely the ransac algorithm) will crash if the scripts arent run
    # how i described
    for i in range(0,img2_matrix.shape[0]):
        for j in range(0,img2_matrix.shape[1]):
            if img2_matrix[i][j] == 0 and i < im.height and j < im.width:
                stitch_matrix[i][j] = img1_matrix[i][j]
            else:
                stitch_matrix[i][j] = img2_matrix[i][j]
    stitched = Image.fromarray(stitch_matrix).convert('RGB')
    stitched.save(args.output_path)
    print(best_model)
    np.savetxt("transformation_matrix.txt",best_model)



if __name__ == "__main__":
    main()
