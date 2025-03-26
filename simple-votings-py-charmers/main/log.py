import logging 

model_format="%(asctime)s %(levelname)s %(message)s"

logging.basicConfig(
    filename="Output.log",
    level=logging.INFO,
    format=model_format
)