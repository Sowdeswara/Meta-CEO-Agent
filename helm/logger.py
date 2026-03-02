"""
Logging configuration for HELM v2.0
Production-grade logging with structured output
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
import json


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_data)


class Logger:
    """Centralized logging configuration - Singleton pattern"""
    
    _instance = None
    _loggers = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.log_dir = Path(__file__).parent.parent / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Standard formatter
        self.std_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # JSON formatter for file
        self.json_formatter = JSONFormatter()
        
        self._initialized = True
    
    def get_logger(
        self, 
        name: str, 
        level: int = logging.INFO,
        use_json: bool = False
    ) -> logging.Logger:
        """Get or create logger instance"""
        
        if name in self._loggers:
            return self._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Remove existing handlers to prevent duplicates
        logger.handlers.clear()
        logger.propagate = False
        
        # Console handler (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(self.std_formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_file = self.log_dir / f"{name}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        formatter = self.json_formatter if use_json else self.std_formatter
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        self._loggers[name] = logger
        return logger


# Convenience function
def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Get logger instance"""
    return Logger().get_logger(name, level)
