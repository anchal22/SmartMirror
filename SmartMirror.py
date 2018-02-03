import sys
import os
import cv2


from PyQt4.QtCore import QSize,Qt
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
from PyQt4.QtGui import *

import locale
import threading
import time
import thread
import datetime

import requests
import json

from contextlib import contextmanager
from forismatic import Forismatic


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



# class calendar
class Calendar(QWidget):
    """docstring fss Calendar"""
    def __init__(self, parent,*args,**kwargs):
        super(Calendar, self).__init__()
        self.initUI()

    def initUI(self):
        self.vbox = QVBoxLayout()
        self.cal = QCalendarWidget()
        self.cal.setGridVisible(True)
        self.vbox.addWidget(self.cal)
        self.setLayout(self,vbox)


# class for Quotes

class Quotes(QWidget):
    """docstring for Quotes"""
    def __init__(self, parent,*args,**kwargs):
        super(Quotes, self).__init__()
        self.initUI()

    def initUI(self):
        self.vbox = QVBoxLayout()
        self.lbl1 = QLabel()
        self.lbl1.setWordWrap(True)
        self.lbl2 = QLabel()
        self.lbl1.setAlignment(Qt.AlignCenter)
        self.lbl2.setAlignment(Qt.AlignCenter)
        self.vbox.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.lbl1)
        self.vbox.addWidget(self.lbl2)
        self.setLayout(self.vbox)
        self.quotes_get()

    def quotes_get(self):
        try:
            url= 'http://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=en'
            res = requests.get(url)
            # print res
            s = res.text
            s.replace('\r\n', '')
            s.replace("\'", "'")
            data = json.loads(s)
            self.lbl1.setText(data["quoteText"])
            self.lbl2.setText("- " + data["quoteAuthor"])
            # print data
            #print self.data_get(self.data_fetch(url))
        except IOError:
            print('no internet')

           



# class for news
class News(QWidget):
    def __init__(self, source=None):
        super(News, self).__init__()
        # source
        if source:
          self.source = source
        else:
          # self.source = 'the-times-of-india'      
          self.source = 'the-times-of-india'      
      
        self.initUI()

    def initUI(self):
        
        self.vbox = QVBoxLayout()
        self.heading = QLabel()
        
        self.size= "480x360"

        
        #self.source="the-times-of-india"
        self.fbox = QFormLayout()
        self.fbox.setAlignment(Qt.AlignLeft)
        self.fbox.setSpacing(8)

        self.heading.setAlignment(Qt.AlignCenter)
        self.heading.setFont(font2)
        
        self.vbox.addWidget(self.heading)
        self.vbox.addLayout(self.fbox)
        
        self.setLayout(self.vbox)
        self.news_fetcher()
        #self.addWidget(News)
        

    #updating news
    def news_fetcher(self):
        
        try:
            
            news_req_url = "'https://newsapi.org/v2/top-headlines?''country=us&''apiKey=76d13e64c224446982e92a6e4ba09167'"
            # print news_req_url
            r = requests.get(news_req_url)
            print r.json

            news_obj = json.loads(r.text)
            
            # print news_obj
            
            data0=news_obj["articles"][0]["title"]
            data1=news_obj["articles"][1]["title"]
            data2=news_obj["articles"][2]["title"]
            data3=news_obj["articles"][3]["title"]
            data4=news_obj["articles"][4]["title"]

          
            data_read = [data0,data1,data2,data3,data4]

            #print data_read
            for i in reversed(range(self.fbox.count())): 
                    self.fbox.itemAt(i).widget().setParent(None)
                
            for (i,x) in enumerate(data_read):
                #INDIA
                image = cv2.imread("assets/Newspaper.png", cv2.CV_LOAD_IMAGE_COLOR);
                image = cv2.resize(image,(25,25), interpolation = cv2.INTER_CUBIC)
                image = QImage(image, image.shape[1], image.shape[0], 
                       image.strides[0], QImage.Format_RGB888)
                newspaperIcon = QLabel()
                newspaperIcon.setPixmap(QPixmap.fromImage(image))

                if self.source == 'the-times-of-india':
                    lbl = QLabel(x)
                    lbl.setWordWrap(True)
                    lbl.setFont(font1)
                    self.fbox.addRow(newspaperIcon,lbl)
                    self.heading.setText('HEADLINES')
                    
                # Sports News
                elif self.source == 'fox-sports':
                    lbl = QLabel(x)
                    lbl.setWordWrap(True)
                    self.fbox.addRow(newspaperIcon,lbl)
                    self.heading.setText('SPORTS NEWS')
                    
                # Tech News
                elif self.source == 'techcrunch':
                    lbl = QLabel(x)
                    lbl.setWordWrap(True)
                    self.fbox.addRow(newspaperIcon,lbl)
                    self.heading.setText('TECHNOLOGY NEWS')
                   
                #WORLD
                elif self.source == 'the-telegraph':
                    lbl = QLabel(x)
                    lbl.setWordWrap(True)
                    self.fbox.addRow(newspaperIcon,lbl)
                    self.heading.setText('WORLD NEWS')
                   
                # Business
                elif self.source == 'business-insider':
                    lbl = QLabel(x)
                    lbl.setWordWrap(True)
                    self.fbox.addRow(newspaperIcon,lbl)
                    self.heading.setText('BUSINESS NEWS')
                    

        except IOError:
            print('no internet')







        


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
        

        # for quotes

        self.qt.hbox2 = QHBoxLayout()
        self.qt.quotes = Quotes(QWidget())
        self.qt.hbox2.addWidget(self.qt.quotes)

        self.qt.vbox = QVBoxLayout()
        self.qt.vbox.addLayout(self.qt.hbox1)
        self.qt.vbox.addLayout(self.qt.hbox2)

        self.qt.setLayout(self.qt.vbox)
        




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

