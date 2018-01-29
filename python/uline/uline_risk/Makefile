NAME = uline_risk


dev: build
	docker run --name $(NAME) --detach --env-file dev.env --volume /tmp/$(NAME):/workdir/log --publish 8835:80 $(NAME)


spd: build
	docker run --name $(NAME) --detach --env-file spd.env --volume /tmp/$(NAME):/workdir/log --publish 8835:80 $(NAME)


build: clean
	docker build -t $(NAME) .


clean:
	find . -type f -name '*.py[co]' -delete
	find . -type d -name '__pycache__' -delete
