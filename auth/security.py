# ============================================================================
# AUTHENTICATION & SECURITY MODULE
# ============================================================================

import sqlite3
import hashlib
import uuid
from datetime import datetime
from typing import Optional

from config import DB_FILE

# Try to import bcrypt
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False


# ============================================================================
# PASSWORD HASHING
# ============================================================================

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt or SHA256 fallback.
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password string
    """
    if BCRYPT_AVAILABLE:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    else:
        return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        password: Plain text password
        hashed: Hashed password
    
    Returns:
        True if password matches
    """
    if BCRYPT_AVAILABLE:
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except:
            # Fallback to SHA256 check
            return hashlib.sha256(password.encode()).hexdigest() == hashed
    else:
        return hashlib.sha256(password.encode()).hexdigest() == hashed


# ============================================================================
# USER AUTHENTICATION
# ============================================================================

def verify_user(username: str, password: str) -> bool:
    """
    Verify user credentials.
    
    Args:
        username: Username
        password: Password
    
    Returns:
        True if credentials are valid
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT password_hash, active FROM user_registry WHERE username = ?", 
            (username,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result and result[1] == 1:  # Check if active
            stored_hash = result[0]
            if verify_password(password, stored_hash):
                # Update last login
                update_last_login(username)
                log_audit(username, "LOGIN_SUCCESS", "Authentication")
                return True
            else:
                log_audit(username, "LOGIN_FAILED", "Authentication", success=False)
        
        return False
    
    except Exception as e:
        print(f"Auth error: {e}")
        return False


def register_user(username: str, password: str, role: str = "Official", email: str = None) -> bool:
    """
    Register a new user.
    
    Args:
        username: Username
        password: Password
        role: User role
        email: Email address
    
    Returns:
        True if registration successful
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if username exists
        cursor.execute("SELECT 1 FROM user_registry WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return False
        
        password_hash = hash_password(password)
        
        cursor.execute(
            "INSERT INTO user_registry VALUES (?, ?, ?, ?, ?, ?, ?)",
            (username, password_hash, role, email, 1, datetime.now().isoformat(), None)
        )
        
        conn.commit()
        conn.close()
        
        log_audit(username, "USER_REGISTERED", "Authentication")
        return True
    
    except Exception as e:
        print(f"Registration error: {e}")
        return False


def get_user_role(username: str) -> str:
    """
    Get the role of a user.
    
    Args:
        username: Username
    
    Returns:
        Role string or empty string
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT role FROM user_registry WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else ""
    
    except:
        return ""


def update_last_login(username: str):
    """Update last login timestamp."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE user_registry SET last_login = ? WHERE username = ?",
            (datetime.now().isoformat(), username)
        )
        
        conn.commit()
        conn.close()
    except:
        pass


# ============================================================================
# AUDIT LOGGING
# ============================================================================

def log_audit(username: str, action: str, module: str, 
              ip_address: str = None, success: bool = True, details: str = None):
    """
    Log an audit event.
    
    Args:
        username: User performing action
        action: Action type
        module: Module where action occurred
        ip_address: Client IP
        success: Whether action succeeded
        details: Additional details
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        log_id = f"LOG-{uuid.uuid4().hex[:12].upper()}"
        
        cursor.execute(
            "INSERT INTO audit_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (log_id, username, action, module, ip_address, 
             1 if success else 0, details, datetime.now().isoformat())
        )
        
        conn.commit()
        conn.close()
    
    except Exception as e:
        print(f"Audit log error: {e}")


# ============================================================================
# ROLE-BASED ACCESS CONTROL
# ============================================================================

# Role groups for permission management
ROLE_GROUPS = {
    'admin': ['SuperAdmin', 'Admin'],
    'management': ['SuperAdmin', 'Admin', 'Manager', 'Official'],
    'staff': ['SuperAdmin', 'Admin', 'Manager', 'Official', 'Staff', 'Scout', 'Coach'],
    'medical': ['SuperAdmin', 'Admin', 'Doctor', 'Psychologist', 'Medical Staff'],
    'all': ['SuperAdmin', 'Admin', 'Manager', 'Official', 'Staff', 'Scout', 'Coach', 
            'Investor', 'Athlete', 'Partner', 'Fan', 'Diaspora', 'Academy Staff',
            'Doctor', 'Psychologist', 'Medical Staff']
}


def require_role(allowed_roles: list):
    """
    Decorator to require specific roles.
    
    Args:
        allowed_roles: List of allowed role names
    """
    def decorator(func):
        def wrapper(username, *args, **kwargs):
            user_role = get_user_role(username)
            if user_role in allowed_roles:
                return func(username, *args, **kwargs)
            else:
                return None
        return wrapper
    return decorator


def requires_role(allowed_roles: list):
    """
    Decorator to require specific roles (alias for require_role).
    
    Args:
        allowed_roles: List of allowed role names
    """
    return require_role(allowed_roles)


def check_permission(required_roles_or_username, required_roles: list = None, silent: bool = False) -> bool:
    """
    Check if user has permission.
    
    Can be called in two ways:
    1. check_permission(username, required_roles) - explicit username
    2. check_permission(required_roles, silent=True) - uses session state
    
    Args:
        required_roles_or_username: Either username (str) or required_roles (list)
        required_roles: List of allowed roles (if first arg is username)
        silent: If True, don't show error messages (default False)
    
    Returns:
        True if user has permission
    """
    import streamlit as st
    
    # Determine if first arg is username or roles list
    if isinstance(required_roles_or_username, list):
        # Called with just roles list: check_permission([roles], silent=True)
        roles_to_check = required_roles_or_username
        username = st.session_state.get('username', '')
    else:
        # Called with username: check_permission(username, [roles])
        username = required_roles_or_username
        roles_to_check = required_roles if required_roles else []
    
    user_role = get_user_role(username)
    
    # Check if roles_to_check is a role group name
    if isinstance(roles_to_check, str) and roles_to_check in ROLE_GROUPS:
        has_permission = user_role in ROLE_GROUPS[roles_to_check]
    else:
        has_permission = user_role in roles_to_check
    
    if not has_permission and not silent:
        st.error(" You don't have permission to access this feature.")
    
    return has_permission


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

def create_session_token(username: str) -> str:
    """
    Create a session token.
    
    Args:
        username: Username
    
    Returns:
        Session token
    """
    token = f"{username}-{uuid.uuid4().hex}"
    return hashlib.sha256(token.encode()).hexdigest()


def invalidate_session(username: str):
    """
    Invalidate all sessions for a user.
    
    Args:
        username: Username
    """
    log_audit(username, "SESSION_INVALIDATED", "Authentication")
