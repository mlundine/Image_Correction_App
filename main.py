# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 13:08:41 2020

@author: mlund
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import glob
import sys
import os
import Lundine_underwater_color_correction as cc
from PIL.ImageQt import ImageQt
import gc

        
class Window(QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(50, 50, 800, 800)
        self.setWindowTitle("Underwater Image Color Correction")
        self.home()

    def exit_func(self, eBut, runBut, imgs):
        runBut.setEnabled(False)
        runBut.hide()
        eBut.setEnabled(False)
        eBut.hide()
        for img in imgs:
            img.hide()
        try:
            del globals()['folderName']
            del globals()['fileName']
            del globals()['vidFileName']
        except:
            pass

        

    def correct(self, path, red, hue, blue, sharp, lab):
        new_img = cc.single_image(path, 
                                  red, 
                                  hue, 
                                  blue, 
                                  sharp)
        
        pixmap2 = QPixmap(new_img)
        small_pixmap2 = pixmap2.scaled(int(pixmap2.width()/5), int(pixmap2.height()/5))
        lab.setPixmap(small_pixmap2)
        lab.resize(int(pixmap2.width()/5), int(pixmap2.height()/5))
        lab.move(960,50)
        lab.show() 
        
    
    def correct_batch(self, folder, red, hue, blue, sharp):
        cc.batch_image(folder, red, hue, blue, sharp)
            
    def correct_vid(self, file, red, hue, blue, sharp):
        cc.single_video(file, red, hue, blue, sharp)
        
        
    def openFileNameDialog(self, button, imLab, rBut, hBut, bBut, sBut, eBut):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        global fileName
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Images (*.jpeg *.jpg *.png *.tif)", options=options)
        if fileName:
            label = QLabel(self)
            pixmap = QPixmap(fileName)
            small_pixmap = pixmap.scaled(int(pixmap.width()/5), int(pixmap.height()/5))
            label.setPixmap(small_pixmap)
            label.move(150,50)
            label.resize(int(pixmap.width()/5),int(pixmap.height()/5))
            label.show()

            button.show()
            button.setEnabled(True)
            button.clicked.connect(lambda: self.correct(fileName, rBut.value(), hBut.value(), bBut.value(), sBut.value(), imLab))

            img_buttons = [label, imLab]
            eBut.show()
            eBut.setEnabled(True)
            eBut.clicked.connect(lambda: self.exit_func(eBut, button, img_buttons))
            
        
    def openDirectory(self, button, rBut, hBut, bBut, sBut, eBut):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        global folderName
        folderName = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if folderName:
            types = ('/*.jpg', '/*.png', '/*.jpeg', '/*.tif')
            file_list = []
            for ext in types:
                for im in glob.glob(folderName + ext):
                    file_list.append(im)
            file_labs = []
            if len(file_list) < 30:
                ct = 0
                for im in file_list:
                    file_lab = QLabel(im, self)
                    file_lab.resize(900,20)
                    file_lab.move(500, ct*20)
                    file_lab.show()
                    ct = ct+1
                    file_labs.append(file_lab)
            else:
                file_lab = QLabel('Working on Folder: ' + folderName, self)
                file_lab.resize(900,20)
                file_lab.move(500, 0)
                file_lab.show()
                file_labs.append(file_lab)

            button.show()
            button.setEnabled(True)

            
            button.clicked.connect(lambda: self.correct_batch(folderName, rBut.value(), hBut.value(), bBut.value(), sBut.value()))

            eBut.show()
            eBut.setEnabled(True)
            eBut.clicked.connect(lambda: self.exit_func(eBut, button, file_labs))
            
    def openVideo(self, button, rBut, hBut, bBut, sBut, eBut):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        global vidFileName
        vidFileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Videos (*.mp4)", options=options)
        if vidFileName:
            vidLabel = QLabel(vidFileName, self)
            vidLabel.resize(900,20)
            vidLabel.move(450, 200)
            vidLabel.show()


            button.show()
            button.setEnabled(True)
            button.clicked.connect(lambda: self.correct_vid(vidFileName, rBut.value(), hBut.value(), bBut.value(), sBut.value()))

            videoLabels = [vidLabel]
            eBut.show()
            eBut.setEnabled(True)
            eBut.clicked.connect(lambda: self.exit_func(eBut, button, videoLabels))
        
    def home(self):
        
        ##Button for single image
        singleImage = QPushButton("Single Image", self)
        singleImage.resize(100,100)

        ## Button for batch of images
        batchIm = QPushButton("Batch of Images", self)
        batchIm.resize(100,100)
        batchIm.move(0,100)
        
        ##Button for a single video
        singleVid = QPushButton('Single Video', self)
        singleVid.resize(100,100)
        singleVid.move(0,200)
        
        ### red slider
        min_avg_red_label = QLabel('Minimum Average Red', self)
        min_avg_red_label.resize(130,25)
        min_avg_red_label.move(5,325)
        min_avg_red_slider = QSpinBox(self)
        min_avg_red_slider.setMinimum(0)
        min_avg_red_slider.setMaximum(255)
        min_avg_red_slider.setValue(60)
        min_avg_red_slider.move(5,350)
        
        
        
        ##hue shift slider
        max_hue_shift_label = QLabel('Maximum Hue Shift', self)
        max_hue_shift_label.resize(125,25)
        max_hue_shift_label.move(5,390)
        max_hue_shift_slider = QSpinBox(self)
        max_hue_shift_slider.setMinimum(0)
        max_hue_shift_slider.setMaximum(255)
        max_hue_shift_slider.setValue(120)
        max_hue_shift_slider.move(5,415)
        
        
        
        #blue magic value slider
        blue_magic_val_label = QLabel('Blue Magic Value', self)
        blue_magic_val_label.resize(125,25)
        blue_magic_val_label.move(5,455)
        blue_magic_val_slider = QDoubleSpinBox(self)
        blue_magic_val_slider.setMinimum(0)
        blue_magic_val_slider.setMaximum(255)
        blue_magic_val_slider.setValue(1.2)
        blue_magic_val_slider.move(5,480)
        
        
        
        ##sharpen slider
        sharpen_label = QLabel('Sharpen Steps', self)
        sharpen_label.resize(125,25)
        sharpen_label.move(5,520)
        sharpen_slider = QSpinBox(self)
        sharpen_slider.setValue(1)
        blue_magic_val_slider.setMinimum(0)
        blue_magic_val_slider.setMaximum(10)
        sharpen_slider.move(5,545)
        
        
        
        ##original image label
        old = QLabel('Original', self)
        old.move(450,800)
        old.resize(100,100)
        
        
        #corrected image label
        new = QLabel('Corrected', self)
        new.move(1250,800)
        new.resize(100,100)
        
        
        #run buttons
        run_algorithm1 = QPushButton('Run', self)
        run_algorithm1.resize(100,100)
        run_algorithm1.move(0,600)
        run_algorithm1.setEnabled(False)

        run_algorithm2 = QPushButton('Run', self)
        run_algorithm2.resize(100,100)
        run_algorithm2.move(0,600)
        run_algorithm2.setEnabled(False)

        run_algorithm3 = QPushButton('Run', self)
        run_algorithm3.resize(100,100)
        run_algorithm3.move(0,600)
        run_algorithm3.setEnabled(False)
        
        #exit button
        exit_button = QPushButton('Close Images', self)
        exit_button.resize(100,100)
        exit_button.move(0,700)
        exit_button.setEnabled(False)
        
        
        ##corrected image label
        label2 = QLabel(self)
        
        #initialize image path
        image = None
        
        
        ##clicking on single image
        singleImage.clicked.connect(lambda: self.openFileNameDialog(run_algorithm1,
                                                                    label2,
                                                                    min_avg_red_slider, 
                                                                    max_hue_shift_slider,
                                                                    blue_magic_val_slider,
                                                                    sharpen_slider,
                                                                    exit_button
                                                                    ))


        ##clicking on batch image
        batchIm.clicked.connect(lambda: self.openDirectory(run_algorithm2,
                                                           min_avg_red_slider, 
                                                           max_hue_shift_slider,
                                                           blue_magic_val_slider,
                                                           sharpen_slider,
                                                           exit_button
                                                           ))
        
        ##clicking on single video
        singleVid.clicked.connect(lambda: self.openVideo(run_algorithm3,
                                                         min_avg_red_slider, 
                                                         max_hue_shift_slider,
                                                         blue_magic_val_slider,
                                                         sharpen_slider,
                                                         exit_button))
        
        
        
        self.show()
        run_algorithm1.hide()
        run_algorithm2.hide()
        run_algorithm3.hide()
        exit_button.hide()
       
def run():
    app = QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())

run()

