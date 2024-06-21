import logging
from pathlib import Path
import sqlite3
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.models import Profile, ProfileEvent, Base, Event


class DatabaseHandler:
    def __init__(self, db_path: Path):
        self.logger = logging.getLogger(__name__)

        self.engine = create_engine(f"sqlite:///{db_path}", echo=True)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        try:
            self.session = self.Session()
        except Exception as e:
            self.logger.error(f"Error creating session: {e}")
            self.session = None

    def close_connection(self):
        """Close the connection to the database."""
        try:
            if self.session:
                self.session.close()
                self.session = None
        except Exception as e:
            self.logger.error(f"Error closing database connection: {e}")

    def get_profile(self, profile_id: int):
        """Get a profile by its ID. Returns a tuple of the profile's attributes."""
        try:
            stmt = select(Profile).where(Profile.id == profile_id)
            return self.session.execute(stmt).scalar()
        except Exception as e:
            self.logger.error(
                f"Error getting profile with profile_id={profile_id}: {e}"
            )
            return None

    def get_profiles(self):
        """Get all profiles. Returns a list of tuples, each containing a profile's attributes."""
        try:
            stmt = select(Profile)
            return self.session.execute(stmt).scalars().all()
        except Exception as e:
            self.logger.error(f"Error getting profiles: {e}")
            return []

    def get_events(self, profile_id: int, include_ignored: bool = True):
        """Get events belonging to a specific profile, optionally including ignored events."""
        try:
            profile_events: list[ProfileEvent] = self.get_profile_events(profile_id)
            if not profile_events:
                return []

            if not include_ignored:
                return [
                    profile_event.event
                    for profile_event in profile_events
                    if not profile_event.ignored
                ]

            return [profile_event.event for profile_event in profile_events]

        except Exception as e:
            self.logger.error(f"Error getting events for profile {profile_id}: {e}")
            return []

    def get_profile_events(self, profile_id: int):
        """Get all profile_events for a profile. Returns a list of tuples, each containing an event's attributes."""
        try:
            stmt = select(ProfileEvent).where(ProfileEvent.profile_id == profile_id)
            return self.session.execute(stmt).scalars().all()
        except Exception as e:
            self.logger.error(
                f"Error getting profile events for profile {profile_id}: {e}"
            )
            return []

    def add_event(self, event: ProfileEvent, profile: Profile):
        """Add an event to a specified profile."""
        try:
            profile.events.append(event)
            self.session.add(event)
            self.session.commit()
        except Exception as e:
            self.logger.error(f"Error adding event: {e}")
            self.session.rollback()
            return

        self.logger.debug(
            f"Added event {event.event_num} from case {event.case_id} to the scrape profile."
        )

    def add_profile(self, profile: Profile):
        try:
            self.session.add(profile)
            self.session.commit()
            print(f"-------'{profile.id}'------")
            return profile.id
        except Exception as e:
            self.logger.error(f"Error adding profile: {e}")
            self.session.rollback()
            return -1

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
        """Get the column names of a table."""
        try:
            stmt = select(table_name)
            return self.session.execute(stmt).keys()
        except Exception as e:
            self.logger.error(f"Error getting headers for table {table_name}: {e}")
            return []

    def __del__(self):
        self.close_connection()
