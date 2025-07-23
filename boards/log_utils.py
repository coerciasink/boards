import os
import logging
from datetime import date

def setup_logger(name=None):
    today = date.today().isoformat()  # e.g., '2025-07-16'
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    log_file_path = os.path.join(logs_dir, f"{today}.log")

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if already set
    if not logger.handlers:
        # File handler
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8", mode='a')
        file_handler.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


# def log_function_call(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         logger.info(f"Entering function: {func.__name__}")
#         return func(*args, **kwargs)
#     return wrapper

# def auto_log_all_functions_in_module(namespace):
#     for name, obj in namespace.items():
#         if inspect.isfunction(obj):
#             namespace[name] = log_function_call(obj)

# auto_log_all_functions_in_module(globals())
# auto_log_all_functions_in_module(vars(boards))
