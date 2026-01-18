"""
Aegis GTK Database Module - Database connectivity and management for aegis-dbview.

Provides a unified interface for connecting to various databases including
PostgreSQL, SQLite, MySQL, DynamoDB, Cassandra, and Redis.
"""

from .drivers import (
    DatabaseDriver,
    DriverType,
    ConnectionField,
    ColumnInfo,
    QueryResult,
    TableInfo,
    ColumnDef,
    IndexInfo,
    ForeignKeyInfo,
    get_driver,
    get_available_drivers,
)
from .connections import (
    ConnectionConfig,
    ConnectionManager,
    DBVIEW_CONFIG_DIR,
    CONNECTIONS_PATH,
)
from .query import QueryExecutor
from .history import QueryHistory, HistoryEntry
from .export import ResultExporter, ExportFormat

__all__ = [
    # Drivers
    'DatabaseDriver',
    'DriverType',
    'ConnectionField',
    'ColumnInfo',
    'QueryResult',
    'TableInfo',
    'ColumnDef',
    'IndexInfo',
    'ForeignKeyInfo',
    'get_driver',
    'get_available_drivers',
    # Connections
    'ConnectionConfig',
    'ConnectionManager',
    'DBVIEW_CONFIG_DIR',
    'CONNECTIONS_PATH',
    # Query
    'QueryExecutor',
    # History
    'QueryHistory',
    'HistoryEntry',
    # Export
    'ResultExporter',
    'ExportFormat',
]
