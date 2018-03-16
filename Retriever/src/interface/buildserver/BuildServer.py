import logging.config
from ftplib import FTP, all_errors
import socket

logging.config.fileConfig("logger.conf")
logger = logging.getLogger("Retriever")
logger.debug('successfully Loaded logger.conf')

class BuildServer:
    def __init__(self, server= '',username='', password=''):
        logger.debug("buildserver is initilized ")
        self.server=server
        self.username=username
        self.password= password
      
    def login(self):
        """
        Login and connect to the build server via ftp connections
        """
        if self.server != '' and self.username != '' and self.password != '':
            try:
                self.ftp = FTP(self.server)
            except (socket.error, socket.gaierror):
                logger.error('cannot reach to %s' % self.server)
                return False
            logger.info('Connected to Build FTP server%s' % self.server)

            try:
                self.ftp.login(self.username, self.password)
            except self.ftp.error_perm:
                logger.error("cannot login anonymously")
                self.ftp.quit()
                return False
            logger.info("Logged on to the build FTP server")
        else:
            logger.fatal("Mandatory parameters missing to connect to build server " + self.server)
            return False
        return True


    def download_build(self, filename):
        self.data = []
        self.ftp.dir(self.data.append)
        for line in self.data: 
            print line
        if filename != '':
            try:
                logger.info ("Downloading File %s",filename )
                self.ftp.retrbinary("RETR " + filename ,open(filename, 'wb').write)
                
                #with open(filename, 'wb') as fhandle:
                    #self.ftp.retrbinary("RETR " + filename ,fhandle.write)
                logger.info ("Download successful")
            except all_errors as e:
                logger.error ("Download failed %s",e)
                return False
            logger.info ("Download successful")
            return True
        else:
            logger.error ("Empty file name")
            return False

    def __del__(self):
        logger.info ("delete BuildServer object successful")
        try:
	    self.ftp.quit()
	except:
	    logger.error("can't delete the buildserver object")
        pass
