"""
Abstract base class for database drivers.

All database drivers must implement this interface to provide
consistent behavior across different database types.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterator


class DriverType(Enum):
    """Supported database driver types."""
    SQLITE = 'sqlite'
    POSTGRESQL = 'postgresql'
    MYSQL = 'mysql'
    DYNAMODB = 'dynamodb'
    CASSANDRA = 'cassandra'
    REDIS = 'redis'
    MONGODB = 'mongodb'


@dataclass
class ConnectionField:
    """Describes a field in the connection configuration form."""
    name: str
    label: str
    field_type: str  # 'text', 'password', 'number', 'file', 'dropdown', 'checkbox'
    required: bool = True
    default: Any = None
    options: list[str] | None = None  # For dropdown fields
    placeholder: str = ''
    tooltip: str = ''


@dataclass
class ColumnInfo:
    """Column metadata for query results."""
    name: str
    type_name: str
    python_type: type = str
    nullable: bool = True
    display_width: int = 0  # Suggested display width in characters


@dataclass
class QueryResult:
    """Result of a query execution."""
    columns: list[ColumnInfo]
    rows: list[tuple]
    row_count: int
    affected_rows: int = 0
    execution_time_ms: float = 0.0
    has_more: bool = False
    error: str | None = None
    warnings: list[str] = field(default_factory=list)

    def to_dicts(self) -> Iterator[dict]:
        """Convert rows to dictionaries."""
        col_names = [c.name for c in self.columns]
        for row in self.rows:
            yield dict(zip(col_names, row))

    @property
    def is_success(self) -> bool:
        """Check if the query executed successfully."""
        return self.error is None


@dataclass
class TableInfo:
    """Table metadata for schema browser."""
    name: str
    schema: str | None = None
    table_type: str = 'table'  # 'table', 'view', 'materialized_view'
    row_count: int | None = None
    size_bytes: int | None = None
    comment: str | None = None

    @property
    def full_name(self) -> str:
        """Get fully qualified table name."""
        if self.schema:
            return f"{self.schema}.{self.name}"
        return self.name


@dataclass
class ColumnDef:
    """Column definition for schema browser."""
    name: str
    data_type: str
    nullable: bool = True
    default: str | None = None
    is_primary_key: bool = False
    is_foreign_key: bool = False
    is_unique: bool = False
    references: str | None = None  # "schema.table.column" for foreign keys
    comment: str | None = None
    ordinal_position: int = 0


@dataclass
class IndexInfo:
    """Index information for a table."""
    name: str
    columns: list[str]
    is_unique: bool = False
    is_primary: bool = False
    index_type: str = 'btree'  # btree, hash, gin, gist, etc.


@dataclass
class ForeignKeyInfo:
    """Foreign key relationship information."""
    name: str
    columns: list[str]
    referenced_table: str
    referenced_columns: list[str]
    on_delete: str = 'NO ACTION'
    on_update: str = 'NO ACTION'


class DatabaseDriver(ABC):
    """Abstract base class for database drivers.

    All database drivers must implement this interface to provide
    consistent behavior for aegis-dbview.
    """

    # Class attributes - must be defined by subclasses
    driver_type: DriverType
    display_name: str
    icon: str  # Emoji for UI display
    default_port: int = 0
    supports_schemas: bool = True
    supports_transactions: bool = True
    supports_explain: bool = False
    supports_cancel: bool = False

    def __init__(self):
        self._connection: Any = None
        self._connected: bool = False
        self._current_schema: str | None = None

    @property
    def is_connected(self) -> bool:
        """Check if driver is currently connected."""
        return self._connected

    @property
    def current_schema(self) -> str | None:
        """Get the current active schema."""
        return self._current_schema

    @classmethod
    @abstractmethod
    def get_connection_fields(cls) -> list[ConnectionField]:
        """Return the fields needed for connection configuration.

        Returns:
            List of ConnectionField objects describing the form fields.
        """
        ...

    @abstractmethod
    async def connect(self, config: dict) -> bool:
        """Establish a connection to the database.

        Args:
            config: Dictionary with connection parameters matching the fields
                    returned by get_connection_fields().

        Returns:
            True if connection was successful.

        Raises:
            Exception: If connection fails.
        """
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the database connection."""
        ...

    @abstractmethod
    async def test_connection(self, config: dict) -> tuple[bool, str]:
        """Test connection without fully connecting.

        Args:
            config: Connection configuration to test.

        Returns:
            Tuple of (success, message) where message contains
            version info on success or error details on failure.
        """
        ...

    @abstractmethod
    async def execute(
        self,
        query: str,
        params: tuple | dict | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> QueryResult:
        """Execute a query and return results.

        Args:
            query: SQL query string.
            params: Query parameters (positional tuple or named dict).
            limit: Maximum number of rows to return.
            offset: Number of rows to skip.

        Returns:
            QueryResult with columns, rows, and metadata.
        """
        ...

    @abstractmethod
    async def get_schemas(self) -> list[str]:
        """Get list of schemas/databases.

        Returns:
            List of schema names. Returns ['default'] for databases
            that don't support schemas.
        """
        ...

    @abstractmethod
    async def get_tables(self, schema: str | None = None) -> list[TableInfo]:
        """Get tables in a schema.

        Args:
            schema: Schema name, or None for default schema.

        Returns:
            List of TableInfo objects.
        """
        ...

    @abstractmethod
    async def get_columns(
        self, table: str, schema: str | None = None
    ) -> list[ColumnDef]:
        """Get column definitions for a table.

        Args:
            table: Table name.
            schema: Schema name, or None for default schema.

        Returns:
            List of ColumnDef objects.
        """
        ...

    @abstractmethod
    async def get_table_preview(
        self,
        table: str,
        schema: str | None = None,
        limit: int = 100,
    ) -> QueryResult:
        """Get a preview of table data.

        Args:
            table: Table name.
            schema: Schema name, or None for default schema.
            limit: Maximum number of rows to return.

        Returns:
            QueryResult with sample data.
        """
        ...

    # Optional methods with default implementations

    async def get_indexes(
        self, table: str, schema: str | None = None
    ) -> list[IndexInfo]:
        """Get index information for a table.

        Args:
            table: Table name.
            schema: Schema name.

        Returns:
            List of IndexInfo objects.
        """
        return []

    async def get_foreign_keys(
        self, table: str, schema: str | None = None
    ) -> list[ForeignKeyInfo]:
        """Get foreign key relationships for a table.

        Args:
            table: Table name.
            schema: Schema name.

        Returns:
            List of ForeignKeyInfo objects.
        """
        return []

    async def explain_query(self, query: str) -> str:
        """Get query execution plan.

        Args:
            query: SQL query to explain.

        Returns:
            Execution plan as a string.
        """
        return "EXPLAIN not supported for this database"

    async def cancel_query(self) -> bool:
        """Cancel the currently running query.

        Returns:
            True if cancellation was successful.
        """
        return False

    async def set_schema(self, schema: str) -> bool:
        """Set the current active schema.

        Args:
            schema: Schema name to activate.

        Returns:
            True if schema was set successfully.
        """
        self._current_schema = schema
        return True

    def quote_identifier(self, identifier: str) -> str:
        """Quote an identifier (table/column name) for safe use in queries.

        Args:
            identifier: The identifier to quote.

        Returns:
            Quoted identifier string.
        """
        # Default implementation uses double quotes (SQL standard)
        return f'"{identifier}"'

    def format_value(self, value: Any, column_info: ColumnInfo | None = None) -> str:
        """Format a value for display.

        Args:
            value: The value to format.
            column_info: Optional column metadata for type-aware formatting.

        Returns:
            Formatted string representation.
        """
        if value is None:
            return 'NULL'
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if isinstance(value, bytes):
            return f'<{len(value)} bytes>'
        return str(value)
