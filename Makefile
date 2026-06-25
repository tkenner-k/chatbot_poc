run-docker-compose:
	uv sync
	docker compose up --build

clean-notebook-outputs:
	python3 -m jupyter nbconvert --clear-output --inplace notebooks/*/*.ipynb
	