from passlib.context import CryptContext
import jwt
import utils.database as database
from utils.exceptions import *
from datetime import datetime,timedelta
import redis
import json
from functools import wraps
import os
from logger import logger

config = json.loads(os.getenv('DB_CONNECTION_STRING', {}))

db = database.DatabaseResource(config)


SECRET_KEY = os.getenv('SECRET_KEY','')
ALGORITHIM =  os.getenv('ALGORITHIM','HS256')

class LoginHandler():
    def __init__(self):
        
        self.SECRET_KEY = SECRET_KEY
        self.ALGORITHM = ALGORITHIM
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 10
        self.REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 1 # 1 day
        self.context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.conn = None
        self.redis_client = None

    def create_redis_client(self):
        redis_client = redis.Redis(host='redis', port=6379,decode_responses=True)
        self.redis_client = redis_client
        return redis_client

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def create_refresh_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.REFRESH_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
    
    def hash_password(self,plain_password):
        return self.context.hash(plain_password)

    def verify_password(self,password_hashed: str, plain_password: str):
        return self.context.verify(plain_password,password_hashed)
    
    
    def login_user(self, email, plain_password,refresh_token):
        # Initialize a DB session if one is not created
        if self.conn is None:
            with db.session() as conn:
                
                existing_user = conn.query(database.User).filter(database.User.email == email).first()
                if existing_user is None:
                    logger.info(f"User with email {email} does not exist!")
                    raise Error(status_code=400,details="User does not exist!")
                
                self.create_redis_client()
                rc = self.redis_client
                # If refresh token is provided. it will be used to validate the user

                data = {"user_id": existing_user.id,"user_name": existing_user.name, "user_email": existing_user.email, "user_role": existing_user.roles[0].name, "user_rank": existing_user.roles[0].rank}
                refresh_token_key = f"refresh_token:{existing_user.email}"
                access_token_key = f"user_token:{existing_user.email}"
                if refresh_token:
                    try:
                        payload = jwt.decode(refresh_token,SECRET_KEY,ALGORITHIM)
                        if payload["user_email"] != email:
                            raise Error(status_code=400,details="Invalid token/user")
                        refresh_token_data = rc.get(f"refresh_token:{email}")
                        if refresh_token_data is None:
                            raise Error(status_code=401,details="Invalid refresh token!")
                    except jwt.ExpiredSignatureError:
                        logger.info(f"Refresh token for user {email} has expired!")
                        raise Error(status_code=401, details="Token expired") 
                    except Exception as e:
                        raise Error(status_code=401,details="Invalid token!")
                else:
                    # Validate if the password matches the hash using passlib verify
                    valid_password = self.verify_password(existing_user.hashed_password, plain_password)
                    if not valid_password:
                        raise Error(status_code=400,details="Incorrect password!")
                    refresh_token = self.create_refresh_token(data)
                    data["token_type"] = "refresh"
                    data["token"] = refresh_token
                    rc.setex(refresh_token_key,self.REFRESH_TOKEN_EXPIRE_MINUTES * 60, json.dumps(data))

                
                data.pop("token", None)
                user_token = self.create_access_token(data)
                data["token_type"] = "access"
                rc.setex(access_token_key,self.ACCESS_TOKEN_EXPIRE_MINUTES * 60,json.dumps(data))
                
                # remove token and token_type from data
                data.pop("token", None)
                data.pop("token_type", None)
                
                
                
                return {"message": "Login sucessful", "access_token": user_token,"refresh_token": refresh_token, "data": data}



                
                
        pass


    @classmethod
    def authenticate_user(cls,func):
        '''
        Decorator classmethod for authenticating all requests
        '''
        @wraps(func)
        async def wrapper(*args,**kwargs):
            if 'request' not in kwargs:
                raise Error(status_code=500,details="No request details found!")
            request = kwargs["request"]
            token = request.headers.get("token")
            if not token:
                raise Error(status_code=401, details="Token not found!")
            
            try:
                payload = jwt.decode(token,SECRET_KEY,ALGORITHIM)
            except jwt.ExpiredSignatureError:
                raise Error(status_code=401, details="Token expired") 
            except Exception as e:
                raise Error(status_code=401,details="Invalid token!")
            
            key = f"user_token:{payload['user_email']}"

            redis_connection_string = os.getenv('REDIS_CONNECTION_STRING', None)
            if not redis_connection_string:
                raise Error(status_code=500, details="Redis connection string not found in environment variables!")
            
            redis_connection_string = json.loads(redis_connection_string)

            rc = redis.Redis(host=redis_connection_string["host"], port=redis_connection_string["port"],decode_responses=True)
            
            cache_data = rc.get(key)
            
            if cache_data is None:
                raise Error(status_code=401,details="Invalid token!")
            else:
                cache_data = json.loads(cache_data)
                if payload["user_email"] != cache_data["user_email"]:
                    raise Error(status_code=400,details="Invalid token/user")
            
            wrapper.auth_data = cache_data
            retval = await func(*args, **kwargs)
            logger.info(f"User {cache_data['user_email']} authenticated successfully!")
            return retval
        return wrapper
    