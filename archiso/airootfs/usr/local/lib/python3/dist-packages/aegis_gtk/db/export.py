"""
Query result export for aegis-dbview.

Supports exporting query results to CSV, JSON, and SQL formats.
"""

import csv
import io
import json
from enum import Enum
from pathlib import Path
from typing import Any

from .drivers.base import QueryResult, ColumnInfo


class ExportFormat(Enum):
    """Supported export formats."""

    CSV = 'csv'
    JSON = 'json'
    JSON_LINES = 'jsonl'
    SQL_INSERT = 'sql_insert'
    SQL_COPY = 'sql_copy'
    MARKDOWN = 'markdown'


class ResultExporter:
    """Exports query results to various formats."""

    def __init__(self, result: QueryResult):
        """Initialize exporter with query result.

        Args:
            result: The QueryResult to export.
        """
        self.result = result

    def export(
        self,
        format: ExportFormat,
        file_path: Path | None = None,
        table_name: str = 'data',
        include_headers: bool = True,
    ) -> str:
        """Export result to specified format.

        Args:
            format: The export format.
            file_path: Optional path to write file. If None, returns string.
            table_name: Table name for SQL exports.
            include_headers: Include column headers (for CSV/Markdown).

        Returns:
            The exported data as a string.
        """
        exporters = {
            ExportFormat.CSV: self._to_csv,
            ExportFormat.JSON: self._to_json,
            ExportFormat.JSON_LINES: self._to_jsonl,
            ExportFormat.SQL_INSERT: lambda: self._to_sql_insert(table_name),
            ExportFormat.SQL_COPY: lambda: self._to_sql_copy(table_name),
            ExportFormat.MARKDOWN: lambda: self._to_markdown(include_headers),
        }

        exporter = exporters.get(format)
        if not exporter:
            raise ValueError(f'Unsupported format: {format}')

        content = exporter()

        if file_path:
            file_path.write_text(content, encoding='utf-8')

        return content

    def _to_csv(self) -> str:
        """Export to CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header row
        writer.writerow([col.name for col in self.result.columns])

        # Data rows
        for row in self.result.rows:
            writer.writerow([self._format_value(v) for v in row])

        return output.getvalue()

    def _to_json(self) -> str:
        """Export to JSON array format."""
        col_names = [col.name for col in self.result.columns]

        data = []
        for row in self.result.rows:
            row_dict = {}
            for i, value in enumerate(row):
                row_dict[col_names[i]] = self._json_serialize(value)
            data.append(row_dict)

        return json.dumps(data, indent=2, ensure_ascii=False, default=str)

    def _to_jsonl(self) -> str:
        """Export to JSON Lines format (one JSON object per line)."""
        col_names = [col.name for col in self.result.columns]
        lines = []

        for row in self.result.rows:
            row_dict = {}
            for i, value in enumerate(row):
                row_dict[col_names[i]] = self._json_serialize(value)
            lines.append(json.dumps(row_dict, ensure_ascii=False, default=str))

        return '\n'.join(lines)

    def _to_sql_insert(self, table_name: str) -> str:
        """Export as SQL INSERT statements."""
        if not self.result.rows:
            return f'-- No data to insert into {table_name}\n'

        col_names = ', '.join(f'"{col.name}"' for col in self.result.columns)
        lines = []

        for row in self.result.rows:
            values = ', '.join(self._sql_value(v) for v in row)
            lines.append(f'INSERT INTO "{table_name}" ({col_names}) VALUES ({values});')

        return '\n'.join(lines)

    def _to_sql_copy(self, table_name: str) -> str:
        """Export as PostgreSQL COPY format."""
        if not self.result.rows:
            return f'-- No data to copy into {table_name}\n'

        col_names = ', '.join(f'"{col.name}"' for col in self.result.columns)
        lines = [f'COPY "{table_name}" ({col_names}) FROM stdin;']

        for row in self.result.rows:
            values = '\t'.join(self._copy_value(v) for v in row)
            lines.append(values)

        lines.append('\\.')
        return '\n'.join(lines)

    def _to_markdown(self, include_headers: bool = True) -> str:
        """Export as Markdown table."""
        if not self.result.columns:
            return 'No data\n'

        lines = []

        if include_headers:
            # Header row
            header = '| ' + ' | '.join(col.name for col in self.result.columns) + ' |'
            lines.append(header)

            # Separator
            separator = '| ' + ' | '.join('---' for _ in self.result.columns) + ' |'
            lines.append(separator)

        # Data rows
        for row in self.result.rows:
            values = [self._format_value(v).replace('|', '\\|') for v in row]
            lines.append('| ' + ' | '.join(values) + ' |')

        return '\n'.join(lines)

    def _format_value(self, value: Any) -> str:
        """Format a value for display."""
        if value is None:
            return ''
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if isinstance(value, bytes):
            return f'<{len(value)} bytes>'
        return str(value)

    def _json_serialize(self, value: Any) -> Any:
        """Prepare a value for JSON serialization."""
        if value is None:
            return None
        if isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, bytes):
            return value.hex()
        if hasattr(value, 'isoformat'):
            return value.isoformat()
        return str(value)

    def _sql_value(self, value: Any) -> str:
        """Format a value for SQL INSERT."""
        if value is None:
            return 'NULL'
        if isinstance(value, bool):
            return 'TRUE' if value else 'FALSE'
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, bytes):
            return f"E'\\\\x{value.hex()}'"
        # String - escape quotes
        escaped = str(value).replace("'", "''")
        return f"'{escaped}'"

    def _copy_value(self, value: Any) -> str:
        """Format a value for PostgreSQL COPY."""
        if value is None:
            return '\\N'
        if isinstance(value, bool):
            return 't' if value else 'f'
        if isinstance(value, bytes):
            return f'\\\\x{value.hex()}'
        # Escape special characters
        s = str(value)
        s = s.replace('\\', '\\\\')
        s = s.replace('\t', '\\t')
        s = s.replace('\n', '\\n')
        s = s.replace('\r', '\\r')
        return s


def get_format_extension(format: ExportFormat) -> str:
    """Get the file extension for an export format.

    Args:
        format: The export format.

    Returns:
        File extension including the dot.
    """
    extensions = {
        ExportFormat.CSV: '.csv',
        ExportFormat.JSON: '.json',
        ExportFormat.JSON_LINES: '.jsonl',
        ExportFormat.SQL_INSERT: '.sql',
        ExportFormat.SQL_COPY: '.sql',
        ExportFormat.MARKDOWN: '.md',
    }
    return extensions.get(format, '.txt')


def get_format_mime_type(format: ExportFormat) -> str:
    """Get the MIME type for an export format.

    Args:
        format: The export format.

    Returns:
        MIME type string.
    """
    mime_types = {
        ExportFormat.CSV: 'text/csv',
        ExportFormat.JSON: 'application/json',
        ExportFormat.JSON_LINES: 'application/x-ndjson',
        ExportFormat.SQL_INSERT: 'application/sql',
        ExportFormat.SQL_COPY: 'application/sql',
        ExportFormat.MARKDOWN: 'text/markdown',
    }
    return mime_types.get(format, 'text/plain')
