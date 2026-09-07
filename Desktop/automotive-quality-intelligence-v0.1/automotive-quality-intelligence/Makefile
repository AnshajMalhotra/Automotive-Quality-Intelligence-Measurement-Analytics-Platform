up:
	docker compose up -d --build

down:
	docker compose down

reset:
	docker compose down -v
	docker compose up -d --build

logs:
	docker compose logs -f

seed:
	python generator/generate_data.py --rows 25000 --mode api --endpoint http://localhost:8000/measurements/batch

stream:
	python generator/generate_data.py --rows 500 --mode nodered --endpoint http://localhost:1880/ingest/measurement --delay-ms 100
