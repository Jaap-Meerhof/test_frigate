pbr:
	docker system prune -f
	docker image rm kafka_image
	docker build -t kafka_image .
	docker run -it --name=kafka_container kafka_image

br:	
	docker build -t kafka_image .
	docker run -it --name=kafka_container kafka_image