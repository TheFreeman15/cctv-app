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


class UserManagement():
    def __init__(self):
        pass

    def list_all_users(self):
        '''
        Fetch all users from database 
        Only specific columns will be fetched to hide sensitive info such as hashed passwords
        '''
        with db.session() as conn:
            data = conn.query(database.User).with_entities(database.User.id,database.User.name,database.User.email,database.User.created_on,database.User.created_by).all()
            print("test>>>",data)
            return data
        
    def create_user(self,data,auth_data):
        '''
        Create new user in our database 
        '''
        
        with db.session() as conn:
            # Check if user exists in our database already
            user_exists = conn.query(database.User).filter(database.User.email == data.user_email).first()
            if user_exists:
                raise Error(status_code=400,details = "User already exists!")
            
            # Check if requested role is present or not
            role_exists = conn.query(database.Role).filter(database.Role.name == data.role).first()
            if not role_exists:
                raise Error(status_code=400, details="Requested role does not exist!")
            
            # Use common function and hash the users password
            login_handler = LoginHandler()
            hashed_password = login_handler.hash_password(data.password)

            # Create entry in users table
            user_entry = database.User(
                name = data.user_name,
                email = data.user_email,
                hashed_password = hashed_password,
                created_on = datetime.now(),
                created_by = auth_data["user_email"],
                updated_on = datetime.now(),
                updated_by = auth_data["user_email"]
            )
            conn.add(user_entry)
            conn.flush()
            
            # Create entry in user_role_map to map user to requested role
            user_role_map_entry = database.UserRoleMap(
                user_id = user_entry.id,
                role_id = role_exists.id,
                created_on = datetime.now(),
                created_by = auth_data["user_email"],
                updated_on = datetime.now(),
                updated_by = auth_data["user_email"]
            )
            # Audit log for user creation
            audit_entry = audit_log(user_id=auth_data["user_id"],
                      action="CREATE_USER",
                      entity_type="User",
                      entity_id=user_entry.id,
                      details=f"User {data.user_name} created by {auth_data['user_email']}", conn=conn)
            
            data = {
                "user_id": user_entry.id,
                "user_name": user_entry.name,
                "user_email": user_entry.email,
                "created_on": user_entry.created_on,
                "created_by": user_entry.created_by,
                "updated_on": user_entry.updated_on,
                "updated_by": user_entry.updated_by
            }
            conn.add(user_role_map_entry)
            conn.add(audit_entry)
            conn.commit()
            
            return data
        
    def modify_user(self, data, auth_data):
        '''
        Modify a user in our database
        '''
        user_email = data.user_email
        with db.session() as conn:
            # Check if user exists in our database
            user_exists = conn.query(database.User).filter(database.User.email == user_email).first()
            if not user_exists:
                raise Error(status_code=400, details="User does not exist!")

            # Update the user entry
            if data.user_name:
                user_exists.name = data.user_name
            if data.role:
                role_exists = conn.query(database.Role).filter(database.Role.name == data.role).first()
                if not role_exists:
                    raise Error(status_code=400, details="Requested role does not exist!")
                # Update the user_role_map entry for this user
                user_role_map_exists = conn.query(database.UserRoleMap).filter(database.UserRoleMap.user_id == user_exists.id).first()
                if user_role_map_exists:
                    user_role_map_exists.role_id = role_exists.id
            if data.password:
                login_handler = LoginHandler()
                hashed_password = login_handler.hash_password(data.password)
                user_exists.hashed_password = hashed_password

            # Update timestamps and updated_by field
            user_exists.updated_on = datetime.now()
            user_exists.updated_by = auth_data["user_email"]

            # Audit log for user modification
            audit_entry = audit_log(user_id=auth_data["user_id"],
                      action="MODIFY_USER",
                      entity_type="User",
                      entity_id=user_exists.id,
                      details=f"User {user_exists.name} modified by {auth_data['user_email']}", conn=conn)

            conn.add(audit_entry)
            conn.commit()
            return {"message": "User modified successfully!"}
        
    def delete_user(self, data, auth_data):
        '''
        Delete a user from our database
        '''
        #TODO: Hide password from response data
        user_email = data.user_email
        if user_email == auth_data["user_email"]:
            raise Error(status_code=400, details="You cannot delete your own account!")
        with db.session() as conn:
            # Check if user exists in our database
            user_exists = conn.query(database.User).filter(database.User.email == user_email).first()
            if not user_exists:
                raise Error(status_code=400, details="User does not exist!")

            # Delete rhe user_role_map entry for this user
            user_role_map_exists = conn.query(database.UserRoleMap).filter(database.UserRoleMap.user_id == user_exists.id).first()
            if user_role_map_exists:
                conn.delete(user_role_map_exists)

            # Delete the user entry
            conn.delete(user_exists)
            
            # Audit log for user deletion
            audit_entry = audit_log(user_id=auth_data["user_id"],
                      action="DELETE_USER",
                      entity_type="User",
                      entity_id=user_exists.id,
                      details=f"User {user_exists.name} deleted by {auth_data['user_email']}", conn=conn)
            
            conn.add(audit_entry)
            conn.commit()
            return {"message": "User deleted successfully!"}