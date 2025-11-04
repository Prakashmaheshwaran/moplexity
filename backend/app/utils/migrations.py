"""
Auto-migration utilities for database schema changes.
Handles adding missing columns and updating schema based on SQLAlchemy models.
"""
from sqlalchemy import inspect, text, Column
from sqlalchemy.ext.asyncio import AsyncEngine


async def check_column_exists(engine: AsyncEngine, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table"""
    async with engine.connect() as conn:
        # For SQLite, we query the sqlite_master table
        if 'sqlite' in str(engine.url):
            result = await conn.execute(
                text(f"PRAGMA table_info({table_name})")
            )
            columns = result.fetchall()
            return any(col[1] == column_name for col in columns)
        else:
            # For other databases, use information_schema
            result = await conn.execute(
                text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = :table_name AND column_name = :column_name
                """),
                {"table_name": table_name, "column_name": column_name}
            )
            return result.fetchone() is not None


async def check_table_exists(engine: AsyncEngine, table_name: str) -> bool:
    """Check if a table exists"""
    async with engine.connect() as conn:
        if 'sqlite' in str(engine.url):
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name=:name"),
                {"name": table_name}
            )
            return result.fetchone() is not None
        else:
            result = await conn.execute(
                text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name = :table_name
                """),
                {"table_name": table_name}
            )
            return result.fetchone() is not None


async def add_column(engine: AsyncEngine, table_name: str, column: Column) -> bool:
    """Add a column to a table if it doesn't exist"""
    column_name = column.name
    
    # Check if column already exists
    if await check_column_exists(engine, table_name, column_name):
        print(f"Column {table_name}.{column_name} already exists, skipping")
        return False
    
    # Build ALTER TABLE statement
    column_type = column.type.compile(engine.dialect)
    nullable = "NULL" if column.nullable else "NOT NULL"
    
    # Handle default values
    default_clause = ""
    if column.server_default is not None:
        # server_default can be a string or a SQL expression
        if hasattr(column.server_default, 'arg'):
            default_value = column.server_default.arg
            if isinstance(default_value, str):
                # If it's a SQL function like CURRENT_TIMESTAMP, use as-is
                if default_value.upper().startswith(('CURRENT_', 'NOW(', 'DATETIME(')):
                    default_clause = f" DEFAULT {default_value}"
                else:
                    # Otherwise, quote it
                    default_clause = f" DEFAULT '{default_value}'"
            else:
                default_clause = f" DEFAULT {default_value}"
    elif column.default is not None:
        if hasattr(column.default, 'arg'):
            default_value = column.default.arg
            if isinstance(default_value, str):
                default_clause = f" DEFAULT '{default_value}'"
            else:
                default_clause = f" DEFAULT {default_value}"
    
    alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} {nullable}{default_clause}"
    
    try:
        async with engine.begin() as conn:
            await conn.execute(text(alter_sql))
            print(f"✓ Added column {table_name}.{column_name}")
            return True
    except Exception as e:
        print(f"✗ Error adding column {table_name}.{column_name}: {e}")
        raise


async def add_foreign_key_constraint(engine: AsyncEngine, table_name: str, column_name: str, 
                                     referenced_table: str, referenced_column: str = "id") -> bool:
    """Add a foreign key constraint (SQLite limited support)"""
    if 'sqlite' in str(engine.url):
        # SQLite has limited ALTER TABLE support
        # Foreign keys are typically defined at table creation
        # We'll check if FK exists by examining the table schema
        async with engine.connect() as conn:
            result = await conn.execute(
                text(f"PRAGMA foreign_key_list({table_name})")
            )
            fks = result.fetchall()
            # Check if FK already exists
            for fk in fks:
                if fk[3] == column_name and fk[2] == referenced_table:
                    print(f"Foreign key {table_name}.{column_name} -> {referenced_table}.{referenced_column} already exists")
                    return False
            
            # SQLite doesn't support adding FKs via ALTER TABLE easily
            # We'll just log a warning - the FK will be enforced at application level
            print(f"Note: SQLite foreign key {table_name}.{column_name} -> {referenced_table}.{referenced_column} "
                  f"should be defined at table creation. FK relationship is handled at application level.")
            return False
    else:
        # For other databases, add FK constraint
        constraint_name = f"fk_{table_name}_{column_name}"
        try:
            async with engine.begin() as conn:
                await conn.execute(
                    text(f"""
                        ALTER TABLE {table_name} 
                        ADD CONSTRAINT {constraint_name} 
                        FOREIGN KEY ({column_name}) 
                        REFERENCES {referenced_table}({referenced_column})
                    """)
                )
                print(f"✓ Added foreign key constraint {constraint_name}")
                return True
        except Exception as e:
            print(f"⚠ Could not add foreign key constraint {constraint_name}: {e}")
            return False


async def drop_table_if_exists(engine: AsyncEngine, table_name: str) -> bool:
    """Drop a table if it exists"""
    if not await check_table_exists(engine, table_name):
        return False
    
    try:
        async with engine.begin() as conn:
            await conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
            print(f"✓ Dropped table {table_name}")
            return True
    except Exception as e:
        print(f"✗ Error dropping table {table_name}: {e}")
        raise


async def migrate_schema(engine: AsyncEngine) -> None:
    """
    Auto-migrate database schema by comparing existing tables with SQLAlchemy models
    and adding missing columns.
    """
    from app.base import Base
    from app.models import Conversation, Message, Source, SearchCache, LLMModel
    
    print("Starting schema migration...")
    
    # Special handling for llm_models table - drop and recreate if it has old schema
    if await check_table_exists(engine, 'llm_models'):
        # Check if it has old columns (provider_id or display_name) or missing new columns (api_key)
        has_old_schema = await check_column_exists(engine, 'llm_models', 'provider_id') or \
                         await check_column_exists(engine, 'llm_models', 'display_name')
        missing_new_schema = not await check_column_exists(engine, 'llm_models', 'api_key')
        
        if has_old_schema or missing_new_schema:
            print("Detected old llm_models schema, dropping and recreating...")
            # Drop old llm_providers table if it exists
            await drop_table_if_exists(engine, 'llm_providers')
            # Drop old llm_models table
            await drop_table_if_exists(engine, 'llm_models')
    
    # Get all models
    models = {
        'conversations': Conversation,
        'messages': Message,
        'sources': Source,
        'search_cache': SearchCache,
        'llm_models': LLMModel,
    }
    
    # Map of foreign keys: (table, column) -> (referenced_table, referenced_column)
    foreign_keys = {
        ('conversations', 'selected_model_id'): ('llm_models', 'id'),
        ('messages', 'conversation_id'): ('conversations', 'id'),
        ('sources', 'message_id'): ('messages', 'id'),
    }
    
    for table_name, model_class in models.items():
        # Check if table exists
        if not await check_table_exists(engine, table_name):
            print(f"Table {table_name} does not exist, will be created by create_all()")
            continue
        
        # Get columns from model
        mapper = inspect(model_class)
        model_columns = {col.key: col for col in mapper.columns}
        
        # Check each column
        for column_name, column in model_columns.items():
            if not await check_column_exists(engine, table_name, column_name):
                print(f"Column {table_name}.{column_name} is missing, adding...")
                try:
                    await add_column(engine, table_name, column)
                    
                    # Try to add foreign key if this column has one
                    fk_key = (table_name, column_name)
                    if fk_key in foreign_keys:
                        ref_table, ref_column = foreign_keys[fk_key]
                        await add_foreign_key_constraint(engine, table_name, column_name, ref_table, ref_column)
                except Exception as e:
                    print(f"✗ Failed to add column {table_name}.{column_name}: {e}")
                    # Continue with other columns
            else:
                pass  # Column exists, skip
    
    print("Schema migration completed")

