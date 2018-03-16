import logging.config
import tarfile
import os
import time
import re
import datetime
import calendar
import sys
from util.Utility import *
from distutils.dir_util import copy_tree
from subprocess import call, Popen
from ConfigParser import SafeConfigParser



logging.config.fileConfig("logger.conf")
logger = logging.getLogger("Retriever.Decoder")




def getDecoderConfigInfo():
    parser = SafeConfigParser()
    try:
        parser.read('config.cfg')
        path_version_file = str(parser.get('Decoder', 'PathToVersionTextFile'))
        print parser.get('Decoder', 'VersionStringName')
        print parser.get('Decoder', 'CURFilePath')
        print parser.get('Decoder', 'DefaultCPEID')
        print parser.get('Decoder', 'DefaultOffset')
        print parser.get('Decoder', 'LogstashPath')
    
    except Exception as e:
        logger.error("Error in reading decoder config %s",e)
#getDecoderConfigInfo()

class Decoder:
    
    def __init__(self):
        logger.info ("Decoder instance created")
    
    def untar_log_file(self, file_name):
        """
        extract the tar file. Return true if success 
        """
        logger.info ("untar the file name %s ",file_name)
        try:
            tar = tarfile.open(file_name, "r:gz")
            tar.extractall()
            tar.close()
            logger.info("untar is successful")
            return True
        except:
            tar.close()
            return False
 
    def find_version(self, path ='tmp/bl_data/BOOTLOG/VERHIST.TXT', string = 'NDS_SW_VERSION' ):
        #tmp/bl_data/BOOTLOG/VERHIST.TXT
        """
        Find version name from VERHIST file.
        """
        logger.info('Finding build version')
        version = ''
        try:
            datafile = open(path, 'rb')
            for line in datafile:
                if string.lower() in line.lower():
                    version = str(line.split('=')[1]).replace('"', '').strip()
                    break
        except:
            logger.error('Error: In finding Version')
                
        logger.info('Build version %s', version)
        return version
        
    def generate_logs(self, version, build_path):
        """
        Copy CUR file to diag  parsed folder and run the diag_bin_parser script.
        """
        try:
            binary_log_dst = '../Diag_builds/'+ version +'/binary_log_full'
            make_empty_directory(binary_log_dst)
            createDirectory(binary_log_dst)
            binary_log_src = os.getcwd() + '/tmp/bl_data/BOOTLOG/DIAGBIN.CUR'
            logger.info("Move file %s to %s ", binary_log_src,binary_log_dst)
            #make_empty_directory('./diag_log_full')
            shutil.move(binary_log_src, binary_log_dst)
            os.chdir(build_path)
            print os.getcwd()
            make_empty_directory(binary_log_dst)
            make_empty_directory('./diag_log_full')
            #sys.
            call(["chmod", "0777", "diag_bin_parser"])
            call(["./diag_bin_parser"])
            
            logger.info('logs generation successful')
            return True
        except:
            logger.error("logs generation failed") 
            return False
            
    def rename_logs(self, CPE_ID = [],cpe_id_pattern='Real CPE_ID=([0-9]+)', folder_path = './diag_log_full'):
        """
        Rename the logs created from diag parser in below format
        Format: file_[CPE_ID]_[logstamp].log
        
        Find CPE_ID and the time where the logs capturing started.
        """
        logger.info ("CpeID %s, generated log folder %s",CPE_ID,folder_path)
        temp_time =[]
        # use this CPE ID if you do not find any CPE if from logs
        default_CPE_ID = '123456789'
        default_offset = '78'
        # If size of logs file is big, them diag parser generate multiple log files.
        # we need to rename all this file
        try:
            for filename in os.listdir(folder_path):
                file_full_name = folder_path+"/"+filename
                logs = open(file_full_name)
                TOTtime = []
                timeoffset =[]
                logger.debug("Found a new file in diag_log_full folder %s", filename)                  
                for line in logs:
                    if not CPE_ID:
                        # If user has not provided the CPE ID
                        CPE_ID = re.findall(cpe_id_pattern,line)
                        #tt = re.search('Real CPE_ID=([0-9]+),',line)
                    
                    if not TOTtime:
                        TOTtime = re.findall('\(Year:Month:Day:Hour:Min:Sec\) ([0-9]+:[0-9]+:[0-9]+:[0-9]+:[0-9]+:[0-9]+)',line)
                        if len(TOTtime) > 0:
                            # Find the offset on this line
                            timeoffset = re.findall('^NDS: \^([0-9]+.[0-9]+) !MIL',line)
                           
                    if TOTtime and CPE_ID:
                        break           
        
                if not TOTtime:                
                    print("timestamp not foundin logs, using default")
                    # default to update
                    logtime = '2017:7:20:11:58:53' 
                    logger.info('Default log time updated - %s',logtime)
                else:
                    logtime = TOTtime[0]
                
                if not CPE_ID:
                    logger.info('CPE_ID not found in logs, using default value %d', default_CPE_ID)
                    CPE_ID.append(default_CPE_ID)
                
                if not timeoffset:
                    logger.info('timeoffset not found in logs, using default value:', default_offset)
                    timeoffset.append(default_offset)
        
                temp_time = [int(item) for item in logtime.split(':')]
                d = datetime.datetime(temp_time[0], temp_time[1], temp_time[2], temp_time[3], temp_time[4], temp_time[5])
                timestamp1 = calendar.timegm(d.timetuple())
                logger.debug('Log time stamp %s',timestamp1)
                
                offset = 0
                if timeoffset:
                    offset = int(timeoffset[0].split('.')[0])
    
                logger.debug('offset %s',offset)
                logstamp = timestamp1 - offset            
                logger.debug('Actual log time stamp %s',logstamp)
               
                old_file = os.path.join(file_full_name)
                new_file_name = "file_" + CPE_ID[0] + "_" + str(logstamp) + ".log"
                #new_file = os.path.join("./logs/diag_binary/diag_log_full", "file_" + CPE_ID[0] + "_" + str(logstamp)+"__"+ str(p) +".log")
                new_file = os.path.join(folder_path, new_file_name)
                #print old_file
                #print new_file
                os.rename(file_full_name, new_file)
                logger.info('The file %s renamed to %s ',filename,new_file_name)
            return True
        except:
            logger.error('The file renaming is failed')
            return False
            
            #dest = dest + '/diag_binary/binary_log_full'
            #shutil.move(src, dest)
    
    def copy_to_logstash(self, folder_path = 'diag_log_full', dest = '/home/health_monitor/Retriever/Decoded'):
        """
        Copy all logs files to the folder where logstash picks-up.
        We need to mention proper destination folder. For find destination path 
        Check logstash-main.conf.txt        .
        Note: mention complete destination path 
        """
        logger.debug(" Move to all parsed files from file from %s to %s", folder_path, dest)
        time.sleep(5)
        try:
            copy_tree(folder_path, dest)
        except  Exception as e:
            logger.error("Error in coping folder %s",e)
            return False
        
        return True

    def run_logstash(self, logstash_path = "/usr/share/logstash/bin/logstash"):
        """
        pass proper logstash path
        """
        try:
            Popen([logstash_path, "--path.settings", "/etc/logstash/", "-f", "/etc/logstash/conf.d/logstash-main.conf", "--path.data" , "/var/log/logstash/logstash2/" ])
        except  Exception as e:
            logger.error("Error in coping folder %s",e)
            return False
        logger.info("successfully ran the logstash")
        return True
        
