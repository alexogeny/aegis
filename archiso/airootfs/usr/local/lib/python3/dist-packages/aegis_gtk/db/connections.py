"""
Connection profile management for aegis-dbview.

Handles saving, loading, and managing database connection profiles.
Passwords are stored securely using libsecret (GNOME Keyring).
"""

import json
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

# Configuration paths
DBVIEW_CONFIG_DIR = Path.home() / '.config' / 'aegis' / 'dbview'
CONNECTIONS_PATH = DBVIEW_CONFIG_DIR / 'connections.json'

# Keyring service name for credential storage
KEYRING_SERVICE = 'aegis-dbview'


@dataclass
class ConnectionConfig:
    """Database connection configuration."""

    id: str
    name: str
    driver_type: str  # 'sqlite', 'postgresql', 'mysql', etc.
    host: str = ''
    port: int = 0
    database: str = ''
    username: str = ''
    read_only: bool = False
    ssl_mode: str = 'prefer'
    color: str = ''  # Optional accent color for UI
    extra_params: dict = field(default_factory=dict)

    # SSH tunnel settings (optional)
    ssh_enabled: bool = False
    ssh_host: str = ''
    ssh_port: int = 22
    ssh_username: str = ''
    ssh_key_path: str = ''

    @classmethod
    def create_new(cls, name: str, driver_type: str) -> 'ConnectionConfig':
        """Create a new connection with a generated ID."""
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            driver_type=driver_type,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'ConnectionConfig':
        """Create from dictionary."""
        # Handle missing fields with defaults
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            name=data.get('name', 'Unnamed'),
            driver_type=data.get('driver_type', 'sqlite'),
            host=data.get('host', ''),
            port=data.get('port', 0),
            database=data.get('database', ''),
            username=data.get('username', ''),
            read_only=data.get('read_only', False),
            ssl_mode=data.get('ssl_mode', 'prefer'),
            color=data.get('color', ''),
            extra_params=data.get('extra_params', {}),
            ssh_enabled=data.get('ssh_enabled', False),
            ssh_host=data.get('ssh_host', ''),
            ssh_port=data.get('ssh_port', 22),
            ssh_username=data.get('ssh_username', ''),
            ssh_key_path=data.get('ssh_key_path', ''),
        )

    def get_display_info(self) -> str:
        """Get a display string for the connection details."""
        if self.driver_type == 'sqlite':
            return self.database
        elif self.host:
            port_str = f':{self.port}' if self.port else ''
            return f'{self.username}@{self.host}{port_str}/{self.database}'
        return self.database


class CredentialManager:
    """Manages credential storage using libsecret (GNOME Keyring)."""

    def __init__(self):
        self._secret = None
        self._available = False
        self._init_secret()

    def _init_secret(self):
        """Initialize libsecret if available."""
        try:
            import gi

            gi.require_version('Secret', '1')
            from gi.repository import Secret

            self._secret = Secret
            self._available = True

            # Define the schema for our credentials
            self._schema = Secret.Schema.new(
                KEYRING_SERVICE,
                Secret.SchemaFlags.NONE,
                {
                    'connection_id': Secret.SchemaAttributeType.STRING,
                },
            )
        except (ImportError, ValueError):
            self._available = False

    @property
    def is_available(self) -> bool:
        """Check if credential storage is available."""
        return self._available

    def store_password(self, connection_id: str, password: str) -> bool:
        """Store a password for a connection.

        Args:
            connection_id: The connection's unique ID.
            password: The password to store.

        Returns:
            True if successful, False otherwise.
        """
        if not self._available or not password:
            return False

        try:
            self._secret.password_store_sync(
                self._schema,
                {'connection_id': connection_id},
                self._secret.COLLECTION_DEFAULT,
                f'aegis-dbview: {connection_id}',
                password,
                None,
            )
            return True
        except Exception:
            return False

    def get_password(self, connection_id: str) -> str | None:
        """Retrieve a password for a connection.

        Args:
            connection_id: The connection's unique ID.

        Returns:
            The password, or None if not found.
        """
        if not self._available:
            return None

        try:
            password = self._secret.password_lookup_sync(
                self._schema,
                {'connection_id': connection_id},
                None,
            )
            return password
        except Exception:
            return None

    def delete_password(self, connection_id: str) -> bool:
        """Delete a stored password.

        Args:
            connection_id: The connection's unique ID.

        Returns:
            True if successful, False otherwise.
        """
        if not self._available:
            return False

        try:
            self._secret.password_clear_sync(
                self._schema,
                {'connection_id': connection_id},
                None,
            )
            return True
        except Exception:
            return False


class ConnectionManager:
    """Manages database connection profiles."""

    def __init__(self, config_path: Path | None = None):
        """Initialize connection manager.

        Args:
            config_path: Path to connections file. Defaults to standard location.
        """
        self.config_path = config_path or CONNECTIONS_PATH
        self.credentials = CredentialManager()
        self._connections: dict[str, ConnectionConfig] = {}
        self._load()

    def _ensure_config_dir(self):
        """Ensure configuration directory exists."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self):
        """Load connections from disk."""
        self._connections = {}

        if not self.config_path.exists():
            return

        try:
            with open(self.config_path) as f:
                data = json.load(f)

            for conn_data in data.get('connections', []):
                config = ConnectionConfig.from_dict(conn_data)
                self._connections[config.id] = config

        except (json.JSONDecodeError, OSError):
            # Invalid or unreadable file, start fresh
            pass

    def _save(self):
        """Save connections to disk."""
        self._ensure_config_dir()

        data = {
            'version': 1,
            'connections': [c.to_dict() for c in self._connections.values()],
        }

        with open(self.config_path, 'w') as f:
            json.dump(data, f, indent=2)

    def list_connections(self) -> list[ConnectionConfig]:
        """Get all saved connections.

        Returns:
            List of connection configurations.
        """
        return list(self._connections.values())

    def get_connection(self, connection_id: str) -> ConnectionConfig | None:
        """Get a connection by ID.

        Args:
            connection_id: The connection's unique ID.

        Returns:
            The connection configuration, or None if not found.
        """
        return self._connections.get(connection_id)

    def save_connection(
        self,
        config: ConnectionConfig,
        password: str | None = None,
    ) -> bool:
        """Save or update a connection.

        Args:
            config: The connection configuration.
            password: Optional password to store securely.

        Returns:
            True if successful.
        """
        self._connections[config.id] = config
        self._save()

        if password is not None:
            self.credentials.store_password(config.id, password)

        return True

    def delete_connection(self, connection_id: str) -> bool:
        """Delete a connection.

        Args:
            connection_id: The connection's unique ID.

        Returns:
            True if the connection was deleted.
        """
        if connection_id not in self._connections:
            return False

        del self._connections[connection_id]
        self._save()

        # Also delete stored password
        self.credentials.delete_password(connection_id)

        return True

    def duplicate_connection(self, connection_id: str) -> ConnectionConfig | None:
        """Create a duplicate of an existing connection.

        Args:
            connection_id: The connection to duplicate.

        Returns:
            The new connection configuration, or None if source not found.
        """
        source = self.get_connection(connection_id)
        if not source:
            return None

        # Create new config with new ID
        new_config = ConnectionConfig.from_dict(source.to_dict())
        new_config.id = str(uuid.uuid4())
        new_config.name = f'{source.name} (copy)'

        self.save_connection(new_config)

        # Copy password if available
        password = self.credentials.get_password(connection_id)
        if password:
            self.credentials.store_password(new_config.id, password)

        return new_config

    def get_password(self, connection_id: str) -> str | None:
        """Get the password for a connection.

        Args:
            connection_id: The connection's unique ID.

        Returns:
            The password, or None if not stored.
        """
        return self.credentials.get_password(connection_id)

    def get_connection_config(self, connection_id: str) -> dict | None:
        """Get the full connection config dict including password.

        Args:
            connection_id: The connection's unique ID.

        Returns:
            Dictionary with all connection parameters including password.
        """
        config = self.get_connection(connection_id)
        if not config:
            return None

        # Build config dict for driver
        result = {
            'host': config.host,
            'port': config.port,
            'database': config.database,
            'username': config.username,
            'ssl_mode': config.ssl_mode,
            'read_only': config.read_only,
            **config.extra_params,
        }

        # Add password from keyring
        password = self.get_password(connection_id)
        if password:
            result['password'] = password

        return result
