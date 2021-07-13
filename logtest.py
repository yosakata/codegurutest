import logging

format_string = "%(asctime)s [%(levelname)s] - %(filename)s : %(message)s"

logging.debug("Eearly debug message")

logging.basicConfig(filemode="w", filename="example.log", fromat=format_string, level=logging.DEBUG)

logging.debug("Debug message %s %s", "a", 1)
logging.info("Info message")
logging.warning("Warning message")
logging.error("Error message")
logging.critical("Critical message")

print("Ran entire script")
