# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 10:27:39 2020

@author: Mark Lundine
"""

import numpy as np
import cv2
import PIL
import sys
from PIL import Image
from PIL.ExifTags import TAGS
Image.MAX_IMAGE_PIXELS = None
import skvideo
import os
wd = os.getcwd()
ffmpeg_path = os.path.join(wd, 'ffmpeg', 'bin')
skvideo.setFFmpegPath(ffmpeg_path)
import skvideo.io
import glob
from PIL import ImageFilter
from os.path import join
import datetime as dt
### Code adapated from javascript code available at https://github.com/nikolajbech/underwater-image-color-correction

def getColorFilterMatrix(img_array, width, height, avg, MIN_AVG_RED, MAX_HUE_SHIFT, BLUE_MAGIC_VALUE):

    ### Magic values:
    NUM_PIXELS = width * height
    THRESHOLD_RATIO = 2000
    THRESHOLD_LEVEL = NUM_PIXELS/THRESHOLD_RATIO

    ## Objects:
    hist = { 'r': [], 'g': [], 'b': [] }
    normalize = { 'r': [], 'g': [], 'b': [] }
    adjust = { 'r': [], 'g': [], 'b': [] }
    hueShift = 0
    
    avg = avg

    ## Calculate shift amount:
    newAvgRed = avg['r']
    while (newAvgRed < MIN_AVG_RED):
        shifted = hueShiftRed(avg['r'], avg['g'], avg['b'], hueShift)
        newAvgRed = shifted[0] + shifted[1] + shifted[2]
        hueShift = hueShift+1
        if (hueShift > MAX_HUE_SHIFT):
            newAvgRed = 60 ## max value
    
    ### New histograms
    red = np.round(img_array[...,0], 0).astype('uint8')
    green = np.round(img_array[...,1], 0).astype('uint8')
    blue = np.round(img_array[...,2], 0).astype('uint8')
    shifted = hueShiftRed(red, green, blue, hueShift)
    red = shifted[0] + shifted[1] + shifted[2]
    red = np.round(red,0).astype('uint8')
    hist['r'] = np.histogram(red, range(256))
    hist['g'] = np.histogram(green, range(256))
    hist['b'] = np.histogram(blue, range(256))

    ## Find values under threshold:
    normalize['r'] = np.nonzero(hist['r'][0]-THRESHOLD_LEVEL < 2)
    normalize['g'] = np.nonzero(hist['g'][0]-THRESHOLD_LEVEL < 2)
    normalize['b'] = np.nonzero(hist['b'][0]-THRESHOLD_LEVEL < 2)
    
    ## Insert 0 as start value in normalize array:
    normalize['r'] = np.insert(normalize['r'],0,0)
    normalize['g'] = np.insert(normalize['g'],0,0)
    normalize['b'] = np.insert(normalize['b'],0,0)

    ## Insert 255 as end value in normalize array:
    normalize['r'] = np.insert(normalize['r'],-1,255)
    normalize['g'] = np.insert(normalize['g'],-1,255)
    normalize['b'] = np.insert(normalize['b'],-1,255)

    #normalize
    adjust['r'] = normalizingInterval(normalize['r'])
    adjust['g'] = normalizingInterval(normalize['g'])
    adjust['b'] = normalizingInterval(normalize['b'])

    ## Make histogram:
    shifted = hueShiftRed(1, 1, 1, hueShift)

    redGain = 256 / (adjust['r'][1] - adjust['r'][0])
    greenGain = 256 / (adjust['g'][1] - adjust['g'][0])
    blueGain = 256 / (adjust['b'][1] - adjust['b'][0])

    redOffset = (-adjust['r'][0] / 256) * redGain
    greenOffset = (-adjust['g'][0] / 256) * greenGain
    blueOffset = (-adjust['b'][0] / 256) * blueGain

    adjstRed = shifted[0] * redGain
    adjstRedGreen = shifted[1] * redGain
    adjstRedBlue = shifted[2] * redGain * BLUE_MAGIC_VALUE
    
    return [
        adjstRed, adjstRedGreen, adjstRedBlue, 0, redOffset,
        0, greenGain, 0, 0, greenOffset,
        0, 0, blueGain, 0, blueOffset,
        0, 0, 0, 1, 0,
    ]

def calculateAverageColor(img_array, width, height):
    avg = {'r': 0, 'g':0, 'b':0}        
    ## Calculate average:
    avg['r'] = np.mean(img_array[...,0])
    avg['g'] = np.mean(img_array[...,1])
    avg['b'] = np.mean(img_array[...,2])

    return avg

def hueShiftRed(r, g, b, h):
    U = np.cos((h * np.pi)/180)
    W = np.sin((h * np.pi)/180)

    r = (0.299 + 0.701 * U + 0.168 * W) * r
    g = (0.587 - 0.587 * U + 0.330 * W) * g
    b = (0.114 - 0.114 * U - 0.497 * W) * b

    return [r,g,b]

def normalizingInterval(normArray):
    high = 255
    low = 0
    maxDist = 0

    for i in range(len(normArray)):
        dist = normArray[i] - normArray[i - 1]
        if (dist > maxDist):
            maxDist = dist
            high = normArray[i]
            low = normArray[i - 1]
    return [low, high]

def applyFilter(data, height, width, filterMatrix):
    new_img = np.zeros((height,width,3))
    new_img[...,0] = np.round(((data[...,0] * filterMatrix[0]) + (data[...,1] * filterMatrix[1])
                               + (data[...,2] * filterMatrix[2])) + filterMatrix[4] * 255,0)
    new_img[...,1] = np.round((data[...,1] * filterMatrix[6]) + filterMatrix[9] * 255,0) # Green
    new_img[...,2] = np.round((data[...,2] * filterMatrix[12]) + filterMatrix[14] * 255,0) ## Blue
    new_img[new_img<0] = 0
    new_img[new_img>255] = 255
    return new_img.astype('uint8')

def gdal_open(image_path):
    ### read in image to classify with gdal
    driverTiff = gdal.GetDriverByName('GTiff')
    input_raster = gdal.Open(image_path)
    nbands = input_raster.RasterCount
    prj = input_raster.GetProjection()
    gt = input_raster.GetGeoTransform()
    ### create an empty array, each column of the empty array will hold one band of data from the image
    ### loop through each band in the image nad add to the data array
    data = np.empty((input_raster.RasterYSize, input_raster.RasterXSize, nbands))
    for i in range(1, nbands+1):
        band = input_raster.GetRasterBand(i).ReadAsArray()
        data[:, :, i-1] = band
    return data, prj, gt

## Base values
#    MIN_AVG_RED = 60
#    MAX_HUE_SHIFT = 120
#    BLUE_MAGIC_VALUE = 1.2
#    Sharpen = 2
### Update to run on single, batch, and different parameters
def single_image(path, MIN_AVG_RED, MAX_HUE_SHIFT, BLUE_MAGIC_VALUE, SHARPEN, geo=False, clahe=False):
    extension = os.path.splitext(os.path.basename(path))[1]
    new_path = os.path.splitext(os.path.basename(path))[0] + '_cc'
    wd = os.getcwd()
    saveFolder = 'correction_results'
    saveFolder = os.path.join(wd, saveFolder)
    new_path = os.path.join(saveFolder, new_path)
    time_str = dt.datetime.now().strftime('%Y%m%d%H%M%S')
    if geo == False:
        img_arr = cv2.imread(path, 1)
        img_arr = img_arr[:, :, [2, 1, 0]]
    else:
        img_arr, prj, gt = gdal_open(path)
        rasterY, rasterX, nbands = np.shape(img_arr)
        if nbands >3:
            alpha = img_arr[:,:,3]
            img_arr = img_arr[:,:,0:3]
        print(np.shape(img_arr))
    height,width,channels = img_arr.shape
    avg = calculateAverageColor(img_arr, width, height)
    filterMatrix = getColorFilterMatrix(img_arr, width, height, avg, MIN_AVG_RED, MAX_HUE_SHIFT, BLUE_MAGIC_VALUE)
    filtered_img = applyFilter(img_arr, height, width, filterMatrix)
    if clahe == True:
        clahefilter = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(16,16))
        #NORMAL
        # convert to gray
        gray = cv2.cvtColor(filtered_img, cv2.COLOR_BGR2GRAY)
        grayimg = gray
        GLARE_MIN = np.array([0, 0, 50],np.uint8)
        GLARE_MAX = np.array([0, 0, 225],np.uint8)
        #CLAHE
        claheCorrecttedFrame = clahefilter.apply(grayimg)

        #COLOR 
        lab = cv2.cvtColor(filtered_img, cv2.COLOR_BGR2LAB)
        lab_planes = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8))
        lab_planes[0] = clahe.apply(lab_planes[0])
        lab = cv2.merge(lab_planes)
        clahe_bgr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        filtered_img = clahe_bgr[:,:,[2,1,0]]
        save_path = (new_path + '_' + time_str + '_red_' + str(MIN_AVG_RED) +
             '_hue' + str(MAX_HUE_SHIFT) +
             '_blue' + str(BLUE_MAGIC_VALUE) +
             '_sharpen' + str(SHARPEN) + '_clahe' +extension)
    else:
        save_path = (new_path + '_' + time_str + '_red_' + str(MIN_AVG_RED) +
             '_hue' + str(MAX_HUE_SHIFT) +
             '_blue' + str(BLUE_MAGIC_VALUE) +
             '_sharpen' + str(SHARPEN) + extension)
    if SHARPEN > 0:
        sharp_filt_img = PIL.Image.fromarray(filtered_img)
        for i in range(SHARPEN):
            sharp_filt_img = sharp_filt_img.filter(ImageFilter.SHARPEN)
        sharp_filt_img = cv2.cvtColor(np.array(sharp_filt_img), cv2.COLOR_RGB2BGR)
    else:
        sharp_filt_img = filtered_img

    print(save_path)
    if geo==False:
        if os.path.isdir(saveFolder):
            cv2.imwrite(save_path, sharp_filt_img)
            sharp_filt_img = None
        else:
            os.makedirs(saveFolder)
            cv2.imwrite(save_path, sharp_filt_img)
            sharp_filt_img = None
    else:
        driverTiff = gdal.GetDriverByName('GTiff')
        clfds = driverTiff.Create(save_path, rasterX, rasterY, nbands, gdal.GDT_Float32)
        clfds.SetGeoTransform(gt)
        clfds.SetProjection(prj)
        for i in range(1,4):
            clfds.GetRasterBand(i).SetNoDataValue(-9999)
            clfds.GetRasterBand(i).WriteArray(sharp_filt_img[:,:,i-1])
        if nbands > 3:
            clfds.GetRasterBand(4).WriteArray(alpha)
        clfds = None
        sharp_filt_img = None  
    return save_path
     
def batch_image(folder, MIN_AVG_RED, MAX_HUE_SHIFT, BLUE_MAGIC_VALUE, SHARPEN, clahe):
    types = ('/*.jpg', '/*.png', '/*.jpeg', '/*.tif')
    files = []
    for ext in types:
        for im in glob.glob(folder + ext):
            files.append(im)
    for im in files:
        single_image(im, MIN_AVG_RED, MAX_HUE_SHIFT, BLUE_MAGIC_VALUE, SHARPEN, clahe=clahe)        
        
def single_video(vid_path, MIN_AVG_RED, MAX_HUE_SHIFT, BLUE_MAGIC_VALUE, SHARPEN, clahe):
    data = skvideo.io.ffprobe(vid_path)
    rate = data['video']['@avg_frame_rate']
    reader =  skvideo.io.FFmpegReader(vid_path)
    wd = os.getcwd()
    new_vid_path = os.path.splitext(os.path.basename(vid_path))[0]
    new_vid_dir = os.path.join(wd, 'correction_results')
    new_vid_path = os.path.join(new_vid_dir, new_vid_path)
    new_vid_path = new_vid_path + '_cc.mp4'
    try:
        writer = skvideo.io.FFmpegWriter(new_vid_path, outputdict = {'-r': rate})
    except:
        os.makedirs(new_vid_dir)
        writer = skvideo.io.FFmpegWriter(new_vid_path, outputdict = {'-r': rate})
    for frame in reader.nextFrame():
        height = frame.shape[0]
        width = frame.shape[1]
        avg = calculateAverageColor(frame, width, height)
        filterMatrix = getColorFilterMatrix(frame, width, height, avg, MIN_AVG_RED, MAX_HUE_SHIFT, BLUE_MAGIC_VALUE)
        filtered_img = applyFilter(frame, height, width, filterMatrix)
        if clahe == True:
            clahefilter = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(16,16))
            #NORMAL
            # convert to gray
            gray = cv2.cvtColor(filtered_img, cv2.COLOR_BGR2GRAY)
            grayimg = gray
            GLARE_MIN = np.array([0, 0, 50],np.uint8)
            GLARE_MAX = np.array([0, 0, 225],np.uint8)
            #CLAHE
            claheCorrecttedFrame = clahefilter.apply(grayimg)

            #COLOR 
            lab = cv2.cvtColor(filtered_img, cv2.COLOR_BGR2LAB)
            lab_planes = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8))
            lab_planes[0] = clahe.apply(lab_planes[0])
            lab = cv2.merge(lab_planes)
            clahe_bgr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            filtered_img = clahe_bgr[:,:,[2,1,0]]
            sharp_filt_img = PIL.Image.fromarray(filtered_img)
        for j in range(SHARPEN):
            sharp_filt_img = sharp_filt_img.filter(ImageFilter.SHARPEN)
        final_arr = np.asarray(sharp_filt_img).astype('uint8')
        writer.writeFrame(final_arr)
    writer.close()
    
def batch_video(folder, MIN_AVG_RED, MAX_HUE_SHIFT, BLUE_MAGIC_VALUE, SHARPEN):
    for vid in glob.glob(folder + '/*.mp4'):
        single_video(vid)


    

def getexif(path):
    img = Image.open(path)
    exif = img.getexif()
    # iterating over all EXIF data fields
    for tag_id in exif:
        # get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        data = exif.get(tag_id)
        # decode bytes 
        if isinstance(data, bytes):
            data = data.decode()
        print(f"{tag:25}: {data}")







