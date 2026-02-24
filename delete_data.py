from database.user_repository import user_repo
from utils.logger import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

user_repo.delete_all()
