import logging
import os
import sqlite3
from sqlite3 import Error

from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt


class CaseProfiles(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        try:
            self.db = sqlite3.connect(os.path.dirname(__file__) + "/db_saves.sqlite3")
            self.cursor = self.db.cursor()
        except Error as e:
            self.logger.error(e)
            self.db = None
        
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
            ### TODO: Change this later to display the data in a format that makes sense ###
            data = str(data[0]) + " - " + str(data[1]) + " - " + str(data[2]) + " - " + str(data[3])
            return str(data)
            ### TODO ###
        return None
    
    @check_connection("Cannot add data")
    def add_data(self, data):
        self.cursor.execute(
            """
            INSERT INTO case_profiles (name, description, date_created, date_modified)
            VALUES (?, ?, ?, ?)
            """,
            data
        )
        self.db.commit()
        self.logger.debug("Added profile: " + str(data[0]))
        self.refresh_data()

    @check_connection("Cannot delete data")
    def delete_data(self, index):
        data = self.data_list[index.row()]
        self.cursor.execute(
            """
            DELETE FROM case_profiles WHERE profile_id = ?
            """,
            (data[0],)
        )
        self.db.commit()
        self.logger.debug("Deleted profile: " + str(data[1]))
        self.refresh_data()

    @check_connection("Cannot refresh data")
    def refresh_data(self):

        # If the table doesn't exists, create it
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS case_profiles (
                profile_id INTEGER PRIMARY KEY,
                name TEXT,
                description TEXT,
                date_created TEXT,
                date_modified TEXT
                );
            """
        )
        self.db.commit()

        # Get all the data from the table
        self.cursor.execute('SELECT * FROM case_profiles')
        self.data_list = self.cursor.fetchall()
        self.layoutChanged.emit()
        self.logger.debug("Refreshed data")

    def __del__(self):
        self.close_database()
