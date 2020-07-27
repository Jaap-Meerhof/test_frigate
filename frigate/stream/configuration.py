import os
 
if 'TOPIC_PARTITIONS' in os.environ:
    TOPIC_PARTITIONS = int(os.environ['TOPIC_PARTITIONS'])
else:
    raise Exception("please declare environment variable 'TOPIC_PARTITIONS'")
 
if 'SUMO_TOOLS_HOME' in os.environ:
    SUMO_TOOLS_HOME = os.environ['SUMO_TOOLS_HOME']    
else:
    raise Exception("please declare environment variable 'SUMO_TOOLS_HOME'")

if 'SUMO_ROADNET_PATH' in os.environ:
    SUMO_ROADNET_PATH = os.environ['SUMO_ROADNET_PATH']    
else:
    raise Exception("please declare environment variable 'SUMO_ROADNET_PATH'")

if 'KAFKA_BROKER_URL_2' in os.environ:
    KAFKA_BROKER_URL_2 = os.environ['KAFKA_BROKER_URL_2']
else:
    raise Exception("please declare environment variable 'KAFKA_BROKER_URL_2'")

if 'ETA' in os.environ:
    ETA = float(os.environ['ETA'])
else:
    raise Exception("please declare environment variable 'ETA'")

# stream
#KAFKA_BROKER_URL_2 = 'kafka://localhost'
#ETA = 0.5


