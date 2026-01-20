import os

from dotenv import load_dotenv


def load_environment_variables() -> None:
    file_path = os.path.abspath(__file__)
    parent_directory = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(file_path)))))
    env_path = os.path.join(parent_directory, ".env")
    load_dotenv(env_path, override=True)


def read_environment_variable(var: str) -> str:
    load_environment_variables()
    value = os.getenv(var)
    return value
