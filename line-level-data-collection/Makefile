current_project_path := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
current_dir_name := $(shell basename ${current_project_path})
root_project_path := $(shell realpath '${current_project_path}/../')
python_package_name := $(current_dir_name)
image_name := "lambda/${current_dir_name}:latest"
external_dependency_path := $(current_project_path)/'external'

setup_python_env:
	pip install -r requirements.txt
	pip install -r extra_requirements.txt
	pip install -r dev_requirements.txt
	cd "${current_project_path}" && pip install . && cd -
	cd "${root_project_path}/out/openapi/python" && python setup.py install && cd -


package:
	# this command is for debugging only, it will package everything and put them into the <current_project>/.serverless folder
	# clear cache
	SLS_DEBUG=* sls requirements cleanCache --stage qa
	SLS_DEBUG=* serverless package --verbose --stage qa

########### test ########################
local:
	DOCKER_BUILDKIT=1 docker build --ssh default -f "${current_project_path}/docker/Dockerfile" "${current_project_path}" -t local-lambda:latest
	DOCKER_BUILDKIT=1 docker build -f "${current_project_path}/docker/awscli.Dockerfile" "${current_project_path}" -t local-aws-cli:latest
	docker-compose -f $(current_project_path)/docker-compose.yml up -d
	# wait for local stack to be ready
	cd $(current_project_path) && bash -c "script/wait-for-postgres.sh"
	# wait for postgres to be ready
	cd $(current_project_path) && bash -c "script/wait-for-it.sh localhost:4566"

	FLYWAY_DB_URL='jdbc:postgresql://localhost:5432/line_level_data_collection' \
	FLYWAY_USER='db_user' \
	FLYWAY_PASSWORD='test' \
 	flyway -locations="filesystem:${current_project_path}/db_migration/sql" \
		  -configFiles="${current_project_path}/db_migration/conf/flyway.conf" \
		  migrate

# run this if you know your images are up-to-date
# or when you change some config of docker-compose that doesn't affect the images.
local_quick:
	docker-compose -f $(current_project_path)/docker-compose.yml up -d
	curl http://localhost:4566/health | jq

# use reboot to clean data.
# but you might need to rerun-schema setup again
local_clean:
	docker-compose restart postgres
	docker-compose restart localstack

remove_dangling_image:
	docker rmi $(shell docker images -f "dangling=true" -q)

remove_stopped_containers:
	docker container prune

test: local
	docker exec local-lambda /bin/bash -c "pip install -e . && pytest tests/"

test_quick:
	docker exec local-lambda /bin/bash -c "pip install -e . && pytest --capture=no tests/"

test_and_shut_down: test
	docker-compose down

shutdown_stack:
	docker-compose down

clean_external_dep:
	rm -rf $(external_dependency_path)

core_dep: clean_external_dep
	mkdir -p $(external_dependency_path)/gn5-client/
	rsync -av --delete "${root_project_path}/out/openapi/python/" $(external_dependency_path)/gn5-client/

build_release_docker:
	DOCKER_BUILDKIT=1 docker build --ssh default -f "${current_project_path}/release/Dockerfile" "${current_project_path}" -t local-lambda:latest
