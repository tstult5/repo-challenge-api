
from client.sql_client import db_session
from dto.user_dto import User as UserDto

import logging

class UserService:

    def __init__(self):
        self.logger = logging.getLogger('divvy_dose_app')
