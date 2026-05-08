"""
数据存储模块
管理剪贴板历史记录的持久化存储
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Generator

from models.clipboard_item import ClipboardItem
from models.enums import ContentType
from config import settings
from utils.logger import get_logger

# 获取日志器
logger = get_logger('Storage')


class Storage:
    """数据存储类"""

    def __init__(self, db_path: Optional[Path] = None):
        """
        初始化存储

        Args:
            db_path: 数据库路径，默认使用配置中的路径
        """
        self.db_path = db_path or settings.db_path
        logger.info(f"Initializing storage at: {self.db_path}")
        self._init_db()
        logger.info("Storage initialized successfully")

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        获取数据库连接（上下文管理器）

        Yields:
            数据库连接对象
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        """初始化数据库表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            logger.debug("Initializing database schema...")

            # 创建主表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clipboard_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT,
                    content_type TEXT,
                    source_app TEXT,
                    source_window_title TEXT,
                    created_at TIMESTAMP,
                    is_favorite BOOLEAN DEFAULT 0,
                    item_size INTEGER DEFAULT 0,
                    file_list TEXT,
                    content_hash TEXT UNIQUE
                )
            ''')

            # 创建索引
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_created_at
                ON clipboard_items(created_at DESC)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_content_hash
                ON clipboard_items(content_hash)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_content_type
                ON clipboard_items(content_type)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_is_favorite
                ON clipboard_items(is_favorite)
            ''')

            conn.commit()

    def add(self, item: ClipboardItem) -> Optional[int]:
        """
        添加剪贴板项

        Args:
            item: 剪贴板项

        Returns:
            插入的ID，如果已存在则返回None
        """
        # 计算内容哈希（用于去重）
        content_hash = self._compute_content_hash(item)

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT OR IGNORE INTO clipboard_items
                    (content, content_type, source_app, source_window_title,
                     created_at, is_favorite, item_size, file_list, content_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.content,
                    item.content_type.value,
                    item.source_app,
                    item.source_window_title,
                    item.created_at.isoformat(),
                    item.is_favorite,
                    item.item_size,
                    '\n'.join(item.file_list) if item.file_list else '',
                    content_hash
                ))

                if cursor.rowcount > 0:
                    conn.commit()
                    item_id = cursor.lastrowid

                    # 检查是否需要清理旧记录
                    self._cleanup_old_records(cursor, conn)

                    logger.debug(f"New item added to storage: id={item_id}, type={item.content_type.value}")
                    return item_id

                logger.debug("Item already exists (duplicate)")
                return None

        except sqlite3.IntegrityError:
            # 内容已存在
            logger.debug("Item already exists (IntegrityError)")
            return None
        except Exception as e:
            logger.error(f"Error adding item to storage: {e}", exc_info=True)
            raise

    def _compute_content_hash(self, item: ClipboardItem) -> str:
        """
        计算内容哈希（用于去重）

        Args:
            item: 剪贴板项

        Returns:
            内容哈希
        """
        import hashlib
        # 对于图片，使用文件路径哈希；对于文本等，使用内容哈希
        content_to_hash = item.content
        if item.content_type == ContentType.IMAGE:
            # 图片使用文件路径作为哈希基础
            content_to_hash = str(item.content)

        return hashlib.md5(content_to_hash.encode('utf-8')).hexdigest()

    def _cleanup_old_records(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection) -> None:
        """
        清理旧记录（保持不超过最大数量）

        Args:
            cursor: 数据库游标
            conn: 数据库连接
        """
        max_items = settings.get('max_history_items', 100)

        # 先检查总数
        cursor.execute('SELECT COUNT(*) as count FROM clipboard_items')
        total = cursor.fetchone()['count']

        if total > max_items:
            # 删除最旧的记录（保留收藏的）
            cursor.execute('''
                DELETE FROM clipboard_items
                WHERE id IN (
                    SELECT id FROM clipboard_items
                    WHERE is_favorite = 0
                    ORDER BY created_at ASC
                    LIMIT ?
                )
            ''', (total - max_items,))
            conn.commit()

    def get(self, item_id: int) -> Optional[ClipboardItem]:
        """
        获取指定ID的剪贴板项

        Args:
            item_id: 剪贴板项ID

        Returns:
            剪贴板项对象，不存在则返回None
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, content, content_type, source_app, source_window_title,
                       created_at, is_favorite, item_size, file_list
                FROM clipboard_items
                WHERE id = ?
            ''', (item_id,))

            row = cursor.fetchone()

            if row:
                return self._row_to_item(row)
            return None

    def get_all(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        content_type: Optional[ContentType] = None,
        favorite_only: bool = False
    ) -> List[ClipboardItem]:
        """
        获取剪贴板项列表

        Args:
            limit: 最大数量
            offset: 偏移量
            content_type: 内容类型过滤
            favorite_only: 是否只获取收藏项

        Returns:
            剪贴板项列表
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            query = '''
                SELECT id, content, content_type, source_app, source_window_title,
                       created_at, is_favorite, item_size, file_list
                FROM clipboard_items
                WHERE 1=1
            '''
            params = []

            if content_type:
                query += ' AND content_type = ?'
                params.append(content_type.value)

            if favorite_only:
                query += ' AND is_favorite = 1'

            query += ' ORDER BY created_at DESC'

            if limit:
                query += ' LIMIT ?'
                params.append(limit)

            if offset:
                query += ' OFFSET ?'
                params.append(offset)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            logger.debug(f"get_all: query returned {len(rows)} rows")
            return [self._row_to_item(row) for row in rows]

    def search(
        self,
        keyword: str,
        limit: Optional[int] = None
    ) -> List[ClipboardItem]:
        """
        搜索剪贴板项

        Args:
            keyword: 搜索关键词
            limit: 最大数量

        Returns:
            剪贴板项列表
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            query = '''
                SELECT id, content, content_type, source_app, source_window_title,
                       created_at, is_favorite, item_size, file_list
                FROM clipboard_items
                WHERE content LIKE ? OR source_app LIKE ? OR source_window_title LIKE ?
                ORDER BY created_at DESC
            '''
            params = [f'%{keyword}%', f'%{keyword}%', f'%{keyword}%']

            if limit:
                query += ' LIMIT ?'
                params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [self._row_to_item(row) for row in rows]

    def update_favorite(self, item_id: int, is_favorite: bool) -> bool:
        """
        更新收藏状态

        Args:
            item_id: 剪贴板项ID
            is_favorite: 是否收藏

        Returns:
            是否成功
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    UPDATE clipboard_items SET is_favorite = ?
                    WHERE id = ?
                ''', (is_favorite, item_id))

                success = cursor.rowcount > 0
                conn.commit()
                return success
        except Exception:
            return False

    def delete(self, item_id: int) -> bool:
        """
        删除剪贴板项

        Args:
            item_id: 剪贴板项ID

        Returns:
            是否成功
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('DELETE FROM clipboard_items WHERE id = ?', (item_id,))
                success = cursor.rowcount > 0
                conn.commit()
                return success
        except Exception:
            return False

    def clear_all(self) -> bool:
        """
        清空所有记录

        Returns:
            是否成功
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('DELETE FROM clipboard_items')
                conn.commit()
                return True
        except Exception:
            return False

    def get_source_apps(self) -> List[str]:
        """
        获取所有来源应用列表

        Returns:
            应用名称列表
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT DISTINCT source_app
                FROM clipboard_items
                WHERE source_app IS NOT NULL AND source_app != ''
                ORDER BY source_app
            ''')

            rows = cursor.fetchall()

            return [row['source_app'] for row in rows]

    def _row_to_item(self, row: sqlite3.Row) -> ClipboardItem:
        """
        将数据库行转换为剪贴板项对象

        Args:
            row: 数据库行

        Returns:
            剪贴板项对象
        """
        created_at = datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        file_list = row['file_list'].split('\n') if row['file_list'] else []

        return ClipboardItem(
            id=row['id'],
            content=row['content'],
            content_type=ContentType(row['content_type']),
            source_app=row['source_app'] or '',
            source_window_title=row['source_window_title'] or '',
            created_at=created_at,
            is_favorite=bool(row['is_favorite']),
            item_size=row['item_size'],
            file_list=file_list,
        )

    def get_count(self) -> int:
        """
        获取总记录数

        Returns:
            记录数
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) as count FROM clipboard_items')
            count = cursor.fetchone()['count']

            return count
