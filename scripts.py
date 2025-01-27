import subprocess
from pydantic import BaseModel
from typing import TypedDict
import fire
from loguru import logger

SCRIPTS: dict[str, str | list[str]] = {
    "code.format": "black .",
    "code.check": "mypy " ".",
    "code.test": "pytest tests",
    "env.export": "conda env export --no-builds -f environment.yml",
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
