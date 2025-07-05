from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Association Models
class UserRoleMap(Base):
    __tablename__ = 'user_role_map'
    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    created_on = Column(Date, nullable=False)
    created_by = Column(String(255), nullable=False)
    updated_on = Column(Date, nullable=False)
    updated_by = Column(String(255), nullable=False)

    role = relationship("Role", back_populates="user_links")
    user = relationship("User", back_populates="role_links")


class RolePermissionMap(Base):
    __tablename__ = 'role_permission_map'
    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    permission_id = Column(Integer, ForeignKey('permissions.id'), primary_key=True)
    created_by = Column(String(255), nullable=False)
    created_on = Column(Date, nullable=False)
    updated_by = Column(String(255), nullable=False)
    updated_on = Column(Date, nullable=False)

    role = relationship("Role", back_populates="permission_links")
    permission = relationship("Permission", back_populates="role_links")


# Main Models
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    hashed_password = Column(String(1000), nullable=False)
    created_on = Column(Date, nullable=False)
    created_by = Column(String(255), nullable=False)
    updated_on = Column(Date, nullable=False)
    updated_by = Column(String(255), nullable=False)

    role_links = relationship('UserRoleMap', back_populates='user', cascade="all, delete-orphan")
    roles = relationship('Role', secondary='user_role_map', back_populates='users', viewonly=True)
    cameras = relationship('Camera', back_populates='user')


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String(255), nullable=False)
    rank = Column(Integer, nullable=False)
    created_on = Column(Date, nullable=False)
    created_by = Column(String(255), nullable=False)
    updated_on = Column(Date, nullable=False)
    updated_by = Column(String(255), nullable=False)

    user_links = relationship('UserRoleMap', back_populates='role', cascade="all, delete-orphan")
    permission_links = relationship('RolePermissionMap', back_populates='role', cascade="all, delete-orphan")

    users = relationship('User', secondary='user_role_map', back_populates='roles', viewonly=True)
    permissions = relationship('Permission', secondary='role_permission_map', back_populates='roles', viewonly=True)


class Permission(Base):
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    permission_name = Column(String(255), nullable=False)
    created_by = Column(String(255), nullable=False)
    created_on = Column(Date, nullable=False)
    updated_by = Column(String(255), nullable=False)
    updated_on = Column(Date, nullable=False)

    role_links = relationship('RolePermissionMap', back_populates='permission', cascade="all, delete-orphan")
    roles = relationship('Role', secondary='role_permission_map', back_populates='permissions', viewonly=True)


class Camera(Base):
    __tablename__ = 'cameras'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    device_name = Column(String(255), nullable=False)
    device_ip = Column(String(255), nullable=False)
    device_location = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_on = Column(Date, nullable=False)
    updated_by = Column(String(255), nullable=False)
    updated_on = Column(String(255), nullable=False)  # Per schema

    user = relationship('User', back_populates='cameras')

class CameraAssignmentMap(Base):
    __tablename__ = 'camera_assignment_map'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    camera_id = Column(Integer, ForeignKey('cameras.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    assigned_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_by = Column(String(255), nullable=False)
    created_on = Column(Date, nullable=False)
    updated_by = Column(String(255), nullable=False)
    updated_on = Column(Date, nullable=False)

    camera = relationship("Camera", foreign_keys=[camera_id])
    user = relationship("User", foreign_keys=[user_id])
    assigner = relationship("User", foreign_keys=[assigned_by])

class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=True)
    details = Column(String(255), nullable=True)
    timestamp = Column(Date, nullable=False)

    user = relationship("User")