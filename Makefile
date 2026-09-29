PYTHON = python

.DEFAULT_GOAL := help

.PHONY: help run migrate migrations shell collectstatic createsuperuser \
        test lint deploy logs nginx-logs

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------
help:
	@echo ""
	@echo "  ahadmix-web — available make targets"
	@echo ""
	@echo "  Development"
	@echo "  -----------"
	@echo "  run              Start the Django development server"
	@echo "  migrate          Apply database migrations"
	@echo "  migrations       Create new migration files"
	@echo "  shell            Open the Django shell"
	@echo "  collectstatic    Collect static files"
	@echo "  createsuperuser  Create a Django superuser"
	@echo "  test             Run the test suite"
	@echo "  lint             Run ruff linter"
	@echo ""
	@echo "  Deployment"
	@echo "  ----------"
	@echo "  deploy           SSH to server and run deploy.sh"
	@echo "  logs             Stream Gunicorn service logs from server"
	@echo "  nginx-logs       Stream Nginx error log from server"
	@echo ""

# ---------------------------------------------------------------------------
# Development
# ---------------------------------------------------------------------------
run:
	$(PYTHON) manage.py runserver

migrate:
	$(PYTHON) manage.py migrate

migrations:
	$(PYTHON) manage.py makemigrations

shell:
	$(PYTHON) manage.py shell

collectstatic:
	$(PYTHON) manage.py collectstatic --noinput

createsuperuser:
	$(PYTHON) manage.py createsuperuser

test:
	$(PYTHON) manage.py test

lint:
	ruff check .

# ---------------------------------------------------------------------------
# Deployment
# ---------------------------------------------------------------------------
deploy:
	ssh ahadmix-server 'cd /var/local/ahadmix/ahadmix-web && bash deploy/scripts/deploy.sh'

logs:
	ssh ahadmix-server 'journalctl -u ahadmix -f'

nginx-logs:
	ssh ahadmix-server 'tail -f /var/log/nginx/error.log'
