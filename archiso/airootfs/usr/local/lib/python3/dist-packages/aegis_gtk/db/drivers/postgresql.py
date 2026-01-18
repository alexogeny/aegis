"""
PostgreSQL database driver.

Provides async connectivity to PostgreSQL databases using asyncpg.
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

# asyncpg is optional - imported at runtime
asyncpg = None


def _ensure_asyncpg():
    """Lazily import asyncpg."""
    global asyncpg
    if asyncpg is None:
        try:
            import asyncpg as _asyncpg

            asyncpg = _asyncpg
        except ImportError as err:
            raise ImportError(
                'asyncpg is required for PostgreSQL support. Install it with: pip install asyncpg'
            ) from err


class PostgreSQLDriver(DatabaseDriver):
    """PostgreSQL database driver using asyncpg."""

    driver_type = DriverType.POSTGRESQL
    display_name = 'PostgreSQL'
    icon = '🐘'
    default_port = 5432
    supports_schemas = True
    supports_transactions = True
    supports_explain = True
    supports_cancel = True

    def __init__(self):
        super().__init__()
        self._current_schema = 'public'

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
                default=5432,
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
            ),
            ConnectionField(
                name='password',
                label='Password',
                field_type='password',
                required=False,
                placeholder='Leave empty for no password',
            ),
            ConnectionField(
                name='ssl_mode',
                label='SSL Mode',
                field_type='dropdown',
                required=False,
                default='prefer',
                options=['disable', 'prefer', 'require', 'verify-full'],
                tooltip='SSL connection mode',
            ),
        ]

    async def connect(self, config: dict) -> bool:
        _ensure_asyncpg()

        ssl_context = None
        ssl_mode = config.get('ssl_mode', 'prefer')

        if ssl_mode in ('require', 'verify-full'):
            import ssl

            ssl_context = ssl.create_default_context()
            if ssl_mode == 'require':
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

        self._connection = await asyncpg.connect(
            host=config['host'],
            port=config.get('port', 5432),
            database=config['database'],
            user=config['username'],
            password=config.get('password', ''),
            ssl=ssl_context if ssl_mode != 'disable' else False,
        )
        self._connected = True
        self._current_schema = 'public'
        return True

    async def disconnect(self) -> None:
        if self._connection:
            await self._connection.close()
            self._connection = None
        self._connected = False

    async def test_connection(self, config: dict) -> tuple[bool, str]:
        _ensure_asyncpg()

        try:
            ssl_mode = config.get('ssl_mode', 'prefer')
            ssl_context = None

            if ssl_mode in ('require', 'verify-full'):
                import ssl

                ssl_context = ssl.create_default_context()
                if ssl_mode == 'require':
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE

            conn = await asyncpg.connect(
                host=config['host'],
                port=config.get('port', 5432),
                database=config['database'],
                user=config['username'],
                password=config.get('password', ''),
                ssl=ssl_context if ssl_mode != 'disable' else False,
                timeout=10,
            )

            version = await conn.fetchval('SELECT version()')
            await conn.close()

            return True, version

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

        start = time.time()

        try:
            # Execute query
            if params:
                if isinstance(params, dict):
                    # Convert named params to positional for asyncpg
                    records = await self._connection.fetch(query, *params.values())
                else:
                    records = await self._connection.fetch(query, *params)
            else:
                records = await self._connection.fetch(query)

            execution_time = (time.time() - start) * 1000

            if not records:
                return QueryResult(
                    columns=[],
                    rows=[],
                    row_count=0,
                    execution_time_ms=execution_time,
                )

            # Build column info from first record
            columns = []
            for key in records[0].keys():
                value = records[0][key]
                python_type = type(value) if value is not None else str
                type_name = self._get_type_name(python_type)
                columns.append(
                    ColumnInfo(
                        name=key,
                        type_name=type_name,
                        python_type=python_type,
                    )
                )

            # Convert records to tuples
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

    def _get_type_name(self, python_type: type) -> str:
        """Map Python types to SQL type names."""
        type_map = {
            int: 'integer',
            float: 'double precision',
            str: 'text',
            bool: 'boolean',
            bytes: 'bytea',
        }
        return type_map.get(python_type, 'unknown')

    async def get_schemas(self) -> list[str]:
        query = """
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
            ORDER BY schema_name
        """
        result = await self.execute(query)

        if not result.is_success:
            return ['public']

        return [row[0] for row in result.rows]

    async def get_tables(self, schema: str | None = None) -> list[TableInfo]:
        schema = schema or self._current_schema or 'public'

        query = """
            SELECT
                t.table_name,
                t.table_type,
                COALESCE(
                    (SELECT reltuples::bigint FROM pg_class
                     WHERE relname = t.table_name
                       AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = t.table_schema)),
                    0
                ) as row_estimate,
                pg_total_relation_size(
                    quote_ident(t.table_schema) || '.' || quote_ident(t.table_name)
                ) as size_bytes,
                obj_description(
                    (quote_ident(t.table_schema) || '.' || quote_ident(t.table_name))::regclass
                ) as comment
            FROM information_schema.tables t
            WHERE t.table_schema = $1
            ORDER BY t.table_name
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
                    size_bytes=size_bytes,
                    comment=comment,
                )
            )

        return tables

    async def get_columns(self, table: str, schema: str | None = None) -> list[ColumnDef]:
        schema = schema or self._current_schema or 'public'

        query = """
            SELECT
                c.column_name,
                c.data_type,
                c.is_nullable = 'YES' as nullable,
                c.column_default,
                c.ordinal_position,
                EXISTS(
                    SELECT 1 FROM information_schema.table_constraints tc
                    JOIN information_schema.constraint_column_usage ccu
                        ON tc.constraint_name = ccu.constraint_name
                        AND tc.table_schema = ccu.table_schema
                    WHERE tc.constraint_type = 'PRIMARY KEY'
                        AND tc.table_schema = c.table_schema
                        AND tc.table_name = c.table_name
                        AND ccu.column_name = c.column_name
                ) as is_primary,
                EXISTS(
                    SELECT 1 FROM information_schema.table_constraints tc
                    JOIN information_schema.constraint_column_usage ccu
                        ON tc.constraint_name = ccu.constraint_name
                        AND tc.table_schema = ccu.table_schema
                    WHERE tc.constraint_type = 'UNIQUE'
                        AND tc.table_schema = c.table_schema
                        AND tc.table_name = c.table_name
                        AND ccu.column_name = c.column_name
                ) as is_unique,
                col_description(
                    (quote_ident(c.table_schema) || '.' || quote_ident(c.table_name))::regclass,
                    c.ordinal_position
                ) as comment
            FROM information_schema.columns c
            WHERE c.table_schema = $1 AND c.table_name = $2
            ORDER BY c.ordinal_position
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
                    nullable=nullable,
                    default=default,
                    is_primary_key=is_primary,
                    is_unique=is_unique,
                    ordinal_position=ordinal,
                    comment=comment,
                )
            )

        # Get foreign key info
        fk_query = """
            SELECT
                kcu.column_name,
                ccu.table_schema || '.' || ccu.table_name || '.' || ccu.column_name as references
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = $1
                AND tc.table_name = $2
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
        schema = schema or self._current_schema or 'public'
        quoted_table = f'"{schema}"."{table}"'
        return await self.execute(f'SELECT * FROM {quoted_table} LIMIT {limit}')

    async def get_indexes(self, table: str, schema: str | None = None) -> list[IndexInfo]:
        schema = schema or self._current_schema or 'public'

        query = """
            SELECT
                i.relname as index_name,
                array_agg(a.attname ORDER BY k.n) as columns,
                ix.indisunique as is_unique,
                ix.indisprimary as is_primary,
                am.amname as index_type
            FROM pg_index ix
            JOIN pg_class i ON i.oid = ix.indexrelid
            JOIN pg_class t ON t.oid = ix.indrelid
            JOIN pg_namespace n ON n.oid = t.relnamespace
            JOIN pg_am am ON am.oid = i.relam
            CROSS JOIN LATERAL unnest(ix.indkey) WITH ORDINALITY AS k(attnum, n)
            JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = k.attnum
            WHERE n.nspname = $1 AND t.relname = $2
            GROUP BY i.relname, ix.indisunique, ix.indisprimary, am.amname
            ORDER BY i.relname
        """
        result = await self.execute(query, (schema, table))

        if not result.is_success:
            return []

        return [
            IndexInfo(
                name=row[0],
                columns=list(row[1]) if row[1] else [],
                is_unique=row[2],
                is_primary=row[3],
                index_type=row[4],
            )
            for row in result.rows
        ]

    async def get_foreign_keys(self, table: str, schema: str | None = None) -> list[ForeignKeyInfo]:
        schema = schema or self._current_schema or 'public'

        query = """
            SELECT
                tc.constraint_name,
                array_agg(kcu.column_name ORDER BY kcu.ordinal_position) as columns,
                ccu.table_schema || '.' || ccu.table_name as referenced_table,
                array_agg(ccu.column_name ORDER BY kcu.ordinal_position) as referenced_columns,
                rc.update_rule,
                rc.delete_rule
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu
                ON ccu.constraint_name = tc.constraint_name
            JOIN information_schema.referential_constraints rc
                ON rc.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = $1
                AND tc.table_name = $2
            GROUP BY tc.constraint_name, ccu.table_schema, ccu.table_name,
                     rc.update_rule, rc.delete_rule
        """
        result = await self.execute(query, (schema, table))

        if not result.is_success:
            return []

        return [
            ForeignKeyInfo(
                name=row[0],
                columns=list(row[1]) if row[1] else [],
                referenced_table=row[2],
                referenced_columns=list(row[3]) if row[3] else [],
                on_update=row[4],
                on_delete=row[5],
            )
            for row in result.rows
        ]

    async def explain_query(self, query: str) -> str:
        result = await self.execute(f'EXPLAIN ANALYZE {query}')

        if not result.is_success:
            return f'Error: {result.error}'

        return '\n'.join(row[0] for row in result.rows)

    async def cancel_query(self) -> bool:
        if self._connection:
            try:
                await self._connection.execute('SELECT pg_cancel_backend(pg_backend_pid())')
                return True
            except Exception:
                return False
        return False

    async def set_schema(self, schema: str) -> bool:
        if self._connection:
            try:
                await self._connection.execute(f'SET search_path TO "{schema}"')
                self._current_schema = schema
                return True
            except Exception:
                return False
        return False

    def quote_identifier(self, identifier: str) -> str:
        return f'"{identifier}"'
