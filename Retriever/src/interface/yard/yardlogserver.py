import logging.config
import time
import pysftp
import os
import ConfigParser
import string

# pysftp is a simple interface to sftp
# Download pysftp at https://pypi.python.org/pypi/pysftp

YARD_SRV_CONFIG = 'interface/yard/yard.cfg'

logging.config.fileConfig("logger.conf")
logger = logging.getLogger("Retriever")
logger.debug('successfully Loaded logger.conf')


class yardlogserver():

    def __init__(self, server='', username='', password=''):
        """
        Login and connect to the external log server via sftp connections
        """
        logger.debug("yardlogserver is initilized ")
        self.server=server
        self.username=username
        self.password= password

    def login(self):
        ret = True
        if self.server != '' and self.username != '' and self.password != '':
            try:
                mycnopts = pysftp.CnOpts()
                mycnopts.hostkeys = None
                logger.info('Connecting to server %s ' % self.server)
                self.sftp = pysftp.Connection(host=self.server, username=self.username, password=self.password, cnopts=mycnopts)
            except:
                logger.fatal('failed SFTP connection!!!')
                ret = False
            logger.info('Connected to SFTP server%s' % self.server)
        else:
            logger.fatal("Mandatory parameters missing to connect to external log server " + self.server)
            ret = False
        return ret

    def read_local_config(self):
        #  READ YARD SERVER SPECIFIC CONFIGURATION DATA
        ret = False
        global config
        config= {}
        cp = ConfigParser.ConfigParser()
        try:
            cp.read(YARD_SRV_CONFIG)
        except:
            logger.error("can't open the config file %s",YARD_SRV_CONFIG)
        for sec in cp.sections():
            name = string.lower(sec)
            for opt in cp.options(sec):
                config[name + "." + string.lower(opt)] = string.strip(cp.get(sec, opt))
                logger.debug('Section: %s,  Field: %s, Value: %s', name, string.lower(opt),
                             string.strip(cp.get(sec, opt)))
                ret = True
        return ret

    def get_file_list(self, CPE_Mac, parsed_file_list):
        """
        Find fresh list of logs files to be processed. Should be like first in first process.
        """
        files = []
        log_root = config.get('yard.log_root')
        log_format= config.get('yard.log_format')
        if self.sftp.exists(log_root):
            for mac_id in CPE_Mac:
                cmd = 'ls ' + log_root + mac_id + log_format
                logger.debug("***************  executing command  *************** ",cmd)
                for line in self.sftp.execute(cmd):
                    file = line.strip('\n')
                    if file not in parsed_file_list and 'No such file' not in file:
                        files.append(file)
                    else:
                        logger.error("already processed file %s",file)

            logger.info("*** found %s new logs ***", len(files))
            time.sleep(5)
        else:
            logger.error("logs folder does not exits")
        return files

    def download_file(self, filename):
        """
        Download log file to retriever local folder
        """
        if filename != '':
            try:
                logger.info("Downloading File %s", filename)
                self.sftp.get(filename)
            except:
                logger.error("Download failed for file %s", filename)
                return False
            logger.info("Download successful")
            return True
        else:
            logger.error("Empty file name")
            return False

    def process_log_file(self, decoder, rulesEngine, filename, retriver_dir):
        if decoder.rename_logs(folder_path='.',cpe_id_pattern=config.get('yard.cpe_id_pattern')):
            logger.debug("Renamed successfully")
        else:
            return False

        if decoder.copy_to_logstash(folder_path=os.getcwd(), dest=config.get('yard.logstash_src')):
                logger.info("All process completed for the file %s", filename)
        else:
            return False
        return True


    def logout(self):
        """
        close login session, if any
        """
        try:
            self.sftp.close()
        except:
            logger.error("not able to close the sftp session")

    def __del__(self):
        pass
