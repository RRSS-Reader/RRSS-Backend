import subprocess
from pydantic import BaseModel
from typing import TypedDict
import fire
from loguru import logger
from sys import stdout

logger.remove()

# Add a new sink with a simple format: [time] [level] message
logger.add(
    stdout,
    format=">>> <green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}",
    level="DEBUG",
)

SCRIPTS: dict[str, str | list[str]] = {
    "code.format": "black .",
    "code.type_check": "mypy " ".",
    "code.test": "pytest tests",
    "code.check": [
        "command:code.format",
        "command:code.type_check",
        "command:code.test",
    ],
    "env.export": "conda env export --no-builds -f environment.yml",
    "env.update": "conda update --update-all",
}


def run_command(name: str):
    global SCRIPTS

    # find received command from terminal
    try:
        command: str | list[str] = SCRIPTS[name]
    except KeyError as e:
        logger.error(f"Command not found: {name}")
        exit(-1)

    # get a list of command to execute
    command_list: list[str]
    if isinstance(command, str):
        command_list = [command]
    else:
        command_list = command

    for c in command_list:
        if c.startswith("command:"):
            logger.info(f"Try running nested command: {c}")
            run_command(c[8:])
            print("\n")
        else:
            # resolve command and run
            res = subprocess.run(c)
            if res.returncode != 0:
                logger.error(
                    "Script execution stopped since non-zero return code detected"
                )
                exit(res.returncode)


if __name__ == "__main__":
    fire.Fire(run_command)
