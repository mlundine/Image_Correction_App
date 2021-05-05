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

        

    def correct(self, path, red, hue, blue, sharp, clahe, lab, scaleFac):
        new_img = cc.single_image(path, 
                                  red, 
                                  hue, 
                                  blue, 
                                  sharp,
                                  clahe=clahe)
        
        pixmap2 = QPixmap(new_img)
        small_pixmap2 = pixmap2.scaled(int(pixmap2.width()/scaleFac), int(pixmap2.height()/scaleFac))
        lab.setPixmap(small_pixmap2)
        lab.resize(int(pixmap2.width()/scaleFac), int(pixmap2.height()/scaleFac))
        #lab.move(960,50)
        self.vbox.addWidget(lab, 2, 1)
        lab.show() 
        
    
    def correct_batch(self, folder, red, hue, blue, sharp, clahe):
        cc.batch_image(folder, red, hue, blue, sharp, clahe)
            
    def correct_vid(self, file, red, hue, blue, sharp, clahe):
        cc.single_video(file, red, hue, blue, sharp,clahe)
        
        
    def singleImageButton(self, button, imLab, rBut, hBut, bBut, sBut, claheBut, eBut):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        global fileName
        fileName, _ = QFileDialog.getOpenFileName(self,"Select Image", "","All Files (*);;Images (*.jpeg *.jpg *.png *.tif)", 						  options=options)
        if fileName:
            label = QLabel(self)
            pixmap = QPixmap(fileName)
            scaleFac = 1
            logical1 = 130 + (pixmap.width()/scaleFac) >= 940
            logical2 = 50 + (pixmap.height()/scaleFac) >= 790
            while (logical1 or logical2):
                scaleFac = scaleFac + 1
                logical1 = 130 + (pixmap.width()/scaleFac) >= 940
                logical2 = 50 + (pixmap.height()/scaleFac) >= 790
            small_pixmap = pixmap.scaled(int(pixmap.width()/scaleFac), int(pixmap.height()/scaleFac))
            label.setPixmap(small_pixmap)
            #label.move(130,50)
            label.resize(int(pixmap.width()/scaleFac),int(pixmap.height()/scaleFac))
            self.vbox.addWidget(label, 1, 1)
            label.show()

            button.show()
            button.setEnabled(True)
            button.clicked.connect(lambda: self.correct(fileName, rBut.value(), hBut.value(), bBut.value(), sBut.value(), claheBut.isChecked(), imLab, scaleFac))

            img_buttons = [label, imLab]
            eBut.show()
            eBut.setEnabled(True)
            eBut.clicked.connect(lambda: self.exit_func(eBut, button, img_buttons))
            
        
    def batchImageButton(self, button, rBut, hBut, bBut, sBut, claheBut, eBut):
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
                    file_lab = QLabel(im)
                    file_lab.resize(900,20)
                    file_lab.move(500, ct*20)
                    self.vbox.addWidget(file_lab, 0, ct)
                    file_lab.show()
                    ct = ct+1
                    file_labs.append(file_lab)
            else:
                file_lab = QLabel('Working on Folder: ' + folderName, self)
                file_lab.resize(900,20)
                file_lab.move(500, 0)
                self.vbox.addWidget(file_lab, 0, 1)
                file_lab.show()
                file_labs.append(file_lab)

            button.show()
            button.setEnabled(True)

            
            button.clicked.connect(lambda: self.correct_batch(folderName, rBut.value(), hBut.value(), bBut.value(), sBut.value(), claheBut.isChecked()))

            eBut.show()
            eBut.setEnabled(True)
            eBut.clicked.connect(lambda: self.exit_func(eBut, button, file_labs))
            
    def openVideo(self, button, rBut, hBut, bBut, sBut, claheBut, eBut):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        global vidFileName
        vidFileName, _ = QFileDialog.getOpenFileName(self,"Select Video", "","All Files (*);;Videos (*.mp4)",                                                                                    options=options)
        if vidFileName:
            vidLabel = QLabel(vidFileName, self)
            vidLabel.resize(900,20)
            vidLabel.move(450, 200)
            vidLabel.show()


            button.show()
            button.setEnabled(True)
            button.clicked.connect(lambda: self.correct_vid(vidFileName, rBut.value(), hBut.value(), bBut.value(), sBut.value(), claheBut.isChecked()))

            videoLabels = [vidLabel]
            eBut.show()
            eBut.setEnabled(True)
            eBut.clicked.connect(lambda: self.exit_func(eBut, button, videoLabels))
        
    def home(self):
        self.scroll = QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.widget = QWidget()                 # Widget that contains the collection of Vertical Box
        self.vbox = QGridLayout()             # The Vertical Box that contains the Horizontal Boxes of  labels and buttons
        self.widget.setLayout(self.vbox)
        

        
        ##Button for single image
        singleImage = QPushButton("Single Image")
        #singleImage.resize(100,100)
        self.vbox.addWidget(singleImage, 0, 0)

        ## Button for batch of images
        batchIm = QPushButton("Batch of Images")
        #batchIm.resize(100,100)
        #batchIm.move(0,100)
        self.vbox.addWidget(batchIm, 1, 0)
        
        ##Button for a single video
        singleVid = QPushButton('Single Video')
        #singleVid.resize(100,100)
        #singleVid.move(0,200)
        self.vbox.addWidget(singleVid,2,0)
        
        ### red slider
        min_avg_red_label = QLabel('Minimum Average Red')
        min_avg_red_label.resize(130,25)
        min_avg_red_label.move(5,325)
        self.vbox.addWidget(min_avg_red_label, 3,0)
        min_avg_red_slider = QSpinBox(self)
        min_avg_red_slider.setMinimum(0)
        min_avg_red_slider.setMaximum(255)
        min_avg_red_slider.setValue(60)
        #min_avg_red_slider.move(5,350)
        self.vbox.addWidget(min_avg_red_slider, 4,0)
        
        
        
        ##hue shift slider
        max_hue_shift_label = QLabel('Maximum Hue Shift')
        #max_hue_shift_label.resize(125,25)
        #max_hue_shift_label.move(5,390)
        self.vbox.addWidget(max_hue_shift_label, 5,0)
        max_hue_shift_slider = QSpinBox()
        max_hue_shift_slider.setMinimum(0)
        max_hue_shift_slider.setMaximum(255)
        max_hue_shift_slider.setValue(120)
        #max_hue_shift_slider.move(5,415)
        self.vbox.addWidget(max_hue_shift_slider, 6,0)
        
        
        #blue magic value slider
        blue_magic_val_label = QLabel('Blue Magic Value')
        #blue_magic_val_label.resize(125,25)
        #blue_magic_val_label.move(5,455)
        self.vbox.addWidget(blue_magic_val_label, 7,0)
        blue_magic_val_slider = QDoubleSpinBox()
        blue_magic_val_slider.setMinimum(0)
        blue_magic_val_slider.setMaximum(5)
        blue_magic_val_slider.setValue(1.2)
        #blue_magic_val_slider.move(5,480)
        self.vbox.addWidget(blue_magic_val_slider, 8,0)
        
        
        
        ##sharpen slider
        sharpen_label = QLabel('Sharpen Steps')
        #sharpen_label.resize(125,25)
        #sharpen_label.move(5,520)
        self.vbox.addWidget(sharpen_label, 9,0)
        sharpen_slider = QSpinBox()
        sharpen_slider.setValue(1)
        sharpen_slider.setMinimum(0)
        sharpen_slider.setMaximum(4)
        #sharpen_slider.move(5,545)
        self.vbox.addWidget(sharpen_slider, 10,0)
        
        ##clahe checkbox
        clahe_label = QLabel('CLAHE (adjusts for glare)')
        clahe = QCheckBox()
        self.vbox.addWidget(clahe_label,11,0)
        self.vbox.addWidget(clahe, 12, 0)
        
        ##original image label
        old = QLabel('Original', self)
        old.move(450,800)
        old.resize(100,100)
        
        
        #corrected image label
        new = QLabel('Corrected', self)
        new.move(1250,800)
        new.resize(100,100)
        
        
        #run buttons
        run_algorithm1 = QPushButton('Run')
        #run_algorithm1.resize(100,100)
        #run_algorithm1.move(0,600)
        run_algorithm1.setEnabled(False)
        self.vbox.addWidget(run_algorithm1, 13,0)

        run_algorithm2 = QPushButton('Run')
        #run_algorithm2.resize(100,100)
        #run_algorithm2.move(0,600)
        run_algorithm2.setEnabled(False)
        self.vbox.addWidget(run_algorithm2, 13,0)

        run_algorithm3 = QPushButton('Run')
        #run_algorithm3.resize(100,100)
        #run_algorithm3.move(0,600)
        run_algorithm3.setEnabled(False)
        self.vbox.addWidget(run_algorithm3, 13,0)
        
        #exit button
        exit_button = QPushButton('Close Images')
        #exit_button.resize(100,100)
        #exit_button.move(0,700)
        exit_button.setEnabled(False)
        self.vbox.addWidget(exit_button, 14,0)
        
        ##corrected image label
        label2 = QLabel()
        
        #initialize image path
        image = None
        
        
        ##clicking on single image
        singleImage.clicked.connect(lambda: self.singleImageButton(run_algorithm1,
                                                                    label2,
                                                                    min_avg_red_slider, 
                                                                    max_hue_shift_slider,
                                                                    blue_magic_val_slider,
                                                                    sharpen_slider,
                                                                    clahe,
                                                                    exit_button
                                                                    ))


        ##clicking on batch image
        batchIm.clicked.connect(lambda: self.batchImageButton(run_algorithm2,
                                                           min_avg_red_slider, 
                                                           max_hue_shift_slider,
                                                           blue_magic_val_slider,
                                                           sharpen_slider,
                                                           clahe,
                                                           exit_button
                                                           ))
        
        ##clicking on single video
        singleVid.clicked.connect(lambda: self.openVideo(run_algorithm3,
                                                         min_avg_red_slider, 
                                                         max_hue_shift_slider,
                                                         blue_magic_val_slider,
                                                         sharpen_slider,
                                                         clahe,
                                                         exit_button))
        
        
        
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.setCentralWidget(self.scroll)
        run_algorithm1.hide()
        run_algorithm2.hide()
        run_algorithm3.hide()
        exit_button.hide()
       
def run():
    app = QApplication(sys.argv)
    GUI = Window()
    GUI.show()
    sys.exit(app.exec_())

run()

