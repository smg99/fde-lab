import logging
import sys
import structlog

def configure_logging(level: str = "INFO", machine_mode: bool = False):
    """Configure structured logging for the application."""
    
    # Set the standard logging level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # In machine mode, all logs MUST go to stderr to prevent polluting stdout JSON
    stream = sys.stderr if machine_mode else sys.stdout
    
    logging.basicConfig(
        format="%(message)s",
        stream=stream,
        level=numeric_level,
    )
    
    # Choose the renderer
    if machine_mode:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            renderer,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def get_logger(name: str):
    return structlog.get_logger(name)
