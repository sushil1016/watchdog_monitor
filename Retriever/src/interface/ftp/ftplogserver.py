import logging.config
from ftplib import FTP, all_errors
import socket
import time
import os
import pysftp

from util.Utility import *
from interface.buildserver.BuildServer import *
# pysftp is a simple interface to sftp

# Download pysftp at https://pypi.python.org/pypi/pysftp


logging.config.fileConfig("logger.conf")
logger = logging.getLogger("ProjectLogServer")
logger.debug('successfully Loaded logger.conf')



class ftplogserver:

    def __init__(self, server= '',username='', password='' ):
        """
        Login to Project logs server    
        """
        logger.info("**** ftplogserver initilized ****")
        self.server= server
        self.username= username
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
        return True
        # Can be defined if required

    def get_file_list(self, CPE_Mac, parsed_file_list):
        """
        Find fresh list of logs files to be processed. Should be like first in first process.
        """
        filename_list = []
        if self.sftp.exists('logs'):
            datelist = []
            filelist =[]
            # Search only below mentioned . extension files. 
            formats=["gz", "zip", "rar", "tar", "bz2", "xz","tgz"]
            for attr in self.sftp.listdir_attr(remotepath = "logs"):
                if str(attr.filename).split(".")[-1] in formats:
                    if attr.filename not in parsed_file_list:
                        datelist.append(attr.st_mtime)
                        filelist.append(attr.filename)

            if filelist:
                combo = zip(datelist,filelist)
                who = dict(combo)
                for key in sorted(who.iterkeys(), reverse=False):
                    print "File %s: %s" % (key,who[key])
                    filename = who[key]
                    print len([1 for x in filename.split('_') if x in CPE_Mac])
                    if len([1 for x in filename.split('_') if x in CPE_Mac]) > 0:
                        filename_list.append(filename)
                logger.info ("Found %s new logs",len(filename_list) )
            else:
                logger.error(" no file found under folder logs")
        else:
            logger.error("logs folder does not exits")
        return filename_list

    def download_file(self, filename):
        """
        Download log file to retriever local folder
        """
        if filename != '':
            try:
                logger.info ("Downloading File %s",filename )
                full_path = 'logs/' + filename
                #print full_path
                self.sftp.get(full_path)
            except :
                logger.error ("Download failed")
                return False
            logger.info ("Download successful")
            return True
        else:
            logger.error ("Empty file name")
            return False

    def rename_file(self, filename):
        """
        Rename already proccessed log
        """
        if filename != '':
            self.ftp.rename(filename,("Parsed_"+ str(filename)))
            logger.info("file %s renamed to %s", filename, ("Parsed_"+ str(filename)))


    def process_log_file(self, decoder, rulesEngine, filename, retriver_dir):

        if not decoder.untar_log_file(filename):
            return False

        # Find build version(method is different for different projects)
        version = decoder.find_version()

        if version != '':
            # os.path.join(retriver_dir,)
            # os.chdir(retriver_dir)
            build_path = retriver_dir + '/Diag_builds/' + version
            logger.info("Diag build Path  %s", build_path)
            if not os.path.exists(build_path):
                build_server_hostname = rulesEngine.get_build_server_hostname()
                build_server_user = rulesEngine.get_build_server_user()
                build_server_password = rulesEngine.get_build_server_password()
                logger.info("log_server_hostname  %s", build_server_hostname)
                build_server = BuildServer(build_server_hostname, build_server_user, build_server_password)
                if not build_server.login():
                    return False
                os.chdir(retriver_dir + '/Diag_builds/')
                createDirectory(version)
                os.chdir(version)

                if not build_server.download_build(version):
                    return False

            if decoder.generate_logs(version, build_path):
                logger.debug("logs generated successfully")
                if decoder.rename_logs():
                    logger.debug("Renaming successfully")
                    if decoder.copy_to_logstash():
                        logger.info("All process completed for the file %s", filename)
                    else:
                        return False
                else:
                    return False
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
