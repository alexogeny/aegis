"""
SQLite database driver.

Provides connectivity to SQLite databases using Python's built-in sqlite3 module.
Operations are run in a thread pool to avoid blocking the UI.
"""

import asyncio
import sqlite3
import time
from pathlib import Path

from .base import (
    DatabaseDriver,
    DriverType,
    ConnectionField,
    ColumnInfo,
    QueryResult,
    TableInfo,
    ColumnDef,
    IndexInfo,
)


class SQLiteDriver(DatabaseDriver):
    """SQLite database driver."""

    driver_type = DriverType.SQLITE
    display_name = 'SQLite'
    icon = '📁'
    default_port = 0
    supports_schemas = False
    supports_transactions = True
    supports_explain = True
    supports_cancel = False

    def __init__(self):
        super().__init__()
        self._db_path: Path | None = None

    @classmethod
    def get_connection_fields(cls) -> list[ConnectionField]:
        return [
            ConnectionField(
                name='database',
                label='Database File',
                field_type='file',
                required=True,
                placeholder='/path/to/database.db',
                tooltip='Path to the SQLite database file',
            ),
            ConnectionField(
                name='read_only',
                label='Read Only',
                field_type='checkbox',
                required=False,
                default=False,
                tooltip='Open database in read-only mode',
            ),
        ]

    async def connect(self, config: dict) -> bool:
        db_path = Path(config['database']).expanduser().resolve()

        if not db_path.exists():
            raise FileNotFoundError(f'Database file not found: {db_path}')

        self._db_path = db_path

        # Build connection URI
        uri = f'file:{db_path}'
        if config.get('read_only', False):
            uri += '?mode=ro'

        # Connect in thread pool since sqlite3 is synchronous
        loop = asyncio.get_event_loop()

        def _connect():
            conn = sqlite3.connect(uri, uri=True, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            # Enable foreign key support
            conn.execute('PRAGMA foreign_keys = ON')
            return conn

        self._connection = await loop.run_in_executor(None, _connect)
        self._connected = True
        return True

    async def disconnect(self) -> None:
        if self._connection:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._connection.close)
            self._connection = None
        self._connected = False
        self._db_path = None

    async def test_connection(self, config: dict) -> tuple[bool, str]:
        try:
            db_path = Path(config['database']).expanduser().resolve()

            if not db_path.exists():
                return False, f'File not found: {db_path}'

            if not db_path.is_file():
                return False, f'Not a file: {db_path}'

            # Try to open and read version
            conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
            version = conn.execute('SELECT sqlite_version()').fetchone()[0]

            # Get basic stats
            tables = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
            conn.close()

            size_mb = db_path.stat().st_size / (1024 * 1024)
            return True, f'SQLite {version}\n{tables} tables, {size_mb:.1f} MB'

        except sqlite3.DatabaseError as e:
            return False, f'Invalid database: {e}'
        except Exception as e:
            return False, str(e)

    async def execute(
        self,
        query: str,
        params: tuple | dict | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> QueryResult:
        if not self._connected:
            return QueryResult(
                columns=[],
                rows=[],
                row_count=0,
                error='Not connected to database',
            )

        loop = asyncio.get_event_loop()
        start = time.time()

        def _execute():
            cursor = self._connection.cursor()
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                # Check if this is a SELECT query
                if cursor.description:
                    rows = cursor.fetchall()
                    return rows, cursor.description, 0
                else:
                    # For INSERT/UPDATE/DELETE
                    self._connection.commit()
                    return [], None, cursor.rowcount
            except Exception as e:
                self._connection.rollback()
                raise e

        try:
            rows, description, affected = await loop.run_in_executor(None, _execute)
            execution_time = (time.time() - start) * 1000

            if not description:
                # Non-SELECT query
                return QueryResult(
                    columns=[],
                    rows=[],
                    row_count=0,
                    affected_rows=affected,
                    execution_time_ms=execution_time,
                )

            # Build column info
            columns = []
            for col in description:
                col_name = col[0]
                columns.append(
                    ColumnInfo(
                        name=col_name,
                        type_name='text',  # SQLite is dynamically typed
                        python_type=str,
                    )
                )

            # Convert Row objects to tuples
            row_tuples = [tuple(row) for row in rows]

            return QueryResult(
                columns=columns,
                rows=row_tuples,
                row_count=len(row_tuples),
                execution_time_ms=execution_time,
            )

        except sqlite3.Error as e:
            return QueryResult(
                columns=[],
                rows=[],
                row_count=0,
                error=str(e),
                execution_time_ms=(time.time() - start) * 1000,
            )

    async def get_schemas(self) -> list[str]:
        # SQLite doesn't have schemas
        return ['main']

    async def get_tables(self, schema: str | None = None) -> list[TableInfo]:
        query = """
            SELECT
                name,
                type
            FROM sqlite_master
            WHERE type IN ('table', 'view')
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """
        result = await self.execute(query)

        if not result.is_success:
            return []

        tables = []
        for row in result.rows:
            name, table_type = row[0], row[1]

            # Get row count for tables
            row_count = None
            if table_type == 'table':
                count_result = await self.execute(f'SELECT COUNT(*) FROM "{name}"')
                if count_result.is_success and count_result.rows:
                    row_count = count_result.rows[0][0]

            tables.append(
                TableInfo(
                    name=name,
                    schema='main',
                    table_type=table_type,
                    row_count=row_count,
                )
            )

        return tables

    async def get_columns(self, table: str, schema: str | None = None) -> list[ColumnDef]:
        result = await self.execute(f"PRAGMA table_info('{table}')")

        if not result.is_success:
            return []

        columns = []
        for row in result.rows:
            # PRAGMA table_info returns: cid, name, type, notnull, dflt_value, pk
            cid, name, data_type, notnull, default, pk = row

            columns.append(
                ColumnDef(
                    name=name,
                    data_type=data_type or 'TEXT',
                    nullable=not notnull,
                    default=default,
                    is_primary_key=bool(pk),
                    ordinal_position=cid,
                )
            )

        # Get foreign key info
        fk_result = await self.execute(f"PRAGMA foreign_key_list('{table}')")
        if fk_result.is_success:
            fk_columns = {row[3] for row in fk_result.rows}  # 'from' column
            for col in columns:
                if col.name in fk_columns:
                    col.is_foreign_key = True

        return columns

    async def get_table_preview(
        self,
        table: str,
        schema: str | None = None,
        limit: int = 100,
    ) -> QueryResult:
        return await self.execute(f'SELECT * FROM "{table}" LIMIT {limit}')

    async def get_indexes(self, table: str, schema: str | None = None) -> list[IndexInfo]:
        # Get index list
        result = await self.execute(f"PRAGMA index_list('{table}')")

        if not result.is_success:
            return []

        indexes = []
        for row in result.rows:
            # index_list returns: seq, name, unique, origin, partial
            _, name, unique, origin, _ = row

            # Get columns for this index
            col_result = await self.execute(f"PRAGMA index_info('{name}')")
            columns = [r[2] for r in col_result.rows] if col_result.is_success else []

            indexes.append(
                IndexInfo(
                    name=name,
                    columns=columns,
                    is_unique=bool(unique),
                    is_primary=(origin == 'pk'),
                    index_type='btree',  # SQLite uses B-tree
                )
            )

        return indexes

    async def explain_query(self, query: str) -> str:
        result = await self.execute(f'EXPLAIN QUERY PLAN {query}')

        if not result.is_success:
            return f'Error: {result.error}'

        lines = []
        for row in result.rows:
            # EXPLAIN QUERY PLAN returns: id, parent, notused, detail
            lines.append(row[3])

        return '\n'.join(lines)

    def quote_identifier(self, identifier: str) -> str:
        # SQLite uses double quotes for identifiers
        return f'"{identifier}"'
