from services.identity_service import identity_service
from utils.logger import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)


def main():
    identity_service.register_from_json("data/users_data.json")


if __name__ == "__main__":
    main()
