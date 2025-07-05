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


class CameraManagement():

    def __init__(self):
        '''
        Initialize the camera management module
        '''
        pass

    def list_all_cameras(self,auth_data):
        return True
    
    def create_camera(self, camera_data, auth_data):
        '''
        Create a new camera in the system
        This will also assign the camera to the user who created it by default (Superadmin in our case)
        '''
        with db.session() as conn:
            # Create a new camera object
            existing_camera = conn.query(database.Camera).filter(database.Camera.device_name == camera_data.device_name).first()
            if existing_camera:
                raise Error(status_code=400, details="Camera with this name already exists!")
            
            new_camera = database.Camera(
                device_name=camera_data.device_name,
                device_ip=camera_data.device_ip,
                device_location=camera_data.device_location,
                created_by=auth_data['user_email'],
                created_on=datetime.utcnow(),
                updated_by=auth_data['user_email'],
                updated_on=datetime.utcnow()
            )
            conn.add(new_camera)
            conn.flush()

            # After creating a camera we assign the camera to the user who created it by default
            camera_assignment = database.CameraAssignmentMap(
                camera_id=new_camera.id,
                user_id=auth_data['user_id'],
                assigned_by=auth_data['user_id'],
                created_by=auth_data['user_email'],
                created_on=datetime.utcnow(),
                updated_by=auth_data['user_email'],
                updated_on=datetime.utcnow()
            )
            
            conn.add(camera_assignment)

            # Create an audit log entry
            create_audit_entry = audit_log(
                user_id=auth_data['user_id'],
                action="CREATE_CAMERA",
                entity_type="Camera",
                entity_id=new_camera.id, 
                details=f"Camera {camera_data.device_name} created by {auth_data['user_email']}",
                conn=conn
            )

            # Log camera assignement
            assign_audit_entry = audit_log(
                user_id=auth_data['user_id'],
                action="ASSIGN_CAMERA",
                entity_type="CameraAssignment",
                entity_id=camera_assignment.id,
                details=f"Camera {camera_data.device_name} assigned to user {auth_data['user_email']}",
                conn=conn
            )

            conn.add(create_audit_entry)
            conn.add(assign_audit_entry)
            conn.commit()
            
            return {"message": "Camera created successfully", "camera_id": new_camera.id, "camera_name": new_camera.device_name}