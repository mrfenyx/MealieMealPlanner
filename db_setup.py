#!/usr/bin/env python3
"""
Comprehensive database setup script for the Meal Planner application.
Handles initialization, migrations, and schema versioning.
"""
import sqlite3
import os
import shutil
import sys
from datetime import datetime
from logging_config import get_logger

logger = get_logger(__name__)

DB_PATH = "planner.db"
CURRENT_SCHEMA_VERSION = 2

def _get_schema_version(conn: sqlite3.Connection) -> int:
    """Get the current schema version from the database."""
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
        result = cursor.fetchone()
        return result[0] if result else 0
    except sqlite3.OperationalError:
        # Table doesn't exist yet
        return 0

def _set_schema_version(conn: sqlite3.Connection, version: int) -> None:
    """Set the schema version in the database."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
    """)
    cursor.execute(
        "INSERT OR REPLACE INTO schema_version (version, applied_at) VALUES (?, ?)",
        (version, datetime.now().isoformat())
    )

def _create_initial_schema(conn: sqlite3.Connection) -> None:
    """Create the initial database schema."""
    cursor = conn.cursor()
    
    # Create main tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS done_meals (
            meal_id INTEGER PRIMARY KEY,
            done_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shopping_list (
            ingredient_id TEXT PRIMARY KEY,
            ingredient_name TEXT
        )
    """)
    
    # Set initial schema version
    _set_schema_version(conn, CURRENT_SCHEMA_VERSION)
    
    logger.info("✅ Created initial database schema")

def _migrate_v0_to_v1(conn: sqlite3.Connection) -> None:
    """Migrate from version 0 to version 1 - fix ingredient_name typo."""
    cursor = conn.cursor()
    
    # Check if the typo exists
    cursor.execute("PRAGMA table_info(shopping_list)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if "ingridient_name" in columns:
        logger.info("Found typo in shopping_list table. Fixing...")
        
        # Create new table with correct schema
        cursor.execute("""
            CREATE TABLE shopping_list_new (
                ingredient_id TEXT PRIMARY KEY,
                ingredient_name TEXT
            )
        """)
        
        # Copy data from old table to new table
        cursor.execute("""
            INSERT INTO shopping_list_new (ingredient_id, ingredient_name)
            SELECT ingredient_id, ingridient_name 
            FROM shopping_list
        """)
        
        # Drop old table and rename new table
        cursor.execute("DROP TABLE shopping_list")
        cursor.execute("ALTER TABLE shopping_list_new RENAME TO shopping_list")
        
        logger.info("✅ Fixed shopping_list table schema")
    else:
        logger.info("✅ No typo found - shopping_list table schema is correct")

def _migrate_v1_to_v2(conn: sqlite3.Connection) -> None:
    """Migrate from version 1 to version 2 - add schema versioning."""
    logger.info("Adding schema versioning system...")
    _set_schema_version(conn, 2)
    logger.info("✅ Schema versioning system added")

def setup_database() -> int:
    """
    Complete database setup: initialization + migrations.
    Ensures data is preserved during upgrades.
    
    Returns:
        int: 0 for success, 1 for failure
    """
    logger.info("🚀 Starting database setup...")
    
    try:
        db_exists = os.path.exists(DB_PATH)
        
        # Create backup only if database will be changed
        backup_created = False
        if db_exists:
            # Check if migrations are needed
            with sqlite3.connect(DB_PATH) as conn:
                current_version = _get_schema_version(conn)
                if current_version < CURRENT_SCHEMA_VERSION:
                    backup_path = f"{DB_PATH}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    shutil.copy2(DB_PATH, backup_path)
                    logger.info(f"📦 Database backed up to {backup_path}")
                    backup_created = True

        with sqlite3.connect(DB_PATH) as conn:            
            # Create initial schema if needed
            if not db_exists:
                logger.info("📊 Database doesn't exist. Creating new database...")
                _create_initial_schema(conn)
                conn.commit()
                logger.info("✅ Database setup completed successfully!")
                return 0
            
            # Get current schema version
            current_version = _get_schema_version(conn)
            logger.info(f"📊 Current schema version: {current_version}")
            logger.info(f"📊 Target schema version: {CURRENT_SCHEMA_VERSION}")
            
            if current_version >= CURRENT_SCHEMA_VERSION:
                logger.info("✅ Database is already up to date")
                if backup_created:
                    logger.info("Backup was created but no changes were made.")
                return 0
            
            # Run migrations in sequence to preserve data
            if current_version < 1:
                logger.info("🔄 Running migration: v0 -> v1")
                _migrate_v0_to_v1(conn)
                _set_schema_version(conn, 1)
                current_version = 1
            
            if current_version < 2:
                logger.info("🔄 Running migration: v1 -> v2")
                _migrate_v1_to_v2(conn)
                current_version = 2
            
            conn.commit()
            logger.info(f"✅ Database setup completed successfully! Schema version: {current_version}")
            return 0
            
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        return 1

def get_schema_version() -> int:
    """
    Get the current schema version of the database.
    
    Returns:
        int: The current schema version, or 0 if not initialized
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            return _get_schema_version(conn)
    except sqlite3.Error as e:
        logger.error(f"Failed to get schema version: {e}")
        return 0

def check_schema_compatibility() -> bool:
    """
    Check if the database schema is compatible with the current code.
    
    Returns:
        bool: True if schema is compatible, False otherwise
    """
    try:
        current_version = get_schema_version()
        return current_version <= CURRENT_SCHEMA_VERSION
    except sqlite3.Error:
        return False

if __name__ == "__main__":
    sys.exit(setup_database())
