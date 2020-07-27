createt :	
	$(info KAFKA_HOME=$(KAFKA_HOME))
	$(info TOPIC_PARTITIONS=$(TOPIC_PARTITIONS))
	$(info creating kafka topics ...)	
	$(KAFKA_HOME)/bin/kafka-topics.sh --create --zookeeper frigate-zookeeper:2181 --replication-factor 1 --partitions $(TOPIC_PARTITIONS) --topic qtable-entry-init-topic 
	$(KAFKA_HOME)/bin/kafka-topics.sh --create --zookeeper frigate-zookeeper:2181 --replication-factor 1 --partitions $(TOPIC_PARTITIONS) --topic qtable-entry-update-topic 
	$(KAFKA_HOME)/bin/kafka-topics.sh --create --zookeeper frigate-zookeeper:2181 --replication-factor 1 --partitions $(TOPIC_PARTITIONS) --topic vehicle-entry-init-topic 
	$(KAFKA_HOME)/bin/kafka-topics.sh --create --zookeeper frigate-zookeeper:2181 --replication-factor 1 --partitions $(TOPIC_PARTITIONS) --topic vehicle-status-topic 
	$(KAFKA_HOME)/bin/kafka-topics.sh --create --zookeeper frigate-zookeeper:2181 --replication-factor 1 --partitions $(TOPIC_PARTITIONS) --topic vehicle-arrival-topic 
	$(KAFKA_HOME)/bin/kafka-topics.sh --create --zookeeper frigate-zookeeper:2181 --replication-factor 1 --partitions $(TOPIC_PARTITIONS) --topic edge-change-topic 
	#$(KAFKA_HOME)/bin/kafka-topics.sh --create --zookeeper frigate-zookeeper:2181 --replication-factor 1 --partitions $(TOPIC_PARTITIONS) --topic stream-service-app-qtable-changelog
	#$(KAFKA_HOME)/bin/kafka-topics.sh --create --zookeeper frigate-zookeeper:2181 --replication-factor 1 --partitions $(TOPIC_PARTITIONS) --topic stream-service-app-vehicle-table-changelog
	$(info waiting 60 s)	
	sleep 60 
	$(info start Python HTTP server at 8080)	
	python3 -m http.server 8080 --bind 0.0.0.0 
	$(info exited python3 HTTP server!)	
