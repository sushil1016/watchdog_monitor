import sys
import logging
import sqlite3

'''
class MyHandler(logging.FileHandler):

    def __init__(self):
        print("inside logger")
        logging.FileHandler.__init__(self,'test.py')
        fmt = '%(asctime)s %(filename)-18s %(levelname)-8s: %(message)s'
        fmt_date = '%Y-%m-%dT%T%Z'
        formatter = logging.Formatter(fmt, fmt_date)
        self.setFormatter(formatter)
        

class One():
    def __init__(self):
        print("Invoked one")

    def  make_print(self,in_arg):
        print("here is your statement=> "+in_arg)

class Two(One):
    def __init__(self):
        print("Invoked Two")
        One.__init__(self)

    def call_base_cls(self,input):
        Two.make_print(self,"custom_data")


my_num=Two()
my_num.call_base_cls("This is ITTTT!!!")


 
'''



from datetime import datetime
start_date = datetime.strptime('2017-08-30 11:59:33', "%Y-%m-%d %H:%M:%S")
end_date = datetime.strptime('2017-08-30 11:59:39', "%Y-%m-%d %H:%M:%S")
print (abs((end_date-start_date).days))

'''
from datetime import datetime

start_date = datetime.strptime('2017-08-30 11:59:33', "%Y-%m-%d %H:%M:%S")
end_date = datetime.strptime('2017-08-31 11:59:39', "%Y-%m-%d %H:%M:%S")

diff_time = (end_date - start_date).days()

print(diff_time)


import arrow

a = arrow.get('2017-05-09')
b = arrow.get('2017-05-11')

delta = (b-a)
print (delta.days)


import time

now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
print("the now time is " + str(now))



exit()
db = []
db_osd_list=['1009','9999']
db_osd_list=str(db_osd_list)[1:-1]
db = ("["+db_osd_list+"]")
#db=eval(db)
print(type(db))
print(db)


exit()
server_osd_list=['1009', '9999']
db_osd_list=['1009','9999']
s=['1009','9999']
#print(",".join(str(db_osd_list)))

l = ['a', 2, 'c']
print (str(l)[l:-1])
#s.lstrip("[").rstrip("]").replace("'","").split(",")

exit()
a = ['1009','2000','45']
b = ['2000','1000','8989','8888']
diff = list((set(server_osd_list).difference(db_osd_list)))
print(diff)

exit()
print("string of a=","".join(str(x) for x in a))


print(type(server_osd_list))
print(type(db_osd_list))
print(list((set(server_osd_list).intersection(db_osd_list))))
diff = list((set(server_osd_list).difference(db_osd_list)))
#diff = list((set(a).difference(b)))
print (diff)
if not diff:
    print("list empty")
else:
    print("List not empty")
#print(set(a).intersection(b))
'''
