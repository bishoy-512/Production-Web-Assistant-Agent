from config.settings import get_settings, LogRenderer, Environment
from pathlib import Path
from concurrent_log_handler import ConcurrentRotatingFileHandler
from typing import List, Any
import structlog
import logging
import sys
import os


settings = get_settings()

def get_or_create_log_file_path():
    env_name = settings.APP_ENV.value
    
    log_file_path = Path(
        settings.LOG_DIR,
        f"{env_name}-log.json"
    )
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    return log_file_path

def setup_logging():
    log_level = settings.LOG_LEVEL
    
    # Console Formatter
    console_formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.dev.ConsoleRenderer(
            colors= settings.LOG_RENDER == LogRenderer.CONSOLE
        )
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    
    # File Formatter
    json_formatter = structlog.stdlib.ProcessorFormatter(
        processor= structlog.processors.JSONRenderer()
    )
    file_handler = ConcurrentRotatingFileHandler(
        get_or_create_log_file_path(),
        mode="a",
        encoding="utf-8",
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(json_formatter)
    

    logging.basicConfig(
        format="%(message)s",
        level=log_level,
        handlers=[file_handler, console_handler],
        force=True,
    )
    
    shared_processors = get_structlog_processors(
        include_file_info=settings.APP_ENV
        in [Environment.STAGING, Environment.PRODUCTION]
    )

    # Configure structlog based on environment
    structlog.configure(
        processors=[
            *shared_processors,
            sort_event_keys,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    
    
def get_structlog_processors(include_file_info: bool = True):

    # Set up processors that are common to both outputs
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.contextvars.merge_contextvars,
    ]
    
    if include_file_info:
        processors.append(
            structlog.processors.CallsiteParameter(
                {
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.MODULE,
                    structlog.processors.CallsiteParameter.PATHNAME,
                }
            )
        )

    # Add environment info
    processors.append(
        lambda _, __, event_dict: {**event_dict, "environment": str(settings.APP_ENV)}
    )

    return processors


def sort_event_keys(_, __, event_dict):
    priority_keys = [
        "timestamp",
        "level",
        "event",
        "logger",
        "environment",
        "pathname",
        "filename",
        "module",
        "func_name",
        "lineno",
    ]

    ordered = {}

    # Add priority keys first
    for key in priority_keys:
        if key in event_dict:
            ordered[key] = event_dict.pop(key)

    # Add remaining keys alphabetically
    for key in sorted(event_dict):
        ordered[key] = event_dict[key]

    return ordered


# Initialize logging
setup_logging()

# Create logger instance
logger = structlog.get_logger()


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )
    print(get_or_create_log_file_path())
    
    logger.info(
        "logging_initialized %s",
        "Adham",
        environment=str(settings.APP_ENV),
        log_level=str(settings.LOG_LEVEL),
        log_renderer=str(settings.LOG_RENDER),
        debug=settings.DEBUG,
    )
    logger.info(
        "logging_initialized",
        environment=str(settings.APP_ENV),
        log_level=str(settings.LOG_LEVEL),
        log_renderer=str(settings.LOG_RENDER),
        debug=settings.DEBUG,
    )
    logger.debug(
        "test_debug",
        environment=str(settings.APP_ENV),
        log_level=str(settings.LOG_LEVEL),
        log_renderer=str(settings.LOG_RENDER),
        debug=settings.DEBUG,
    )
    logger.warning(
        "test_warning",
        environment=str(settings.APP_ENV),
        log_level=str(settings.LOG_LEVEL),
        log_renderer=str(settings.LOG_RENDER),
        debug=settings.DEBUG,
    )
    logger.error(
        "test_error",
        environment=str(settings.APP_ENV),
        log_level=str(settings.LOG_LEVEL),
        log_renderer=str(settings.LOG_RENDER),
        debug=settings.DEBUG,
    )


if __name__ == "__main__":
    main()
