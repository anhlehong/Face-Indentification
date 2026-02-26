from utils.logger import setup_logging
import logging
from services.user_service import user_service

setup_logging()
logger = logging.getLogger(__name__)


def main():
    user_service.create_from_json("data/users_data.json")


if __name__ == "__main__":
    main()
