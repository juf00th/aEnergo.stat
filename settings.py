#!/usr/bin/env python
import os

pathImage = 'img'
pathUI = 'ui'
confile = 'conf.txt'



pathMAIL = '/data/energo/mail'
pathFilesOK = '/data/energo/loaded'
pathFilesBAD = '/data/energo/badfiles'

MAILfileCodepage = 'cp1251'

CounterCoeff = 4000



mysql_host = os.environ['aenergosqlhost']
mysql_user = os.environ['aenergosqluser']
mysql_pass = os.environ['aenergosqlpass']
mysql_db = 'energo'
mysql_tbl = 'pystat'




