import logging
from pathlib import Path
import sqlite3
from sqlite3 import Error

from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt


class ScrapeProfiles(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        try:
            db_path = Path(__file__).parent / "db_saves.sqlite3"
            self.db = sqlite3.connect(db_path)
            self.cursor = self.db.cursor()
        except Error as e:
            self.logger.error(e)
            self.db = None
        
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scrape_profiles (
                profile_id INTEGER PRIMARY KEY,
                name TEXT,
                description TEXT,
                date_created TEXT,
                date_modified TEXT
                );
            """
        )
        self.db.commit()

        self.data_list = []

    def check_connection(msg=None):
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                if not self.db:
                    if msg:
                        self.logger.error(msg + ": No database connection.")
                    return False
                return func(self, *args, **kwargs)
            return wrapper
        return decorator

    @check_connection("Cannot close database")
    def close_database(self):
        self.cursor.close()
        self.db.close()
        self.db = None
        self.cursor = None

    @check_connection()
    def rowCount(self, parent=QModelIndex()):
        return len(self.data_list)

    @check_connection()
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            data = self.data_list[index.row()]
            name = data[1]
            time = data[3]
            data = str(name) + " - " + str(time)
            return str(data)
        elif role == Qt.ItemDataRole.UserRole:
            return self.data_list[index.row()]
        return None
    
    @check_connection("Cannot add data")
    def add_data(self, data: dict):
        name = data["name"]
        description = data["description"]
        date_created = data["created"]
        date_modified = data["modified"]
        self.cursor.execute(
            """
            INSERT INTO scrape_profiles (name, description, date_created, date_modified)
            VALUES (?, ?, ?, ?)
            """,
            (name, description, date_created, date_modified)
        )
        self.db.commit()
        self.logger.debug(f"Added profile: {name}")
        self.refresh_data()
        return self.cursor.lastrowid

    @check_connection("Cannot delete data")
    def delete_data(self, index: QModelIndex):
        data = self.data_list[index.row()]
        profile_id = data[0]
        self.cursor.execute(
            """
            DELETE FROM scrape_profiles WHERE profile_id = ?
            """,
            (profile_id,)
        )
        self.db.commit()
        name = data[1]
        self.logger.debug(f"Deleted profile: '{name}'")
        self.refresh_data()

    @check_connection("Cannot refresh data")
    def refresh_data(self):
        self.cursor.execute('SELECT * FROM scrape_profiles')
        self.data_list = self.cursor.fetchall()
        self.layoutChanged.emit()
        self.logger.debug("Refreshed data")

    def __del__(self):
        self.close_database()
