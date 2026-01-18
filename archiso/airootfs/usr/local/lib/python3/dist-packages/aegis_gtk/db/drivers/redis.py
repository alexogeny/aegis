"""
Redis database driver.

Provides connectivity to Redis key-value stores using redis-py.
Note: Redis is not a SQL database, so this driver provides a key-browser interface.
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
)

# redis is optional - imported at runtime
redis_lib = None


def _ensure_redis():
    """Lazily import redis."""
    global redis_lib
    if redis_lib is None:
        try:
            import redis as _redis

            redis_lib = _redis
        except ImportError as err:
            raise ImportError('redis is required for Redis support. Install it with: pip install redis') from err


class RedisDriver(DatabaseDriver):
    """Redis key-value store driver using redis-py."""

    driver_type = DriverType.REDIS
    display_name = 'Redis'
    icon = '🔴'
    default_port = 6379
    supports_schemas = True  # Redis uses database numbers as schemas
    supports_transactions = False
    supports_explain = False
    supports_cancel = False

    def __init__(self):
        super().__init__()
        self._current_db = 0
        self._client = None

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
                default=6379,
            ),
            ConnectionField(
                name='database',
                label='Database Number',
                field_type='number',
                required=False,
                default=0,
                placeholder='0-15',
                tooltip='Redis database number (0-15 by default)',
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
                label='Use SSL/TLS',
                field_type='checkbox',
                required=False,
                default=False,
                tooltip='Enable SSL/TLS encrypted connection',
            ),
        ]

    async def connect(self, config: dict) -> bool:
        _ensure_redis()

        self._client = redis_lib.Redis(
            host=config['host'],
            port=config.get('port', 6379),
            db=config.get('database', 0),
            password=config.get('password') or None,
            ssl=config.get('ssl', False),
            decode_responses=True,
            socket_timeout=10,
        )

        # Test connection
        self._client.ping()

        self._connected = True
        self._current_db = config.get('database', 0)
        return True

    async def disconnect(self) -> None:
        if self._client:
            self._client.close()
            self._client = None
        self._connected = False

    async def test_connection(self, config: dict) -> tuple[bool, str]:
        _ensure_redis()

        try:
            client = redis_lib.Redis(
                host=config['host'],
                port=config.get('port', 6379),
                db=config.get('database', 0),
                password=config.get('password') or None,
                ssl=config.get('ssl', False),
                decode_responses=True,
                socket_timeout=10,
            )

            info = client.info('server')
            client.close()

            version = info.get('redis_version', 'Unknown')
            return True, f'Redis {version}'

        except Exception as e:
            return False, str(e)

    async def execute(
        self,
        query: str,
        params: tuple | dict | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> QueryResult:
        """
        Execute Redis commands.

        Supports common commands like:
        - KEYS pattern
        - GET key
        - HGETALL key
        - LRANGE key start stop
        - SMEMBERS key
        - ZRANGE key start stop
        - INFO [section]
        """
        if not self._connected or not self._client:
            return QueryResult(
                columns=[],
                rows=[],
                row_count=0,
                error='Not connected to Redis',
            )

        start = time.time()

        try:
            # Parse the command
            parts = query.strip().split(None, 1)
            if not parts:
                return QueryResult(
                    columns=[],
                    rows=[],
                    row_count=0,
                    error='Empty command',
                )

            cmd = parts[0].upper()
            args = parts[1].split() if len(parts) > 1 else []

            # Execute command
            result = self._execute_command(cmd, args)
            execution_time = (time.time() - start) * 1000

            return self._format_result(result, execution_time)

        except Exception as e:
            return QueryResult(
                columns=[],
                rows=[],
                row_count=0,
                error=str(e),
                execution_time_ms=(time.time() - start) * 1000,
            )

    def _execute_command(self, cmd: str, args: list[str]) -> Any:
        """Execute a Redis command and return the result."""
        # Key listing
        if cmd == 'KEYS':
            pattern = args[0] if args else '*'
            return self._client.keys(pattern)

        # String operations
        elif cmd == 'GET':
            if not args:
                raise ValueError('GET requires a key')
            return self._client.get(args[0])

        elif cmd == 'MGET':
            if not args:
                raise ValueError('MGET requires at least one key')
            return self._client.mget(args)

        # Hash operations
        elif cmd == 'HGETALL':
            if not args:
                raise ValueError('HGETALL requires a key')
            return self._client.hgetall(args[0])

        elif cmd == 'HGET':
            if len(args) < 2:
                raise ValueError('HGET requires key and field')
            return self._client.hget(args[0], args[1])

        # List operations
        elif cmd == 'LRANGE':
            if len(args) < 3:
                raise ValueError('LRANGE requires key, start, and stop')
            return self._client.lrange(args[0], int(args[1]), int(args[2]))

        elif cmd == 'LLEN':
            if not args:
                raise ValueError('LLEN requires a key')
            return self._client.llen(args[0])

        # Set operations
        elif cmd == 'SMEMBERS':
            if not args:
                raise ValueError('SMEMBERS requires a key')
            return self._client.smembers(args[0])

        elif cmd == 'SCARD':
            if not args:
                raise ValueError('SCARD requires a key')
            return self._client.scard(args[0])

        # Sorted set operations
        elif cmd == 'ZRANGE':
            if len(args) < 3:
                raise ValueError('ZRANGE requires key, start, and stop')
            return self._client.zrange(args[0], int(args[1]), int(args[2]), withscores=True)

        elif cmd == 'ZCARD':
            if not args:
                raise ValueError('ZCARD requires a key')
            return self._client.zcard(args[0])

        # Key info
        elif cmd == 'TYPE':
            if not args:
                raise ValueError('TYPE requires a key')
            return self._client.type(args[0])

        elif cmd == 'TTL':
            if not args:
                raise ValueError('TTL requires a key')
            return self._client.ttl(args[0])

        elif cmd == 'EXISTS':
            if not args:
                raise ValueError('EXISTS requires a key')
            return self._client.exists(args[0])

        # Server info
        elif cmd == 'INFO':
            section = args[0] if args else None
            return self._client.info(section)

        elif cmd == 'DBSIZE':
            return self._client.dbsize()

        elif cmd == 'SCAN':
            cursor = int(args[0]) if args else 0
            pattern = args[1] if len(args) > 1 else '*'
            count = int(args[2]) if len(args) > 2 else 100
            return self._client.scan(cursor=cursor, match=pattern, count=count)

        else:
            # Try to execute as generic command
            return self._client.execute_command(cmd, *args)

    def _format_result(self, result: Any, execution_time: float) -> QueryResult:
        """Format Redis result into QueryResult."""
        if result is None:
            return QueryResult(
                columns=[ColumnInfo(name='value', type_name='null', python_type=type(None))],
                rows=[('(nil)',)],
                row_count=1,
                execution_time_ms=execution_time,
            )

        # Simple value
        if isinstance(result, (str, int, float, bool)):
            return QueryResult(
                columns=[ColumnInfo(name='value', type_name=type(result).__name__, python_type=type(result))],
                rows=[(result,)],
                row_count=1,
                execution_time_ms=execution_time,
            )

        # List of keys/values
        if isinstance(result, (list, set)):
            result = list(result)
            if not result:
                return QueryResult(
                    columns=[ColumnInfo(name='value', type_name='list', python_type=list)],
                    rows=[],
                    row_count=0,
                    execution_time_ms=execution_time,
                )

            # Check if it's a list of tuples (sorted set with scores)
            if result and isinstance(result[0], tuple):
                return QueryResult(
                    columns=[
                        ColumnInfo(name='member', type_name='str', python_type=str),
                        ColumnInfo(name='score', type_name='float', python_type=float),
                    ],
                    rows=result,
                    row_count=len(result),
                    execution_time_ms=execution_time,
                )

            return QueryResult(
                columns=[ColumnInfo(name='value', type_name='str', python_type=str)],
                rows=[(v,) for v in result],
                row_count=len(result),
                execution_time_ms=execution_time,
            )

        # Hash (dict)
        if isinstance(result, dict):
            if not result:
                return QueryResult(
                    columns=[
                        ColumnInfo(name='field', type_name='str', python_type=str),
                        ColumnInfo(name='value', type_name='str', python_type=str),
                    ],
                    rows=[],
                    row_count=0,
                    execution_time_ms=execution_time,
                )

            return QueryResult(
                columns=[
                    ColumnInfo(name='field', type_name='str', python_type=str),
                    ColumnInfo(name='value', type_name='str', python_type=str),
                ],
                rows=[(k, v) for k, v in result.items()],
                row_count=len(result),
                execution_time_ms=execution_time,
            )

        # Tuple (SCAN result)
        if isinstance(result, tuple) and len(result) == 2:
            cursor, keys = result
            return QueryResult(
                columns=[
                    ColumnInfo(name='cursor', type_name='int', python_type=int),
                    ColumnInfo(name='key', type_name='str', python_type=str),
                ],
                rows=[(cursor, k) for k in keys] if keys else [(cursor, '(no keys)')],
                row_count=len(keys) if keys else 1,
                execution_time_ms=execution_time,
            )

        # Fallback - convert to string
        return QueryResult(
            columns=[ColumnInfo(name='result', type_name='str', python_type=str)],
            rows=[(str(result),)],
            row_count=1,
            execution_time_ms=execution_time,
        )

    async def get_schemas(self) -> list[str]:
        """Get list of database numbers (0-15 by default)."""
        # Redis typically has 16 databases by default
        return [str(i) for i in range(16)]

    async def get_tables(self, schema: str | None = None) -> list[TableInfo]:
        """
        Get key patterns as 'tables'.

        We scan for unique key prefixes to provide structure.
        """
        if not self._client:
            return []

        try:
            # Get a sample of keys to identify patterns
            cursor = 0
            prefixes = set()
            seen_keys = 0
            max_keys = 1000

            while seen_keys < max_keys:
                cursor, keys = self._client.scan(cursor=cursor, count=100)
                for key in keys:
                    # Extract prefix (part before first : or entire key)
                    if ':' in key:
                        prefix = key.split(':')[0]
                        prefixes.add(prefix)
                    else:
                        prefixes.add(key)
                    seen_keys += 1

                if cursor == 0:
                    break

            tables = []
            for prefix in sorted(prefixes):
                # Count keys matching this prefix
                pattern = f'{prefix}*' if ':' in str(self._client.keys(f'{prefix}:*')[:1]) else prefix
                count = len(list(self._client.scan_iter(match=f'{pattern}*', count=100)))

                tables.append(
                    TableInfo(
                        name=prefix,
                        schema=str(self._current_db),
                        table_type='keys',
                        row_count=min(count, 100),  # Approximate
                        comment=f'Key pattern: {prefix}*',
                    )
                )

            return tables[:50]  # Limit to 50 prefixes

        except Exception:
            return []

    async def get_columns(self, table: str, schema: str | None = None) -> list[ColumnDef]:
        """
        Get structure of a key.

        For Redis, we inspect the key type and return appropriate columns.
        """
        if not self._client:
            return []

        try:
            # Check if table is a key or a prefix
            key_type = self._client.type(table)

            if key_type == 'string':
                return [
                    ColumnDef(name='value', data_type='string', nullable=False),
                ]
            elif key_type == 'hash':
                # Get hash fields
                fields = self._client.hkeys(table)
                return [
                    ColumnDef(name=field, data_type='string', nullable=True)
                    for field in fields[:50]  # Limit fields
                ]
            elif key_type == 'list':
                return [
                    ColumnDef(name='index', data_type='integer', nullable=False),
                    ColumnDef(name='value', data_type='string', nullable=False),
                ]
            elif key_type == 'set':
                return [
                    ColumnDef(name='member', data_type='string', nullable=False),
                ]
            elif key_type == 'zset':
                return [
                    ColumnDef(name='member', data_type='string', nullable=False),
                    ColumnDef(name='score', data_type='float', nullable=False),
                ]
            else:
                return [
                    ColumnDef(name='value', data_type='unknown', nullable=True),
                ]

        except Exception:
            return []

    async def get_table_preview(
        self,
        table: str,
        schema: str | None = None,
        limit: int = 100,
    ) -> QueryResult:
        """Preview data for a key or key pattern."""
        if not self._client:
            return QueryResult(columns=[], rows=[], row_count=0, error='Not connected')

        start = time.time()

        try:
            key_type = self._client.type(table)

            if key_type == 'string':
                value = self._client.get(table)
                return QueryResult(
                    columns=[ColumnInfo(name='value', type_name='string', python_type=str)],
                    rows=[(value,)],
                    row_count=1,
                    execution_time_ms=(time.time() - start) * 1000,
                )

            elif key_type == 'hash':
                data = self._client.hgetall(table)
                return QueryResult(
                    columns=[
                        ColumnInfo(name='field', type_name='string', python_type=str),
                        ColumnInfo(name='value', type_name='string', python_type=str),
                    ],
                    rows=list(data.items())[:limit],
                    row_count=min(len(data), limit),
                    execution_time_ms=(time.time() - start) * 1000,
                )

            elif key_type == 'list':
                values = self._client.lrange(table, 0, limit - 1)
                return QueryResult(
                    columns=[
                        ColumnInfo(name='index', type_name='integer', python_type=int),
                        ColumnInfo(name='value', type_name='string', python_type=str),
                    ],
                    rows=[(i, v) for i, v in enumerate(values)],
                    row_count=len(values),
                    execution_time_ms=(time.time() - start) * 1000,
                )

            elif key_type == 'set':
                members = list(self._client.smembers(table))[:limit]
                return QueryResult(
                    columns=[ColumnInfo(name='member', type_name='string', python_type=str)],
                    rows=[(m,) for m in members],
                    row_count=len(members),
                    execution_time_ms=(time.time() - start) * 1000,
                )

            elif key_type == 'zset':
                members = self._client.zrange(table, 0, limit - 1, withscores=True)
                return QueryResult(
                    columns=[
                        ColumnInfo(name='member', type_name='string', python_type=str),
                        ColumnInfo(name='score', type_name='float', python_type=float),
                    ],
                    rows=members,
                    row_count=len(members),
                    execution_time_ms=(time.time() - start) * 1000,
                )

            else:
                # Pattern search - list keys matching pattern
                keys = list(self._client.scan_iter(match=f'{table}*', count=limit))[:limit]
                return QueryResult(
                    columns=[ColumnInfo(name='key', type_name='string', python_type=str)],
                    rows=[(k,) for k in keys],
                    row_count=len(keys),
                    execution_time_ms=(time.time() - start) * 1000,
                )

        except Exception as e:
            return QueryResult(
                columns=[],
                rows=[],
                row_count=0,
                error=str(e),
                execution_time_ms=(time.time() - start) * 1000,
            )

    async def set_schema(self, schema: str) -> bool:
        """Switch to a different database number."""
        if self._client:
            try:
                db_num = int(schema)
                self._client.select(db_num)
                self._current_db = db_num
                return True
            except (ValueError, Exception):
                return False
        return False

    def quote_identifier(self, identifier: str) -> str:
        # Redis keys don't need quoting
        return identifier
