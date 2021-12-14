# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 10:47:26 2021

@author: knopi
"""

import sys
import os
import glob
import subprocess
import ctypes
import threading
import logging
import re
import webbrowser
import datetime

import scipy, matplotlib
import math
import matplotlib.pyplot as plt
from scipy import signal
import numpy as np
from scipy.signal import hilbert, chirp

import scilab2py

from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

import time
from threading import Thread
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import serial
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# ----------------------------------------------------------------------------------------------------------------------
class Ui_MainWindow(object):

    news_liste_items = pyqtSignal(float)

    def __init__(self):

        self.close = None
        self.lock_TXT_nb = threading.RLock()
        self.it = 0
        self.frequence = 0
        self.fre_1 = 0
        self.zmax = 0
        self.zmin = 0
        self.omega = 0

    def setupUi(self, MainWindow):

        self.stylesheet_tab = """
                            QTabBar::tab{background: orange;}
                            QTabBar::tab:selected {background: rgb(211,211,211);}
                            QTabWidget>QWidget>QWidget{background: rgb(245,245,220);}

                            QScrollBar:vertical {border: none;width: 15px;margin: 15px 0px 15px 0px;}

                            QScrollBar::handle:vertical {border: 1px solid orange;background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                            stop: 0 rgba(240,230,140,255),stop: 0.15 rgba(255,140,0,255),stop: 0.5 rgba(105,105,105,255),
                            stop: 0.85 rgba(255,140,0,255), stop:1 rgba(240,230,140,255));min-height: 15px;}

                            QScrollBar::add-line:vertical {background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop: 0 rgba(240,230,140,255), stop: 0.15 rgba(105,105,105, 255),stop: 0.5 rgba(0,0,0,0), 
                            stop: 0.85 rgba(105,105,105, 255), stop:1 rgba(240,230,140,255));
                            subcontrol-position: bottom;subcontrol-origin: margin;height: 15px;}

                            QScrollBar::sub-line:vertical {background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop: 0 rgba(240,230,140,255), stop: 0.20 rgba(105,105,105, 255),stop: 0.5 rgba(0,0,0,0), 
                            stop: 0.80 rgba(105,105,105, 255), stop:1 rgba(240,230,140,255));
                            subcontrol-position: top;subcontrol-origin: margin;height: 15px;}

                            QScrollBar:horizontal {border: none;height: 15px;margin: 0px 15px 0px 15px;}

                            QScrollBar::handle:horizontal{border: 1px solid orange;background:qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop: 0 rgba(240,230,140,255),stop: 0.20 rgba(255,140,0,255),stop: 0.5 rgba(105,105,105,255), 
                            stop: 0.80 rgba(255,140,0,255), stop:1 rgba(240,230,140,255));min-width: 15px; }

                            QScrollBar::add-line:horizontal {background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                            stop: 0 rgba(240,230,140,255), stop: 0.20 rgba(105,105,105, 255),stop: 0.5 rgba(0,0,0,0),
                            stop: 0.80 rgba(105,105,105, 255), stop:1 rgba(240,230,140,255));
                            subcontrol-position: right;subcontrol-origin: margin;width: 15px;}

                            QScrollBar::sub-line:horizontal {background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                            stop: 0 rgba(240,230,140,255), stop: 0.20 rgba(105,105,105, 255),stop: 0.5 rgba(0,0,0,0),
                            stop: 0.80 rgba(105,105,105, 255), stop:1 rgba(240,230,140,255));
                            subcontrol-position: left;subcontrol-origin:margin;width: 15px;}
                            """

        self.Pbar_STYLE_analysis = """
                                    QProgressBar:horizontal{
                                    border-radius: 9px;background: rgb(245,245,220);
                                    padding: 3px;text-align: center;margin-right: 4ex;}

                                    QProgressBar::chunk:horizontal{ margin-right: 2px; width: 10px;
                                    background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 0.2, stop: 0 rgb(255, 255, 0), 
                                    stop: 0.25 rgb(255, 191, 0), stop: 0.5 gold, stop: 1 rgb(255, 128, 0));}
                                   """


        # *********************************************************************

        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(1800, 790)
        # MainWindow.setPalette(palette)
        MainWindow.setWindowFlags(QtCore.Qt.CustomizeWindowHint
                                  | QtCore.Qt.WindowCloseButtonHint
                                  | QtCore.Qt.WindowMinimizeButtonHint)

# ----------------------------------------------------------------------------------------------------------------------

        # ************************** tab1: General ****************************

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("Centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(5, 5, 415, 730))
        self.tabWidget.setStyleSheet("background-color: gray;")

        self.groupBox_2 = QtWidgets.QGroupBox(MainWindow)
        self.groupBox_2.setGeometry(QtCore.QRect(440, 6, 1333, 725))
        self.groupBox_2.setStyleSheet("background-color: gray;")
        self.groupBox_2.setObjectName("groupBox")

        self.label_plot = QtWidgets.QLabel(self.groupBox_2)
        self.label_plot.setGeometry(QtCore.QRect(580, 5, 191, 30))
        self.label_plot.setStyleSheet("background-color: rgb(245,245,220);")
        self.label_plot.setObjectName("label_plot")
        self.label_plot.setAlignment(Qt.AlignCenter)

        self.graphWidget = pg.PlotWidget(self.groupBox_2)
        self.graphWidget.setGeometry(QtCore.QRect(25, 45, 620, 200))
        self.graphWidget.setBackground('w')
        self.graphWidget.setTitle("Accélération", color="b", size="10pt")
        self.graphWidget.setLabel('left', "<span style=\"color:red;font-size:10px\">"
                                          "Accélération (m/s^2)</span>")
        self.graphWidget.setLabel('bottom', "<span style=\"color:red;font-size:10px\">"
                                            "Temps (s)</span>")

        self.graphWidget_1 = pg.PlotWidget(self.groupBox_2)
        self.graphWidget_1.setGeometry(QtCore.QRect(25, 265, 620, 200))
        self.graphWidget_1.setTitle("Vitesse", color="b", size="10pt")
        self.graphWidget_1.setLabel('left', "<span style=\"color:red;font-size:10px\">"
                                          "Vitesse (m/s)</span>")
        self.graphWidget_1.setLabel('bottom', "<span style=\"color:red;font-size:10px\">"
                                            "Temps (s)</span>")

        self.graphWidget_2 = pg.PlotWidget(self.groupBox_2)
        self.graphWidget_2.setGeometry(QtCore.QRect(25, 485, 620, 200))
        self.graphWidget_2.setBackground('w')
        self.graphWidget_2.setTitle("Position", color="b", size="10pt")
        self.graphWidget_2.setLabel('left', "<span style=\"color:red;font-size:10px\">"
                                            "Deplacement (m)</span>")
        self.graphWidget_2.setLabel('bottom', "<span style=\"color:red;font-size:10px\">"
                                              "Temps (s)</span>")

        # ---------------------------------------------- #
        self.graphWidget_3 = pg.PlotWidget(self.groupBox_2)
        self.graphWidget_3.setGeometry(QtCore.QRect(695, 45, 620, 200))
        self.graphWidget_3.setBackground('w')
        self.graphWidget_3.setTitle("Spectre frequentiel réponse",
                                    color="b", size="10pt")
        self.graphWidget_3.setLabel('left', "<span style=\"color:red;font-size:10px\">"
                                            "FFT (U)</span>")
        self.graphWidget_3.setLabel('bottom', "<span style=\"color:red;font-size:10px\">"
                                              "Omega</span>")

        self.graphWidget_4 = pg.PlotWidget(self.groupBox_2)
        self.graphWidget_4.setGeometry(QtCore.QRect(695, 265, 620, 200))
        self.graphWidget_4.setTitle("Accélération avec l'enveloppe du signale",
                                    color="b", size="10pt")
        self.graphWidget_4.setLabel('left', "<span style=\"color:red;font-size:10px\">"
                                          "Accélération (m/s^2)</span>")
        self.graphWidget_4.setLabel('bottom', "<span style=\"color:red;font-size:10px\">"
                                            "Temps (s)</span>")

        self.graphWidget_5 = pg.PlotWidget(self.groupBox_2)
        self.graphWidget_5.setGeometry(QtCore.QRect(695, 485, 620, 200))
        self.graphWidget_5.setBackground('w')
        self.graphWidget_5.setTitle("Enveloppe du signale",
                                    color="b", size="10pt")
        self.graphWidget_5.setLabel('left', "<span style=\"color:red;font-size:10px\">"
                                          "Accélération (m/s^2)</span>")
        self.graphWidget_5.setLabel('bottom', "<span style=\"color:red;font-size:10px\">"
                                            "Temps (s)</span>")

        # ----------------------------------------------------------------------------------------------------------------------

        # ****************** create btn_import + Line Edit ********************
        self.groupBox_1_0 = QtWidgets.QGroupBox(MainWindow)
        self.groupBox_1_0.setGeometry(QtCore.QRect(10, 50, 401, 110))
        self.groupBox_1_0.setStyleSheet("background-color: rgb(211,211,211);")
        self.groupBox_1_0.setObjectName("groupBox")

        self.label_plot_2 = QtWidgets.QLabel(MainWindow)
        self.label_plot_2.setGeometry(QtCore.QRect(112, 10, 191, 30))
        self.label_plot_2.setStyleSheet("background-color: rgb(245,245,220);")
        self.label_plot_2.setObjectName("label_plot_2")
        self.label_plot_2.setAlignment(Qt.AlignCenter)

        self.label_calibre = QtWidgets.QLabel(self.groupBox_1_0)
        self.label_calibre.setGeometry(QtCore.QRect(92, 10, 211, 30))
        self.label_calibre.setStyleSheet("background-color: rgb(245,245,220);")
        self.label_calibre.setObjectName("label_calibre")
        self.label_calibre.setAlignment(Qt.AlignCenter)

        self.pushButton_z_min = QtWidgets.QToolButton(self.groupBox_1_0)
        self.pushButton_z_min.setGeometry(QtCore.QRect(10, 50, 111, 23))
        self.pushButton_z_min.setStyleSheet("background-color: orange;")
        self.pushButton_z_min.setObjectName("pushButton_z_min")
        self.pushButton_z_min.clicked.connect(self.pushButton_z_min_clicked)

        self.pushButton_z_max = QtWidgets.QToolButton(self.groupBox_1_0)
        self.pushButton_z_max.setGeometry(QtCore.QRect(280, 50, 111, 23))
        self.pushButton_z_max.setStyleSheet("background-color: orange;")
        self.pushButton_z_max.setObjectName("pushButton_z_min")
        self.pushButton_z_max.clicked.connect(self.pushButton_z_max_clicked)

        self.calibre_1 = QLabel(self.groupBox_1_0)
        self.calibre_1.setGeometry(QtCore.QRect(10, 80, 111, 20))
        self.calibre_1.setStyleSheet("background-color:rgb(255, 255, 255);")
        self.calibre_1.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.calibre_1.setText(str(0))

        self.calibre_2 = QLabel(self.groupBox_1_0)
        self.calibre_2.setGeometry(QtCore.QRect(280, 80, 111, 20))
        self.calibre_2.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.calibre_2.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.calibre_2.setText(str(0))

# ----------------------------------------------------------------------------------------------------------------------

        # ******************** groupBox2 select_log ***************************

        self.groupBox_1_2 = QtWidgets.QGroupBox(MainWindow)
        self.groupBox_1_2.setGeometry(QtCore.QRect(10, 175, 401, 110))
        self.groupBox_1_2.setStyleSheet("background-color: rgb(211,211,211);")
        self.groupBox_1_2.setObjectName("groupBox")

        self.label_type = QtWidgets.QLabel(self.groupBox_1_2)
        self.label_type.setGeometry(QtCore.QRect(92, 10, 211, 30))
        self.label_type.setStyleSheet("background-color: rgb(245,245,220);")
        self.label_type.setObjectName("label_type")
        self.label_type.setAlignment(Qt.AlignCenter)

        # **************** create Check box to select All ********************

        self.checkBox = QtWidgets.QCheckBox(self.groupBox_1_2)
        self.checkBox.setGeometry(QtCore.QRect(10, 50, 111, 20))
        self.checkBox.setStyleSheet("background-color: rgb(245,245,220);;")
        self.checkBox.setObjectName("checkBox")

        # **************** create Check box to select Manual ********************

        self.checkBox2 = QtWidgets.QCheckBox(self.groupBox_1_2)
        self.checkBox2.setGeometry(QtCore.QRect(280, 50, 111, 20))
        self.checkBox2.setStyleSheet("background-color: rgb(245,245,220);;")
        self.checkBox2.setChecked(True)
        self.checkBox2.setObjectName("checkBox")

        # **************************** progressBar ****************************

        self.groupBox_1_3 = QtWidgets.QGroupBox(MainWindow)
        self.groupBox_1_3.setGeometry(QtCore.QRect(10, 300, 401, 165))
        self.groupBox_1_3.setStyleSheet("background-color: rgb(211,211,211);")
        self.groupBox_1_3.setObjectName("groupBox")

        self.temps = QtWidgets.QLabel(self.groupBox_1_3)
        self.temps.setGeometry(QtCore.QRect(10, 10, 211, 20))
        self.temps.setStyleSheet("background-color: rgb(245,245,220);border: 1px solid orange")
        self.temps.setObjectName("temps")
        self.temps.setAlignment(Qt.AlignCenter)

        self.freq = QtWidgets.QLabel(self.groupBox_1_3)
        self.freq.setGeometry(QtCore.QRect(10, 100, 211, 20))
        self.freq.setStyleSheet("background-color: rgb(245,245,220);border: 1px solid orange")
        self.freq.setObjectName("frequence")
        self.freq.setAlignment(Qt.AlignCenter)

        # -------------------------------------------------------------------- #


        self.slider = QtWidgets.QSlider(self.groupBox_1_3)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setGeometry(QtCore.QRect(10, 50, 380, 30))
        self.slider.setRange(0, 2000)
        self.slider.setFocusPolicy(Qt.NoFocus)
        self.slider.setValue(0)

        self.slider.valueChanged.connect(self.updateLabel)

        self.label = QtWidgets.QLabel(self.groupBox_1_3)
        self.label.setGeometry(QtCore.QRect(280, 10, 111, 20))
        self.label.setStyleSheet("background-color: rgb(245,245,220);border: 1px solid orange")
        self.label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.label.setText(str(0))

        # -------------------------------------------------------------------- #

        self.slider_freq = QtWidgets.QSlider(self.groupBox_1_3)
        self.slider_freq.setOrientation(QtCore.Qt.Horizontal)
        self.slider_freq.setGeometry(QtCore.QRect(10, 130, 380, 30))
        self.slider_freq.setRange(0, 100)
        self.slider_freq.setFocusPolicy(Qt.NoFocus)
        # self.slider_freq.setPageStep(5)
        self.slider_freq.setValue(0)

        self.slider_freq.valueChanged.connect(self.updateLabel_freq)

        self.label_freq = QtWidgets.QLabel(self.groupBox_1_3)
        self.label_freq.setGeometry(QtCore.QRect(280, 100, 111, 20))
        self.label_freq.setStyleSheet("background-color: rgb(245,245,220);border: 1px solid orange")
        self.label_freq.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.label_freq.setText(str(0))

        # ************************** create btn_exit **************************

        self.pushButton_exit_1 = QtWidgets.QPushButton(MainWindow)
        self.pushButton_exit_1.setGeometry(QtCore.QRect(1700, 750, 75, 23))
        self.pushButton_exit_1.setStyleSheet("background-color: orange;")
        self.pushButton_exit_1.setObjectName("pushButton_exit_2")
        self.pushButton_exit_1.clicked.connect(QCoreApplication.instance().quit)

        self.label_Ksi = QtWidgets.QLabel(MainWindow)
        self.label_Ksi.setGeometry(QtCore.QRect(1200, 750, 411, 23))
        self.label_Ksi.setStyleSheet("background-color: rgb(245,245,220);border: 1px solid orange")
        self.label_Ksi.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.label_Ksi.setText(str("Ksi = "))

        self.pushButton_reset = QtWidgets.QPushButton(MainWindow)
        self.pushButton_reset.setGeometry(QtCore.QRect(10, 750, 75, 23))
        self.pushButton_reset.setStyleSheet("background-color: orange;")
        self.pushButton_reset.setObjectName("pushButton_reset")
        self.pushButton_reset.clicked.connect(self.reset)

        self.pushButton_run = QtWidgets.QPushButton(MainWindow)
        self.pushButton_run.setGeometry(QtCore.QRect(20, 500, 111, 30))
        self.pushButton_run.setStyleSheet("background-color: orange;")
        self.pushButton_run.setObjectName("pushButton_run")
        self.pushButton_run.setEnabled(False)
        self.pushButton_run.clicked.connect(self.it_value)

        self.pybutton_ksi = QtWidgets.QPushButton(MainWindow)
        self.pybutton_ksi.setGeometry(QtCore.QRect(288, 500, 111, 30))
        self.pybutton_ksi.setStyleSheet("background-color: orange;")
        self.pybutton_ksi.setObjectName("pushButton_run")
        self.pybutton_ksi.setEnabled(False)
        self.pybutton_ksi.clicked.connect(self.Ksi_plot)

        self.groupBox_1_4 = QtWidgets.QGroupBox(MainWindow)
        self.groupBox_1_4.setGeometry(QtCore.QRect(10, 575, 401, 150))
        self.groupBox_1_4.setStyleSheet("background-color: rgb(211,211,211);")
        self.groupBox_1_4.setObjectName("groupBox_1_4")

        self.Control_graph = QtWidgets.QLabel(self.groupBox_1_4)
        self.Control_graph.setGeometry(QtCore.QRect(92, 10, 211, 30))
        self.Control_graph.setStyleSheet("background-color: rgb(245,245,220);")
        self.Control_graph.setObjectName("Control_graph")
        self.Control_graph.setAlignment(Qt.AlignCenter)


        self.line = QLineEdit(self.groupBox_1_4)
        self.line.setStyleSheet("background-color: rgb(245,245,220);border: 1px solid orange")
        self.line.setGeometry(QtCore.QRect(10, 60, 191, 30))

        self.pushButton_Omega = QPushButton(self.groupBox_1_4)
        self.pushButton_Omega.setGeometry(QtCore.QRect(280, 60, 111, 30))
        self.pushButton_Omega.setStyleSheet("background-color: orange;")
        self.pushButton_Omega.setEnabled(False)
        self.pushButton_Omega.clicked.connect(self.get_Omega)

# ----------------------------------------------------------------------------------------------------------------------
        MainWindow.setCentralWidget(self.centralwidget)
        self.translateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def translateUi(self, Main_Window):

        _translate = QtCore.QCoreApplication.translate
        Main_Window.setWindowTitle(_translate("MainWindow", "CMV"))
        Main_Window.setWindowIcon(QIcon('icon.jpg'))

        self.groupBox_1_0.setTitle(_translate("MainWindow", ""))
        self.groupBox_1_2.setTitle(_translate("MainWindow", ""))

        self.checkBox.setText(_translate("MainWindow", "Harmonique"))
        self.checkBox2.setText(_translate("MainWindow", "Libre"))

        self.pushButton_exit_1.setText(_translate("MainWindow", "EXIT"))
        self.pushButton_reset.setText(_translate("MainWindow", "RESET"))
        self.pushButton_run.setText(_translate("MainWindow", "RUN"))
        self.pybutton_ksi.setText(_translate("MainWindow", "KSI"))
        self.pushButton_Omega.setText(_translate("MainWindow", "Omega"))

        self.pushButton_z_min.setText(_translate("MainWindow", "Z MIN"))
        self.pushButton_z_max.setText(_translate("MainWindow", "Z MAX"))

        self.label_calibre.setText(_translate("MainWindow", "Calibrage de l'acccéléromètre"))
        self.label_type.setText(_translate("MainWindow", "Type d'étude"))
        self.temps.setText(_translate("MainWindow", "Nombre d'acquisition"))
        self.freq.setText(_translate("MainWindow", "Fréquence d'acquisition en Hz"))
        self.label_plot.setText(_translate("MainWindow", "Graphes"))
        self.label_plot_2.setText(_translate("MainWindow", "Control"))
        self.Control_graph.setText(_translate("MainWindow", "Plot"))

# ------------------------------------------------------------------------------ #

    def get_Omega(self):
        print('Omega: ' + self.line.text())
        self.omega = float(self.line.text())
        print(self.omega)
        self.Omega_plot()
# ------------------------------------------------------------------------------------------------------------------- #
    def reset(self):

        self.it = 0
        self.frequence = 0
        self.fre_1 = 0
        self.zmax = 0
        self.zmin = 0
        self.omega = 0

        self.label_Ksi.setText(str("Ksi = "))
        self.line.setText(str(""))
        self.pushButton_run.setEnabled(False)
        self.pushButton_Omega.setEnabled(False)
        self.pybutton_ksi.setEnabled(False)
        self.pushButton_z_max.setEnabled(True)
        self.pushButton_z_min.setEnabled(True)

        self.calibre_2.setText(str(0))
        self.calibre_1.setText(str(0))

        self.slider.setRange(0, 2000)
        self.slider.setFocusPolicy(Qt.NoFocus)
        self.slider.setValue(0)
        self.label.setText(str(0))

        self.slider_freq.setRange(0, 100)
        self.slider_freq.setFocusPolicy(Qt.NoFocus)
        self.slider_freq.setValue(0)

        self.slider_freq.setValue(0)

        self.graphWidget.clear()
        self.graphWidget_1.clear()
        self.graphWidget_2.clear()
        self.graphWidget_3.clear()
        self.graphWidget_4.clear()
        self.graphWidget_5.clear()
    # --------------------------------------------------------------------- #
    def updateLabel(self, value):
        self.label.setText(str(value))
        print(str(value))
        self.it = int(value)

    def updateLabel_freq(self, value):
        self.label_freq.setText(str(value))
        print(str(value))
        self.frequence = int(value)

    # ------------------------------------------------------------------------ #

    def pushButton_z_min_clicked(self):
        print("Z MIN IS Clicked")
        x = self.run()
        self.zmin = x
        self.calibre_1.setText(str(x))
        self.pushButton_z_min.setEnabled(False)
        if self.zmax != 0 and self.zmin != 0:
            self.pushButton_run.setEnabled(True)

    def pushButton_z_max_clicked(self):
        print("Z MAX IS Clicked")
        x = self.run()
        self.zmax = x
        self.calibre_2.setText(str(x))
        self.pushButton_z_max.setEnabled(False)
        if self.zmax != 0 and self.zmin != 0:
            self.pushButton_run.setEnabled(True)

    def it_value(self):
        if self.it != 0 and self.frequence != 0:
            print("****************** this is the value of It ***********************")
            print(self.it)
            print("**************** this is the value of Freq ***********************")
            print(self.frequence)
            print("******************************************************************")
            self.temps_loop()
        else:
            pass
    def temps_loop(self):
        serial_port = serial.Serial(port="COM5", baudrate=9600)
        serial_port.flushInput()
        new_az = []
        new_t = []
        new_az1 = []
        new_t1 = []
        i = 0
        it = self.it
        Fe = 100
        self.fre_1 = self.frequence
        # self.fre_2 = self.frequenc
        print(Fe/self.fre_1)
        while i <= (self.it * (Fe/self.fre_1)):
            ser_bytes = serial_port.readline()

            try:
                decoded_bytes = float(ser_bytes[0:len(ser_bytes) - 2].decode("utf-8"))
                print(decoded_bytes)
                if int(decoded_bytes) >= 1000:
                    az = float(900)
                else:
                    az = decoded_bytes
            except:
                pass
            new_az1.append(az)
            new_t1.append(( i*1/Fe))
            i = i + 1


        i=0
        print("******************************************************************")
        while i < len(new_az1):
            print(i)
            new_az.append(new_az1[i])
            new_t.append(new_t1[i])
            i=i+int(Fe/self.fre_1)


        zRawMin = self.zmin
        zRawMax = self.zmax

        # zRawMin = 429
        # zRawMax = 640

        g = 9.81

        aa = 2000 / (zRawMax - zRawMin)
        bb = -1000 - aa * zRawMin
        az0 = []

        for i in range(len(new_az)):
            az0.append((aa*new_az[i]+bb)/1000)

        az1 = []

        for i in range(len(new_az)):
            az1.append((az0[i]-az0[0])*g)
            # print(az1)
            # t1 = []
        moy = 0
        for i in range(len(az1)):
            moy = moy + az1[i]
        moy = moy/len(az1)

        acceleration = []
        for i in range(len(az1)):
            acceleration.append(az1[i]-moy)


        pen = pg.mkPen(color=(0, 255, 0))
        self.graphWidget.plot(new_t, acceleration, name=" Signale Brute ", pen=pen)

        # ------------------------------------------------------------- #

        velocity = [0]
        time_1 = 1 / self.fre_1
        for acc in acceleration:
            velocity.append(velocity[-1] + acc * time_1)
        del velocity[0]

        moy = 0
        for i in range(len(velocity)):
            moy = moy + velocity[i]
        moy = moy / len(velocity)

        velocity_moy = []
        for i in range(len(velocity)):
            velocity_moy.append(velocity[i] - moy)

        pen = pg.mkPen(color=(240, 195, 0))
        self.graphWidget_1.plot(new_t, velocity_moy, name=" Signale Brute ", pen=pen)


        position = [0]
        for vel in velocity:
            position.append(position[-1] + vel * time_1)
        del position[0]

        pen = pg.mkPen(color=(0, 255, 0))
        self.graphWidget_2.plot(new_t, position, name=" Position ", pen=pen)

        self.new_t = new_t
        self.acceleration = acceleration
        self.time_1 = time_1

        self.pushButton_run.setEnabled(False)
        self.pybutton_ksi.setEnabled(True)
        serial_port.close()
        # ----------------------------------------------------------------------------- #

    def Ksi_plot(self):
        tt = self.new_t
        yy = self.acceleration
        g = 9.8;
        hh = self.time_1

        pen = pg.mkPen(color=(0, 255, 0))
        self.graphWidget.plot(tt, yy, name=" Signale Brute ", pen=pen)

        g = 9.8;
        NN = len(tt)
        ff = []
        i = 0
        N_2 = int(NN / 2)

        while i < N_2:
            # print(i)
            x = tt[i] * ((1 / hh) / NN)
            ff.append(x)
            i += 1
        # print(ff)
        sx = scipy.fft.fft(yy)
        # print(sx)

        nn = math.floor(0.5 * len(ff))
        # print(nn)

        plot_1 = []
        i = 0
        while i < N_2:
            y = 2 * math.pi * ff[i]
            plot_1.append(y)
            i += 1

        ab = []
        i = 0
        while i < N_2:
            k = abs(sx[i])
            ab.append(k)
            i += 1

        print(plot_1)
        print(ab)

        pen = pg.mkPen(color=(102, 0, 153))
        self.graphWidget_3.plot(plot_1, ab, name=" Signale Brute ", pen=pen)

        self.yy = yy
        self.hh = hh
        self.tt = tt

        self.pushButton_run.setEnabled(False)
        self.pybutton_ksi.setEnabled(False)
        self.pushButton_Omega.setEnabled(True)
        # ---------------------------------------------------------------------- #

    def Omega_plot(self):

        yy = self.yy
        hh = self.hh
        tt = self.tt

        fe = 1 / hh
        om1 = self.omega
        frequ = om1 / (2*math.pi)
        deltaf = frequ / 10
        freqmin = frequ - deltaf
        freqmax = frequ + deltaf
        f1 = freqmin/fe
        f2 = freqmax/fe

        # yy_filt = []
        # filtered= []
        # yy_filt = signal.butter(17, [f1,f2], 'bp', fe, output='sos')
        # print(yy_filt)
        # filtered = signal.sosfilt(yy_filt, yy)
        # print(filtered)
        # hz = signal.iirfilter(17, [freqmin/fe, freqmax/fe], rs=60,
        #                         btype='band', analog=True, ftype='butter')
        #
        # arr1 = np.array(yy)
        # arr1_transpose = arr1.transpose()
        # yy_trasn = arr1_transpose
        # yy_filt = []
        # # x = sciscipy.flts(hz,yy_trasn)
        # hilbert_yy_filt = hilbert(yy_filt)
        # env_yy_filt = abs(hilbert_yy_filt)
        #
        # hz = signal.butter(1, [freqmin / fe, freqmax / fe], 'bp')
        # print(hz)

        hilbert_yy_filt = hilbert(yy)
        env_yy_filt = abs(hilbert_yy_filt)
        print(len(env_yy_filt))

        pen = pg.mkPen(color=(255, 0, 127))
        self.graphWidget_4.plot(tt, env_yy_filt, pen=pen)
        pen = pg.mkPen(color=(0, 255, 0))
        self.graphWidget_4.plot(tt, yy, pen=pen)
        # pen = pg.mkPen(color=(46, 0, 108))
        # self.graphWidget_4.plot(tt, filtered, pen=pen)

        pen = pg.mkPen(color=(46, 0, 108))
        self.graphWidget_5.plot(tt, env_yy_filt, name=" Signale Brute ", pen=pen)


        x1 = math.floor(3 * len(yy) / 10)
        x2 = env_yy_filt[x1]
        x3 = math.log(x2)
        x4 = math.floor(7 * len(yy) / 10)
        x5 = env_yy_filt[x4]
        x6 = math.log(x5)
        # ksi = (math.log(env_yy_filt(math.floor(3*len(yy)/10)))
        #        -math.log(env_yy_filt(math.floor(7*len(yy)/10))))/\
        #       ((max(tt)*0.4)/(2 * math.pi * frequ))

        ksi = (x3 - x6) / ((max(tt) * 0.4) / (2 * math.pi * frequ))
        print(ksi)
        self.label_Ksi.setText(str("Ksi = %f" %ksi))

    def run(self):

        serial_port = serial.Serial(port="COM5", baudrate=9600)
        serial_port.flushInput()
        i = 0
        while i <= 20:
            ser_bytes = serial_port.readline()

            try:
                decoded_bytes = float(ser_bytes[0:len(ser_bytes) - 2].decode("utf-8"))
                print(decoded_bytes)
                if int(decoded_bytes) >= 1000:
                    az = float(900)
                else:
                    az = decoded_bytes
            except:
                pass
            i = i + 1
        serial_port.close()
        return az

# ------------------------------------------------------------------------------------------------------------------- #

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())