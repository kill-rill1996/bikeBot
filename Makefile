up-dev:
	docker compose -f docker-compose.dev.yml up --build

up-prod:
	sudo docker compose -f docker-compose.prod.yml up --build

up-prod-d:
	sudo docker compose -f docker-compose.prod.yml up --build -d

down-prod:
	sudo docker compose -f docker-compose.prod.yml down