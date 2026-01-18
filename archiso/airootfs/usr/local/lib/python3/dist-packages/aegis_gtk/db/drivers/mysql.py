"""
MySQL/MariaDB database driver.

Provides async connectivity to MySQL and MariaDB databases using aiomysql.
"""

import time
from typing import Any

from .base import (
    DatabaseDriver,
    DriverType,
    ConnectionField,
    ColumnInfo,
    QueryResult,
    TableInfo,
    ColumnDef,
    IndexInfo,
    ForeignKeyInfo,
)

# aiomysql is optional - imported at runtime
aiomysql = None


def _ensure_aiomysql():
    """Lazily import aiomysql."""
    global aiomysql
    if aiomysql is None:
        try:
            import aiomysql as _aiomysql

            aiomysql = _aiomysql
        except ImportError as err:
            raise ImportError('aiomysql is required for MySQL support. Install it with: pip install aiomysql') from err


class MySQLDriver(DatabaseDriver):
    """MySQL/MariaDB database driver using aiomysql."""

    driver_type = DriverType.MYSQL
    display_name = 'MySQL / MariaDB'
    icon = '🐬'
    default_port = 3306
    supports_schemas = True  # MySQL uses databases as schemas
    supports_transactions = True
    supports_explain = True
    supports_cancel = True

    def __init__(self):
        super().__init__()
        self._current_schema = None
        self._pool = None

    @classmethod
    def get_connection_fields(cls) -> list[ConnectionField]:
        return [
            ConnectionField(
                name='host',
                label='Host',
                field_type='text',
                required=True,
                default='localhost',
                placeholder='localhost or IP address',
            ),
            ConnectionField(
                name='port',
                label='Port',
                field_type='number',
                required=True,
                default=3306,
            ),
            ConnectionField(
                name='database',
                label='Database',
                field_type='text',
                required=True,
                placeholder='Database name',
            ),
            ConnectionField(
                name='username',
                label='Username',
                field_type='text',
                required=True,
                default='root',
            ),
            ConnectionField(
                name='password',
                label='Password',
                field_type='password',
                required=False,
                placeholder='Leave empty for no password',
            ),
            ConnectionField(
                name='ssl',
                label='Use SSL',
                field_type='checkbox',
                required=False,
                default=False,
                tooltip='Enable SSL/TLS encrypted connection',
            ),
        ]

    async def connect(self, config: dict) -> bool:
        _ensure_aiomysql()

        ssl_ctx = None
        if config.get('ssl', False):
            import ssl

            ssl_ctx = ssl.create_default_context()

        self._pool = await aiomysql.create_pool(
            host=config['host'],
            port=config.get('port', 3306),
            db=config['database'],
            user=config['username'],
            password=config.get('password', ''),
            ssl=ssl_ctx,
            autocommit=True,
            minsize=1,
            maxsize=5,
        )
        self._connected = True
        self._current_schema = config['database']
        return True

    async def disconnect(self) -> None:
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()
            self._pool = None
        self._connected = False

    async def test_connection(self, config: dict) -> tuple[bool, str]:
        _ensure_aiomysql()

        try:
            ssl_ctx = None
            if config.get('ssl', False):
                import ssl

                ssl_ctx = ssl.create_default_context()

            conn = await aiomysql.connect(
                host=config['host'],
                port=config.get('port', 3306),
                db=config['database'],
                user=config['username'],
                password=config.get('password', ''),
                ssl=ssl_ctx,
                connect_timeout=10,
            )

            async with conn.cursor() as cur:
                await cur.execute('SELECT VERSION()')
                version = await cur.fetchone()

            conn.close()

            return True, version[0] if version else 'Connected'

        except Exception as e:
            return False, str(e)

    async def execute(
        self,
        query: str,
        params: tuple | dict | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> QueryResult:
        if not self._connected or not self._pool:
            return QueryResult(
                columns=[],
                rows=[],
                row_count=0,
                error='Not connected to database',
            )

        start = time.time()

        try:
            async with self._pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    # Execute query
                    if params:
                        await cur.execute(query, params)
                    else:
                        await cur.execute(query)

                    # Fetch all results
                    records = await cur.fetchall()
                    description = cur.description

                    execution_time = (time.time() - start) * 1000

                    if not records or not description:
                        return QueryResult(
                            columns=[],
                            rows=[],
                            row_count=cur.rowcount if cur.rowcount >= 0 else 0,
                            execution_time_ms=execution_time,
                        )

                    # Build column info
                    columns = []
                    for col in description:
                        columns.append(
                            ColumnInfo(
                                name=col[0],
                                type_name=self._get_type_name(col[1]),
                                python_type=str,
                            )
                        )

                    # Convert dict records to tuples
                    rows = [tuple(r.values()) for r in records]

                    return QueryResult(
                        columns=columns,
                        rows=rows,
                        row_count=len(rows),
                        execution_time_ms=execution_time,
                    )

        except Exception as e:
            return QueryResult(
                columns=[],
                rows=[],
                row_count=0,
                error=str(e),
                execution_time_ms=(time.time() - start) * 1000,
            )

    def _get_type_name(self, type_code: int) -> str:
        """Map MySQL type codes to type names."""
        # Common MySQL field type codes
        type_map = {
            0: 'DECIMAL',
            1: 'TINYINT',
            2: 'SMALLINT',
            3: 'INT',
            4: 'FLOAT',
            5: 'DOUBLE',
            6: 'NULL',
            7: 'TIMESTAMP',
            8: 'BIGINT',
            9: 'MEDIUMINT',
            10: 'DATE',
            11: 'TIME',
            12: 'DATETIME',
            13: 'YEAR',
            15: 'VARCHAR',
            16: 'BIT',
            245: 'JSON',
            246: 'DECIMAL',
            252: 'BLOB',
            253: 'VARCHAR',
            254: 'CHAR',
        }
        return type_map.get(type_code, 'UNKNOWN')

    async def get_schemas(self) -> list[str]:
        """Get list of databases (MySQL uses databases as schemas)."""
        query = 'SHOW DATABASES'
        result = await self.execute(query)

        if not result.is_success:
            return [self._current_schema] if self._current_schema else []

        # Filter out system databases
        system_dbs = {'information_schema', 'mysql', 'performance_schema', 'sys'}
        return [row[0] for row in result.rows if row[0] not in system_dbs]

    async def get_tables(self, schema: str | None = None) -> list[TableInfo]:
        schema = schema or self._current_schema

        if not schema:
            return []

        query = """
            SELECT
                TABLE_NAME,
                TABLE_TYPE,
                TABLE_ROWS,
                DATA_LENGTH + INDEX_LENGTH as size_bytes,
                TABLE_COMMENT
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = %s
            ORDER BY TABLE_NAME
        """
        result = await self.execute(query, (schema,))

        if not result.is_success:
            return []

        tables = []
        for row in result.rows:
            name, table_type, row_count, size_bytes, comment = row
            tables.append(
                TableInfo(
                    name=name,
                    schema=schema,
                    table_type='view' if table_type == 'VIEW' else 'table',
                    row_count=int(row_count) if row_count else None,
                    size_bytes=int(size_bytes) if size_bytes else None,
                    comment=comment if comment else None,
                )
            )

        return tables

    async def get_columns(self, table: str, schema: str | None = None) -> list[ColumnDef]:
        schema = schema or self._current_schema

        if not schema:
            return []

        query = """
            SELECT
                COLUMN_NAME,
                COLUMN_TYPE,
                IS_NULLABLE = 'YES' as nullable,
                COLUMN_DEFAULT,
                ORDINAL_POSITION,
                COLUMN_KEY = 'PRI' as is_primary,
                COLUMN_KEY = 'UNI' as is_unique,
                COLUMN_COMMENT
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION
        """
        result = await self.execute(query, (schema, table))

        if not result.is_success:
            return []

        columns = []
        for row in result.rows:
            (name, data_type, nullable, default, ordinal, is_primary, is_unique, comment) = row

            columns.append(
                ColumnDef(
                    name=name,
                    data_type=data_type,
                    nullable=bool(nullable),
                    default_value=default,
                    is_primary_key=bool(is_primary),
                    is_unique=bool(is_unique),
                    ordinal_position=ordinal,
                    comment=comment if comment else None,
                )
            )

        # Get foreign key info
        fk_query = """
            SELECT
                COLUMN_NAME,
                CONCAT(REFERENCED_TABLE_SCHEMA, '.', REFERENCED_TABLE_NAME, '.', REFERENCED_COLUMN_NAME) as ref
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = %s
                AND TABLE_NAME = %s
                AND REFERENCED_TABLE_NAME IS NOT NULL
        """
        fk_result = await self.execute(fk_query, (schema, table))

        if fk_result.is_success:
            fk_map = {row[0]: row[1] for row in fk_result.rows}
            for col in columns:
                if col.name in fk_map:
                    col.is_foreign_key = True
                    col.references = fk_map[col.name]

        return columns

    async def get_table_preview(
        self,
        table: str,
        schema: str | None = None,
        limit: int = 100,
    ) -> QueryResult:
        schema = schema or self._current_schema
        quoted_table = f'`{schema}`.`{table}`'
        return await self.execute(f'SELECT * FROM {quoted_table} LIMIT {limit}')

    async def get_indexes(self, table: str, schema: str | None = None) -> list[IndexInfo]:
        schema = schema or self._current_schema

        if not schema:
            return []

        query = """
            SELECT
                INDEX_NAME,
                GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) as columns,
                NOT NON_UNIQUE as is_unique,
                INDEX_NAME = 'PRIMARY' as is_primary,
                INDEX_TYPE
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            GROUP BY INDEX_NAME, NON_UNIQUE, INDEX_TYPE
            ORDER BY INDEX_NAME
        """
        result = await self.execute(query, (schema, table))

        if not result.is_success:
            return []

        return [
            IndexInfo(
                name=row[0],
                columns=row[1].split(',') if row[1] else [],
                is_unique=bool(row[2]),
                is_primary=bool(row[3]),
                index_type=row[4],
            )
            for row in result.rows
        ]

    async def get_foreign_keys(self, table: str, schema: str | None = None) -> list[ForeignKeyInfo]:
        schema = schema or self._current_schema

        if not schema:
            return []

        query = """
            SELECT
                CONSTRAINT_NAME,
                GROUP_CONCAT(COLUMN_NAME ORDER BY ORDINAL_POSITION) as columns,
                CONCAT(REFERENCED_TABLE_SCHEMA, '.', REFERENCED_TABLE_NAME) as ref_table,
                GROUP_CONCAT(REFERENCED_COLUMN_NAME ORDER BY ORDINAL_POSITION) as ref_columns
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = %s
                AND TABLE_NAME = %s
                AND REFERENCED_TABLE_NAME IS NOT NULL
            GROUP BY CONSTRAINT_NAME, REFERENCED_TABLE_SCHEMA, REFERENCED_TABLE_NAME
        """
        result = await self.execute(query, (schema, table))

        if not result.is_success:
            return []

        # Get update/delete rules
        rules_query = """
            SELECT
                CONSTRAINT_NAME,
                UPDATE_RULE,
                DELETE_RULE
            FROM information_schema.REFERENTIAL_CONSTRAINTS
            WHERE CONSTRAINT_SCHEMA = %s
                AND TABLE_NAME = %s
        """
        rules_result = await self.execute(rules_query, (schema, table))
        rules_map = {}
        if rules_result.is_success:
            rules_map = {row[0]: (row[1], row[2]) for row in rules_result.rows}

        return [
            ForeignKeyInfo(
                name=row[0],
                columns=row[1].split(',') if row[1] else [],
                referenced_table=row[2],
                referenced_columns=row[3].split(',') if row[3] else [],
                on_update=rules_map.get(row[0], ('NO ACTION', 'NO ACTION'))[0],
                on_delete=rules_map.get(row[0], ('NO ACTION', 'NO ACTION'))[1],
            )
            for row in result.rows
        ]

    async def explain_query(self, query: str) -> str:
        result = await self.execute(f'EXPLAIN {query}')

        if not result.is_success:
            return f'Error: {result.error}'

        # Format as table
        if not result.columns or not result.rows:
            return 'No execution plan available'

        lines = []
        headers = [col.name for col in result.columns]
        lines.append(' | '.join(headers))
        lines.append('-' * len(lines[0]))

        for row in result.rows:
            lines.append(' | '.join(str(v) if v is not None else 'NULL' for v in row))

        return '\n'.join(lines)

    async def cancel_query(self) -> bool:
        # MySQL doesn't have a direct way to cancel queries from the same connection
        # Would need to use KILL QUERY from a separate connection
        return False

    async def set_schema(self, schema: str) -> bool:
        """Switch to a different database."""
        if self._pool:
            try:
                async with self._pool.acquire() as conn:
                    await conn.select_db(schema)
                    self._current_schema = schema
                return True
            except Exception:
                return False
        return False

    def quote_identifier(self, identifier: str) -> str:
        return f'`{identifier}`'
