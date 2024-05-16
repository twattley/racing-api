import logging

logging.basicConfig(
    format="%(asctime)s - %(levelname)-8s [%(filename)s:%(lineno)s] - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)

logger = logging.getLogger(__name__)
