from __future__ import annotations
from loguru import logger
import inspect
from functools import wraps
from typing import Optional, Callable
from datetime import datetime


LEVELS = {
    "DEBUG": "debug",
    "INFO": "info",
    "WARNING": "warning",
    "ERROR": "error",
    "CRITICAL": "critical",
    "EXCEPTION": "exception",
    "TRACE": "trace",
}

def sort_logs():
    today = datetime.strftime(datetime.now(), "%Y-%m-%d")
    log_file = f"file_{today}.log"
    log_levels = {
        "DEBUG": [],
        "INFO": [],
        "WARNING": [],
        "ERROR": [],
        "CRITICAL": [],
        "EXCEPTION": [],
        "TRACE": []
    }
    with open(log_file, "r") as f:
        lines = f.readlines()
    for line in lines:
        for level in log_levels.keys():
            if level in line:
                log_levels[level].append(line)
                break
    with open(log_file, "w") as f:
        for level, logs in log_levels.items():
            f.write(f"{level:-^80}\n")
            f.write("\n".join(logs))
            f.write("\n")


def log_it(func, message=None, level="INFO", func_name=None):
    """Log a function call"""
    LEVEL = level.strip().upper()
    if LEVEL not in LEVELS:
        raise ValueError(f"Invalid level: {level}")
    if func_name is None:
        func_name = inspect.getsourcelines(func)[0][0][4:].replace("\n", "")
    module_name = inspect.getmodule(func).__name__
    line_number = inspect.getsourcelines(func)[1]
    default_message = f"Call to '{func_name}' at line {line_number}"
    log_message = message or default_message
    logger.add(f"file_{{time:YYYY-MM-DD}}.log",
               format="{time:YYYY-MM-DD at HH:mm:ss} "
                      "| module {extra[module_name]} "
                      "| line {extra[lineno]} "
                      "| function {extra[func_name]} "
                      "| <bold>{level}</bold> "
                      "| {message}",
               rotation="00:00",
               compression="zip",
               diagnose=True,
               retention="14 days"
               )
    context_logger = logger.bind(func_name=func_name, module_name=module_name, lineno=line_number)
    context_logger.level(name="ERROR", icon='❌', color="<red><bold>")
    context_logger.level(name="WARNING", icon='⚠️', color="<yellow><bold>")
    context_logger.level(name="INFO", icon='i', color="<blue><bold>")
    context_logger.level(name="DEBUG", icon='🐞', color="<green><bold>")
    context_logger.level(name="TRACE", icon='🔮', color="<cyan><bold>")
    try:
        context_logger.level(name="EXCEPTION", no=50, icon='🔥', color="<magenta><bold>")
    except Exception:
        pass
    get_level = LEVELS[LEVEL]
    level_attribute = getattr(context_logger, get_level)
    level_attribute(log_message)


def log_call(func=None, *, message: Optional[str] = None, level="INFO", sorted_logs: bool = False) -> Callable:
    """Decorator to log function call"""

    def decorator(func):
        func_name = func.__name__
        @wraps(func)
        def wrapper(*args, **kwargs):
            log_it(func, message, level, func_name=func_name)
            return func(*args, **kwargs)

        return wrapper

    if sorted_logs:
        try:
            sort_logs()
        except Exception as e:
            logger.exception(f"Failed to sort logs with error: {e}")
    if func is None:
        return decorator
    else:
        return decorator(func)


