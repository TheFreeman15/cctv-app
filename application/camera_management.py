from passlib.context import CryptContext
import utils.database as database
from utils.exceptions import *
import json
from functools import wraps
from datetime import datetime
from .authentication import LoginHandler
from .service import audit_log



config = {"dialect": "mysql", "username": "root", "password": "cctv-rootpass", "host": "mysql", "port": "3306", "db_name": "cctvdb"}
db = database.DatabaseResource(config)


def __init__():
    '''
    Initialize the camera management module
    '''
    pass

def list_all_cameras(auth_data):
    return True