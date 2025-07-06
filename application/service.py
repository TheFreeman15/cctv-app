'''
Contains all generalized logic
'''
import utils.database as database
from utils.exceptions import *
from datetime import datetime
import os 
import json

config = json.loads(os.getenv('DB_CONNECTION_STRING', {}))
db = database.DatabaseResource(config)

def require_permissions(auth_data,permission_type):
    user_id = auth_data["user_id"]
    with db.session() as conn:
        all_permissions = []
        data = conn.query(database.User).filter(database.User.id == user_id).first()
        user_role = data.roles
        user_role_id = user_role[0].id

        role_details = conn.query(database.Role).filter(database.Role.id == user_role_id).first()
        role_permissions = role_details.permissions
        for i in role_permissions:
            all_permissions.append(i.permission_name)
        
        if permission_type in all_permissions:
            return True
        else:
            raise Error(status_code=400, details="User is not authorized to perform this action!")


def audit_log(user_id, action, entity_type, entity_id=None, details=None,conn=None):
    '''
    Function to log audit logs into our database
    '''
    audit_entry = database.AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        timestamp=datetime.now()
    )
    # Let the commit be driven by the caller
    # This allows the caller to control transaction boundaries
    return audit_entry

def fetch_activity_logs():
    '''
    Fetch all activity logs from our database ordered by latest first
    '''
    with db.session() as conn:
        logs = conn.query(database.AuditLog).order_by(database.AuditLog.timestamp.desc()).all()
        return logs