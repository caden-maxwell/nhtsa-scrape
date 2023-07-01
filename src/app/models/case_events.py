import logging
from pathlib import Path
import sqlite3
from sqlite3 import Error

from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt


class CaseEvents(QAbstractListModel):
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
            return str(data)
            ### TODO ###
        return None
    
    @check_connection("Cannot add data")
    def add_data(self, event):
        case_id = event["case_id"]
        event_num = event["event_num"]
        vehicle_num = event["veh_num"]
        make = event["make"]
        model = event["model"]
        model_year = event["model_year"]

        try:
            self.cursor.execute(
                """
                INSERT OR IGNORE INTO case_events (
                    case_id,
                    event_num,
                    vehicle_num,
                    make,
                    model,
                    model_year
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (case_id, event_num, vehicle_num, make, model, model_year)
            )
            self.db.commit()
            if self.cursor.rowcount > 0:
                self.logger.debug(f"Record added to db: case_id={case_id}, event_num={event_num}, veh_num={event_num}")
            else:
                self.logger.warning(f"Record already exists: case_id={case_id}, event_num={event_num}, veh_num={event_num}")
        except sqlite3.Error as e:
            self.logger.error("Error adding record:", e)

    @check_connection("Cannot delete data")
    def delete_data(self, index):
        data = self.data_list[index.row()]
        self.cursor.execute(
            """
            DELETE FROM case_events WHERE (case_id, event_num, vehicle_num) = ?
            """,
            (data[0],)
        )
        self.db.commit()
        self.logger.debug("Deleted profile: " + str(data[1]))
        self.refresh_data()

    @check_connection("Cannot refresh data")
    def refresh_data(self):

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cases (
                case_id INTEGER PRIMARY KEY,
                case_num TEXT,
                summary TEXT
            );
            """
        )
        self.db.commit()

        # If the table doesn't exists, create it
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS case_events (
                case_id INTEGER,
                event_num INTEGER,
                vehicle_num INTEGER,
                make TEXT,
                model TEXT,
                model_year INTEGER,
                PRIMARY KEY (case_id, event_num, vehicle_num),
                FOREIGN KEY (case_id) REFERENCES cases(case_id)
                );
            """
        )
        self.db.commit()

        # Get all the data from the table
        self.cursor.execute('SELECT * FROM case_events')
        self.data_list = self.cursor.fetchall()
        self.layoutChanged.emit()
        self.logger.debug("Refreshed data")

    def __del__(self):
        self.close_database()
