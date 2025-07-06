from fastapi import APIRouter, Header,Request,Response,Depends
import utils.database as database
from application.schema import *
from passlib.context import CryptContext
from application.authentication import LoginHandler
from utils.exceptions import *
import traceback
from typing import Annotated
from application.service import *
from application.user_management import UserManagement
from application.camera_management import CameraManagement

v1 = APIRouter()

# Move to env variables later on 


@v1.post("/login", tags=["User login / Authentication management"])
async def login(data: UserLogin):
     '''
     Below API to perform the below actions 
     1. Check if users password hash is valid 
     2. If valid hash generate a JWT token for the user 
     3. Publish the JWT token into redis
     
     In redis data will be maintained as
     user_token:<user_email>: token_data

     '''
     
     try:
          login_handler = LoginHandler()
          x = login_handler.login_user(data.email,data.password,data.refresh_token)
          return {"responseData": x}
     except Error as e:
          # Pass through any custom raised errors as-is
          raise
     except Exception as e:
          traceback.print_exc()
          # Handle anything exceptional that we have not encountered anywhere
          raise Error(status_code=500,details="Something went wrong!")
     

@v1.get("/users/me", tags=["User login / Authentication management"])
@LoginHandler.authenticate_user
async def current_user(request: Request, token: str = Header(None)):
     '''
     Return information about the current logged in user
     auth_data is being injected by login decorator
     '''
     return current_user.auth_data


@v1.get("/users", tags=["User Management"])
@LoginHandler.authenticate_user
async def list_users(request: Request, token: str = Header(None)):
     '''
     List All users currently created in our database
     Can only be accessed by the superadmin OR users with "VIEW_ALL_USERS permission"
     '''
     permission_required = "VIEW_ALL_USERS"
     try:
         require_permissions(list_users.auth_data, permission_required)
         user_management = UserManagement()
         return {"responseData": user_management.list_all_users()}
     except Error as e:
          # Pass through any custom raised errors as-is
          raise
     except Exception as e:
          traceback.print_exc()
          # Handle anything exceptional that we have not encountered anywhere
          raise Error(status_code=500,details="Something went wrong!")


@v1.post("/users", tags=["User Management"])
@LoginHandler.authenticate_user
async def create_user(data: CreateUser, request: Request, response: Response, token: str = Header(None),):
     '''
     Create a user in our database
     Can only be accessed by the superadmin OR users with "CREATE_USER permission"
     '''
     permission_required = "CREATE_USER"
     try:
         auth_data = create_user.auth_data
         require_permissions(auth_data, permission_required)
         user_management = UserManagement()
         response.status_code = 201
         return {"responseData":{"message":"User created!", "data":user_management.create_user(data,auth_data)}}
     except Error as e:
          # Pass through any custom raised errors as-is
          raise
     except Exception as e:
          traceback.print_exc()
          # Handle anything exceptional that we have not encountered anywhere
          raise Error(status_code=500,details="Something went wrong!")


@v1.patch("/users", tags=["User Management"])
@LoginHandler.authenticate_user
async def edit_user(data: ModifyUser, request: Request, response: Response, token: str = Header(None),):
     '''
     Delete a user in our database
     Can only be accessed by the superadmin OR users with "EDIT_USER permission"
     '''

     permission_required = "EDIT_USER"
     try:
         auth_data = edit_user.auth_data
         require_permissions(auth_data, permission_required)
         user_management = UserManagement()
         response.status_code = 200
         return {"responseData":{"message":"User modified!", "data":user_management.modify_user(data,auth_data)}}
     except Error as e:
          # Pass through any custom raised errors as-is
          raise
     except Exception as e:
          traceback.print_exc()
          # Handle anything exceptional that we have not encountered anywhere
          raise Error(status_code=500,details="Something went wrong!")


@v1.delete("/users", tags=["User Management"])
@LoginHandler.authenticate_user
async def delete_user(data: DeleteUser, request: Request, response: Response, token: str = Header(None),):
     '''
     Delete a user in our database
     Can only be accessed by the superadmin OR users with "DELETE_USER permission"
     '''

     permission_required = "DELETE_USER"
     try:
         auth_data = delete_user.auth_data
         require_permissions(auth_data, permission_required)
         user_management = UserManagement()
         response.status_code = 200
         return {"responseData":{"message":"User deleted!", "data":user_management.delete_user(data,auth_data)}}
     except Error as e:
          # Pass through any custom raised errors as-is
          raise
     except Exception as e:
          traceback.print_exc()
          # Handle anything exceptional that we have not encountered anywhere
          raise Error(status_code=500,details="Something went wrong!")
     
@v1.get("/activity", tags=["Activity Logs"])
@LoginHandler.authenticate_user
async def list_activity_logs(request: Request, token: str = Header(None)):
     '''
     List all activity logs in our database
     Can only be accessed by the superadmin OR users with "VIEW_ACTIVITY_LOGS permission"
     '''
     permission_required = "VIEW_ACTIVITY_LOGS"
     try:
         require_permissions(list_activity_logs.auth_data, permission_required)
         return {"responseData": fetch_activity_logs()}
     except Error as e:
          # Pass through any custom raised errors as-is
          raise
     except Exception as e:
          traceback.print_exc()
          # Handle anything exceptional that we have not encountered anywhere
          raise Error(status_code=500,details="Something went wrong!")

@v1.get("/camera", tags=["Camera Management"])
@LoginHandler.authenticate_user
async def get_cameras(request: Request, response: Response, token: str = Header(None),):
     '''
     Fetch all cameras assigned to the user
     If the user is a superadmin then fetch all cameras in the system
     Can only be accessed by the superadmin OR users with "VIEW_CAMERA permission"
     '''
     permission_required = "VIEW_CAMERA"
     try:
         auth_data = get_cameras.auth_data
         require_permissions(auth_data, permission_required)
         camera_management = CameraManagement()
         return {"responseData": camera_management.list_all_cameras(auth_data)}
     except Error as e:
          # Pass through any custom raised errors as-is
          raise
     except Exception as e:
          traceback.print_exc()
          # Handle anything exceptional that we have not encountered anywhere
          raise Error(status_code=500,details="Something went wrong!")

@v1.post("/camera", tags=["Camera Management"])
@LoginHandler.authenticate_user
async def create_camera(data: CreateCamera, request: Request, response: Response, token: str = Header(None),):
     '''
     Create a camera in our database
     This will also assign the camera to the user who created it by default (Superadmin in our case)
     Can only be accessed by the superadmin OR users with "CREATE_CAMERA permission"
     '''
     permission_required = "CREATE_CAMERA"
     try:
         auth_data = create_camera.auth_data
         require_permissions(auth_data, permission_required)
         camera_management = CameraManagement()
         response.status_code = 201
         return {"responseData":{"message":"Camera created!", "data":camera_management.create_camera(data,auth_data)}}
     except Error as e:
          # Pass through any custom raised errors as-is
          raise
     except Exception as e:
          traceback.print_exc()
          # Handle anything exceptional that we have not encountered anywhere
          raise Error(status_code=500,details="Something went wrong!")


@v1.post("/camera/assign", tags=["Camera Management"])
@LoginHandler.authenticate_user
async def assign_camera(data: AssignCamera, request: Request, response: Response, token: str = Header(None),):
     '''
     Assign a camera to a user
     Can only be accessed by users with "ASSIGN_CAMERA permission"
     '''
     permission_required = "ASSIGN_CAMERA"
     try:
         auth_data = assign_camera.auth_data
         require_permissions(auth_data, permission_required)
         camera_management = CameraManagement()
         response.status_code = 201
         return {"responseData":{"message":"Camera assigned!", "data":camera_management.assign_camera(data,auth_data)}}
     except Error as e:
          # Pass through any custom raised errors as-is
          raise
     except Exception as e:
          traceback.print_exc()
          # Handle anything exceptional that we have not encountered anywhere
          raise Error(status_code=500,details="Something went wrong!")
     
# delete camera
@v1.delete("/camera", tags=["Camera Management"])
@LoginHandler.authenticate_user
async def delete_camera(data: DeleteCamera, request: Request, response: Response, token: str = Header(None),):
     '''
     Delete a camera in our database
     Can only be accessed by the superadmin OR users with "DELETE_CAMERA permission"
     '''
     permission_required = "DELETE_CAMERA"
     try:
         auth_data = delete_camera.auth_data
         require_permissions(auth_data, permission_required)
         camera_management = CameraManagement()
         response.status_code = 200
         return {"responseData":{"message":"Camera deleted!", "data":camera_management.delete_camera(data,auth_data)}}
     except Error as e:
          # Pass through any custom raised errors as-is
          raise
     except Exception as e:
          traceback.print_exc()
          # Handle anything exceptional that we have not encountered anywhere
          raise Error(status_code=500,details="Something went wrong!")     


# Edit camera
@v1.patch("/camera", tags=["Camera Management"])
@LoginHandler.authenticate_user
async def edit_camera(data: ModifyCamera, request: Request, response: Response, token: str = Header(None),):
     '''
     Edit a camera in our database
     Can only be accessed by users with "EDIT_CAMERA permission"
     '''
     permission_required = "EDIT_CAMERA"
     try:
         auth_data = edit_camera.auth_data
         require_permissions(auth_data, permission_required)
         camera_management = CameraManagement()
         response.status_code = 200
         return {"responseData":{"message":"Camera modified!", "data":camera_management.modify_camera(data,auth_data)}}
     except Error as e:
          # Pass through any custom raised errors as-is
          raise
     except Exception as e:
          traceback.print_exc()
          # Handle anything exceptional that we have not encountered anywhere
          raise Error(status_code=500,details="Something went wrong!")

# Deassign user from camera
@v1.post("/camera/deassign", tags=["Camera Management"])
@LoginHandler.authenticate_user
async def deassign_camera(data: DeassignCamera, request: Request, response: Response, token: str = Header(None),):
     '''
     Deassign a camera from a user
     Can only be accessed by users with "ASSIGN_CAMERA" permission"
     '''
     permission_required = "ASSIGN_CAMERA"
     try:
         auth_data = deassign_camera.auth_data
         require_permissions(auth_data, permission_required)
         camera_management = CameraManagement()
         response.status_code = 200
         return {"responseData":{"message":"Camera deassigned!", "data":camera_management.deassign_camera(data,auth_data)}}
     except Error as e:
          # Pass through any custom raised errors as-is
          raise
     except Exception as e:
          traceback.print_exc()
          # Handle anything exceptional that we have not encountered anywhere
          raise Error(status_code=500,details="Something went wrong!")