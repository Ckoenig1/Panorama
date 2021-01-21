import numpy as np
import copy
from PIL import Image
from PIL import ImageDraw
import argparse
import math
import sys
import pickle as pkl
# Christopher Koenig
# Usually I run the code like this:
# python .\harris_corner_detector.py --img_path C:\Users\Chris\Pictures\corner.jpg --pickle_name harris_window.pkl -- output_path C:\Users\Chris\Pictures\corner_detected.jpg
# this code will take an image named corner and save an edited version of that image with the corners that were detected drawn as green rectangles
# it will also store the corner locations along with a Gx and Gy window for that location in a lst and then saves that list as a pickle file
# this file is then used in the corner_matcher script

def main():

    def conv1dx(img):
        (img_h, img_w) = img.shape
        # convolution img is 2 smaller to get rid of the padding
        conv_img = np.zeros((img_h - 2,img_w - 2), np.float64)

    # minus 1 because the filter stops at img_h - 1 and range doesnt include the last value
        for i in range(1, img_h - 1):
            for j in range(1, img_w - 1):
                sum = 0.0
                sum = sum + (-1 * float(img[i][j-1]))
                sum = sum + (1 * float(img[i][j+1]))
                conv_img[i - 1][j - 1] = sum

        return conv_img


    def conv1dy(img):
        (img_h, img_w) = img.shape
        # convolution img is 2 smaller to get rid of the padding
        conv_img = np.zeros((img_h - 2,img_w - 2), np.float64)

    # minus 1 because the filter stops at img_h - 1 and range doesnt include the last value
        for i in range(1, img_h - 1):
            for j in range(1, img_w - 1):
                sum = 0.0
                sum = sum + (-1 * float(img[i-1][j]))
                sum = sum + ( 1 * float(img[i+1][j]))
                # subtract 1 to make it index the matrix correctly
                conv_img[i - 1][j - 1] = sum

        return conv_img

    def find_r_value(Gx,Gy,y,x,sizeofM):
        diff = int(sizeofM/2)
        startx = y - diff
        # plus 1 is added to account for range being non inclusive
        endx = y + diff + 1
        starty = x - diff
        endy = x + diff + 1
        Mx = 0
        Mxy = 0
        My = 0
        # i use 3 different variables for the values of the M matrix because i am lazy
        for i in range(startx, endx):
            for j in range(starty, endy):
                Mx += Gx[i][j] ** 2
                Mxy += Gx[i][j] * Gy[i][j]
                My += Gy[i][j] ** 2
        R = (Mx * My - Mxy * Mxy) - 0.05 * ((Mx + My) ** 2)
        return R



    def detectCorners(Gx,Gy,sizeofM):
        rMatrix = np.zeros(Gx.shape,np.float64)
        size = int(sizeofM/2)
        paddedGx = np.pad(Gx,size,'edge')
        paddedGy = np.pad(Gy,size,'edge')
        (height,width) = paddedGx.shape
        print("beginning pic")
        for i in range(size, height - size):

            for j in range(size, width - size):
                rMatrix[i-size][j - size] = find_r_value(paddedGx,paddedGy,i,j,sizeofM)
        return rMatrix


    def sortingfunc(e):
        (r_val,left,right,top,bottom) = e
        return r_val



    def intersection_value(left1,left2,right1,right2,top1,top2,bottom1,bottom2):
        x_overlap = max(0, min(right1,right2) - max(left1,left2))
        y_overlap = max(0, min(bottom1,bottom2) - max(top1,top2))
        return x_overlap * y_overlap

    def nms(list):
        suppressed_list = []
        while(len(list) > 0):
            suppressed_list.append(list[0])
            (garbage,left1,right1,top1,bottom1) = list[0]
            list.pop(0)
            removallst = []
            for item in list:
                (garbage,left2,right2,top2,bottom2) = item
                if(intersection_value(left1,left2,right1,right2,top1,top2,bottom1,bottom2) > 0):
                    removallst.append(item)
            for item in removallst:
                list.remove(item)
        return suppressed_list

    # this function allows me to find the windows of gradients around each corner so that i can store them as a list
    # and pickle them to be used in the corner matching script
    def get_windows(Gx,Gy,i,j):
        (height,width) = Gx.shape
        start_row = i - 2
        start_column = j - 2
        # add one to account for range not being inclusive
        end_row = i + 2 + 1
        end_column = j + 2 + 1
        Gx_list = []
        Gy_list = []
        for y in range(start_row,end_row):
            for x in range(start_column,end_column):
                # check if indexing is out of bounds and if it is set value as zero
                if y < 0 or y > height - 1 or x < 0 or x > width - 1:
                    Gx_list.append(0)
                    Gy_list.append(0)
                else:
                    Gx_list.append(Gx[y][x])
                    Gy_list.append(Gy[y][x])
        return (Gx_list,Gy_list)




    parser = argparse.ArgumentParser(description='code')
    parser.add_argument('--img_path', type=str, default=None,
                        help='path to img')
    parser.add_argument('--pickle_name', type=str, default=None,
                        help='name of the pickle file that will be created including the .pkl')
    parser.add_argument('--output_path', type=str, default=None,
                        help='path of the output img')
    args = parser.parse_args()
    im = Image.open(args.img_path).convert("L")
    imgMatrix = np.asarray(im, dtype = np.float64)
    paddedImg = np.pad(imgMatrix, 1, 'edge')
    Gx = conv1dx(paddedImg)
    Gy = conv1dy(paddedImg)
    r_matrix = detectCorners(Gx,Gy,3)
    (height,width) = r_matrix.shape
    im = im.convert('RGB')
    draw = ImageDraw.Draw(im)
    lst = []
    # creating a list of rvalues that are > than 1000 to cut down corners checked for nms
    for i in range(0,height):
        for j in range(0, width):
            if r_matrix[i][j] > 10000:
                # here i define the bounds of the rectangle associated with each corner
                # to be used in nms to determine overlap
                left = j - 2
                right = j + 2
                top = i - 2
                bottom = i + 2
                lst.append((r_matrix[i][j],left,right,top,bottom))
    # list is now sorted by rvalue so i can run a nms algorithm on it
    lst.sort(reverse=True,key = sortingfunc)
    if len(lst) > 500:
        lst = lst[0:500]
    harris_corners = nms(lst)
    harris_windows = []
    for i in harris_corners:
        (garb, left, right, top, bottom) = i
        draw.rectangle((left,top,right,bottom),fill=(0,255,0))
        # this is kinda just messy coding but i add 2 to the top and left values to get the center of the corner
        # since the function takes a center value not the top and left values
        x = left + 2
        y = top + 2
        (Gx_window,Gy_window) = get_windows(Gx, Gy, y, x)
        harris_windows.append((x,y,Gx_window,Gy_window))
    # save windows as pickle
    with open(args.pickle_name,'wb') as f:
        pkl.dump(harris_windows, f)
    # save modified image
    im.save(args.output_path)




if __name__ == "__main__":
    main()
