"""
API Configuration Repository
=============================

Data access layer for API configuration management.

Features:
- CRUD operations for API configurations
- Single active configuration enforcement
- Encrypted API key handling
- Comprehensive error handling
"""

import sqlite3
import logging
from typing import List, Dict, Optional
from app.database import get_db
from app.services.encryption_service import encryption_service

logger = logging.getLogger(__name__)


class APIConfigRepository:
    """Repository for API configuration CRUD operations."""

    def get_all(self) -> List[Dict]:
        """
        Retrieve all API configurations with decrypted keys.

        Returns:
            List of configuration dictionaries with decrypted API keys

        Example:
            >>> repo = APIConfigRepository()
            >>> configs = repo.get_all()
            >>> configs[0]['openai_hk_api_key']  # Decrypted key
        """
        db = get_db()
        try:
            cursor = db.execute('''
                SELECT id, name, description, is_active,
                       openai_hk_base_url, openai_hk_api_key_encrypted,
                       created_at, updated_at
                FROM api_config_groups
                ORDER BY created_at DESC
            ''')

            rows = cursor.fetchall()
            configs = []

            for row in rows:
                try:
                    # Decrypt API key for display
                    decrypted_key = encryption_service.decrypt(row['openai_hk_api_key_encrypted'])

                    config = {
                        'id': row['id'],
                        'name': row['name'],
                        'description': row['description'],
                        'is_active': bool(row['is_active']),
                        'settings': {
                            'openai_hk_base_url': row['openai_hk_base_url'],
                            'openai_hk_api_key': decrypted_key
                        },
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at']
                    }
                    configs.append(config)

                except Exception as e:
                    logger.error(f"Failed to decrypt API key for config ID {row['id']}: {str(e)}")
                    # Skip corrupted configurations
                    continue

            logger.info(f"Retrieved {len(configs)} API configurations")
            return configs

        except sqlite3.Error as e:
            logger.error(f"Database error while retrieving configurations: {str(e)}")
            raise RuntimeError(f"Failed to retrieve configurations: {str(e)}") from e

    def get_by_id(self, config_id: int) -> Optional[Dict]:
        """
        Retrieve configuration by ID.

        Args:
            config_id: Configuration ID

        Returns:
            Configuration dictionary or None if not found
        """
        db = get_db()
        try:
            cursor = db.execute('''
                SELECT id, name, description, is_active,
                       openai_hk_base_url, openai_hk_api_key_encrypted,
                       created_at, updated_at
                FROM api_config_groups
                WHERE id = ?
            ''', (config_id,))

            row = cursor.fetchone()
            if not row:
                logger.warning(f"Configuration ID {config_id} not found")
                return None

            return {
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'is_active': bool(row['is_active']),
                'openai_hk_base_url': row['openai_hk_base_url'],
                'openai_hk_api_key_encrypted': row['openai_hk_api_key_encrypted'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }

        except sqlite3.Error as e:
            logger.error(f"Database error while retrieving config {config_id}: {str(e)}")
            raise RuntimeError(f"Failed to retrieve configuration: {str(e)}") from e

    def get_by_name(self, name: str) -> Optional[Dict]:
        """
        Retrieve configuration by name.

        Args:
            name: Configuration name

        Returns:
            Configuration dictionary or None if not found
        """
        db = get_db()
        try:
            cursor = db.execute('''
                SELECT id, name, description, is_active,
                       openai_hk_base_url, openai_hk_api_key_encrypted,
                       created_at, updated_at
                FROM api_config_groups
                WHERE name = ?
            ''', (name,))

            row = cursor.fetchone()
            if not row:
                return None

            return {
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'is_active': bool(row['is_active']),
                'openai_hk_base_url': row['openai_hk_base_url'],
                'openai_hk_api_key_encrypted': row['openai_hk_api_key_encrypted'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }

        except sqlite3.Error as e:
            logger.error(f"Database error while retrieving config by name '{name}': {str(e)}")
            raise RuntimeError(f"Failed to retrieve configuration: {str(e)}") from e

    def get_active(self) -> Optional[Dict]:
        """
        Retrieve the currently active configuration.

        Returns:
            Active configuration dictionary or None if no active config
        """
        db = get_db()
        try:
            cursor = db.execute('''
                SELECT id, name, description, is_active,
                       openai_hk_base_url, openai_hk_api_key_encrypted,
                       created_at, updated_at
                FROM api_config_groups
                WHERE is_active = 1
                LIMIT 1
            ''')

            row = cursor.fetchone()
            if not row:
                logger.info("No active API configuration found")
                return None

            return {
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'is_active': bool(row['is_active']),
                'openai_hk_base_url': row['openai_hk_base_url'],
                'openai_hk_api_key_encrypted': row['openai_hk_api_key_encrypted'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }

        except sqlite3.Error as e:
            logger.error(f"Database error while retrieving active config: {str(e)}")
            raise RuntimeError(f"Failed to retrieve active configuration: {str(e)}") from e

    def create(
        self,
        name: str,
        openai_hk_base_url: str,
        openai_hk_api_key_encrypted: bytes,
        description: str = '',
        is_active: bool = False
    ) -> int:
        """
        Create new API configuration.

        Args:
            name: Configuration name (must be unique)
            openai_hk_base_url: API base URL
            openai_hk_api_key_encrypted: Encrypted API key (bytes)
            description: Optional description
            is_active: Activation status

        Returns:
            int: ID of created configuration

        Raises:
            ValueError: If name already exists
            RuntimeError: If database operation fails
        """
        db = get_db()
        try:
            # If setting as active, deactivate others first
            if is_active:
                db.execute('UPDATE api_config_groups SET is_active = 0')

            cursor = db.execute('''
                INSERT INTO api_config_groups
                (name, description, is_active, openai_hk_base_url,
                 openai_hk_api_key_encrypted)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, description, int(is_active), openai_hk_base_url,
                  openai_hk_api_key_encrypted))

            config_id = cursor.lastrowid
            db.commit()

            logger.info(f"Created API configuration: {name} (ID: {config_id})")
            return config_id

        except sqlite3.IntegrityError as e:
            db.rollback()
            logger.warning(f"Configuration creation failed - name conflict: {name}")
            raise ValueError(f"Configuration with name '{name}' already exists") from e

        except sqlite3.Error as e:
            db.rollback()
            logger.error(f"Database error while creating configuration: {str(e)}")
            raise RuntimeError(f"Failed to create configuration: {str(e)}") from e

    def update(self, config_id: int, **kwargs) -> None:
        """
        Update configuration fields.

        Args:
            config_id: Configuration ID
            **kwargs: Fields to update (name, description, is_active, etc.)

        Raises:
            ValueError: If configuration not found
            RuntimeError: If database operation fails
        """
        db = get_db()
        try:
            # Verify config exists
            cursor = db.execute('SELECT id FROM api_config_groups WHERE id = ?', (config_id,))
            if not cursor.fetchone():
                raise ValueError(f'Configuration with ID {config_id} not found')

            # Build update query dynamically
            update_fields = []
            update_values = []

            allowed_fields = {
                'name', 'description', 'is_active',
                'openai_hk_base_url', 'openai_hk_api_key_encrypted'
            }

            for field, value in kwargs.items():
                if field in allowed_fields:
                    update_fields.append(f"{field} = ?")
                    # Convert boolean to int for SQLite
                    if field == 'is_active':
                        value = int(value)
                    update_values.append(value)

            if not update_fields:
                logger.warning(f"No valid fields to update for config ID {config_id}")
                return  # Nothing to update

            # If activating, deactivate others first
            if 'is_active' in kwargs and kwargs['is_active']:
                db.execute(
                    'UPDATE api_config_groups SET is_active = 0 WHERE id != ?',
                    (config_id,)
                )

            # Perform update
            update_query = f'''
                UPDATE api_config_groups
                SET {', '.join(update_fields)}
                WHERE id = ?
            '''
            update_values.append(config_id)

            db.execute(update_query, update_values)
            db.commit()

            logger.info(f"Updated API configuration ID {config_id}")

        except sqlite3.IntegrityError as e:
            db.rollback()
            logger.warning(f"Configuration update failed - constraint violation: {str(e)}")
            raise ValueError(f"Update failed: {str(e)}") from e

        except sqlite3.Error as e:
            db.rollback()
            logger.error(f"Database error while updating config {config_id}: {str(e)}")
            raise RuntimeError(f"Failed to update configuration: {str(e)}") from e

    def delete(self, config_id: int) -> None:
        """
        Delete configuration.

        Args:
            config_id: Configuration ID to delete

        Raises:
            ValueError: If configuration not found
            RuntimeError: If database operation fails
        """
        db = get_db()
        try:
            # Verify config exists
            cursor = db.execute('SELECT id FROM api_config_groups WHERE id = ?', (config_id,))
            if not cursor.fetchone():
                raise ValueError(f'Configuration with ID {config_id} not found')

            db.execute('DELETE FROM api_config_groups WHERE id = ?', (config_id,))
            db.commit()

            logger.info(f"Deleted API configuration ID {config_id}")

        except sqlite3.Error as e:
            db.rollback()
            logger.error(f"Database error while deleting config {config_id}: {str(e)}")
            raise RuntimeError(f"Failed to delete configuration: {str(e)}") from e
