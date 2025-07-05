from passlib.context import CryptContext
import jwt
import utils.database as database
from utils.exceptions import *
from datetime import datetime,timedelta
import redis
import json
from functools import wraps

config = {"dialect": "mysql", "username": "root", "password": "cctv-rootpass", "host": "mysql", "port": "3306", "db_name": "cctvdb"}
db = database.DatabaseResource(config)

#TODO: Move this to env variables 
SECRET_KEY = "JWTENCODESECRET321"
ALGORITHIM = "HS256"

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
    
    
    def login_user(self, email, plain_password):
        # Initialize a DB session if one is not created
        if self.conn is None:
            with db.session() as conn:
                
                existing_user = conn.query(database.User).filter(database.User.email == email).first()
                if existing_user is None:
                    raise Error(status_code=400,details="User does not exist!")
                
                # Validate if the password matches the hash using passlib verify
                valid_password = self.verify_password(existing_user.hashed_password, plain_password)
                if not valid_password:
                    raise Error(status_code=400,details="Incorrect password!")
                

                # Check in redis if for this user
                self.create_redis_client()
                rc = self.redis_client

                
                # Generate a token for the user
                data = {"user_id": existing_user.id,"user_name": existing_user.name, "user_email": existing_user.email, "user_role": existing_user.roles[0].name, "user_rank": existing_user.roles[0].rank}
                user_token = self.create_access_token(data)
                key = f"user_token:{existing_user.email}"
                rc.setex(key,self.ACCESS_TOKEN_EXPIRE_MINUTES * 60,json.dumps(data))
                return {"message": "Login sucessful", "token": user_token, "data": data}



                
                
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

            #TODO: Can be improved to be only called on service startup
            rc = redis.Redis(host='redis', port=6379,decode_responses=True)
            
            cache_data = rc.get(key)
            cache_data = json.loads(cache_data)
            if cache_data is None:
                raise Error(status_code=401,details="Invalid token!")
            else:
                if payload["user_email"] != cache_data["user_email"]:
                    raise Error(status_code=400,details="Invalid token/user")
            
            print(cache_data)
            wrapper.auth_data = cache_data
            retval = await func(*args, **kwargs)

            return retval
        return wrapper
    