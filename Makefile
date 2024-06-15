docker-run:
	docker-compose up -d

docker-down:
	docker-compose down

run:
	uvicorn app.main:app --reload

install-requirements:
	pip install -r requirements.txt
