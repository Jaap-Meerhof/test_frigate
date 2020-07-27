import os

if 'SUMO_TOOLS_HOME' in os.environ:
    SUMO_TOOLS_HOME = os.environ['SUMO_TOOLS_HOME']    
else:
    raise Exception("please declare environment variable 'SUMO_TOOLS_HOME'")

if 'SUMO_ROADNET_PATH' in os.environ:
    SUMO_ROADNET_PATH = os.environ['SUMO_ROADNET_PATH']    
else:
    raise Exception("please declare environment variable 'SUMO_ROADNET_PATH'")

if 'ENDPOINT_SERVER_HOST' in os.environ:
    ENDPOINT_SERVER_HOST = os.environ['ENDPOINT_SERVER_HOST']    
else:
    raise Exception("please declare environment variable 'ENDPOINT_SERVER_HOST'")

if 'ENDPOINT_SERVER_PORT' in os.environ:
    ENDPOINT_SERVER_PORT = os.environ['ENDPOINT_SERVER_PORT']    
else:
    raise Exception("please declare environment variable 'ENDPOINT_SERVER_PORT'")

if 'KAFKA_BROKER_URL' in os.environ:
    KAFKA_BROKER_URL = os.environ['KAFKA_BROKER_URL']    
else:
    raise Exception("please declare environment variable 'KAFKA_BROKER_URL'")

if 'STREAM_SERVICE_WEB_URL' in os.environ:
    STREAM_SERVICE_WEB_URL = os.environ['STREAM_SERVICE_WEB_URL']    
else:
    raise Exception("please declare environment variable 'STREAM_SERVICE_WEB_URL'")





#ENDPOINT_SERVER_HOST = "localhost"
#ENDPOINT_SERVER_PORT = 5000 

