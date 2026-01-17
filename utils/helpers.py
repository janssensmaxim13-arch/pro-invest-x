# ============================================================================
# UTILITY HELPERS
# ============================================================================

import re
import uuid
import pandas as pd
from datetime import datetime
from typing import Dict

from config import DB_FILE, ALLOWED_TABLES


def generate_uuid(prefix: str = "PIX") -> str:
    """Generate a unique ID with prefix."""
    return f"{prefix}-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"


def sanitize_id(raw_id: str) -> str:
    """Sanitize an ID string."""
    if not raw_id or len(raw_id.strip()) < 3:
        return ""
    cleaned = re.sub(r'[^a-zA-Z0-9\-_]', '', raw_id.strip())
    return cleaned if len(cleaned) >= 3 else ""


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename."""
    return re.sub(r'[^a-zA-Z0-9._-]', '_', filename)


def get_identity_names_map() -> Dict[str, str]:
    """Get a map of identity IDs to names."""
    try:
        import sqlite3
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM identity_shield")
        results = cursor.fetchall()
        conn.close()
        return {row[0]: row[1] for row in results}
    except:
        return {}


def format_currency(amount: float, currency: str = "€") -> str:
    """Format a number as currency."""
    return f"{currency} {amount:,.2f}"


def format_date(date_str: str, format_out: str = "%d %b %Y") -> str:
    """Format a date string."""
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime(format_out)
    except:
        return date_str


def calculate_age(birth_date: str) -> int:
    """Calculate age from birth date."""
    try:
        birth = datetime.fromisoformat(birth_date)
        today = datetime.now()
        return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    except:
        return 0
