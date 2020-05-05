# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 10:27:39 2020

@author: Mark Lundine
"""

import numpy as np
import PIL
import skvideo
import os
wd = os.getcwd()
ffmpeg_path = os.path.join(wd, 'ffmpeg', 'bin')
skvideo.setFFmpegPath(ffmpeg_path)
import skvideo.io
import glob
from PIL import ImageFilter
from os.path import join
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

    ## Push 0 as start value in normalize array:
    normalize['r'].append(0)
    normalize['g'].append(0)
    normalize['b'].append(0)

    ## Find values under threshold:
    for i in range(255): 
        if (hist['r'][0][i] - THRESHOLD_LEVEL < 2):
            normalize['r'].append(i)
        if (hist['g'][0][i] - THRESHOLD_LEVEL < 2):
            normalize['g'].append(i)
        if (hist['b'][0][i] - THRESHOLD_LEVEL < 2):
            normalize['b'].append(i)
    
    ## Push 255 as end value in normalize array:
    normalize['r'].append(255)
    normalize['g'].append(255)
    normalize['b'].append(255)

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
    new_img[...,0] = np.round(((data[...,0] * filterMatrix[0]) + (data[...,1] * filterMatrix[1]) + (data[...,2] * filterMatrix[2])) + filterMatrix[4] * 255,0)
    new_img[...,1] = np.round((data[...,1] * filterMatrix[6]) + filterMatrix[9] * 255,0) # Green
    new_img[...,2] = np.round((data[...,2] * filterMatrix[12]) + filterMatrix[14] * 255,0) ## Blue
    new_img[new_img<0] = 0
    new_img[new_img>255] = 255
    return new_img.astype('uint8')


## Base values
#    MIN_AVG_RED = 60
#    MAX_HUE_SHIFT = 120
#    BLUE_MAGIC_VALUE = 1.2
#    Sharpen = 2
### Update to run on single, batch, and different parameters
def single_image(path, MIN_AVG_RED, MAX_HUE_SHIFT, BLUE_MAGIC_VALUE, SHARPEN):
    img = PIL.Image.open(path)
    #exif = img.info['exif']
    width,height = img.size
    img_arr = np.asarray(img)
    avg = calculateAverageColor(img_arr, width, height)
    filterMatrix = getColorFilterMatrix(img_arr, width, height, avg, MIN_AVG_RED, MAX_HUE_SHIFT, BLUE_MAGIC_VALUE)
    filtered_img = applyFilter(img_arr, height, width, filterMatrix)
    sharp_filt_img = PIL.Image.fromarray(filtered_img)
    for i in range(SHARPEN):
        sharp_filt_img = sharp_filt_img.filter(ImageFilter.SHARPEN)
    new_path = os.path.splitext(os.path.basename(path))[0] + '_cc.jpeg'
    wd = os.getcwd()
    new_path = os.path.join(wd, 'correction_results', new_path)
    try:
        sharp_filt_img.save(new_path)
    except:
        newDir = os.path.join(wd, 'correction_results')
        os.makedirs(newDir)
        sharp_filt_img.save(new_path)
    return new_path
     
def batch_image(folder, MIN_AVG_RED, MAX_HUE_SHIFT, BLUE_MAGIC_VALUE, SHARPEN):
    types = ('/*.jpg', '/*.png', '/*.jpeg', '/*.tif')
    files = []
    for ext in types:
        for im in glob.glob(folder + ext):
            files.append(im)
    for im in files:
        single_image(im, MIN_AVG_RED, MAX_HUE_SHIFT, BLUE_MAGIC_VALUE, SHARPEN)        
        
def single_video(vid_path, MIN_AVG_RED, MAX_HUE_SHIFT, BLUE_MAGIC_VALUE, SHARPEN):
    data = skvideo.io.ffprobe(vid_path)['video']
    rate = data['@r_frame_rate']
    reader =  skvideo.io.FFmpegReader(vid_path)
    wd = os.getcwd()
    new_vid_path = os.path.splitext(os.path.basename(vid_path))[0]
    new_vid_dir = os.path.join(wd, 'correction_results')
    try:
        new_vid_path = os.path.join(new_vid_dir, new_vid_path)
        new_vid_path = new_vid_path + '_cc.mp4'
        writer = skvideo.io.FFmpegWriter(new_vid_path, outputdict = {'-r': rate})
    except:
        os.makedirs(new_vid_dir)
        new_vid_path = os.path.join(new_vid_dir, new_vid_path)
        new_vid_path = new_vid_path + '_cc.mp4'
        writer = skvideo.io.FFmpegWriter(new_vid_path + '_cc.mp4', outputdict = {'-r': rate})
    for frame in reader.nextFrame():
        height = frame.shape[0]
        width = frame.shape[1]
        avg = calculateAverageColor(frame, width, height)
        filterMatrix = getColorFilterMatrix(frame, width, height, avg, MIN_AVG_RED, MAX_HUE_SHIFT, BLUE_MAGIC_VALUE)
        filtered_img = applyFilter(frame, height, width, filterMatrix)
        sharp_filt_img = PIL.Image.fromarray(filtered_img)
        for j in range(SHARPEN):
            sharp_filt_img = sharp_filt_img.filter(ImageFilter.SHARPEN)
        final_arr = np.asarray(sharp_filt_img).astype('uint8')
        writer.writeFrame(final_arr)
    writer.close()
    
def batch_video(folder, MIN_AVG_RED, MAX_HUE_SHIFT, BLUE_MAGIC_VALUE, SHARPEN):
    for vid in glob.glob(folder + '/*.mp4'):
        single_video(vid)



