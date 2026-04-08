import asyncio
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

from mcnexus.database.exceptions import (
    MigrationError,
    DatabaseConnectionError,
    MigrationDataError
)

class SQLiteMigrator:
    """
    Automates the migration of local SQLite databases to cloud databases 
    (MySQL, PostgreSQL, MongoDB).
    """

    @staticmethod
    async def get_tables(sqlite_cursor) -> List[str]:
        """Fetch all user tables from an SQLite database."""
        await sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        rows = await sqlite_cursor.fetchall()
        return [row[0] for row in rows]

    @staticmethod
    async def get_columns(sqlite_cursor, table_name: str) -> List[Dict[str, Any]]:
        """Fetch column definitions for a given table."""
        await sqlite_cursor.execute(f"PRAGMA table_info({table_name});")
        rows = await sqlite_cursor.fetchall()
        # Returns: cid, name, type, notnull, dflt_value, pk
        return [{"name": row[1], "type": row[2], "notnull": row[3], "pk": row[5]} for row in rows]

    @classmethod
    async def to_mysql(cls, sqlite_path: str, mysql_config: Dict[str, Any], batch_size: int = 500) -> Dict[str, Any]:
        """
        Migrates all tables and data from a local SQLite file to a MySQL database.
        
        :param sqlite_path: Path to the local .db file
        :param mysql_config: Dict with host, port, user, password, db
        :return: Migration statistics
        """
        import aiosqlite
        import aiomysql

        stats = {"tables": 0, "rows_migrated": 0}

        try:
            async with aiosqlite.connect(sqlite_path) as sl_db:
                # Convert aiosqlite rows to dictionaries
                sl_db.row_factory = aiosqlite.Row
                
                async with aiomysql.create_pool(**mysql_config) as pool:
                    async with pool.acquire() as my_conn:
                        async with my_conn.cursor() as my_cursor:
                            async with sl_db.cursor() as sl_cursor:
                                tables = await cls.get_tables(sl_cursor)
                                stats["tables"] = len(tables)

                                for table in tables:
                                    logger.info(f"Migrating table {table} to MySQL...")
                                    columns = await cls.get_columns(sl_cursor, table)
                                    
                                    # Create table in MySQL
                                    col_defs = []
                                    for col in columns:
                                        ctype = col["type"].upper()
                                        if ctype == "INTEGER": ctype = "INT"
                                        elif ctype == "REAL": ctype = "DOUBLE"
                                        elif ctype == "": ctype = "TEXT"
                                        
                                        pk = "PRIMARY KEY" if col["pk"] else ""
                                        nn = "NOT NULL" if col["notnull"] else ""
                                        col_defs.append(f"`{col['name']}` {ctype} {pk} {nn}".strip())
                                    
                                    create_sql = f"CREATE TABLE IF NOT EXISTS `{table}` ({', '.join(col_defs)});"
                                    await my_cursor.execute(create_sql)
                                    
                                    # Fetch and insert data
                                    await sl_cursor.execute(f"SELECT * FROM {table};")
                                    rows = await sl_cursor.fetchall()
                                    
                                    if not rows:
                                        continue
                                        
                                    col_names = [col["name"] for col in columns]
                                    placeholders = ", ".join(["%s"] * len(col_names))
                                    insert_sql = f"INSERT INTO `{table}` (`{'`, `'.join(col_names)}`) VALUES ({placeholders});"
                                    
                                    data_to_insert = [tuple(row) for row in rows]
                                    
                                    # Insert in batches
                                    for i in range(0, len(data_to_insert), batch_size):
                                        await my_cursor.executemany(insert_sql, data_to_insert[i:i+batch_size])
                                        stats["rows_migrated"] += len(data_to_insert[i:i+batch_size])
                                    
                                    await my_conn.commit()
            return stats
        except Exception as e:
            raise MigrationDataError(f"MySQL Migration failed: {e}")

    @classmethod
    async def to_postgres(cls, sqlite_path: str, pg_config: Dict[str, Any], batch_size: int = 500) -> Dict[str, Any]:
        """
        Migrates all tables and data from a local SQLite file to a PostgreSQL database.
        
        :param pg_config: Dict with host, port, user, password, database
        """
        import aiosqlite
        import asyncpg

        stats = {"tables": 0, "rows_migrated": 0}

        try:
            # We map the dict keys to asyncpg connect arguments
            dsn = f"postgresql://{pg_config['user']}:{pg_config['password']}@{pg_config['host']}:{pg_config.get('port', 5432)}/{pg_config.get('database', pg_config.get('db'))}"
            
            async with aiosqlite.connect(sqlite_path) as sl_db:
                pg_conn = await asyncpg.connect(dsn)
                
                try:
                    async with sl_db.cursor() as sl_cursor:
                        tables = await cls.get_tables(sl_cursor)
                        stats["tables"] = len(tables)

                        for table in tables:
                            logger.info(f"Migrating table {table} to PostgreSQL...")
                            columns = await cls.get_columns(sl_cursor, table)
                            
                            col_defs = []
                            for col in columns:
                                ctype = col["type"].upper()
                                if ctype == "REAL": ctype = "DOUBLE PRECISION"
                                elif "INT" in ctype: ctype = "INTEGER"
                                elif "VARCHAR" not in ctype and "TEXT" not in ctype: ctype = "TEXT"
                                
                                pk = "PRIMARY KEY" if col["pk"] else ""
                                nn = "NOT NULL" if col["notnull"] else ""
                                col_defs.append(f'"{col["name"]}" {ctype} {pk} {nn}'.strip())
                                
                            create_sql = f'CREATE TABLE IF NOT EXISTS "{table}" ({", ".join(col_defs)});'
                            await pg_conn.execute(create_sql)
                            
                            # Insert data
                            await sl_cursor.execute(f"SELECT * FROM {table};")
                            rows = await sl_cursor.fetchall()
                            
                            if not rows:
                                continue
                                
                            # Prepare asyncpg executemany
                            # asyncpg uses $1, $2 instead of ? or %s
                            placeholders = ", ".join([f"${i+1}" for i in range(len(columns))])
                            insert_sql = f'INSERT INTO "{table}" VALUES ({placeholders})'
                            
                            data_to_insert = [tuple(row) for row in rows]
                            
                            for i in range(0, len(data_to_insert), batch_size):
                                await pg_conn.executemany(insert_sql, data_to_insert[i:i+batch_size])
                                stats["rows_migrated"] += len(data_to_insert[i:i+batch_size])
                finally:
                    await pg_conn.close()
            return stats
        except Exception as e:
            raise MigrationDataError(f"PostgreSQL Migration failed: {e}")

    @classmethod
    async def to_mongodb(cls, sqlite_path: str, mongo_uri: str, database_name: str, batch_size: int = 500) -> Dict[str, Any]:
        """
        Migrates all tables and data from a local SQLite file to a MongoDB database.
        Each table becomes a collection. Each row becomes a JSON document.
        """
        import aiosqlite
        from motor.motor_asyncio import AsyncIOMotorClient

        stats = {"collections": 0, "documents_migrated": 0}

        try:
            client = AsyncIOMotorClient(mongo_uri)
            db = client[database_name]
            
            async with aiosqlite.connect(sqlite_path) as sl_db:
                sl_db.row_factory = aiosqlite.Row
                
                async with sl_db.cursor() as sl_cursor:
                    tables = await cls.get_tables(sl_cursor)
                    stats["collections"] = len(tables)

                    for table in tables:
                        logger.info(f"Migrating table {table} to MongoDB collection...")
                        collection = db[table]
                        
                        await sl_cursor.execute(f"SELECT * FROM {table};")
                        rows = await sl_cursor.fetchall()
                        
                        if not rows:
                            continue
                            
                        # Convert Row objects to dicts
                        documents = [dict(row) for row in rows]
                        
                        # Insert in batches
                        for i in range(0, len(documents), batch_size):
                            await collection.insert_many(documents[i:i+batch_size])
                            stats["documents_migrated"] += len(documents[i:i+batch_size])
                            
            client.close()
            return stats
        except Exception as e:
            raise MigrationDataError(f"MongoDB Migration failed: {e}")
