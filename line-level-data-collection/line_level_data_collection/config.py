import os
from pathlib import Path

project_root = Path(__file__).parent.parent


class ProjectConfig:
    def __init__(self, env="local"):
        self.env = env
        self.content = {
            "database": {
                "database_name": os.environ["DATABASE_NAME"],
                "username": os.environ["USER_NAME"],
                "password": os.environ["PASSWORD"],
                "host": os.environ["HOST"],
                "port": os.environ["PORT"]
            }
        }

    def get_config(self):
        return self.content
