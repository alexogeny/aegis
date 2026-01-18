"""
Amazon DynamoDB database driver.

Provides connectivity to DynamoDB using boto3.
Supports PartiQL queries for SQL-like syntax.
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

# boto3 is optional - imported at runtime
boto3 = None


def _ensure_boto3():
    """Lazily import boto3."""
    global boto3
    if boto3 is None:
        try:
            import boto3 as _boto3

            boto3 = _boto3
        except ImportError as err:
            raise ImportError(
                'boto3 is required for DynamoDB support. Install it with: pip install boto3'
            ) from err


class DynamoDBDriver(DatabaseDriver):
    """Amazon DynamoDB driver using boto3."""

    driver_type = DriverType.DYNAMODB
    display_name = 'Amazon DynamoDB'
    icon = '⚡'
    default_port = 443
    supports_schemas = False  # DynamoDB doesn't have schemas
    supports_transactions = True
    supports_explain = False
    supports_cancel = False

    def __init__(self):
        super().__init__()
        self._client = None
        self._resource = None
        self._region = None

    @classmethod
    def get_connection_fields(cls) -> list[ConnectionField]:
        return [
            ConnectionField(
                name='region',
                label='AWS Region',
                field_type='dropdown',
                required=True,
                default='us-east-1',
                options=[
                    'us-east-1',
                    'us-east-2',
                    'us-west-1',
                    'us-west-2',
                    'eu-west-1',
                    'eu-west-2',
                    'eu-central-1',
                    'ap-northeast-1',
                    'ap-northeast-2',
                    'ap-southeast-1',
                    'ap-southeast-2',
                    'ap-south-1',
                    'sa-east-1',
                ],
                tooltip='AWS region where your DynamoDB tables are located',
            ),
            ConnectionField(
                name='access_key',
                label='Access Key ID',
                field_type='text',
                required=False,
                placeholder='Leave empty to use default credentials',
                tooltip='AWS Access Key ID (optional if using IAM roles or environment variables)',
            ),
            ConnectionField(
                name='secret_key',
                label='Secret Access Key',
                field_type='password',
                required=False,
                placeholder='Leave empty to use default credentials',
            ),
            ConnectionField(
                name='endpoint',
                label='Custom Endpoint',
                field_type='text',
                required=False,
                placeholder='http://localhost:8000 (for local DynamoDB)',
                tooltip='Custom endpoint URL for DynamoDB Local or other compatible services',
            ),
        ]

    async def connect(self, config: dict) -> bool:
        _ensure_boto3()

        session_kwargs = {}
        client_kwargs = {
            'region_name': config['region'],
        }

        # Add credentials if provided
        if config.get('access_key') and config.get('secret_key'):
            session_kwargs['aws_access_key_id'] = config['access_key']
            session_kwargs['aws_secret_access_key'] = config['secret_key']

        # Add custom endpoint if provided
        if config.get('endpoint'):
            client_kwargs['endpoint_url'] = config['endpoint']

        session = boto3.Session(**session_kwargs)
        self._client = session.client('dynamodb', **client_kwargs)
        self._resource = session.resource('dynamodb', **client_kwargs)
        self._region = config['region']
        self._connected = True

        return True

    async def disconnect(self) -> None:
        self._client = None
        self._resource = None
        self._connected = False

    async def test_connection(self, config: dict) -> tuple[bool, str]:
        _ensure_boto3()

        try:
            session_kwargs = {}
            client_kwargs = {
                'region_name': config['region'],
            }

            if config.get('access_key') and config.get('secret_key'):
                session_kwargs['aws_access_key_id'] = config['access_key']
                session_kwargs['aws_secret_access_key'] = config['secret_key']

            if config.get('endpoint'):
                client_kwargs['endpoint_url'] = config['endpoint']

            session = boto3.Session(**session_kwargs)
            client = session.client('dynamodb', **client_kwargs)

            # List tables to verify connection
            response = client.list_tables(Limit=1)
            table_count = len(response.get('TableNames', []))

            return True, f'DynamoDB ({config["region"]}) - {table_count}+ tables'

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
        Execute PartiQL queries against DynamoDB.

        Supports:
        - SELECT * FROM "TableName" WHERE pk = 'value'
        - SELECT * FROM "TableName"
        - INSERT INTO "TableName" VALUE {...}
        - UPDATE "TableName" SET ... WHERE ...
        - DELETE FROM "TableName" WHERE ...
        """
        if not self._connected or not self._client:
            return QueryResult(
                columns=[],
                rows=[],
                row_count=0,
                error='Not connected to DynamoDB',
            )

        start = time.time()

        try:
            # Check if it's a PartiQL query or a simple table scan
            query = query.strip()

            if query.upper().startswith('SELECT') or query.upper().startswith('INSERT') or \
               query.upper().startswith('UPDATE') or query.upper().startswith('DELETE'):
                return await self._execute_partiql(query, params, start)
            else:
                # Treat as table name for scan
                return await self._scan_table(query, limit or 100, start)

        except Exception as e:
            return QueryResult(
                columns=[],
                rows=[],
                row_count=0,
                error=str(e),
                execution_time_ms=(time.time() - start) * 1000,
            )

    async def _execute_partiql(
        self,
        query: str,
        params: tuple | dict | None,
        start: float,
    ) -> QueryResult:
        """Execute a PartiQL statement."""
        try:
            request_params = {'Statement': query}

            if params:
                # Convert params to DynamoDB format
                if isinstance(params, dict):
                    request_params['Parameters'] = [
                        self._python_to_dynamodb(v) for v in params.values()
                    ]
                else:
                    request_params['Parameters'] = [
                        self._python_to_dynamodb(v) for v in params
                    ]

            response = self._client.execute_statement(**request_params)
            execution_time = (time.time() - start) * 1000

            items = response.get('Items', [])

            if not items:
                return QueryResult(
                    columns=[],
                    rows=[],
                    row_count=0,
                    execution_time_ms=execution_time,
                )

            # Build columns from first item
            first_item = self._dynamodb_to_python(items[0])
            columns = [
                ColumnInfo(
                    name=key,
                    type_name=type(value).__name__,
                    python_type=type(value),
                )
                for key, value in first_item.items()
            ]

            # Convert all items to rows
            rows = []
            for item in items:
                py_item = self._dynamodb_to_python(item)
                row = tuple(py_item.get(col.name) for col in columns)
                rows.append(row)

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

    async def _scan_table(
        self,
        table_name: str,
        limit: int,
        start: float,
    ) -> QueryResult:
        """Scan a DynamoDB table."""
        try:
            response = self._client.scan(
                TableName=table_name,
                Limit=limit,
            )
            execution_time = (time.time() - start) * 1000

            items = response.get('Items', [])

            if not items:
                return QueryResult(
                    columns=[],
                    rows=[],
                    row_count=0,
                    execution_time_ms=execution_time,
                )

            # Build columns from all items (DynamoDB items can have different attributes)
            all_keys = set()
            for item in items:
                all_keys.update(item.keys())

            columns = [
                ColumnInfo(name=key, type_name='variant', python_type=str)
                for key in sorted(all_keys)
            ]

            # Convert all items to rows
            rows = []
            for item in items:
                py_item = self._dynamodb_to_python(item)
                row = tuple(py_item.get(col.name) for col in columns)
                rows.append(row)

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

    def _dynamodb_to_python(self, item: dict) -> dict:
        """Convert DynamoDB item to Python dict."""
        result = {}
        for key, value in item.items():
            result[key] = self._dynamodb_value_to_python(value)
        return result

    def _dynamodb_value_to_python(self, value: dict) -> Any:
        """Convert a single DynamoDB value to Python."""
        if 'S' in value:
            return value['S']
        elif 'N' in value:
            num_str = value['N']
            return float(num_str) if '.' in num_str else int(num_str)
        elif 'B' in value:
            return value['B']
        elif 'BOOL' in value:
            return value['BOOL']
        elif 'NULL' in value:
            return None
        elif 'L' in value:
            return [self._dynamodb_value_to_python(v) for v in value['L']]
        elif 'M' in value:
            return self._dynamodb_to_python(value['M'])
        elif 'SS' in value:
            return set(value['SS'])
        elif 'NS' in value:
            return {float(n) if '.' in n else int(n) for n in value['NS']}
        elif 'BS' in value:
            return set(value['BS'])
        else:
            return str(value)

    def _python_to_dynamodb(self, value: Any) -> dict:
        """Convert Python value to DynamoDB format."""
        if value is None:
            return {'NULL': True}
        elif isinstance(value, bool):
            return {'BOOL': value}
        elif isinstance(value, str):
            return {'S': value}
        elif isinstance(value, (int, float)):
            return {'N': str(value)}
        elif isinstance(value, bytes):
            return {'B': value}
        elif isinstance(value, list):
            return {'L': [self._python_to_dynamodb(v) for v in value]}
        elif isinstance(value, dict):
            return {'M': {k: self._python_to_dynamodb(v) for k, v in value.items()}}
        elif isinstance(value, set):
            if all(isinstance(v, str) for v in value):
                return {'SS': list(value)}
            elif all(isinstance(v, (int, float)) for v in value):
                return {'NS': [str(v) for v in value]}
            else:
                return {'SS': [str(v) for v in value]}
        else:
            return {'S': str(value)}

    async def get_schemas(self) -> list[str]:
        """DynamoDB doesn't have schemas - return empty list."""
        return []

    async def get_tables(self, schema: str | None = None) -> list[TableInfo]:
        """Get list of DynamoDB tables."""
        if not self._client:
            return []

        try:
            tables = []
            paginator = self._client.get_paginator('list_tables')

            for page in paginator.paginate():
                for table_name in page.get('TableNames', []):
                    # Get table info
                    try:
                        desc = self._client.describe_table(TableName=table_name)
                        table_info = desc.get('Table', {})

                        tables.append(
                            TableInfo(
                                name=table_name,
                                schema=self._region,
                                table_type='table',
                                row_count=table_info.get('ItemCount'),
                                size_bytes=table_info.get('TableSizeBytes'),
                                comment=table_info.get('TableStatus'),
                            )
                        )
                    except Exception:
                        tables.append(
                            TableInfo(
                                name=table_name,
                                schema=self._region,
                                table_type='table',
                            )
                        )

            return tables

        except Exception:
            return []

    async def get_columns(self, table: str, schema: str | None = None) -> list[ColumnDef]:
        """Get key schema for a DynamoDB table."""
        if not self._client:
            return []

        try:
            desc = self._client.describe_table(TableName=table)
            table_info = desc.get('Table', {})

            columns = []

            # Key schema
            key_schema = table_info.get('KeySchema', [])
            attribute_defs = {
                attr['AttributeName']: attr['AttributeType']
                for attr in table_info.get('AttributeDefinitions', [])
            }

            for key in key_schema:
                name = key['AttributeName']
                key_type = key['KeyType']  # HASH or RANGE
                attr_type = attribute_defs.get(name, 'S')

                columns.append(
                    ColumnDef(
                        name=name,
                        data_type=self._dynamodb_type_name(attr_type),
                        nullable=False,
                        is_primary_key=key_type == 'HASH',
                        comment=f'{key_type} key',
                    )
                )

            # Global Secondary Indexes
            for gsi in table_info.get('GlobalSecondaryIndexes', []):
                for key in gsi.get('KeySchema', []):
                    name = key['AttributeName']
                    if not any(c.name == name for c in columns):
                        attr_type = attribute_defs.get(name, 'S')
                        columns.append(
                            ColumnDef(
                                name=name,
                                data_type=self._dynamodb_type_name(attr_type),
                                nullable=True,
                                comment=f'GSI: {gsi["IndexName"]}',
                            )
                        )

            # Local Secondary Indexes
            for lsi in table_info.get('LocalSecondaryIndexes', []):
                for key in lsi.get('KeySchema', []):
                    name = key['AttributeName']
                    if not any(c.name == name for c in columns):
                        attr_type = attribute_defs.get(name, 'S')
                        columns.append(
                            ColumnDef(
                                name=name,
                                data_type=self._dynamodb_type_name(attr_type),
                                nullable=True,
                                comment=f'LSI: {lsi["IndexName"]}',
                            )
                        )

            return columns

        except Exception:
            return []

    def _dynamodb_type_name(self, attr_type: str) -> str:
        """Convert DynamoDB attribute type to readable name."""
        type_map = {
            'S': 'String',
            'N': 'Number',
            'B': 'Binary',
            'SS': 'String Set',
            'NS': 'Number Set',
            'BS': 'Binary Set',
            'M': 'Map',
            'L': 'List',
            'BOOL': 'Boolean',
            'NULL': 'Null',
        }
        return type_map.get(attr_type, attr_type)

    async def get_table_preview(
        self,
        table: str,
        schema: str | None = None,
        limit: int = 100,
    ) -> QueryResult:
        """Preview data from a DynamoDB table."""
        return await self._scan_table(table, limit, time.time())

    async def set_schema(self, schema: str) -> bool:
        """DynamoDB doesn't have schemas - no-op."""
        return True

    def quote_identifier(self, identifier: str) -> str:
        return f'"{identifier}"'
