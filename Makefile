.DEFAULT_GOAL := help
.PHONY: *

##@ Dev
dev: ## Build docker containers
	docker-compose up -d --build

clean: ## Remove docker containers
	docker-compose down -v

docs: ## Open swagger docs
	open http://localhost:8004/docs


##@ DB
add-migration: ## Create migration. Usage make add-migration name=""
	@test -n "$(name)" || (echo 'A name must be defined for the migration. Ex: make add-migration name=init' && exit 1)
	docker-compose exec web alembic revision --autogenerate -m "$(name)"

migrate: ## Apply alembic migrations
	docker-compose exec web alembic upgrade head

##@ Test
test: ## Run tests
	pytest

##@ Lint
check: ## mypy, flake8m, isort and black checks
	mypy ./app ./tests
	flake8 ./app ./tests --max-line-length=90
	isort ./app ./tests
	black ./app ./tests

##@ Misc
logs: ## Get web logs
	docker-compose logs web

install: ## Install python dependencies
	pip install -r requirements.txt

freeze: ## Save current dependencies to requirements.txt
	pip-compile

help: ## Help
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)