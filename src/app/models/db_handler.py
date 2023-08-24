import logging
from pathlib import Path

import sqlite3


class DatabaseHandler:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.connection = None
        self.logger = logging.getLogger(__name__)
        self.open_connection()

    def open_connection(self):
        try:
            if not self.connection:
                self.connection = sqlite3.connect(self.db_path)
                self.create_tables()
        except sqlite3.Error as e:
            self.logger.error(f"Error connecting to database: {e}")

    def close_connection(self):
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
        except sqlite3.Error as e:
            self.logger.error(f"Error closing database connection: {e}")

    def create_tables(self):
        cursor = self.connection.cursor()
        try:
            self.connection.execute("PRAGMA foreign_keys = ON")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS profiles (
                    profile_id INTEGER PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    make TEXT,
                    model TEXT,
                    start_year INTEGER,
                    end_year INTEGER,
                    primary_dmg TEXT,
                    secondary_dmg TEXT,
                    min_dv INTEGER,
                    max_dv INTEGER,
                    max_cases INTEGER,
                    created INTEGER,
                    modified INTEGER
                );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS cases (
                    case_id INTEGER PRIMARY KEY,
                    case_num TEXT,
                    summary TEXT
                );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    case_id INTEGER,
                    vehicle_num INTEGER,
                    event_num INTEGER,
                    make TEXT,
                    model TEXT,
                    model_year INTEGER,
                    curb_weight INTEGER,
                    dmg_loc TEXT,
                    underride TEXT,
                    edr TEXT,
                    total_dv INTEGER,
                    long_dv INTEGER,
                    lat_dv INTEGER,
                    smashl INTEGER,
                    crush1 INTEGER,
                    crush2 INTEGER,
                    crush3 INTEGER,
                    crush4 INTEGER,
                    crush5 INTEGER,
                    crush6 INTEGER,
                    a_veh_num TEXT,
                    a_make TEXT,
                    a_model TEXT,
                    a_year TEXT,
                    a_curb_weight INTEGER,
                    a_dmg_loc TEXT,
                    c_bar INTEGER,
                    NASS_dv INTEGER,
                    NASS_vc INTEGER,
                    e INTEGER,
                    TOT_dv INTEGER,
                    PRIMARY KEY (case_id, event_num, vehicle_num),
                    FOREIGN KEY (case_id) REFERENCES cases(case_id)
                );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS profile_events (
                    profile_id INTEGER,
                    case_id INTEGER,
                    vehicle_num INTEGER,
                    event_num INTEGER,
                    ignored INTEGER DEFAULT 0,
                    FOREIGN KEY (profile_id)
                        REFERENCES profiles(profile_id),
                    FOREIGN KEY (case_id, event_num, vehicle_num)
                        REFERENCES events(case_id, event_num, vehicle_num)
                );
                """
            )
            self.connection.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Error creating database tables: {e}")
        finally:
            cursor.close()

    def get_profile(self, profile_id: int):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """
                SELECT * FROM profiles WHERE profile_id = ?
                """,
                (profile_id,),
            )
            return cursor.fetchone()
        except sqlite3.Error as e:
            self.logger.error(f"Error getting profile: {e}")
            return None
        finally:
            cursor.close()

    def get_profiles(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT * FROM profiles")
            return cursor.fetchall()
        except sqlite3.Error as e:
            self.logger.error(f"Error getting profiles: {e}")
        finally:
            cursor.close()

    def get_events(self, profile_id: int, include_ignored: bool = True):
        cursor = self.connection.cursor()
        if include_ignored:
            query = """
                SELECT * FROM events
                WHERE (case_id, vehicle_num, event_num) IN (
                    SELECT case_id, vehicle_num, event_num FROM profile_events
                    WHERE profile_id = ?
                )
                """
        else:
            query = """
                SELECT * FROM events
                WHERE (case_id, vehicle_num, event_num) IN (
                    SELECT case_id, vehicle_num, event_num FROM profile_events
                    WHERE profile_id = ? AND ignored = 0
                )
                """
        try:
            cursor.execute(query, (profile_id,))
            return cursor.fetchall()
        except sqlite3.Error as e:
            self.logger.error(f"Error getting events for profile {profile_id}: {e}")
        finally:
            cursor.close()

    def get_profile_events(self, profile_id: int):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """
                SELECT * FROM profile_events
                WHERE profile_id = ?
                """,
                (profile_id,),
            )
            return cursor.fetchall()
        except sqlite3.Error as e:
            self.logger.error(
                f"Error getting profile events for profile {profile_id}: {e}"
            )
        finally:
            cursor.close()

    def add_event(self, event: dict, profile_id: int):
        cursor = self.connection.cursor()
        try:
            case_id = event["case_id"]
            cursor.execute(
                """
                    INSERT OR IGNORE INTO cases (case_id, case_num, summary)
                    VALUES (?, ?, ?)
                    """,
                (case_id, event["case_num"], event["summary"]),
            )

            vehicle_num = event["vehicle_num"]
            event_num = event["event_num"]
            cursor.execute(
                """
                    INSERT OR REPLACE INTO events (
                        case_id,
                        vehicle_num,
                        event_num,
                        make,
                        model,
                        model_year,
                        curb_weight,
                        dmg_loc,
                        underride,
                        edr,
                        total_dv,
                        long_dv,
                        lat_dv,
                        smashl,
                        crush1,
                        crush2,
                        crush3,
                        crush4,
                        crush5,
                        crush6,
                        a_veh_num,
                        a_make,
                        a_model,
                        a_year,
                        a_curb_weight,
                        a_dmg_loc,
                        c_bar,
                        NASS_dv,
                        NASS_vc,
                        e,
                        TOT_dv
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                (
                    case_id,
                    vehicle_num,
                    event_num,
                    event["make"],
                    event["model"],
                    event["model_year"],
                    event["curb_weight"],
                    event["dmg_loc"],
                    event["underride"],
                    event["edr"],
                    event["total_dv"],
                    event["long_dv"],
                    event["lat_dv"],
                    event["smashl"],
                    event["crush"][0],
                    event["crush"][1],
                    event["crush"][2],
                    event["crush"][3],
                    event["crush"][4],
                    event["crush"][5],
                    event["a_veh_num"],
                    event["a_make"],
                    event["a_model"],
                    event["a_year"],
                    event["a_curb_weight"],
                    event["a_dmg_loc"],
                    event["c_bar"],
                    event["NASS_dv"],
                    event["NASS_vc"],
                    event["e"],
                    event["TOT_dv"],
                ),
            )
            cursor.execute(
                """
                    INSERT OR IGNORE INTO profile_events (
                        profile_id,
                        case_id,
                        vehicle_num,
                        event_num
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                (profile_id, case_id, vehicle_num, event_num),
            )
            self.connection.commit()
        except (KeyError, sqlite3.Error) as e:
            self.logger.error(f"Error adding event: {e}")
            return
        finally:
            cursor.close()
        self.logger.debug(
            f"Added event {event_num} from case {case_id} to the scrape profile."
        )

    def add_profile(self, profile: dict):
        cursor = self.connection.cursor()
        new_profile_id = None
        try:
            cursor.execute(
                """
                INSERT INTO profiles (
                    name,
                    description,
                    make,
                    model,
                    start_year,
                    end_year,
                    primary_dmg,
                    secondary_dmg,
                    min_dv,
                    max_dv,
                    max_cases,
                    created,
                    modified
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    profile["name"],
                    profile["description"],
                    profile["make"],
                    profile["model"],
                    profile["start_year"],
                    profile["end_year"],
                    profile["primary_dmg"],
                    profile["secondary_dmg"],
                    profile["min_dv"],
                    profile["max_dv"],
                    profile["max_cases"],
                    profile["created"],
                    profile["modified"],
                ),
            )
            self.connection.commit()
            new_profile_id = cursor.lastrowid
        except (KeyError, sqlite3.Error) as e:
            self.logger.error(f"Error adding profile: {e}")
            return -1
        finally:
            cursor.close()
        return new_profile_id if new_profile_id else -1

    def delete_event(self, event: tuple, profile_id: int):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """
                DELETE FROM profile_events
                WHERE case_id = ? AND vehicle_num = ? AND event_num = ? AND profile_id = ?
                """,
                (event[0], event[1], event[2], profile_id),
            )
            cursor.execute(
                """
                SELECT * FROM profile_events
                WHERE case_id = ? AND vehicle_num = ? AND event_num = ?
                """,
                (event[0], event[1], event[2]),
            )
            if not cursor.fetchall():
                cursor.execute(
                    """
                    DELETE FROM events
                    WHERE case_id = ? AND vehicle_num = ? AND event_num = ?
                    """,
                    (event[0], event[1], event[2]),
                )
            self.connection.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting event: {e}")
            return
        finally:
            cursor.close()
        self.logger.debug(
            f"Deleted event: Case {event[0]} Vehicle {event[1]} Event {event[2]}"
        )

    def delete_profile(self, profile_id: int):
        cursor = self.connection.cursor()
        try:
            # Delete all events that belong to this profile
            # and are not referred to by another profile
            cursor.execute(
                """
                SELECT case_id, vehicle_num, event_num FROM profile_events
                WHERE profile_id = ?;
                """,
                (profile_id,),
            )
            events = cursor.fetchall()
            for event in events:
                case_id, vehicle_num, event_num = event
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM profile_events
                    WHERE case_id = ?
                        AND vehicle_num = ?
                        AND event_num = ?
                        AND profile_id != ?;
                    """,
                    (case_id, vehicle_num, event_num, profile_id),
                )
                count = cursor.fetchone()[0]
                cursor.execute(
                    """
                    DELETE FROM profile_events
                    WHERE case_id = ?
                        AND vehicle_num = ?
                        AND event_num = ?
                        AND profile_id = ?;
                    """,
                    (case_id, vehicle_num, event_num, profile_id),
                )
                if count < 1:
                    cursor.execute(
                        """
                        DELETE FROM events
                        WHERE case_id = ?
                            AND vehicle_num = ?
                            AND event_num = ?;
                        """,
                        (case_id, vehicle_num, event_num),
                    )
            cursor.execute(
                """
                DELETE FROM profiles
                WHERE profile_id = ?
                """,
                (profile_id,),
            )
            self.connection.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting profile: {e}")
            return
        finally:
            cursor.close()

    def rename_profile(self, profile_id: int, new_name: str):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """
                UPDATE profiles
                SET name = ?
                WHERE profile_id = ?
                """,
                (new_name, profile_id),
            )
            self.connection.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Error renaming profile: {e}")
            return
        finally:
            cursor.close()

    def toggle_ignored(self, event: tuple, profile_id: int):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """
                UPDATE profile_events
                SET ignored = NOT ignored
                WHERE case_id = ? AND vehicle_num = ? AND event_num = ? AND profile_id = ?
                """,
                (event[0], event[1], event[2], profile_id),
            )
            self.connection.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Error toggling ignored: {e}")
            return
        finally:
            cursor.close()
        self.logger.debug(
            f"Toggled ignored for event: Case {event[0]} Vehicle {event[1]} Event {event[2]}"
        )

    def get_headers(self, table_name: str):
        cursor = self.connection.cursor()
        try:
            query = f"PRAGMA table_info({table_name})"
            cursor.execute(query)
            columns = cursor.fetchall()
            return [column[1] for column in columns]  # Column names are at index 1
        except sqlite3.Error as e:
            print("Error fetching column names:", e)
            return []
        finally:
            cursor.close()

    def __del__(self):
        self.close_connection()
