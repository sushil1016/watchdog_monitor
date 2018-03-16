from ConfigParser import SafeConfigParser

def getDecoderConfigInfo():
    parser = SafeConfigParser()
    parser.read('config.cfg')
    print parser.get('Decoder', 'PathToVersionTextFile')
    print parser.get('Decoder', 'VersionStringName')
    print parser.get('Decoder', 'CURFilePath')
    print parser.get('Decoder', 'DefaultCPEID')
    print parser.get('Decoder', 'DefaultOffset')
    print parser.get('Decoder', 'LogstashPath')
    
getDecoderConfigInfo()