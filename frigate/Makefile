rebuild:	
	$(info rebuilding ...)
	- docker stack rm frigate
	docker-compose build
	docker-compose push

start:	
	$(info starting ...)
	docker stack deploy -c docker-compose.yml frigate

stop:	
	$(info starting ...)
	docker stack rm frigate	

restart:
	$(info restarting ...)
	- docker stack rm frigate	
	docker stack deploy -c docker-compose.yml frigate

run:
	$(info running ...)
	curl -G 127.0.0.1:8010/run

run-stream:
	$(info running stream ...)
	curl -G 127.0.0.1:8010/stream

login-stream1:
	$(info logging in service container ...)
	docker exec -ti frigate_frigate-stream-1.1.$(docker service ps -f 'name=frigate_frigate-stream-1.1' frigate_frigate-stream-1 -q --no-trunc | head -n1) /bin/bash

logs-simulator0:
	clear
	docker service logs frigate_frigate-simulator-0 -f --tail 1000

logs-simulator1:
	clear
	docker service logs frigate_frigate-simulator-1 -f --tail 1000

logs-simulator2:
	clear
	docker service logs frigate_frigate-simulator-2 -f --tail 1000

logs-simulator3:
	clear
	docker service logs frigate_frigate-simulator-3 -f --tail 1000

logs-simulator4:
	clear
	docker service logs frigate_frigate-simulator-4 -f --tail 1000

logs-simulator5:
	clear
	docker service logs frigate_frigate-simulator-5 -f --tail 1000

logs-simulator6:
	clear
	docker service logs frigate_frigate-simulator-6 -f --tail 1000

logs-simulator7:
	clear
	docker service logs frigate_frigate-simulator-7 -f --tail 1000




logs-endpoint0:
	clear
	docker service logs frigate_frigate-endpoint-0 -f --tail 1000


logs-endpoint1:
	clear
	docker service logs frigate_frigate-endpoint-1 -f --tail 1000

logs-endpoint2:
	clear
	docker service logs frigate_frigate-endpoint-2 -f --tail 1000

logs-endpoint3:
	clear
	docker service logs frigate_frigate-endpoint-3 -f --tail 1000

logs-endpoint4:
	clear
	docker service logs frigate_frigate-endpoint-4 -f --tail 1000

logs-endpoint5:
	clear
	docker service logs frigate_frigate-endpoint-5 -f --tail 1000

logs-endpoint6:
	clear
	docker service logs frigate_frigate-endpoint-6 -f --tail 1000

logs-endpoint7:
	clear
	docker service logs frigate_frigate-endpoint-7 -f --tail 1000


logs-endpoint-proxy:
	clear
	docker service logs frigate_frigate-endpoint-proxy -f --tail 1000

logs-stream-proxy:
	clear
	docker service logs frigate_frigate-stream-proxy -f --tail 1000

logs-kafka-setup:
	clear
	docker service logs frigate_frigate-kafka-setup -f --tail 1000

logs-kafka:
	clear
	docker service logs frigate_frigate-kafka -f --tail 1000

logs-zookeeper:
	clear
	docker service logs frigate_frigate-zookeeper -f --tail 1000

logs-stream0:
	clear
	docker service logs frigate_frigate-stream-0 -f --tail 1000

logs-stream1:
	clear
	docker service logs frigate_frigate-stream-1 -f --tail 1000

logs-stream2:
	clear
	docker service logs frigate_frigate-stream-2 -f --tail 1000

logs-stream3:
	clear
	docker service logs frigate_frigate-stream-3 -f --tail 1000

logs-stream4:
	clear
	docker service logs frigate_frigate-stream-4 -f --tail 1000

logs-stream5:
	clear
	docker service logs frigate_frigate-stream-5 -f --tail 1000

logs-stream6:
	clear
	docker service logs frigate_frigate-stream-6 -f --tail 1000

logs-stream7:
	clear
	docker service logs frigate_frigate-stream-7 -f --tail 1000







monitor-stream0:
	watch "curl -G 127.0.0.1:6066/stats/ | python -m json.tool"

monitor-stream1:
	watch "curl -G 127.0.0.1:6067/stats/ | python -m json.tool"

graphite:
	# https://hub.docker.com/r/graphiteapp/graphite-statsd/
	# https://computingforgeeks.com/how-to-install-and-configure-graphite-on-ubuntu-18-04/
	# https://github.com/robinhood/faust/blob/c52677d6e3db6a2deb6fb1902b5a5b1d49bf085e/faust/sensors/statsd.py
	docker run -d  --name graphite  --restart=always  -p 81:80  -p 2003-2004:2003-2004  -p 2023-2024:2023-2024  -p 8125:8125/udp  -p 8126:8126  graphiteapp/graphite-statsd

