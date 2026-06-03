.venv:
	python3 -m venv .venv

install: .venv
	.venv/bin/pip install -r requirements.txt

run:
	env $(shell cat .env | xargs) .venv/bin/python src/extraction.py

freeze:	
	.venv/bin/pip freeze > requirements.txt

PSQL=/Applications/Postgres.app/Contents/Versions/18/bin/psql

db-create:
	$(PSQL) -U ryansiebert -f sql/001_create_database.sql

db-migrate:
	$(PSQL) -U ryansiebert -d climatiq_pipeline -f sql/002_bronze_schema.sql

db-setup: db-create db-migrate

db-reset:
	$(PSQL) -U ryansiebert -d climatiq_pipeline -f sql/999_reset_bronze.sql
	$(PSQL) -U ryansiebert -d climatiq_pipeline -f sql/002_bronze_schema.sql

db-truncate:
	$(PSQL) -U ryansiebert -d climatiq_pipeline -c "TRUNCATE bronze.emission_factors, bronze.estimates RESTART IDENTITY;"