### How to set up the project

```shell
# this will configure the local python version
# https://realpython.com/intro-to-pyenv/#specifying-your-python-version
# this will pick up python version from .python-version
pyenv local
pyenv virtualenv lldc
pyenv activate lldc
make setup_python_env
```

### intention of different requirement files and folders

* docker: folder to store Dockerfiles for integration tests.
* script: folder to store scripts useful for integration tests.
* vendor: storing libraries that cannot be easily installed via requirements.txt like pycopg2. It will be copy to the
  dependency folder before uploading to aws
* dev_requirements.txt: store dependencies like pytest which is not used by the production env
* extra_requirements.txt: store dependencies that are needed by cannot be easily deployed in a Zip file format for
  lambda. For example, pycopg2 is needed by cannot be directly specified in requirements.txt, we'll put the dependency
  here because the integration test suite can install this.

### IDE setup

* You will be better off using different projects to access line-level-data-collection folder which needs python3.7 and
  python_playground which uses poetry and python3.10