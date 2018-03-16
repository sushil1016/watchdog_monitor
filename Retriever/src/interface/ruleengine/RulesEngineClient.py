import urllib2
import logging.config
import json


logging.config.fileConfig("logger.conf")
logger = logging.getLogger("Retriever")
logger.debug('RulesEngineClient successfully Loaded logger.conf')

class RulesEngineClient:

    def __init__(self):
        """
        Initialize class variables
        """
        self.project_log_server_hostname = ''
        self.project_log_server_serverVersion = ''
        self.project_log_server_user = ''
        self.project_log_server_password = ''

        self.build_server_hostname = ''
        self.build_server_serverVersion = ''
        self.build_server_user = ''
        self.build_server_password = ''

        self.master_logs_DB_hostname = ''
        self.master_logs_DB_serverVersion = ''
        self.master_logs_DB_user = ''
        self.master_logs_DB_password = ''

    def get_servers_info(self, url):
        """
            Parse the JSON response to get the login credential of 
            LogServer, BuildServer and MasterLogsDB.
            values are stored in class variables.            
        """
        logger.debug("CPE_ID list %s", url)

        logger.info("Server %s ", url)
        try:
            response = urllib2.urlopen(url)
            logger.info("response code from %s ==> %s ",url,str(response.getcode()))
            data = response.read().decode()
            #print('Retrieved', len(data), 'characters')
            servers = json.loads(data)
        except:
            logger.error("Error while getting json response from server %s ", url)
            servers = None
            return False

        for server in servers:
            logger.info("Server %s ", server)
            if server.get('serverType', None).lower() in ['yardlogserver','ftplogserver']:
                logger.info("Got LogServer server details")
                self.project_log_server_name = server.get('serverType', None)
                self.project_log_server_hostname = server.get('hostname', None)
                self.project_log_server_serverVersion = server.get('serverVersion', None)
                self.project_log_server_user = server.get('user', None)
                self.project_log_server_password = server.get('password', None)
                logger.info("project_log_server_hostname %s, project_log_server_serverVersion %s, project_log_server_user =%s, project_log_server_password =%s ",
                            self.project_log_server_hostname,self.project_log_server_serverVersion,self.project_log_server_user, self.project_log_server_password )

            elif server.get('serverType', None).lower() == 'buildserver':
                logger.info(" Got BuildServer  details")
                self.build_server_hostname = server.get('hostname', None)
                self.build_server_serverVersion = server.get('serverVersion', None)
                self.build_server_user = server.get('user', None)
                self.build_server_password = server.get('password', None)
                logger.info("build_server_hostname %s, build_server_serverVersion %s, build_server_user =%s, build_server_password =%s ",
                            self.build_server_hostname,self.build_server_serverVersion,self.build_server_user, self.build_server_password )

            elif server.get('serverType', None).lower() == 'logsdb':
                logger.info(" Got MasterLogsDB server details ")
                self.master_logs_DB_hostname = server.get('hostname', None)
                self.master_logs_DB_serverVersion = server.get('serverVersion', None)
                self.master_logs_DB_user = server.get('user', None)
                self.master_logs_DB_password = server.get('password', None)
                logger.info("master_logs_DB_hostname %s, master_logs_DB_serverVersion %s, master_logs_DB_user =%s, master_logs_DB_password =%s ",
                            self.master_logs_DB_hostname,self.master_logs_DB_serverVersion,self.master_logs_DB_user, self.master_logs_DB_password )
        return True

    def get_project_log_server_name(self):
        if self.project_log_server_name is None:
            logger.error("Don't have project_log_server_name")
        return self.project_log_server_name

    def get_project_log_server_hostname(self):
        if self.project_log_server_hostname is None:
            logger.error("Don't have project_log_server_hostname")
        return self.project_log_server_hostname

    def get_log_server_serverVersion(self):
        if self.log_server_serverVersion is None:
            logger.error("Don't have log_server_serverVersion")
        return self.log_server_serverVersion

    def get_log_server_user(self):
        if self.project_log_server_user == None:
            logger.error("Dont have log_server_user")
        return self.project_log_server_user

    def get_project_log_server_password(self):
        if self.project_log_server_password == None:
            logger.error("Don't have project_log_server_password")
        return self.project_log_server_password

    def get_build_server_hostname(self):
        if self.build_server_hostname == None:
            logger.error("Don't have build_server_hostname")
        return self.build_server_hostname

    def get_build_server_serverVersion(self):
        if self.build_server_serverVersion == None:
            logger.error("Don't have build_server_serverVersion")
        return self.build_server_serverVersion

    def get_build_server_user(self):
        if self.build_server_user == None:
            logger.error("Don't have build_server_user")
        return self.build_server_user

    def get_build_server_password(self):
        if self.build_server_password == None:
            logger.error("Don't have build_server_password")
        return self.build_server_password

    def get_master_logs_DB_hostname(self):
        if self.master_logs_DB_hostname == None:
            logger.error("Don't have master_logs_DB_hostname")
        return self.master_logs_DB_hostname

    def get_master_logs_DB_serverVersion(self):
        if self.master_logs_DB_serverVersion == None:
            logger.error("Don't have master_logs_DB_serverVersion")
        return self.master_logs_DB_serverVersion

    def get_master_logs_DB_user(self):
        if self.master_logs_DB_user == None:
            logger.error("Don't have master_logs_DB_user")
        return self.master_logs_DB_user

    def get_master_logs_DB_password(self):
        if self.master_logs_DB_password == None:
            logger.error("Don't have master_logs_DB_password")
        return self.master_logs_DB_password


    def get_SFTPserver_info(self, url):
        response = urllib2.urlopen(url)
        data = response.read().decode()
        #print('Retrieved', len(data), 'characters')

        try:
            Servers = json.loads(data)
        except:
            Servers = None
        logger.info("Sun %s %s ", type(Servers),Servers)
        for Server in Servers:
            logger.info("Sun %s %s ", type(Server),Server)
            if Server.get('serverType', None) == 'SFTPserver':
                print("\n!!====================  Got sftpserver server details =========================!!\n")
                logger.info(" Got sftpserver server details : %s ", Server['serverType'])
                return Server

    def get_BuildServer_info(self, url):
        response = urllib2.urlopen(url)
        data = response.read().decode()
        print('Retrieved', len(data), 'characters')

        try:
            Servers = json.loads(data)
        except:
            Servers = None
        logger.info("Sun %s %s ", type(Servers),Servers)
        for BuildServer in Servers:
            logger.info("Sun %s %s ", type(BuildServer),BuildServer)
            if BuildServer.get('serverType', None) == 'BuildServer':
                print("\n!!====================  Got BuildServer server details =========================!!\n")
                logger.info(" Got BuildServer  details : %s ", BuildServer['serverType'])
                return BuildServer

    def get_CPE_list(self, url):
        """
            Parse the JSON response to get CPE IDs and MAC ID.
            returns MAC ID and CPE ID List
        """
        logger.info("Get Device list from the url %s ", url)
        CPE_ID_list = []
        CPE_MAC_list = []
        DeviceList = []

        try:
            response = urllib2.urlopen(url)
            data = response.read().decode()
            DeviceList = json.loads(data)
        except:
            logger.error("Error getting response from server %s ",url)

        for Device in DeviceList:
            logger.debug(" Got Device details : %s ", Device['cpeid'])
            if Device.get('cpeid', None) != None:
                CPE_ID_list.append(str(Device['cpeid']))

            if Device.get('macid', None) != None:
                CPE_MAC_list.append(str(Device['macid']))

        logger.info("Number of devices %s", len(DeviceList))
        return DeviceList,CPE_ID_list,CPE_MAC_list
