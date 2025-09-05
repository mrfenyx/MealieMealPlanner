import sqlite3
from datetime import datetime, UTC
from typing import List, Tuple, Optional, Union
from logging_config import get_logger

DB_PATH = "planner.db"
SCHEMA_VERSION = 2  # Increment when schema changes

logger = get_logger(__name__)

def init_db():
    """Initialize the database with proper schema versioning and migrations."""
    from db_setup import setup_database
    result = setup_database()
    if result != 0:
        raise RuntimeError("Database setup failed")
    logger.info("Database initialization completed successfully")

def mark_done(meal_id: Union[int, str]) -> bool:
    """
    Mark a meal as done.
    
    Args:
        meal_id: The ID of the meal to mark as done
        
    Returns:
        bool: True if the meal was marked as done, False if it was already done
        
    Raises:
        ValueError: If meal_id is invalid
        sqlite3.Error: If database operation fails
    """
    if meal_id is None:
        raise ValueError("meal_id cannot be None")
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Check if already done
            cursor.execute("SELECT 1 FROM done_meals WHERE meal_id = ?", (meal_id,))
            if cursor.fetchone():
                logger.info(f"Meal {meal_id} is already marked as done")
                return False
            
            cursor.execute(
                "INSERT INTO done_meals (meal_id, done_at) VALUES (?, ?)",
                (meal_id, datetime.now(UTC).isoformat())
            )
            conn.commit()
            logger.info(f"Marked meal {meal_id} as done")
            return True
            
    except sqlite3.Error as e:
        logger.error(f"Failed to mark meal {meal_id} as done: {e}")
        raise

def is_done(meal_id: Union[int, str]) -> bool:
    """
    Check if a meal is marked as done.
    
    Args:
        meal_id: The ID of the meal to check
        
    Returns:
        bool: True if the meal is marked as done, False otherwise
        
    Raises:
        ValueError: If meal_id is invalid
        sqlite3.Error: If database operation fails
    """
    if meal_id is None:
        raise ValueError("meal_id cannot be None")
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM done_meals WHERE meal_id = ?", (meal_id,))
            return cursor.fetchone() is not None
            
    except sqlite3.Error as e:
        logger.error(f"Failed to check if meal {meal_id} is done: {e}")
        raise

def get_all_done_ids() -> List[Union[int, str]]:
    """
    Get all meal IDs that are marked as done.
    
    Returns:
        List[Union[int, str]]: List of meal IDs that are marked as done
        
    Raises:
        sqlite3.Error: If database operation fails
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT meal_id FROM done_meals ORDER BY done_at DESC")
            return [row[0] for row in cursor.fetchall()]
            
    except sqlite3.Error as e:
        logger.error(f"Failed to get all done meal IDs: {e}")
        raise

def re_add(meal_id: Union[int, str]) -> bool:
    """
    Remove a meal from the done list (re-add it to the meal planner).
    
    Args:
        meal_id: The ID of the meal to re-add
        
    Returns:
        bool: True if the meal was removed from done list, False if it wasn't in the done list
        
    Raises:
        ValueError: If meal_id is invalid
        sqlite3.Error: If database operation fails
    """
    if meal_id is None:
        raise ValueError("meal_id cannot be None")
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM done_meals WHERE meal_id = ?", (meal_id,))
            rows_affected = cursor.rowcount
            conn.commit()
            
            if rows_affected > 0:
                logger.info(f"Re-added meal {meal_id} to meal planner")
                return True
            else:
                logger.info(f"Meal {meal_id} was not in the done list")
                return False
                
    except sqlite3.Error as e:
        logger.error(f"Failed to re-add meal {meal_id}: {e}")
        raise

def get_shopping_ids() -> List[str]:
    """
    Get all ingredient IDs from the shopping list.
    
    Returns:
        List[str]: List of ingredient IDs in the shopping list
        
    Raises:
        sqlite3.Error: If database operation fails
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ingredient_id FROM shopping_list ORDER BY ingredient_name")
            return [row[0] for row in cursor.fetchall()]
            
    except sqlite3.Error as e:
        logger.error(f"Failed to get shopping list IDs: {e}")
        raise

def add_shopping_items(items: List[Tuple[str, str]]) -> int:
    """
    Replace all items in the shopping list with new items.
    
    Args:
        items: List of tuples containing (ingredient_id, ingredient_name)
        
    Returns:
        int: Number of items added to the shopping list
        
    Raises:
        ValueError: If items is invalid
        sqlite3.Error: If database operation fails
    """
    if items is None:
        raise ValueError("items cannot be None")
    
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    
    # Validate items format
    for i, item in enumerate(items):
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise ValueError(f"Item at index {i} must be a tuple/list of length 2")
        if not isinstance(item[0], str) or not isinstance(item[1], str):
            raise ValueError(f"Item at index {i} must contain two strings")
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Use a transaction to ensure atomicity
            cursor.execute("BEGIN TRANSACTION")
            
            try:
                # Clear existing items
                cursor.execute("DELETE FROM shopping_list")
                
                # Insert new items
                if items:  # Only insert if there are items
                    cursor.executemany(
                        "INSERT INTO shopping_list (ingredient_id, ingredient_name) VALUES (?, ?)",
                        items
                    )
                
                conn.commit()
                logger.info(f"Updated shopping list with {len(items)} items")
                return len(items)
                
            except Exception as e:
                conn.rollback()
                raise e
                
    except sqlite3.Error as e:
        logger.error(f"Failed to update shopping list: {e}")
        raise

# Import schema versioning functions from db_setup.py
from db_setup import get_schema_version, check_schema_compatibility