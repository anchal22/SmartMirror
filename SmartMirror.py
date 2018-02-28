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

window_width = 540
window_height = 960
window_x = 400
window_y =150
dynamic_frame_w = 600
dynamic_frame_h = 400
ip = '<IP>'
ui_locale = '' # '' as default
news_country_code = 'us'
weather_api_token = 'e4aaf1c42f8fbf5216885bf1133c1202'
weather_lang = 'en'
weather_unit = 'us'
latitude = None
longitude = None


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




icon_lookup = {
    'clear-day': "assets/Sun.png",  # clear sky day
    'wind': "assets/Wind.png",   #wind
    'cloudy': "assets/Cloud.png",  # cloudy day
    'partly-cloudy-day': "assets/PartlySunny.png",  # partly cloudy day
    'rain': "assets/Rain.png",  # rain day
    'snow': "assets/Snow.png",  # snow day
    'snow-thin': "assets/Snow.png",  # sleet day
    'fog': "assets/Haze.png",  # fog day
    'clear-night': "assets/Moon.png",  # clear sky night
    'partly-cloudy-night': "assets/PartlyMoon.png",  # scattered clouds night
    'thunderstorm': "assets/Storm.png",  # thunderstorm
    'tornado': "assests/Tornado.png",    # tornado
    'hail': "assests/Hail.png"  # hail
}

# class weather
class Weather(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(Weather, self).__init__()
        self.initUI()

    def initUI(self):
        font1 = QFont('Helvetica', small_text_size)
        font2 = QFont('Helvetica', medium_text_size)
        font3 = QFont('Helvetica', large_text_size)

        self.temperature = ''
        self.forecast = ''
        self.location = ''
        self.currently = ''
        self.icon = ''

        self.vbox= QVBoxLayout()
        self.temperatureLbl  = QLabel('Tepr')
        self.iconLbl = QLabel()
        self.currentlyLbl = QLabel('currently')
        self.forecastLbl = QLabel('forecast')
        self.locationLbl = QLabel('location')

        self.temperatureLbl.setFont(font3)
        self.currentlyLbl.setFont(font2)
        self.forecastLbl.setFont(font1)
        self.locationLbl.setFont(font1)

        self.hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()
        self.vbox1 = QVBoxLayout()
        self.hbox.addWidget(self.temperatureLbl)
        self.hbox.addWidget(self.iconLbl)
        self.hbox.setAlignment(Qt.AlignLeft)
        self.vbox1.addWidget(self.currentlyLbl)
        self.vbox1.addWidget(self.forecastLbl)
        self.vbox1.addWidget(self.locationLbl)
        self.vbox1.addStretch(1)

        self.vbox.addLayout(self.hbox)
        self.vbox.addLayout(self.vbox1)
        self.vbox.setContentsMargins(0,0,0,0)
        self.setLayout(self.vbox)
        self.get_weather()
        self.weather_update()


    def weather_update(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.get_weather)
        self.timer.start(60000*60)



    def get_ip(self):
        try:
            ip_url = "http://jsonip.com/"
            req = requests.get(ip_url)
            ip_json = json.loads(req.text)
            return ip_json['ip']
        except Exception as e:
            traceback.print_exc()
            return "Error: %s. Cannot get ip." % e

    def get_weather(self):
        try:
            print 'Getting weather ......'
            if latitude is None and longitude is None:
                # get location
                location_req_url = "http://freegeoip.net/json/%s" % self.get_ip()
                r = requests.get(location_req_url)
                location_obj = json.loads(r.text)

                lat = location_obj['latitude']
                lon = location_obj['longitude']

                location2 = "%s, %s" % (location_obj['city'], location_obj['region_code'])

                # get weather
                weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (weather_api_token, lat,lon,weather_lang,weather_unit)
            else:
                location2 = ""
                # get weather
                weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (weather_api_token, latitude, longitude, weather_lang, weather_unit)

            r = requests.get(weather_req_url)
            weather_obj = json.loads(r.text)

            degree_sign= u'\N{DEGREE SIGN}'
            f = int(weather_obj['currently']['temperature'])
            c = int(5*(f-32)/9)
            temperature2 = "%s%s" % (str(c), degree_sign)
            currently2 = weather_obj['currently']['summary']
            forecast2 = weather_obj["hourly"]["summary"]

            icon_id = weather_obj['currently']['icon']
            icon2 = None

            if icon_id in icon_lookup:
                icon2 = icon_lookup[icon_id]

            if icon2 is not None:
                if self.icon != icon2:
                    self.icon = icon2
                    image = cv2.imread(icon2, cv2.IMREAD_COLOR);
                    image = cv2.resize(image,(50,50), interpolation = cv2.INTER_CUBIC)
                    image = QImage(image, image.shape[1], image.shape[0], 
                       image.strides[0], QImage.Format_RGB888)
        
                    #pix = pil2qpixmap(image)

                    self.iconLbl.setPixmap(QPixmap.fromImage(image))
            else:
                # remove image
                self.iconLbl.setPixmap(QPixmap(''))
                a=1

            if self.currently != currently2:
                print self.currently
                self.currently = currently2
                self.currentlyLbl.setText(currently2)
            if self.forecast != forecast2:
                self.forecast = forecast2
                self.forecastLbl.setText(forecast2)
            if self.temperature != temperature2:
                self.temperature = temperature2
                self.temperatureLbl.setText(temperature2)
            if self.location != location2:
                if location2 == ", ":
                    self.location = "Cannot Pinpoint Location"
                    self.locationLbl.setText("Cannot Pinpoint Location")
                else:
                    self.location = location2
                    self.locationLbl.setText(location2)
        except Exception as e:
            traceback.print_exc()
            print "Error: %s. Cannot get weather." % e


    @staticmethod
    def convert_kelvin_to_fahrenheit(kelvin_temp):
        return 1.8 * (kelvin_temp - 273) + 32




		
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
            
            news_req_url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=76d13e64c224446982e92a6e4ba09167" 
            # print news_req_url
            r = requests.get(news_req_url)
            news_obj = json.loads(r.text)
            print news_obj
            
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
                image = cv2.imread("assets/Newspaper.png", cv2.IMREAD_COLOR);
                image = cv2.resize(image,(25,25), interpolation = cv2.INTER_CUBIC)
                image = QImage(image, image.shape[1], image.shape[0], 
                       image.strides[0], QImage.Format_RGB888)
                newspaperIcon = QLabel()
                newspaperIcon.setPixmap(QPixmap.fromImage(image))

                if self.source == 'The New York Times':
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

        # for weather
        
        self.qt.hbox3 = QHBoxLayout()
        self.qt.weather = Weather(QWidget())
       
        self.qt.hbox3.addWidget(self.qt.weather)


        self.qt.vbox = QVBoxLayout()
        self.qt.vbox.addLayout(self.qt.hbox1)
        self.qt.vbox.addLayout(self.qt.hbox2)
        self.qt.vbox.addLayout(self.qt.hbox3)
        

        


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

