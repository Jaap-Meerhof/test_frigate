import os

OUTPUT_FOLDER = "/output"

if 'NUM_STREAM_SERVERS' in os.environ:
    NUM_STREAM_SERVERS = int(os.environ['NUM_STREAM_SERVERS'])
else:
    raise Exception("please declare environment variable 'NUM_STREAM_SERVERS'")

if 'GRAPHITE_HOST' in os.environ:
    GRAPHITE_HOST = os.environ['GRAPHITE_HOST']
else:
    raise Exception("please declare environment variable 'GRAPHITE_HOST'")

if 'GRAPHITE_PORT' in os.environ:
    GRAPHITE_PORT = int(os.environ['GRAPHITE_PORT'])
else:
    raise Exception("please declare environment variable 'GRAPHITE_PORT'")

# Statsd metrics to monitor
STATSD_METRICS = [] 
for i in range(NUM_STREAM_SERVERS):
    STATSD_METRICS.append( f"stats.gauges.frigate-stream.frigate-stream-{i}.process_vehicle_arrival" )

