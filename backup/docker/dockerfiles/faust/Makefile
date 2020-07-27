pbr:
	docker system prune -f
	docker image rm faust_image
	docker build -t faust_image .
	docker run -it --name=faust_container faust_image

br:	
	docker build -t faust_image .
	docker run -it --name=faust_container faust_image