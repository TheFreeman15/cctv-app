from passlib.context import CryptContext
import utils.database as database
from utils.exceptions import *
import json
from functools import wraps
from datetime import datetime
from .authentication import LoginHandler
from .service import audit_log
import os

config = json.loads(os.getenv('DB_CONNECTION_STRING', {}))
db = database.DatabaseResource(config)


SUPERADMIN_RANK = int(os.getenv('SUPERADMIN_RANK', 1))

class CameraManagement():

    def __init__(self):
        '''
        Initialize the camera management module
        '''
        pass

    def list_all_cameras(self,auth_data):
        '''
        List all cameras asssigned to the user
        If the user is a superadmin then list all cameras in the system
        '''
        with db.session() as conn:
            user_data = conn.query(database.User).filter(database.User.id == auth_data['user_id']).first()
            if not user_data:
                raise Error(status_code=404, details="User not found!")

            if user_data.roles[0].rank == SUPERADMIN_RANK:
                # If the user is a superadmin, return all cameras
                cameras = conn.query(database.Camera).all()
                return cameras
            else:
                # If the user is not a superadmin, return only cameras assigned to the user
                # Fetch result in a joined query
                cameras = conn.query(database.Camera).join(
                    database.CameraAssignmentMap,
                    database.Camera.id == database.CameraAssignmentMap.camera_id
                ).filter(
                    database.CameraAssignmentMap.user_id == user_data.id
                ).all()

                return cameras
        

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
            conn.flush()

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
        
    def assign_camera(self, camera_data, auth_data):
        '''
        Assign a camera to a user
        '''
        with db.session() as conn:
            # Check if the camera exists
            existing_camera = conn.query(database.Camera).filter(database.Camera.device_name == camera_data.device_name).first()
            if not existing_camera:
                raise Error(status_code=404, details="Camera not found!")
            
            # Check if the user exists
            existing_user = conn.query(database.User).filter(database.User.email == camera_data.user_email).first()
            if not existing_user:
                raise Error(status_code=404, details="User not found!")
            
            # Check if the camera is already assigned to the user
            existing_assignment = conn.query(database.CameraAssignmentMap).filter(
                database.CameraAssignmentMap.camera_id == existing_camera.id,
                database.CameraAssignmentMap.user_id == existing_user.id
            ).first()

            if existing_assignment:
                raise Error(status_code=400, details="Camera is already assigned to this user!")
            
            # Create a new assignment
            new_assignment = database.CameraAssignmentMap(
                camera_id=existing_camera.id,
                user_id=existing_user.id,
                assigned_by=auth_data['user_id'],
                created_by=auth_data['user_email'],
                created_on=datetime.utcnow(),
                updated_by=auth_data['user_email'],
                updated_on=datetime.utcnow()
            )
            
            conn.add(new_assignment)
            conn.flush()
            # Create an audit log entry for the assignment
            assign_audit_entry = audit_log(
                user_id=auth_data['user_id'],
                action="ASSIGN_CAMERA",
                entity_type="CameraAssignment",
                entity_id=new_assignment.id,
                details=f"Camera {existing_camera.device_name} assigned to user {existing_user.email}",
                conn=conn
            )
            
            conn.add(assign_audit_entry)
            conn.commit()
            
            return {"message": "Camera assigned successfully", "assignment_id": new_assignment.id}
        
    def delete_camera(self, camera_data, auth_data):
        '''
        Delete a camera from the system

        Check if the camera exists and if it is assigned to current user
        Check the rank of current user and assigned_by user in the assignment map
        If the assigned user rank is higher than the current user, then raise an error
        '''
        with db.session() as conn:
            # Check if the camera exists
            existing_camera = conn.query(database.Camera).filter(database.Camera.device_name == camera_data.device_name).first()
            if not existing_camera:
                raise Error(status_code=404, details="Camera not found!") 
            # Check if the camera is assigned to the user
            existing_assignment = conn.query(database.CameraAssignmentMap).filter(
                database.CameraAssignmentMap.camera_id == existing_camera.id,
                database.CameraAssignmentMap.user_id == auth_data['user_id']
            ).first()

            if not existing_assignment:
                raise Error(status_code=404, details="Camera is not assigned to you!")
            
            # Check the rank of the user who assigned the camera
            assigner_rank = existing_assignment.assigner.roles[0].rank
            current_user_rank = auth_data['user_rank']
            print(f"Assigner Rank: {assigner_rank}, Current User Rank: {current_user_rank}")
            if assigner_rank < current_user_rank:
                raise Error(status_code=403, details="You do not have permission to delete this camera!")
            # Delete the camera assignment
            conn.delete(existing_assignment)
            # Create an audit log entry for the deletion
            delete_audit_entry = audit_log(
                user_id=auth_data['user_id'],
                action="DELETE_CAMERA_ASSIGNMENT",
                entity_type="CameraAssignment",
                entity_id=existing_assignment.id,
                details=f"Camera {existing_camera.device_name} deleted by {auth_data['user_email']}",
                conn=conn
            )
           
            conn.add(delete_audit_entry)
            # Delete the camera itself
            conn.delete(existing_camera)
            # Create an audit log entry for the camera deletion
            camera_delete_audit_entry = audit_log(
                user_id=auth_data['user_id'],
                action="DELETE_CAMERA",
                entity_type="Camera",
                entity_id=existing_camera.id,
                details=f"Camera {existing_camera.device_name} deleted by {auth_data['user_email']}",
                conn=conn
            )
            
            conn.add(camera_delete_audit_entry)
            conn.commit()
            
            return {"message": "Camera deleted successfully", "camera_name": existing_camera.device_name}
        
    def modify_camera(self, camera_data, auth_data):
        '''
        Edit a camera in the system
        This will update the camera details and also update the assignment if the camera is assigned to the user
        '''
        with db.session() as conn:
            # Check if the camera exists
            existing_camera = conn.query(database.Camera).filter(database.Camera.device_name == camera_data.device_name).first()
            if not existing_camera:
                raise Error(status_code=404, details="Camera not found!")
            
            # Check if the camera is assigned to the user
            existing_assignment = conn.query(database.CameraAssignmentMap).filter(
                database.CameraAssignmentMap.camera_id == existing_camera.id,
                database.CameraAssignmentMap.user_id == auth_data['user_id']
            ).first()

            if not existing_assignment:
                raise Error(status_code=404, details="Camera is not assigned to you!")
            
            # Update the camera details
            if camera_data.new_device_name:
                existing_camera.device_name = camera_data.new_device_name
            if camera_data.new_device_ip:
                existing_camera.device_ip = camera_data.new_device_ip
            if camera_data.new_device_location:
                existing_camera.device_location = camera_data.new_device_location
            
            existing_camera.updated_by = auth_data['user_email']
            existing_camera.updated_on = datetime.utcnow()
            
            # Update the assignment details
            existing_assignment.updated_by = auth_data['user_email']
            existing_assignment.updated_on = datetime.utcnow()
            
            conn.add(existing_camera)
            conn.add(existing_assignment)
            conn.flush()
            # Create an audit log entry for the edit
            edit_audit_entry = audit_log(
                user_id=auth_data['user_id'],
                action="EDIT_CAMERA",
                entity_type="Camera",
                entity_id=existing_camera.id,
                details=f"Camera {existing_camera.device_name} edited by {auth_data['user_email']}",
                conn=conn
            )
            
            conn.add(edit_audit_entry)
            conn.commit()
            
            return {"message": "Camera edited successfully", "camera_name": existing_camera.device_name}
        
    def deassign_camera(self, camera_data, auth_data):
        '''
        Deassign a camera from a user. Users email is given in input
        This will remove the camera assignment from the user
        '''
        with db.session() as conn:
            # Check if the camera exists
            existing_camera = conn.query(database.Camera).filter(database.Camera.device_name == camera_data.device_name).first()
            if not existing_camera:
                raise Error(status_code=404, details="Camera not found!")
            
            # Check if the user exists
            existing_user = conn.query(database.User).filter(database.User.email == camera_data.user_email).first()
            if not existing_user:
                raise Error(status_code=404, details="User not found!")
            
            # Check if the camera is assigned to the user
            existing_assignment = conn.query(database.CameraAssignmentMap).filter(
                database.CameraAssignmentMap.camera_id == existing_camera.id,
                database.CameraAssignmentMap.user_id == existing_user.id
            ).first()

            if not existing_assignment:
                raise Error(status_code=404, details="Camera is not assigned to this user!")
            
            # Check the rank of the user who assigned the camera
            assigner_rank = existing_assignment.assigner.roles[0].rank
            current_user_rank = auth_data['user_rank']
            print(f"Assigner Rank: {assigner_rank}, Current User Rank: {current_user_rank}")
            if assigner_rank < current_user_rank:
                raise Error(status_code=403, details="You do not have permission to deassign this camera!")
            
            # Delete the camera assignment
            conn.delete(existing_assignment)
            # Create an audit log entry for the deassignment
            deassign_audit_entry = audit_log(
                user_id=auth_data['user_id'],
                action="DEASSIGN_CAMERA",
                entity_type="CameraAssignment",
                entity_id=existing_assignment.id,
                details=f"Camera {existing_camera.device_name} deassigned from user {existing_user.email} by {auth_data['user_email']}",
                conn=conn
            )
            
            conn.add(deassign_audit_entry)
            conn.commit()
            
            return {"message": "Camera deassigned successfully", "camera_name": existing_camera.device_name}
            