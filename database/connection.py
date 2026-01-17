# ============================================================================
# DATABASE CONNECTION & HELPERS
# ============================================================================

import sqlite3
import pandas as pd
import logging
from typing import Any, List, Optional, Tuple
from contextlib import contextmanager

from config import DB_FILE, ALLOWED_TABLES

# Configure logging
logger = logging.getLogger(__name__)


@contextmanager
def get_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def run_query(query: str, params: Tuple = ()) -> bool:
    """
    Execute a write query (INSERT, UPDATE, DELETE).
    
    Args:
        query: SQL query string
        params: Query parameters
    
    Returns:
        True if successful, False otherwise
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Database error: {e}")
        return False


def run_transaction(queries: list) -> bool:
    """
    Execute multiple queries in a single transaction.
    
    Args:
        queries: List of tuples (query_string, params_tuple)
                 Example: [("INSERT INTO x VALUES (?, ?)", (1, 2)), ...]
    
    Returns:
        True if all queries successful, False otherwise (with rollback)
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            for query, params in queries:
                cursor.execute(query, params if params else ())
            
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Transaction error: {e}")
        # Connection context manager handles rollback on exception
        return False


def get_data(table: str, where: str = None, params: Tuple = (), 
             limit: int = None, order_by: str = None) -> pd.DataFrame:
    """
    Get data from a table as DataFrame.
    
    Args:
        table: Table name (must be in ALLOWED_TABLES)
        where: Optional WHERE clause (without WHERE keyword)
        params: Query parameters
        limit: Optional LIMIT
        order_by: Optional ORDER BY clause (without ORDER BY keyword)
    
    Returns:
        DataFrame with results
    """
    if table not in ALLOWED_TABLES:
        logger.warning(f"Table {table} not in allowed tables")
        return pd.DataFrame()
    
    try:
        query = f"SELECT * FROM {table}"
        
        if where:
            query += f" WHERE {where}"
        
        if order_by:
            query += f" ORDER BY {order_by}"
        
        if limit:
            query += f" LIMIT {limit}"
        
        with get_connection() as conn:
            result = pd.read_sql_query(query, conn, params=params)
            return result
    
    except Exception as e:
        logger.error(f"Error getting data from {table}: {e}")
        return pd.DataFrame()


def check_duplicate_id(id_value: str, table: str, id_column: str = "id") -> bool:
    """
    Check if an ID already exists in a table.
    
    Args:
        id_value: The ID value to check
        table: Table name
        id_column: Name of the ID column
    
    Returns:
        True if duplicate exists, False otherwise
    """
    if table not in ALLOWED_TABLES:
        return False
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT 1 FROM {table} WHERE {id_column} = ? LIMIT 1", (id_value,))
            return cursor.fetchone() is not None
    except:
        return False


def count_records(table: str, where: str = None, params: Tuple = ()) -> int:
    """
    Count records in a table.
    
    Args:
        table: Table name
        where: Optional WHERE clause
        params: Query parameters
    
    Returns:
        Record count
    """
    if table not in ALLOWED_TABLES:
        return 0
    
    try:
        query = f"SELECT COUNT(*) FROM {table}"
        if where:
            query += f" WHERE {where}"
        
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result[0] if result else 0
    except:
        return 0


def aggregate_sum(table: str, column: str, where: str = None, params: Tuple = ()) -> float:
    """
    Sum a column in a table.
    
    Args:
        table: Table name
        column: Column to sum
        where: Optional WHERE clause
        params: Query parameters
    
    Returns:
        Sum value
    """
    if table not in ALLOWED_TABLES:
        return 0.0
    
    try:
        query = f"SELECT COALESCE(SUM({column}), 0) FROM {table}"
        if where:
            query += f" WHERE {where}"
        
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            return float(result[0]) if result else 0.0
    except:
        return 0.0


def get_single_record(table: str, id_value: str, id_column: str = "id") -> Optional[dict]:
    """
    Get a single record by ID.
    
    Args:
        table: Table name
        id_value: The ID value
        id_column: Name of the ID column
    
    Returns:
        Dict with record data or None
    """
    if table not in ALLOWED_TABLES:
        return None
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table} WHERE {id_column} = ?", (id_value,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    except:
        return None


def update_record(table: str, id_value: str, updates: dict, id_column: str = "id") -> bool:
    """
    Update a record.
    
    Args:
        table: Table name
        id_value: The ID value
        updates: Dict of column: value updates
        id_column: Name of the ID column
    
    Returns:
        True if successful
    """
    if table not in ALLOWED_TABLES or not updates:
        return False
    
    try:
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [id_value]
        
        query = f"UPDATE {table} SET {set_clause} WHERE {id_column} = ?"
        
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Update error: {e}")
        return False


def delete_record(table: str, id_value: str, id_column: str = "id") -> bool:
    """
    Delete a record.
    
    Args:
        table: Table name
        id_value: The ID value
        id_column: Name of the ID column
    
    Returns:
        True if successful
    """
    if table not in ALLOWED_TABLES:
        return False
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {table} WHERE {id_column} = ?", (id_value,))
            conn.commit()
            return cursor.rowcount > 0
    except:
        return False


def execute_many(query: str, data: List[Tuple]) -> bool:
    """
    Execute a query with multiple parameter sets.
    
    Args:
        query: SQL query string
        data: List of parameter tuples
    
    Returns:
        True if successful
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, data)
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Execute many error: {e}")
        return False
