#from datetime import date
#f_date = date(2014, 7, 2)
#l_date = date(2014, 7, 11)
#delta = l_date - f_date
#print(delta.days)

#https://docs.micropython.org/en/latest/library/utime.html
import utime

#mktime returns seconds since Jan 1, 2000
f_date = utime.mktime((2014,7,2, 0,0,0, 0,0)) #(year, month, mday, hour, minute, second, weekday, yearday)
l_date = utime.mktime((2014,7,11, 0,0,0, 0,0))

delta_seconds = l_date - f_date
delta_days = delta_seconds / 60 / 60 / 24
print(delta_days)

