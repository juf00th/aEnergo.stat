#!/usr/bin/env python3
import os
from settings import *
import pymysql


class loadEnergoFiles():
    def __init__(self):
        super(loadEnergoFiles, self).__init__()
        self.sqlcon = None

    def LoadDirFiles(self):
        files = self.lsdir(pathMAIL)
        if len(files) > 0:
            for file in files:
                self.loadfile(pathMAIL+'/'+file)
        else:
            print('dir empty')


    def loadfile(self, filename):
        file = {'date': None, 'apowercnt': None, 'rpowercnt': None, 'gpowercnt': None}
        file2 = {'date': None, 'apower': None, 'rpower': None, 'gpower': None, 'h2apower': None, 'h2rpower': None, 'h2gpower': None}
        
        filelines = self.readfile(filename)
        if len(filelines) > 0:
            for fileline in filelines:

                # маленький файл
                if not fileline.find("//30818") == -1:
                    _, monthday, _ = fileline.split(":", 2)
                    yearFromFile = os.path.basename(filename)[8:12]
                    if monthday == "1231":
                        yearFromFile = "%.0f" % round (float(yearFromFile) - 1, 0)
                    file['date'] = "%s%s" % (yearFromFile, monthday)

                # великий файл
                if not fileline.find("//30917") == -1:
                    _, monthday, _ = fileline.split(":", 2)
                    yearFromFile = os.path.basename(filename)[8:12]
                    if monthday == "1231":
                        yearFromFile = "%.0f" % round (float(yearFromFile) - 1, 0)
                    file2['date'] = "%s%s" % (yearFromFile, monthday)

                    
            if file['date']:
                for fileline in filelines:

                    if not fileline.find("1):") == -1:
                        _, apowercnt, _ = fileline.split(":", 2)
                        if apowercnt:
                            apowercnt = apowercnt.replace(',', '.')
                            file['apowercnt'] = round (float(apowercnt) * CounterCoeff, 0)
                        else:
                            file['apowercnt'] = None
                        
                    if not fileline.find("3):") == -1:
                        _, rpowercnt, _ = fileline.split(":", 2)
                        if rpowercnt:
                            rpowercnt = rpowercnt.replace(',', '.')
                            file['rpowercnt'] = round (float(rpowercnt) * CounterCoeff, 0)
                        else:
                            file['rpowercnt'] = None
                        
                    if not fileline.find("5):") == -1:
                        _, gpowercnt, _ = fileline.split(":", 2)
                        if gpowercnt:
                            gpowercnt = gpowercnt.replace(',', '.')
                            file['gpowercnt'] = round (float(gpowercnt) * CounterCoeff, 0)
                        else:
                            file['gpowercnt'] = None

# ========= великий файл
            if file2['date']:
                for fileline in filelines:
                    power = self.bigFileString(fileline, '1):')
                    if power:
                        file2['apower'] = power['power']
                        file2['h2apower'] = power['h2power']

                    power = self.bigFileString(fileline, '3):')
                    if power:
                        file2['rpower'] = power['power']
                        file2['h2rpower'] = power['h2power']

                    power = self.bigFileString(fileline, '4):')
                    if power:
                        file2['gpower'] = power['power']
                        file2['h2gpower'] = power['h2power']



                            
                        
                        
        else:
           print('file is zero')


           
        if file['date'] and file['apowercnt'] and file['rpowercnt'] and file['gpowercnt']:
            print(file)
            indbexist = None
            indbexist = self.sql("SELECT `date` FROM "+ mysql_tbl +" WHERE `date` = '"+ file['date'] +"' LIMIT 0,1")
            if indbexist:
                print('update db')
                self.sql("UPDATE "+ mysql_tbl +" SET `date` = '"+ file['date'] +"', `apowercnt` = '"+ "%s" % file['apowercnt'] +"', `rpowercnt` = '"+ "%s" % file['rpowercnt'] +"', `gpowercnt` = '"+ "%s" % file['gpowercnt'] +"' WHERE `date` = '"+ file['date'] +"'")
            else:
                self.sql("INSERT INTO "+ mysql_tbl +" SET `date` = '"+ file['date'] +"', `apowercnt` = '"+ "%s" % file['apowercnt'] +"', `rpowercnt` = '"+ "%s" % file['rpowercnt'] +"', `gpowercnt` = '"+ "%s" % file['gpowercnt'] +"'")



        if file2['date']:
            print(file2)
            indbexist = None
            indbexist = self.sql("SELECT `date` FROM "+ mysql_tbl +" WHERE `date` = '"+ file2['date'] +"' LIMIT 0,1")
            if indbexist:
                print('update db')
                self.sql("UPDATE "+ mysql_tbl +" SET `date` = '"+ file2['date'] +"', `apower` = '"+ "%s" % file2['apower'] +"', `rpower` = '"+ "%s" % file2['rpower'] +"', `gpower` = '"+ "%s" % file2['gpower'] +"', `h2apower` = '"+ "%s" % file2['h2apower'] +"', `h2rpower` = '"+ "%s" % file2['h2rpower'] +"', `h2gpower` = '"+ "%s" % file2['h2gpower'] +"' WHERE `date` = '"+ file2['date'] +"'")
            else:
                self.sql("INSERT INTO "+ mysql_tbl +" SET `date` = '"+ file2['date'] +"', `apower` = '"+ "%s" % file2['apower'] +"', `rpower` = '"+ "%s" % file2['rpower'] +"', `gpower` = '"+ "%s" % file2['gpower'] +"', `h2apower` = '"+ "%s" % file2['h2apower'] +"', `h2rpower` = '"+ "%s" % file2['h2rpower'] +"', `h2gpower` = '"+ "%s" % file2['h2gpower'] +"'")


        if __name__ == '__main__':
            if (file['date'] and file['apowercnt'] and file['rpowercnt'] and file['gpowercnt']) or (file2['date'] and file2['apower']):
                # перенос
                pass
                os.rename(pathMAIL+'/'+filename, pathFilesOK+'/'+filename)
            else:
                pass
                os.rename(pathMAIL+'/'+filename, pathFilesBAD+'/'+filename)
                    

    def bigFileString(self, fileline, findstr):
        file = {'power': None, 'h2power': None}
        if not fileline.find(findstr) == -1:
            string = fileline.replace(',', '.')
            stringlist = string.split(":")
            power = stringlist[1]
            h2power = stringlist[2:-1]
            oldfile = None
            for powerdev2 in h2power:
                if powerdev2 == '':
                    powerdev2 = '0.0000'
                if float(powerdev2) < 1 and float(powerdev2) > 0:
                    oldfile = True
            if power == '':
                power = '0.0000'
#            print('old file format')
            file['power'] = ''
            file['h2power'] = ''
            for powerdev2 in h2power:
                if powerdev2 == '':
                    powerdev2 = '0.0000'
                if oldfile:
                    file['h2power'] = "%s:%.0f" % (file['h2power'], round( float(powerdev2) * CounterCoeff, 0))
                else:
                    file['h2power'] = "%s:%.0f" % (file['h2power'], round( float(powerdev2), 0))
            file['h2power'] = "%s:" % file['h2power']
            if oldfile:
                file['power'] = "%.0f" % round( float(power) * CounterCoeff, 0)
            else:
                file['power'] = "%.0f" % round( float(power), 0)
            if file['power']:
                return(file)
            else:
                return(None)



    def readfile(self, filename):
            with open( filename, 'r', encoding=MAILfileCodepage) as f:
                filelines = f.read().splitlines()
            return (filelines)

            
    def lsdir(self, path):
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        return files


    def sql(self, req):
        if not self.sqlcon:
            self.sqlcon = pymysql.connect(mysql_host, mysql_user, mysql_pass, mysql_db)
        with self.sqlcon:
            cur = self.sqlcon.cursor()
            cur.execute(req)
            return(cur.fetchall())
    



if __name__ == '__main__':
    import sys
    lef = loadEnergoFiles()
    lef.LoadDirFiles()
