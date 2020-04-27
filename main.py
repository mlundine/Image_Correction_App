# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 13:08:41 2020

@author: mlund
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
# Only needed for access to command line arguments
import sys
import Lundine_underwater_color_correction as cc
from PIL.ImageQt import ImageQt
import matplotlib.pyplot as plt
        
class Window(QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(50, 50, 500, 300)
        self.setWindowTitle("Underwater Image Color Correction")
        self.home()            
            
            

    def correct(self, algorithm_dict, lab):
        new_img = cc.single_image(algorithm_dict['path'], 
                                  algorithm_dict['red'], 
                                  algorithm_dict['hue'], 
                                  algorithm_dict['blue'], 
                                  algorithm_dict['sharp'])
        
        pixmap2 = QPixmap(new_img)
        small_pixmap2 = pixmap2.scaled(int(pixmap2.width()/5), int(pixmap2.height()/5))
        lab.setPixmap(small_pixmap2)
        lab.resize(int(pixmap2.width()/5), int(pixmap2.height()/5))
        lab.move(960,50)
        lab.show() 
        
    
    def change_value(self,val):
        red = val
        return red
        

    def make_algorithm_dict(self, path, red, hue, blue, sharp):
        algorithm_dict = {'path':path,
                          'red':red, 
                          'hue':hue,
                          'blue':blue,
                          'sharp':sharp}      
        return algorithm_dict
    
    def correct_batch(self, folder, red, hue, blue, sharp):
        cc.batch_image(folder, red, hue, blue, sharp)
        
    def correct_vid(self, file, red, hue, blue, sharp):
        cc.single_video(file, red, hue, blue, sharp)
        
    def openFileNameDialog(self, red, hue, blue, sharp, button, imLab, rBut, hBut, bBut, sBut):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Images (*.jpeg *.jpg *.png *.tif)", options=options)
        if fileName:
            label = QLabel(self)
            pixmap = QPixmap(fileName)
            small_pixmap = pixmap.scaled(int(pixmap.width()/5), int(pixmap.height()/5))
            label.setPixmap(small_pixmap)
            label.move(150,50)
            label.resize(int(pixmap.width()/5),int(pixmap.height()/5))
            label.show()  
            alg_dict = self.make_algorithm_dict(fileName, red, hue, blue, sharp)
            button.setEnabled(True)
            button.clicked.connect(lambda: self.correct(alg_dict, imLab))
            return alg_dict
        
    def openDirectory(self, red, hue, blue, sharp, button, rBut, hBut, bBut, sBut):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        folderName = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if folderName:
            button.setEnabled(True)
            button.clicked.connect(lambda: self.correct_batch(folderName, red, hue, blue, sharp))
            
    def openVideo(self, red, hue, blue, sharp, button, rBut, hBut, bBut, sBut):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Videos (*.mp4)", options=options)
        if fileName:
            button.setEnabled(True)
            button.clicked.connect(lambda: self.correct_vid(fileName, red, hue, blue, sharp))
        
        
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
        min_avg_red_label.resize(125,25)
        min_avg_red_label.move(5,325)
        min_avg_red_slider = QSpinBox(self)
        min_avg_red_slider.setMinimum(0)
        min_avg_red_slider.setMaximum(255)
        min_avg_red_slider.setValue(60)
        min_avg_red_slider.move(5,350)
        red = min_avg_red_slider.value()
        
        
        ##hue shift slider
        max_hue_shift_label = QLabel('Maximum Hue Shift', self)
        max_hue_shift_label.resize(125,25)
        max_hue_shift_label.move(5,390)
        max_hue_shift_slider = QSpinBox(self)
        max_hue_shift_slider.setMinimum(0)
        max_hue_shift_slider.setMaximum(255)
        max_hue_shift_slider.setValue(120)
        max_hue_shift_slider.move(5,415)
        hue = max_hue_shift_slider.value()
        
        
        #blue magic value slider
        blue_magic_val_label = QLabel('Blue Magic Value', self)
        blue_magic_val_label.resize(125,25)
        blue_magic_val_label.move(5,455)
        blue_magic_val_slider = QDoubleSpinBox(self)
        blue_magic_val_slider.setMinimum(0)
        blue_magic_val_slider.setMaximum(255)
        blue_magic_val_slider.setValue(1.2)
        blue_magic_val_slider.move(5,480)
        blue = blue_magic_val_slider.value()
        
        
        ##sharpen slider
        sharpen_label = QLabel('Sharpen Steps', self)
        sharpen_label.resize(125,25)
        sharpen_label.move(5,520)
        sharpen_slider = QSpinBox(self)
        sharpen_slider.setValue(1)
        sharpen_slider.move(5,545)
        sharp = sharpen_slider.value()
        
        
        ##original image label
        old = QLabel('Original', self)
        old.move(450,800)
        old.resize(100,100)
        
        
        #corrected image label
        new = QLabel('Corrected', self)
        new.move(1250,800)
        new.resize(100,100)
        
        
        #run button
        run_algorithm = QPushButton('Run', self)
        run_algorithm.resize(100,100)
        run_algorithm.move(0,600)
        run_algorithm.setEnabled(False)
        
        
        ##corrected image label
        label2 = QLabel(self)
        
        #initialize image path
        image = None
        
        
        ##Actions
        ##changing red value
        red = min_avg_red_slider.valueChanged.connect(lambda: self.change_value(min_avg_red_slider.value()))
        alg_dict = min_avg_red_slider.valueChanged.connect(lambda: self.make_algorithm_dict(image, 
                                                                                            min_avg_red_slider.value(), 
                                                                                            max_hue_shift_slider.value(),
                                                                                            blue_magic_val_slider.value(),
                                                                                            sharpen_slider.value()))
        
        ##changing hue value
        hue = max_hue_shift_slider.valueChanged.connect(lambda: self.change_value(max_hue_shift_slider.value()))
        alg_dict = max_hue_shift_slider.valueChanged.connect(lambda: self.make_algorithm_dict(image, 
                                                                                              min_avg_red_slider.value(), 
                                                                                              max_hue_shift_slider.value(),
                                                                                              blue_magic_val_slider.value(),
                                                                                              sharpen_slider.value()))
        
        ##changing blue magic val
        blue = blue_magic_val_slider.valueChanged.connect(lambda: self.change_value(blue_magic_val_slider.value()))
        alg_dict = blue_magic_val_slider.valueChanged.connect(lambda: self.make_algorithm_dict(image, 
                                                                                               min_avg_red_slider.value(), 
                                                                                               max_hue_shift_slider.value(),
                                                                                               blue_magic_val_slider.value(),
                                                                                               sharpen_slider.value()))
        
        ##changing sharpen value
        sharp = sharpen_slider.valueChanged.connect(lambda: self.change_value(sharpen_slider.value()))
        alg_dict = sharpen_slider.valueChanged.connect(lambda: self.make_algorithm_dict(image, 
                                                                                        min_avg_red_slider.value(), 
                                                                                        max_hue_shift_slider.value(),
                                                                                        blue_magic_val_slider.value(),
                                                                                        sharpen_slider.value()))
        
        
        ##clicking on single image
        alg_dict = singleImage.clicked.connect(lambda: self.openFileNameDialog(min_avg_red_slider.value(), 
                                                                               max_hue_shift_slider.value(),
                                                                               blue_magic_val_slider.value(),
                                                                               sharpen_slider.value(),
                                                                               run_algorithm,
                                                                               label2,
                                                                               min_avg_red_slider, 
                                                                               max_hue_shift_slider,
                                                                               blue_magic_val_slider,
                                                                               sharpen_slider
                                                                               ))


        ##clicking on batch image
        batchIm.clicked.connect(lambda: self.openDirectory(min_avg_red_slider.value(), 
                                                           max_hue_shift_slider.value(),
                                                           blue_magic_val_slider.value(),
                                                           sharpen_slider.value(),
                                                           run_algorithm,
                                                           min_avg_red_slider, 
                                                           max_hue_shift_slider,
                                                           blue_magic_val_slider,
                                                           sharpen_slider))
        
        ##clicking on single video
        singleVid.clicked.connect(lambda: self.openVideo(min_avg_red_slider.value(), 
                                                         max_hue_shift_slider.value(),
                                                         blue_magic_val_slider.value(),
                                                         sharpen_slider.value(),
                                                         run_algorithm,
                                                         min_avg_red_slider, 
                                                         max_hue_shift_slider,
                                                         blue_magic_val_slider,
                                                         sharpen_slider))
        
        
        
        self.show()
       
def run():
    app = QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())

run()

