import sys
import os

from PyQt4.QtCore import QSize,Qt
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
from PyQt4.QtGui import *

import locale
import threading
import time
import thread
import datetime

from contextlib import contextmanager


#global declaration of variables

ui_locale = ''
time_format =12
date_format = "%b %d, %Y"
today = datetime.datetime.now().strftime("%d-%m-%Y")
xlarge_text_size = 48
large_text_size = 28
medium_text_size = 18
small_text_size = 10

# set font
font1 = QFont('Helvetica', small_text_size)
font2 = QFont('Helvetica', medium_text_size)
font3 = QFont('Helvetica', large_text_size) 



# to prevent simultaneous access of variable by two processes
LOCALE_LOCK = threading.Lock()

@contextmanager
def setlocale(name): #thread proof function to work with locale
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        finally:
            locale.setlocale(locale.LC_ALL, saved)


# class for time

class Clock(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(Clock, self).__init__()
        self.initUI()

    def initUI(self):
        font1 = QFont('Helvetica', large_text_size)
        font2 = QFont('Helvetica', small_text_size)

        self.vbox= QVBoxLayout()
        self.time1 = ''
        self.timeLbl = QLabel('')
        self.timeLbl.setAlignment(Qt.AlignRight)
        self.timeLbl.setFont(font1)
        self.day_of_week1 = ''
        self.dayOWLbl = QLabel('')
        self.dayOWLbl.setAlignment(Qt.AlignRight)
        self.date1 = ''
        self.dateLbl = QLabel('')
        self.dateLbl.setAlignment(Qt.AlignRight)
        self.vbox.addWidget(self.timeLbl)
        self.vbox.addWidget(self.dayOWLbl)
        self.vbox.addWidget(self.dateLbl)
        self.vbox.addStretch(2)
        self.vbox.setSpacing(0)
        self.setContentsMargins(0,0,0,0)
        self.setLayout(self.vbox)
        self.time_update()

    def time_update(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(200)


    def tick(self):
        with setlocale(ui_locale):
            if time_format == 12:
                time2 = time.strftime('%I:%M %p') #hour in 12h format
            else:
                time2 = time.strftime('%H:%M') #hour in 24h format

            day_of_week2 = time.strftime('%A')
            date2 = time.strftime(date_format)
            # if time string has changed, update it
            if time2 != self.time1:
                self.time1 = time2
                self.timeLbl.setText(time2)
            if day_of_week2 != self.day_of_week1:
                self.day_of_week1 = day_of_week2
                self.dayOWLbl.setText(day_of_week2)
            if date2 != self.date1:
                self.date1 = date2
                self.dateLbl.setText(date2)


# for displaying Smart Mirror

class SmartMirrorWindow:

     def __init__(self, parent, *args, **kwargs):
        self.qt = QWidget()
        self.qt.show()
        

        self.pal=QPalette()
        self.pal.setColor(QPalette.Background,Qt.black)
        self.pal.setColor(QPalette.Foreground,Qt.white)
        self.qt.setPalette(self.pal)

        # for clock

        self.qt.hbox1 = QHBoxLayout()
        self.qt.clock = Clock(QWidget())
        self.qt.clock.setFixedHeight(150)
        self.qt.hbox1.addWidget(self.qt.clock)
        self.qt.setLayout(self.qt.hbox1)



def start_qt(tmp):
    a = QApplication(sys.argv)
    w = SmartMirrorWindow(a)
    sys.exit(a.exec_())




if __name__ == '__main__':

    try:

        thread.start_new_thread(start_qt,(1,))


    except Exception as e:

        print "Error : unable to start thread"
        print e

    while 1:
        pass

