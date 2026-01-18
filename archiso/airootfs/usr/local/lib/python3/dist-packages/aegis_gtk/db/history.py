"""
Query history management for aegis-dbview.

Tracks executed queries with timestamps and results metadata.
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

from .connections import DBVIEW_CONFIG_DIR

HISTORY_PATH = DBVIEW_CONFIG_DIR / 'history.json'
MAX_HISTORY_ENTRIES = 500


@dataclass
class HistoryEntry:
    """A single query history entry."""

    query: str
    connection_id: str
    connection_name: str
    executed_at: str  # ISO format timestamp
    execution_time_ms: float
    row_count: int
    success: bool
    error: str | None = None

    @classmethod
    def create(
        cls,
        query: str,
        connection_id: str,
        connection_name: str,
        execution_time_ms: float,
        row_count: int,
        success: bool,
        error: str | None = None,
    ) -> 'HistoryEntry':
        """Create a new history entry with current timestamp."""
        return cls(
            query=query.strip(),
            connection_id=connection_id,
            connection_name=connection_name,
            executed_at=datetime.now().isoformat(),
            execution_time_ms=execution_time_ms,
            row_count=row_count,
            success=success,
            error=error,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'HistoryEntry':
        """Create from dictionary."""
        return cls(**data)

    @property
    def timestamp(self) -> datetime:
        """Get executed_at as datetime object."""
        return datetime.fromisoformat(self.executed_at)

    @property
    def preview(self) -> str:
        """Get a short preview of the query for display."""
        # Normalize whitespace and truncate
        normalized = ' '.join(self.query.split())
        if len(normalized) > 80:
            return normalized[:77] + '...'
        return normalized


class QueryHistory:
    """Manages query execution history."""

    def __init__(self, history_path: Path | None = None):
        """Initialize query history.

        Args:
            history_path: Path to history file. Defaults to standard location.
        """
        self.history_path = history_path or HISTORY_PATH
        self._entries: list[HistoryEntry] = []
        self._load()

    def _ensure_dir(self):
        """Ensure history directory exists."""
        self.history_path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self):
        """Load history from disk."""
        self._entries = []

        if not self.history_path.exists():
            return

        try:
            with open(self.history_path) as f:
                data = json.load(f)

            for entry_data in data.get('entries', []):
                entry = HistoryEntry.from_dict(entry_data)
                self._entries.append(entry)

        except (json.JSONDecodeError, OSError, TypeError):
            # Invalid or unreadable file, start fresh
            pass

    def _save(self):
        """Save history to disk."""
        self._ensure_dir()

        data = {
            'version': 1,
            'entries': [e.to_dict() for e in self._entries],
        }

        with open(self.history_path, 'w') as f:
            json.dump(data, f, indent=2)

    def add(
        self,
        query: str,
        connection_id: str,
        connection_name: str,
        execution_time_ms: float,
        row_count: int,
        success: bool,
        error: str | None = None,
    ) -> HistoryEntry:
        """Add a query to history.

        Args:
            query: The SQL query that was executed.
            connection_id: ID of the connection used.
            connection_name: Display name of the connection.
            execution_time_ms: Query execution time in milliseconds.
            row_count: Number of rows returned.
            success: Whether the query succeeded.
            error: Error message if query failed.

        Returns:
            The created history entry.
        """
        entry = HistoryEntry.create(
            query=query,
            connection_id=connection_id,
            connection_name=connection_name,
            execution_time_ms=execution_time_ms,
            row_count=row_count,
            success=success,
            error=error,
        )

        # Add to front of list (most recent first)
        self._entries.insert(0, entry)

        # Trim to max size
        if len(self._entries) > MAX_HISTORY_ENTRIES:
            self._entries = self._entries[:MAX_HISTORY_ENTRIES]

        self._save()
        return entry

    def get_entries(
        self,
        connection_id: str | None = None,
        limit: int | None = None,
        success_only: bool = False,
    ) -> list[HistoryEntry]:
        """Get history entries with optional filtering.

        Args:
            connection_id: Filter by connection ID.
            limit: Maximum number of entries to return.
            success_only: Only include successful queries.

        Returns:
            List of matching history entries.
        """
        entries = self._entries

        if connection_id:
            entries = [e for e in entries if e.connection_id == connection_id]

        if success_only:
            entries = [e for e in entries if e.success]

        if limit:
            entries = entries[:limit]

        return entries

    def search(self, query_text: str, limit: int = 50) -> list[HistoryEntry]:
        """Search history for queries containing text.

        Args:
            query_text: Text to search for (case-insensitive).
            limit: Maximum number of results.

        Returns:
            List of matching history entries.
        """
        query_lower = query_text.lower()
        matches = [e for e in self._entries if query_lower in e.query.lower()]
        return matches[:limit]

    def clear(self, connection_id: str | None = None):
        """Clear history.

        Args:
            connection_id: If provided, only clear history for this connection.
        """
        if connection_id:
            self._entries = [e for e in self._entries if e.connection_id != connection_id]
        else:
            self._entries = []

        self._save()

    def get_recent_queries(
        self,
        connection_id: str | None = None,
        limit: int = 10,
    ) -> list[str]:
        """Get unique recent queries for autocomplete.

        Args:
            connection_id: Filter by connection ID.
            limit: Maximum number of queries to return.

        Returns:
            List of unique query strings.
        """
        seen = set()
        queries = []

        entries = self._entries
        if connection_id:
            entries = [e for e in entries if e.connection_id == connection_id]

        for entry in entries:
            if entry.success and entry.query not in seen:
                seen.add(entry.query)
                queries.append(entry.query)
                if len(queries) >= limit:
                    break

        return queries
