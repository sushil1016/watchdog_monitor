import pickle
import logging.config

# Pickle is used for serializing and de-serializing a Python object structure. 
# Any object in python can be pickled so that it can be saved on disk.
# What pickle does is that it serialises the object first before writing it to file. 
# Pickling is a way to convert a python object (list, dict, etc.) into a character stream.
# The idea is that this character stream contains all the information necessary to reconstruct the object.

logging.config.fileConfig("logger.conf")
logger = logging.getLogger("PickleData")

# Name of the data file. Should be in retriever folder.
# Do not delete this file
data_file = "db/OldLogsFile.pkl"



def get_parsed_file_list():
    """
        Returns already processed log files list.
    """
    logger.info('Read %s file',data_file)
    file_list = []
    try:
        with open(data_file, 'rb') as pkl_file:
            try:
                # Pickle methods load used to load an object from a file object
                file_list =  pickle.load(pkl_file)
                print type(file_list)
                print file_list
                pkl_file.close()
            except EOFError:
                logger.error("return empty list")
    except IOError:
        logger.error("Data file %s not created. Return empty list",data_file)
    return file_list
    
def store_parsed_file(log_file_name):
    """
        Add processed log files to data file
    """
    logger.info('Log file %s stored to %s', log_file_name,data_file)
    file_list =[]
    try:
        with open(data_file, 'rb') as pkl_file:
            try:            
                file_list = pickle.load(pkl_file)
                if log_file_name not in file_list:
                    file_list.append(log_file_name)
                pkl_file.close()

            except EOFError:
                pkl_file.close()
                file_list.append(log_file_name)
    except IOError:
        file_list.append(log_file_name)    
    print file_list
    with open(data_file, 'wb') as pkl_file:
        # Pickle methods dump used to dump an object to a file object
        pickle.dump(file_list, pkl_file, -1)
        pkl_file.close()
        print file_list
        logger.info('Log %s successfully stored', log_file_name)
        return True
    return False
