br:
	docker system prune -f
	docker image rm zookeeper_image
	docker build -t zookeeper_image .
	docker run -it --name=zookeeper_container zookeeper_image