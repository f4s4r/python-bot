include .env
export


# HELP =================================================================================================================
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help
help: ## Display this help screen
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

up: ### Run docker-compose
	docker-compose up --build -d && docker-compose logs -f
.PHONY: up

down: ### Down docker-compose
	docker-compose down --remove-orphans
.PHONY: down

rm-volume: ### remove docker volume
	docker volume rm python-bot_db-data
.PHONY: rm-volume
