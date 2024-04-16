import os
import tempfile
from io import TextIOWrapper
import threading
from loguru import logger
import inspect
from functools import wraps
from typing import Optional, Callable
from datetime import datetime


def run_once(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return func(*args, **kwargs)
        else:
            return None

    wrapper.has_run = False
    return wrapper


class LogHandler:
    __instance = None
    __lock = threading.Lock()
    LEVELS = {
        "DEBUG": "debug",
        "INFO": "info",
        "WARNING": "warning",
        "ERROR": "error",
        "CRITICAL": "critical",
        "EXCEPTION": "exception",
        "TRACE": "trace",
    }

    def __new__(cls, *args, **kwargs):
        with cls.__lock:
            if cls.__instance is None:
                cls.__instance = super(LogHandler, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self, only_file: bool = False):
        self._setup_logging(only_file=only_file)
        self.log_file = None

    def _setup_logging(self, only_file: bool = False):
        if only_file:
            logger.remove()
        logger.add(
            "./logs/file_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD at HH:mm:ss} | module {extra[module_name]} | line {extra[lineno]} | function {extra[func_name]} | <bold>{level}</bold> | {message}",
            rotation="00:00",
            compression="zip",
            diagnose=True,
            retention="14 days"
        )
        self._configure_log_levels()

    def _configure_log_levels(self):
        context_logger = logger.bind()
        for level, item in {
            "ERROR": ('❌', "<red><bold>"),
            "WARNING": ('⚠️', "<yellow><bold>"),
            "INFO": ('i', "<blue><bold>"),
            "DEBUG": ('🐞', "<green><bold>"),
            "TRACE": ('🔮', "<cyan><bold>"),
        }.items():
            context_logger.level(name=level, icon=item[0], color=item[1])
        try:
            context_logger.level(name="EXCEPTION", no=50, icon='🔥', color="<magenta><bold>")
        except Exception:
            pass

    def sort_logs(self, temp=False):
        today = datetime.strftime(datetime.now(), "%Y-%m-%d")
        self.log_file = f"./logs/file_{today}.log"
        log_levels = {level: [] for level in self.LEVELS}
        with open(self.log_file, "r") as f:
            lines = f.readlines()
        for line in lines:
            for level in log_levels.keys():
                if level in line:
                    log_levels[level].append(line)
                    break

        def write(cursor: TextIOWrapper):
            for level, logs in log_levels.items():
                cursor.write(f"{level:-^80}\n")
                cursor.write("\n".join(logs))
                cursor.write("\n")

        if temp:
            with tempfile.NamedTemporaryFile(dir=os.path.join(os.getcwd(), "logs"), mode="w", delete=False, prefix="sorted_", suffix=".log") as f:
                write(f)
                self.log_file = f.name
        else:
            with open(self.log_file, "w") as f:
                write(f)

    def log_call(self, func=None, *, message: Optional[str] = None, level="INFO", sorted_logs: bool = False) -> Callable:
        """Decorator to log function call"""

        def decorator(func):
            func_name = func.__name__

            @wraps(func)
            def wrapper(*args, **kwargs):
                if sorted_logs:
                    self.sort_logs(temp=True)
                @run_once
                def inner_wrapper():
                    self.log_it(func, message, level, func_name=func_name)
                inner_wrapper()
                return func(*args, **kwargs)

            return wrapper

        if func is None:
            return decorator
        else:
            return decorator(func)

    def _remove_duplication(self):
        """Remove duplicate lines in log file"""
        # Read the log file and remove duplicate lines
        with open(self.log_file, "r") as f:
            lines = f.read().split("\n")

        # Remove duplicate lines
        for i in range(len(lines) - 1):
            if lines[i] == lines[i + 1]:
                lines[i] = ""

        # Write the updated log file
        with open(self.log_file, "w") as f:
            f.write("\n".join(lines))
    def log_it(self, func, message=None, level="INFO", func_name=None):
        """Log a function call"""
        LEVEL = level.strip().upper()

        # Check if level is valid
        if LEVEL not in self.LEVELS:
            raise ValueError(f"Invalid level: {level}")

        # Set the function name if not provided
        if func_name is None:
            func_name = inspect.getsourcelines(func)[0][0][4:].replace("\n", "")

        # Basic config
        module_name = inspect.getmodule(func).__name__
        line_number = inspect.getsourcelines(func)[1]
        default_message = f"Call to '{func_name}' at line {line_number}"
        log_message: str = message or default_message

        # Binding for customization
        context_logger = logger.bind(func_name=func_name, module_name=module_name, lineno=line_number)
        get_level = self.LEVELS[LEVEL]

        # Log the message
        level_attribute = getattr(context_logger, get_level)
        level_attribute(log_message)

