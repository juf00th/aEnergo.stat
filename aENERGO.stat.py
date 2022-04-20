#!/usr/bin/env python3
from PyQt5 import uic, QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt ,QRectF, QSize, QTimer, QDate
from PyQt5.QtGui import QPainter, QPixmap, QPen, QFont, QImage, QIcon, QColor
from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsObject, QGraphicsView, QGraphicsScene, QDesktopWidget, QDialog, QGraphicsTextItem
import numpy as np
import time
import os
import json
from settings import *
from datetime import date
import openpyxl
from load_energo_files import *

if os.name == 'nt':
    import mysql.connector
else:
    import pymysql

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from calendar import monthrange


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure

import matplotlib.pyplot as plt


h2hour_label = ['00:30', '01:00', '01:30', '02:00', '02:30', '03:00', '03:30', '04:00', '04:30', '05:00', '05:30', '06:00', '06:30', '07:00', '07:30', '08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30', '22:00', '22:30', '23:00', '23:30', '00:00']

months_label = ['Січень\n01', 'Лютий\n02', 'Березень\n03', 'Квітень\n04', 'Травень\n05', 'Червень\n06', 'Липень\n07', 'Серпень\n08', 'Вересень\n09', 'Жовтень\n10', 'Литопад\n11', 'Грудень\n12']
months_xls = ['', 'січень', 'лютий', 'березень', 'квітень', 'травень', 'червень', 'липень', 'серпень', 'вересень', 'жовтень', 'литопад', 'грудень']
months_xlsR = ['', 'січня', 'лютого', 'березеня', 'квітня', 'травня', 'червня', 'липня', 'серпня', 'вересня', 'жовтня', 'литопада', 'грудня']


Form_main, _ = uic.loadUiType ( pathUI + '/' + "main.ui" )
Form_date, _ = uic.loadUiType ( pathUI + '/' + "date.ui" )
Form_about, _ = uic.loadUiType ( pathUI + '/' + "about.ui" )
Form_error, _ = uic.loadUiType ( pathUI + '/' + "error.ui" )
Form_ok, _ = uic.loadUiType ( pathUI + '/' + "ok.ui" )
Form_que, _ = uic.loadUiType ( pathUI + '/' + "que.ui" )



class MatplotlibWidget(Canvas):
    def __init__(self, parent=None, title='', xlabel='', ylabel='', dpi=80, hold=False):
        super(MatplotlibWidget, self).__init__(Figure())
        self.setParent(parent)
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.figure = Figure(dpi=dpi)
        self.canvas = Canvas(self.figure)
        self.theplot = self.figure.add_subplot(111)


    def plotData(self, x, y, rotation=False):
        self.theplot.set_title(self.title)
        self.theplot.set_xlabel(self.xlabel)
        self.theplot.set_ylabel(self.ylabel)
        
        self.theplot.spines['top'].set_visible(False)
        self.theplot.spines['right'].set_visible(False)
        self.theplot.spines['left'].set_visible(False)
        self.theplot.spines['bottom'].set_color('#DDDDDD')
        self.theplot.tick_params(bottom=False, left=False)
        self.theplot.set_axisbelow(True)
        self.theplot.yaxis.grid(True, color='#EEEEEE')
        self.theplot.xaxis.grid(False)
        
        self.theplot.bar(x,y)
        self.draw_idle()
#        print(y)
        for x,y in zip(x,y):
            if y:
                label = "{:.0f}".format(y)
            else:
                label = ''
            self.theplot.annotate(label,
                         (x, y),
                         textcoords="offset points",
                         xytext=(1, 5),
                         ha='center',
                         va='bottom',
                         rotation=90)

        if rotation:
            for rotation in self.theplot.get_xticklabels():
                rotation.set_rotation(90)


    def plotClear(self):
        self.theplot.clear()




class MatplotlibWidgetDiff(Canvas):
    def __init__(self, parent=None, title='', xlabel='', ylabel='', dpi=80, hold=False):
        super(MatplotlibWidgetDiff, self).__init__(Figure())
        self.setParent(parent)
        self.wBox = 0.35
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.figure = Figure(dpi=dpi)
        self.canvas = Canvas(self.figure)
        self.theplot = self.figure.add_subplot(111)


    def plotData(self, x, y, y2, year=0, year2=0):
        xnumber = np.arange(len(x))
        self.theplot.set_title(self.title)
        self.theplot.set_xlabel(self.xlabel)
        self.theplot.set_ylabel(self.ylabel)
        self.theplot.set_xticks(xnumber)
        self.theplot.set_xticklabels(x)
        self.theplot.spines['top'].set_visible(False)
        self.theplot.spines['right'].set_visible(False)
        self.theplot.spines['left'].set_visible(False)
        self.theplot.spines['bottom'].set_color('#DDDDDD')
        self.theplot.tick_params(bottom=False, left=False)
        self.theplot.set_axisbelow(True)
        self.theplot.yaxis.grid(True, color='#EEEEEE')
        self.theplot.xaxis.grid(False)
        self.rects1 = self.theplot.bar(xnumber - self.wBox/2, y, self.wBox, label=year)
        self.rects2 = self.theplot.bar(xnumber + self.wBox/2, y2, self.wBox, label=year2)
        self.draw_idle()
        self.autolabel(self.rects1)
        self.autolabel(self.rects2)
        if year:
            self.theplot.legend(loc='upper right', frameon=False)


    def plotClear(self):
        self.theplot.clear()


    def autolabel(self, rects):
        for rect in rects:
            height = rect.get_height()
            if height:
                label = '{:.0f}'.format(height)
            else:
                label = ''
            self.theplot.annotate(label,
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', rotation=90)





class dateDialogUI(QDialog, Form_date):
    def __init__(self, parent=None):
        super(dateDialogUI, self).__init__(parent=parent)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon( pathImage + '/' + "energo2.png" ))

class aboutDialogUI(QDialog, Form_about):
    def __init__(self, parent=None):
        super(aboutDialogUI, self).__init__(parent=parent)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon( pathImage + '/' + "energo2.png" ))

class errorDialogUI(QDialog, Form_error):
    def __init__(self, parent=None):
        super(errorDialogUI, self).__init__(parent=parent)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon( pathImage + '/' + "energo2.png" ))

class okDialogUI(QDialog, Form_ok):
    def __init__(self, parent=None):
        super(okDialogUI, self).__init__(parent=parent)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon( pathImage + '/' + "energo2.png" ))

class queDialogUI(QDialog, Form_que):
    def __init__(self, parent=None):
        super(queDialogUI, self).__init__(parent=parent)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon( pathImage + '/' + "energo2.png" ))
    
       
        
class MAIN(QMainWindow, Form_main):    
    def __init__(self):
        super(MAIN, self).__init__()
        self.setupUi(self)
        
       
        self.setWindowIcon(QtGui.QIcon( pathImage + '/' + "energo2.png" ))
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.sqlcon = None


        self.action_loadfile.triggered.connect(self.loadFile)
        self.action_loadfile.setShortcut("Ctrl+O")
        self.action_loadfile.setIcon(QIcon("img/file.svg"))

        self.action_savefile.triggered.connect(self.saveFile)
        self.action_savefile.setShortcut("Ctrl+S")
        self.action_savefile.setIcon(QIcon("img/save.svg"))        

        self.action_update.triggered.connect(self.updateAll)
        self.action_update.setShortcut("F5")
        self.action_update.setIcon(QIcon("img/update.svg"))        


        self.action_exit.triggered.connect(self.appquit)
        self.action_exit.setShortcut("Ctrl+Q")
        self.action_exit.setIcon(QIcon("img/exit.svg"))        

        self.action_about.triggered.connect(self.viewDialogAbout)
        self.action_about.setIcon(QIcon("img/about2.svg"))        

        self.date = self.getDate(date=datetime.now().strftime("%Y%m%d"), day=-1)
        self.dateChangeMonth = self.date
        self.dateChangeYear = self.date
        self.datebef = self.getDate(date=datetime.now().strftime("%Y%m%d"), day=-2)


        self.reCalculate()
        self.updateUI()
        self.calendarWidget.setMinimumDate(QDate(2017, 4, 1))
        self.calendarWidget.setSelectedDate(datetime.strptime(self.date, "%Y%m%d"))
        self.calendarWidget.selectionChanged.connect(self.dateChanged)
        self.pushButton_loadfile.clicked.connect(self.loadFile)
        self.pushButton_savefile.clicked.connect(self.saveFile)
        self.pushButton_update.clicked.connect(self.updateAll)
        self.pushButton_datenow.clicked.connect(self.dateSetNow)
        self.errorDialogView = errorDialogUI()
        iconErrorPixmap = QPixmap( pathImage + '/' + "error2.png" )
        self.errorDialogView.label_icon.setPixmap(iconErrorPixmap)
        self.errorDialogView.pushButton_ok.clicked.connect(self.errorDialogView.close)
        self.okDialogView = okDialogUI()
        iconOKPixmap = QPixmap( pathImage + '/' + "ok2.png" )
        self.okDialogView.label_icon.setPixmap(iconOKPixmap)
        self.okDialogView.pushButton_ok.clicked.connect(self.okDialogView.close)
        self.widget_day = None
        self.widget_month = None
        self.widget_year = None
        if os.path.isfile(confile):
            with open(confile) as confjson:
                try:
                    self.conf = json.load(confjson)
                except:
                    pass
        else:
            self.conf = {}
            self.conf['pathopen'] = '/home'
            self.conf['pathsave'] = '/home'

        self.plotDay()
        self.plotMonth()
        self.plotYear()
        
        
        self.okDialogView = okDialogUI()
        iconOKPixmap = QPixmap( pathImage + '/' + "ok2.png" )
        self.okDialogView.label_icon.setPixmap(iconOKPixmap)
        self.okDialogView.pushButton_ok.clicked.connect(self.okDialogView.close)

        
# ===================================================================================== defs
    def plotDay(self):
        self.getDayHours(self.date)
    
        if self.widget_day:
            self.widget_day.plotClear()
        else:
            self.widget_day = MatplotlibWidget(self.pltWidget_day, ylabel='кВт/г', dpi=80)
            self.widget_day.setGeometry(QtCore.QRect(-80, 0, 1200, 560))
        if sum(self.h2powers) > 0:
            self.widget_day.plotData(h2hour_label, self.h2powers, rotation=True)
        else:
            zerodata = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            self.widget_day.plotData(h2hour_label, zerodata, rotation=True)


    def plotMonth(self):
        days = self.getMonthDays(self.date)
        xdate = []
        ypower = []
        for day in days:
#            xdate.append(day['date'].strftime("%d.%m"))
            xdate.append(day['date'][:2])
            ypower.append(day['power'])
        if self.widget_month:
            self.widget_month.plotClear()
        else:
            self.widget_month = MatplotlibWidget(self.pltWidget_month, ylabel='кВт/г', dpi=80)
            self.widget_month.setGeometry(QtCore.QRect(-80, 0, 1200, 560))
        if sum(ypower) > 0:
            self.widget_month.plotData(xdate,ypower)
        else:
            zerodata = []
            for i in range (0,len(xdate)):
                zerodata.append(0)
            self.widget_month.plotData(xdate, zerodata)
            

    def plotYear(self):
        ypowerMin1 = []
        xlabel = []
        ypower = []
        dateYear = self.date[:4]
        dateYearMin1 = "%04.d" % (float(self.date[:4]) - 1)
        for month in range (1,13):
            apowerMonth = 0
            monthText = "%02.d" % month
            xlabel.append("%s" % monthText)
            powerMonthdb = self.sql("SELECT * FROM "+ mysql_tbl +" WHERE `apowercnt` > '0' AND YEAR(date) = ('"+ str(dateYear) +"') AND MONTH(date) = ('"+ str(month) +"') ORDER BY date DESC LIMIT 0,1")
            powerMonthdbMin1 = self.sql("SELECT * FROM "+ mysql_tbl +" WHERE `apowercnt` > '0' AND YEAR(date) = ('"+ str(dateYearMin1) +"') AND MONTH(date) = ('"+ str(month) +"') ORDER BY date DESC LIMIT 0,1")

            datedef=self.getMonth(date="%s%02.d%02.d" % (dateYear, month, 1), month=-1)
            powerMonthBefdb = self.sql("SELECT * FROM "+ mysql_tbl +" WHERE `apowercnt` > '0' AND YEAR(date) = YEAR('"+ datedef +"') AND MONTH(date) = MONTH('"+ datedef +"') ORDER BY date DESC LIMIT 0,1")            
            datedefMin1=self.getMonth(date="%s%02.d%02.d" % (dateYearMin1, month, 1), month=-1)
            powerMonthBefdbMin1 = self.sql("SELECT * FROM "+ mysql_tbl +" WHERE `apowercnt` > '0' AND YEAR(date) = YEAR('"+ datedefMin1 +"') AND MONTH(date) = MONTH('"+ datedefMin1 +"') ORDER BY date DESC LIMIT 0,1")            

            if powerMonthdb and powerMonthBefdb:
                if powerMonthdb[0][1] > 0 and powerMonthBefdb[0][1] > 0:
                    apowerMonth = powerMonthdb[0][1] - powerMonthBefdb[0][1]
                else:
                    apowerMonth = 0
            else:
                apowerMonth = 0
            ypower.append(apowerMonth)

            if powerMonthdbMin1 and powerMonthBefdbMin1:
                if powerMonthdbMin1[0][1] > 0 and powerMonthBefdbMin1[0][1] > 0:
                    apowerMonthMin1 = powerMonthdbMin1[0][1] - powerMonthBefdbMin1[0][1]
                else:
                    apowerMonthMin1 = 0
            else:
                apowerMonthMin1 = 0
            ypowerMin1.append(apowerMonthMin1)

        if self.widget_year:
            self.widget_year.plotClear()
        else:
            self.widget_year = MatplotlibWidgetDiff(self.pltWidget_year, ylabel='кВт/г', dpi=80)
            self.widget_year.setGeometry(QtCore.QRect(-80, 0, 1200, 560))
        if sum(ypower) > 0 and sum(ypowerMin1) > 0:
            self.widget_year.plotData(months_label, ypower, ypowerMin1, dateYear, dateYearMin1)
        else:
            zerodata = [0,0,0,0,0,0,0,0,0,0,0,0]
            self.widget_year.plotData(months_label, zerodata, zerodata, '', '')


    def getDayHours(self, date=None):
        if date:
            today = datetime.strptime(date, "%Y%m%d")
            todaydb = datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d")
        else:
            today = datetime.now()
            todaydb = today.strftime("%Y-%m-%d")
#        print(todaydb)
        h2powerstr = self.sql("SELECT `h2apower` FROM "+ mysql_tbl +" WHERE `date` = '"+ todaydb +"' LIMIT 0,1")
        if h2powerstr:
            h2powerstr = h2powerstr[0][0]
        else:
            h2powerstr = ':0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:'
        h2powers = h2powerstr.split(':')
        h2powers = h2powers[1:-1]
        self.h2powers = []
        for h2power in h2powers:
            h2power = float(h2power)
            self.h2powers.append(h2power)
        

    def getMonthDays(self, date=None):
        if date:
            today = datetime.strptime(date, "%Y%m%d").strftime("%Y%m%d")
            todaydb = datetime.strptime(date, "%Y%m%d").strftime("%Y-%m")
            todayMonth = datetime.strptime(date, "%Y%m%d").strftime("%m")
        monthdays = self.getDaysOfMonth(today)
        lastdaybefmonth = self.getLastDateOfMonth(date=self.getMonth(date=today, month=-1))
        lastdaybefmonthdb = datetime.strptime(lastdaybefmonth, "%Y%m%d").strftime("%Y-%m-%d")
        days = []
        for monthday in range(1, monthdays+1):
            monthdaydb = "%02d" % monthday
            power = 0
            daydb = self.sql("SELECT * FROM "+ mysql_tbl +" WHERE `date` = '"+ todaydb +"-"+ monthdaydb +"' LIMIT 0,1")
            if daydb:
                power = daydb[0][4]
            dateLabel = "%s.%s" % (monthdaydb, todayMonth)
            days.append({'date': dateLabel, 'power': power})
        return days


    def getLastDateOfMonth(self, date=None):
        date2 = datetime.strptime(date, "%Y%m%d")
        lastday = monthrange(date2.year, date2.month)[1]
        lastdate = datetime.strptime("%s%s%s" % (date2.year, date2.month, lastday), "%Y%m%d").strftime("%Y%m%d")
        return lastdate
        

    def getDaysOfMonth(self, date=None):
        if not date:
            date = datetime.now()
        else:
            date = datetime.strptime(date, "%Y%m%d")
        days = monthrange(date.year, date.month)
        return days[1]


    def getMonth(self, date=None, month=None):
        date = datetime.strptime(date, "%Y%m%d")
        date_after_month = date + relativedelta(months=month)
        date_after_month = datetime.strftime(date_after_month, "%Y%m%d")
        return date_after_month


    def getDate(self, date_format = '%Y%m%d', date = None, day = 0):
        if date:
            today = datetime.strptime(date, "%Y%m%d")
        else:
            today = datetime.now()
        result = today + timedelta(days=day)
        return result.strftime(date_format)
            
            
    def saveConf(self):
        with open(confile, 'w') as confilejson:
            json.dump(self.conf, confilejson)


# ====================================================================================== Load File
    def loadFile(self):
        pathfull, _ = QtWidgets.QFileDialog.getOpenFileName(None, 'Вибрати файл для заванаження до бази', self.conf['pathopen'], "Nikotex_*.txt ( Nikotex_*.txt Nikotex_*.TXT)")
        if pathfull != '':
            pathfile, filenamefull = os.path.split(pathfull)
            filename = os.path.splitext(filenamefull)[0]
            self.conf['pathopen'] = pathfull
            lef = loadEnergoFiles()
            try:
                lef.loadfile(pathfull)
                self.saveConf()
                self.updateAll()
                self.statusBar().showMessage("Файл завантажено", 10000)
                self.okDialogView.label_mess.setText("Файл завантажено.")
                self.okDialogView.exec_()
            except:
                self.statusBar().showMessage("Помилка!", 10000)
                self.errorDialogView.label_mess.setText('Помилка!')



    def saveFile(self):
    
        if self.power['apowerMonth'] > 0 or self.power['rpowerMonth'] > 0 or self.power['gpowerMonth'] > 0:
            pathfull, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Зберегти АКТ", "%s.xlsx" % self.conf['pathsave'], "XLS (*.xlsx *.XLSX)")
            if pathfull != '':
                pathfile, filenamefull = os.path.split(pathfull)
                filename = os.path.splitext(filenamefull)[0]
                self.conf['pathsave'] = "%s/%s" % (pathfile, filename)
                self.saveConf()

                datenow = datetime.now().strftime("%Y%m%d")
                datenowTextTop = "%s %sр." % (months_xls[int(datenow[4:6])], datenow[:4])
                datenowTextBottom = "\"%s\" %s %sр." % (datenow[6:8], months_xlsR[int(datenow[4:6])], datenow[:4])
                xls = openpyxl.load_workbook(filename = "template.xlsx")
                xlslist = xls['energo']
                xlslist['E4'] = datenowTextTop
                xlslist['B21'] = datenowTextBottom
                
                xlslist['E11'] = "%.4f" % (self.power['apowerMonthCnt'] / CounterCoeff)
                xlslist['E13'] = "%.4f" % (self.power['rpowerMonthCnt'] / CounterCoeff)
                xlslist['E15'] = "%.4f" % (self.power['gpowerMonthCnt'] / CounterCoeff)
                
                xlslist['F11'] = "%.4f" % (self.power['apowerMonthCntBef'] / CounterCoeff)
                xlslist['F13'] = "%.4f" % (self.power['rpowerMonthCntBef'] / CounterCoeff)
                xlslist['F15'] = "%.4f" % (self.power['gpowerMonthCntBef'] / CounterCoeff)

                xlslist['F11'] = "%.4f" % (self.power['apowerMonthCntBef'] / CounterCoeff)
                xlslist['F13'] = "%.4f" % (self.power['rpowerMonthCntBef'] / CounterCoeff)
                xlslist['F15'] = "%.4f" % (self.power['gpowerMonthCntBef'] / CounterCoeff)

                xlslist['G11'] = "%.4f" % (self.power['apowerMonth'] / CounterCoeff)
                xlslist['G13'] = "%.4f" % (self.power['rpowerMonth'] / CounterCoeff)
                xlslist['G15'] = "%.4f" % (self.power['gpowerMonth'] / CounterCoeff)

                xlslist['I11'] = "%.0f" % self.power['apowerMonth']
                xlslist['I13'] = "%.0f" % self.power['rpowerMonth']
                xlslist['I15'] = "%.0f" % self.power['gpowerMonth']

                xls.save("%s/%s.xlsx" % (pathfile, filename))
                self.statusBar().showMessage("Файл \"%s.xlsx\" збережено" % filename, 10000)
        else:
            self.statusBar().showMessage("Нема що зберігати! Нема данних за місяць.", 10000)
            self.errorDialogView.label_mess.setText('Нема що зберігати!\n\nНема данних за місяць.')
            self.errorDialogView.exec_()



    def dateSetNow(self):
        self.date = self.getDate(date=datetime.now().strftime("%Y%m%d"), day=-1)
        date = datetime.strptime(self.date, "%Y%m%d")
        self.calendarWidget.setSelectedDate(date)
        self.updateAll()


    def updateAll(self):
        self.reCalculate()
        self.updateUI()
        self.plotDay()
        self.plotMonth()
        self.plotYear()


    def dateChanged(self):
        self.date = self.calendarWidget.selectedDate().toString("yyyyMMdd")
#        print(self.date)
        self.reCalculate()
        self.updateUI()
        self.plotDay()
        if self.date[:6] != self.dateChangeMonth[:6]:
            self.dateChangeMonth = self.date
            self.plotMonth()
        if self.date[:4] != self.dateChangeYear[:4]:
            self.dateChangeYear = self.date
            self.plotYear()


    def updateUI(self):
        self.lineEdit_apowerDay.setText("%.0f" % self.power['apowerDay'])
        self.lineEdit_rpowerDay.setText("%.0f" % self.power['rpowerDay'])
        self.lineEdit_gpowerDay.setText("%.0f" % self.power['gpowerDay'])
        self.lineEdit_apowerMonth.setText("%.0f" % self.power['apowerMonth'])
        self.lineEdit_rpowerMonth.setText("%.0f" % self.power['rpowerMonth'])
        self.lineEdit_gpowerMonth.setText("%.0f" % self.power['gpowerMonth'])
        self.lineEdit_apowerYear.setText("%.0f" % self.power['apowerYear'])
        self.lineEdit_rpowerYear.setText("%.0f" % self.power['rpowerYear'])
        self.lineEdit_gpowerYear.setText("%.0f" % self.power['gpowerYear'])
        self.lineEdit_apowerCnt.setText("%.0f" % self.power['apowerCnt'])
        self.lineEdit_rpowerCnt.setText("%.0f" % self.power['rpowerCnt'])
        self.lineEdit_gpowerCnt.setText("%.0f" % self.power['gpowerCnt'])
        

    def reCalculate(self):
        self.power = {}
        self.datebef = self.getDate(date=self.date, day=-1)
        powerdb = self.sql("SELECT * FROM "+ mysql_tbl +" WHERE `date` = '"+ self.date +"' LIMIT 0,1")
        if powerdb:
            self.power['apowerCnt'] = powerdb[0][1]
            self.power['rpowerCnt'] = powerdb[0][2]
            self.power['gpowerCnt'] = powerdb[0][3]
            self.power['apowerDay'] = powerdb[0][4]
            self.power['rpowerDay'] = powerdb[0][5]
            self.power['gpowerDay'] = powerdb[0][6]
        else:
            self.power['apowerCnt'] = 0
            self.power['rpowerCnt'] = 0
            self.power['gpowerCnt'] = 0
            self.power['apowerDay'] = 0
            self.power['rpowerDay'] = 0
            self.power['gpowerDay'] = 0
        LastDateBefOfMonth = self.getLastDateOfMonth(date=self.getMonth(date=self.date, month=-1))

        powerLastDateBefOfMonthdb = self.sql("SELECT * FROM "+ mysql_tbl +" WHERE MONTH(date) = MONTH('"+ LastDateBefOfMonth +"') AND YEAR(date) = YEAR('"+ LastDateBefOfMonth +"') ORDER BY date DESC LIMIT 0,1")
        powerLastDateOfMonthdb = self.sql("SELECT * FROM "+ mysql_tbl +" WHERE MONTH(date) = MONTH('"+ self.date +"') AND YEAR(date) = YEAR('"+ self.date +"') ORDER BY date DESC LIMIT 0,1")

        if powerLastDateOfMonthdb and powerLastDateBefOfMonthdb:
            if powerLastDateOfMonthdb[0][1] > 0 and powerLastDateBefOfMonthdb[0][1] > 0:
                self.power['apowerMonth'] = powerLastDateOfMonthdb[0][1] - powerLastDateBefOfMonthdb[0][1]
                self.power['apowerMonthCnt'] = powerLastDateOfMonthdb[0][1]
                self.power['apowerMonthCntBef'] = powerLastDateBefOfMonthdb[0][1]
            else:
                self.power['apowerMonth'] = 0
                self.power['apowerMonthBef'] = 0

            if powerLastDateOfMonthdb[0][2] > 0 and powerLastDateBefOfMonthdb[0][2] > 0:
                self.power['rpowerMonth'] = powerLastDateOfMonthdb[0][2] - powerLastDateBefOfMonthdb[0][2]
                self.power['rpowerMonthCnt'] = powerLastDateOfMonthdb[0][2]
                self.power['rpowerMonthCntBef'] = powerLastDateBefOfMonthdb[0][2]
            else:
                self.power['rpowerMonth'] = 0
                self.power['rpowerMonthCnt'] = 0
                self.power['rpowerMonthBef'] = 0

            if powerLastDateOfMonthdb[0][3] > 0 and powerLastDateBefOfMonthdb[0][3] > 0:
                self.power['gpowerMonth'] = powerLastDateOfMonthdb[0][3] - powerLastDateBefOfMonthdb[0][3]
                self.power['gpowerMonthCnt'] = powerLastDateOfMonthdb[0][3]
                self.power['gpowerMonthCntBef'] = powerLastDateBefOfMonthdb[0][3]
            else:
                self.power['gpowerMonth'] = 0
                self.power['gpowerMonthCnt'] = 0
                self.power['gpowerMonthCntBef'] = 0
        else:
            self.power['apowerMonth'] = 0
            self.power['rpowerMonth'] = 0
            self.power['gpowerMonth'] = 0
            self.power['apowerMonthCnt'] = 0
            self.power['rpowerMonthCnt'] = 0
            self.power['gpowerMonthCnt'] = 0
            self.power['apowerMonthCntBef'] = 0
            self.power['rpowerMonthCntBef'] = 0
            self.power['gpowerMonthCntBef'] = 0

# ======================================================================== за год
        dateBefYear = str(float(self.date[:4]) - 1)

        powerBefYeardb = self.sql("SELECT * FROM "+ mysql_tbl +" WHERE YEAR(date) = ('"+ dateBefYear +"') ORDER BY date DESC LIMIT 0,1")
        powerYeardb = self.sql("SELECT * FROM "+ mysql_tbl +" WHERE YEAR(date) = ('"+ self.date[:4] +"') ORDER BY date DESC LIMIT 0,1")
        if powerYeardb and powerBefYeardb:
            if powerYeardb[0][1] > 0 and powerBefYeardb[0][1] > 0:
                self.power['apowerYear'] = powerYeardb[0][1] - powerBefYeardb[0][1]
            else:
                self.power['apowerYear'] = 0

            if powerYeardb[0][2] > 0 and powerBefYeardb[0][2] > 0:
                self.power['rpowerYear'] = powerYeardb[0][2] - powerBefYeardb[0][2]
            else:
                self.power['rpowerYear'] = 0

            if powerYeardb[0][3] > 0 and powerBefYeardb[0][3] > 0:
                self.power['gpowerYear'] = powerYeardb[0][3] - powerBefYeardb[0][3]
            else:
                self.power['gpowerYear'] = 0
        else:
            self.power['apowerYear'] = 0
            self.power['rpowerYear'] = 0
            self.power['gpowerYear'] = 0


    def viewDialogAbout(self):
        aboutDialogView = aboutDialogUI()
        iconPixmap = QPixmap( pathImage + '/' + "about2.png" )
        aboutDialogView.label.setPixmap(iconPixmap)
        aboutDialogView.pushButton_ok.clicked.connect(aboutDialogView.close)
        aboutDialogView.exec_()
 
 
    def sql(self, req):
        if not self.sqlcon:
            if os.name == 'nt':
                self.sqlcon = mysql.connector.connect(host=mysql_host, user=mysql_user, password=mysql_pass, database=mysql_db)
            else:
                self.sqlcon = pymysql.connect(host=mysql_host, user=mysql_user, passwd=mysql_pass, db=mysql_db)
        with self.sqlcon:
            if os.name == 'nt':
                self.sqlcon.reconnect()
            cur = self.sqlcon.cursor()
            cur.execute(req)
            result = cur.fetchall()
            #cur.close()
            #self.sqlcon.close()
            return result
    

    def appquit(self, _):
#        self.sqlcon.close()
        sys.exit()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = MAIN()
    w.show()
    sys.exit(app.exec_())
