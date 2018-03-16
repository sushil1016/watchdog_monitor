import logging.config
import os
import shutil


logging.config.fileConfig("logger.conf")
logger = logging.getLogger("Retriever")
logger.debug('successfully Loaded logger.conf')

def constructFullUri(Ip, Path):
    logger.debug('RulesEngineIP %s Path %s', Ip, Path)
    if Ip == None:        
        return None
    return str(Ip)+str(Path)


def createDirectory(directory_name):
    logger.debug('create directory %s', directory_name)
    try:
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)
    except OSError:
        logger.error('Error: Creating directory. ' + directory_name)
    
def make_empty_directory(directory_name):
    logger.debug('clean directory %s', directory_name)
    try:
        if os.path.exists(directory_name):
            shutil.rmtree(directory_name)
    except OSError:
        logger.error('Error: clean directory. ' + directory_name)

 
def move_file(src, dst):
    pass
      
def find_diag_build(path, version):
    full_path = path+'/'+ version
    logger.debug('Diag build folder %s', full_path)
    if os.path.exists(full_path):
        return True
    else:
        return False