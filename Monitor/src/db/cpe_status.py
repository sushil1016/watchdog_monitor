import sqlite3
from sqlite3 import Error
import time
import logging, logging.config

logging.config.fileConfig("logger.conf")
logger = logging.getLogger("MONITOR")
logger.raiseExceptions = False


class CPEStatus(object):
    def __init__(self):
        logger.info("DB initialized!!")
        try:
            self.conn = sqlite3.connect('db/cpe-status.db')
            curr = self.conn.cursor()
            curr.execute('SELECT SQLITE_VERSION()')
            version = curr.fetchall()
            logger.info("Sqlite version :" + str(version))
        except Error as con_err:
            logger.error("Can't connect to database ", con_err)
            exit()
        try:
            self.conn.execute('''CREATE TABLE CPE_STATE
                             (CPE_ID PRIMARY KEY NOT NULL,
                             OSD             CHAR(15),
                             PROCESSING_DATE    INT,
                             STATE             CHAR(10));''')
            logger.info("Table created successfully")
        except Error as err:
            logger.info("Table creation failed "+ str(err))
            if 'Table creation failed' in str(err):
                exit()

    def add_cpe_state(self, cpe_id, state):
        logger.info("Inserting Data")
        status = True
        sql = '''insert into CPE_STATE(CPE_ID,OSD,PROCESSING_DATE,STATE) 
                 VALUES(?,?,?,?);'''
        value_str = (cpe_id, "", 0, state)
        logger.info("value str=>"+str(value_str))
        try:
            with self.conn:
                self.conn.execute(sql, value_str)
        except sqlite3.IntegrityError as e:
            logger.error("Insert Failed "+str(e))
            if 'UNIQUE constraint failed' in e.__str__():
                logger.error("This CPE is already added in the DB")
            status = False

        return status

    def update_cpe_state(self, cpe_id, state="", osd=""):
        logger.info("Updating the state of CPE to " + state + " cpe_id= " + str(cpe_id))
        status = True
        if "" != osd:
            osd = str(osd)[1:-1]  # sqlite can't store list, convert the list to a string

        sql = '''update CPE_STATE set processing_date = ?,state= ?, osd = ? where cpe_id = ?;'''
        value_str = (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())) + ','
                     + state + ',' + str(osd))
        logger.info("query appender=> "+value_str)
        try:
            with self.conn:
                logger.info("Executing Update...")
                self.conn.execute(sql, (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), state, osd, cpe_id))
        except Error as err:
            logger.error("Update failed..." + str(err))
            status = False

        return status

    # use int(time.time()) for processing time
    # time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())) will lead to 2017-08-21 17:36:19
    def is_cpe_processed(self, cpe_id):
        logger.info("Checking if the record is already processed")
        status = True
        # sql = '''select 1 from CPE_STATE where cpe_id =? and date(processing_date, 'start of day')
                 # =date('now', 'start of day');'''
        sql = '''select 1 from CPE_STATE where cpe_id = ?;'''
        value_str = cpe_id
        logger.info("value string=>" +str(value_str))
        try:
            cur = self.conn.cursor()
            cur.execute(sql,(cpe_id,))
            rows = cur.fetchall()
            if not rows:
                logger.error("No row found...")
                status = False
            else:  # Expecting just single row
                logger.info("Record exists")
        except Error as err:
            logger.info("Select error" + str(err))
            status = False

        return status

    def get_cpe_info(self, cpe_id):
        #logger.info("fetch data about this cpe", +str(cpe_id))
        # sql = '''select 1 from CPE_STATE where cpe_id =? and date(processing_date, 'start of day') =date('now', 'start of day');'''
        #rows = (0, '')
        status = True
        processing_date = 0
        osd = []
        sql = '''select processing_date, osd from CPE_STATE where cpe_id = ?;'''
        logger.info("fetching details for cpe " + str(cpe_id))
        try:
            cur = self.conn.cursor()
            cur.execute(sql,(cpe_id,))
            #cur.execute('select * from cpe_state where cpe_id=?', (cpe_id,))
            rows = cur.fetchall()
            if not rows:
                logger.error("No row found...")
                status = False
            else:  # Expecting just single row
                print(rows)
                print("osd type ", type(osd))
                for processing_date, osd in rows:
                    logger.info('processing_date= ' + str(processing_date))
                    logger.info('osd= ' + str(osd))
        except Error as err:
            logger.info("Select error" + str(err))
            status = False
        return status, processing_date, eval("["+osd+"]")  # convert back the osd string to list object


    def close_db(self):
        logger.info("Closing the DB gracefully...")
        self.conn.close()




