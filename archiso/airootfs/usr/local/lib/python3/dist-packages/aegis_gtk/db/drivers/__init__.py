"""
Database drivers for aegis-dbview.

Each driver implements the DatabaseDriver interface for a specific database type.
"""

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

# Import drivers - they register themselves
from . import sqlite as _sqlite
from . import postgresql as _postgresql

# Driver registry
_DRIVERS: dict[DriverType, type[DatabaseDriver]] = {}


def register_driver(driver_class: type[DatabaseDriver]) -> None:
    """Register a database driver."""
    _DRIVERS[driver_class.driver_type] = driver_class


def get_driver(driver_type: DriverType | str) -> type[DatabaseDriver]:
    """Get a driver class by type."""
    if isinstance(driver_type, str):
        driver_type = DriverType(driver_type)
    if driver_type not in _DRIVERS:
        raise ValueError(f'Unknown driver type: {driver_type}')
    return _DRIVERS[driver_type]


def get_available_drivers() -> list[type[DatabaseDriver]]:
    """Get all available driver classes."""
    return list(_DRIVERS.values())


# Register built-in drivers
register_driver(_sqlite.SQLiteDriver)
register_driver(_postgresql.PostgreSQLDriver)

__all__ = [
    'DatabaseDriver',
    'DriverType',
    'ConnectionField',
    'ColumnInfo',
    'QueryResult',
    'TableInfo',
    'ColumnDef',
    'IndexInfo',
    'ForeignKeyInfo',
    'register_driver',
    'get_driver',
    'get_available_drivers',
]
