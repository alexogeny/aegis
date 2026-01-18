"""
Query execution engine for aegis-dbview.

Handles async query execution with progress tracking and cancellation.
"""

import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Any
from collections.abc import Callable

from .drivers.base import DatabaseDriver, QueryResult
from .history import QueryHistory, HistoryEntry


class QueryState(Enum):
    """Query execution state."""

    IDLE = 'idle'
    RUNNING = 'running'
    CANCELLING = 'cancelling'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


@dataclass
class QueryExecution:
    """Represents a query execution."""

    query: str
    state: QueryState = QueryState.IDLE
    result: QueryResult | None = None
    task: asyncio.Task | None = None


class QueryExecutor:
    """Manages query execution with state tracking and history."""

    def __init__(
        self,
        driver: DatabaseDriver,
        history: QueryHistory | None = None,
        connection_id: str = '',
        connection_name: str = '',
    ):
        """Initialize query executor.

        Args:
            driver: The database driver to use.
            history: Query history manager.
            connection_id: ID of the current connection.
            connection_name: Display name of the connection.
        """
        self.driver = driver
        self.history = history
        self.connection_id = connection_id
        self.connection_name = connection_name

        self._current_execution: QueryExecution | None = None
        self._on_state_change: Callable[[QueryState], None] | None = None

    @property
    def state(self) -> QueryState:
        """Get current execution state."""
        if self._current_execution:
            return self._current_execution.state
        return QueryState.IDLE

    @property
    def is_running(self) -> bool:
        """Check if a query is currently running."""
        return self.state == QueryState.RUNNING

    def on_state_change(self, callback: Callable[[QueryState], None]):
        """Set callback for state changes.

        Args:
            callback: Function to call when state changes.
        """
        self._on_state_change = callback

    def _set_state(self, state: QueryState):
        """Update execution state and notify callback."""
        if self._current_execution:
            self._current_execution.state = state
        if self._on_state_change:
            self._on_state_change(state)

    async def execute(
        self,
        query: str,
        params: tuple | dict | None = None,
        limit: int | None = None,
    ) -> QueryResult:
        """Execute a query.

        Args:
            query: SQL query to execute.
            params: Query parameters.
            limit: Maximum rows to return.

        Returns:
            QueryResult with columns, rows, and metadata.
        """
        # Cancel any existing execution
        if self._current_execution and self._current_execution.state == QueryState.RUNNING:
            await self.cancel()

        self._current_execution = QueryExecution(query=query)
        self._set_state(QueryState.RUNNING)

        try:
            result = await self.driver.execute(query, params, limit)

            if self._current_execution.state == QueryState.CANCELLING:
                self._set_state(QueryState.CANCELLED)
                return QueryResult(
                    columns=[],
                    rows=[],
                    row_count=0,
                    error='Query cancelled',
                )

            self._current_execution.result = result

            if result.is_success:
                self._set_state(QueryState.COMPLETED)
            else:
                self._set_state(QueryState.FAILED)

            # Record in history
            if self.history:
                self.history.add(
                    query=query,
                    connection_id=self.connection_id,
                    connection_name=self.connection_name,
                    execution_time_ms=result.execution_time_ms,
                    row_count=result.row_count,
                    success=result.is_success,
                    error=result.error,
                )

            return result

        except asyncio.CancelledError:
            self._set_state(QueryState.CANCELLED)
            return QueryResult(
                columns=[],
                rows=[],
                row_count=0,
                error='Query cancelled',
            )

        except Exception as e:
            self._set_state(QueryState.FAILED)
            error_result = QueryResult(
                columns=[],
                rows=[],
                row_count=0,
                error=str(e),
            )

            # Record failed query in history
            if self.history:
                self.history.add(
                    query=query,
                    connection_id=self.connection_id,
                    connection_name=self.connection_name,
                    execution_time_ms=0,
                    row_count=0,
                    success=False,
                    error=str(e),
                )

            return error_result

    async def execute_in_background(
        self,
        query: str,
        params: tuple | dict | None = None,
        limit: int | None = None,
        on_complete: Callable[[QueryResult], None] | None = None,
    ) -> asyncio.Task:
        """Execute a query in the background.

        Args:
            query: SQL query to execute.
            params: Query parameters.
            limit: Maximum rows to return.
            on_complete: Callback when query completes.

        Returns:
            The asyncio task for the execution.
        """

        async def _run():
            result = await self.execute(query, params, limit)
            if on_complete:
                on_complete(result)
            return result

        task = asyncio.create_task(_run())
        if self._current_execution:
            self._current_execution.task = task
        return task

    async def cancel(self) -> bool:
        """Cancel the currently running query.

        Returns:
            True if cancellation was initiated.
        """
        if not self._current_execution:
            return False

        if self._current_execution.state != QueryState.RUNNING:
            return False

        self._set_state(QueryState.CANCELLING)

        # Try driver-level cancellation
        if self.driver.supports_cancel:
            try:
                await self.driver.cancel_query()
            except Exception:
                pass

        # Cancel the task
        if self._current_execution.task:
            self._current_execution.task.cancel()
            try:
                await self._current_execution.task
            except asyncio.CancelledError:
                pass

        self._set_state(QueryState.CANCELLED)
        return True

    async def explain(self, query: str) -> str:
        """Get execution plan for a query.

        Args:
            query: SQL query to explain.

        Returns:
            Execution plan as a string.
        """
        if not self.driver.supports_explain:
            return 'EXPLAIN not supported for this database'

        return await self.driver.explain_query(query)

    def get_last_result(self) -> QueryResult | None:
        """Get the result of the last execution.

        Returns:
            The last QueryResult, or None if no query has been executed.
        """
        if self._current_execution:
            return self._current_execution.result
        return None
