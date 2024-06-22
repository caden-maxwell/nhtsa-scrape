import logging
from pathlib import Path
from sqlalchemy import create_engine, select, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.models import Profile, ProfileEvent, Base, Event


class DatabaseHandler:
    def __init__(self, db_path: Path):
        self.logger = logging.getLogger(__name__)

        self.engine = create_engine(f"sqlite:///{db_path}")
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

    def get_profiles(self):
        """Get all profiles. Returns a list of tuples, each containing a profile's attributes."""
        try:
            stmt = select(Profile)
            return self.session.execute(stmt).scalars().all()
        except Exception as e:
            self.logger.error(f"Error getting profiles: {e}")
            return []

    def get_events(self, profile: Profile, include_ignored: bool = True):
        """Get events belonging to a specific profile, optionally including ignored events."""
        try:
            profile_events: list[ProfileEvent] = self.get_profile_events(profile)
            if not profile_events:
                return []
            events = []

            if not include_ignored:
                events = [
                    profile_event.event
                    for profile_event in profile_events
                    if not profile_event.ignored
                ]
            else:
                events = [profile_event.event for profile_event in profile_events]

            return events

        except Exception as e:
            self.logger.error(f"Error getting events for profile {profile.id}: {e}")
            return []

    def get_profile_events(self, profile: Profile):
        """Get all profile_events for a profile. Returns a list of tuples, each containing an event's attributes."""
        try:
            stmt = select(ProfileEvent).where(ProfileEvent.profile == profile)
            return self.session.execute(stmt).scalars().all()
        except Exception as e:
            self.logger.error(
                f"Error getting profile events for profile {profile.id}: {e}"
            )
            return []

    def add_event(self, event: Event, profile: Profile):
        """Add an event to a specified profile."""
        try:
            # Check if the event already exists in the database, and use the existing event if it does
            stmt = select(Event).where(
                Event.case_id == event.case_id,
                Event.vehicle_num == event.vehicle_num,
                Event.event_num == event.event_num,
            )

            if existing_event := self.session.execute(stmt).scalar_one_or_none():
                event = existing_event
            else:
                self.session.add(event)

            profile.events.append(event)
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
            return profile.id
        except Exception as e:
            self.logger.error(f"Error adding profile: {e}")
            self.session.rollback()
            return -1

    def del_profile_event(self, profile_event: ProfileEvent):
        """Deletes a ProfileEvent and its corresponding Event, but only if the Event is not used by any other Profile."""
        try:
            event = profile_event.event
            self.session.delete(profile_event)

            if not event.profiles:
                self.session.delete(event)

            self.session.commit()
        except Exception as e:
            self.logger.error(f"Error deleting profile event: {e}")
            self.session.rollback()
            return

        self.logger.info(
            f"Deleted event: Case {event.case_id} Vehicle {event.vehicle_num} Event {event.event_num}"
        )

    def delete_profile(self, profile: Profile):
        try:
            self.session.delete(profile)
            for event in profile.events:
                if not event.profiles:
                    self.session.delete(event)
            self.session.commit()

        except Exception as e:
            self.logger.error(f"Error deleting profile {profile.id}: {e}")
            self.session.rollback()
            return

        self.logger.info(f"Deleted profile {profile.id}.")
        return

    def rename_profile(self, profile: Profile, new_name: str):
        try:
            profile.name = new_name
            self.session.commit()
        except Exception as e:
            self.logger.error(f"Error renaming profile: {e}")
            return
        self.logger.info(f"Renamed profile {profile.id} to {new_name}")

    def toggle_ignored(self, profile_event: ProfileEvent):
        try:
            profile_event.ignored = not profile_event.ignored
            self.session.commit()
        except Exception as e:
            self.logger.error(f"Error toggling ignored: {e}")
            self.session.rollback()
            return
        event = profile_event.event
        self.logger.info(
            f"Toggled ignored for event: Case {event.case_id} Vehicle {event.vehicle_num} Event {event.event_num}"
        )

    def get_headers(self, table: Base):
        """Get the column names of a table."""
        try:
            return inspect(table).columns.keys()
        except Exception as e:
            self.logger.error(f"Error getting headers for table {table}: {e}")
            return []

    def __del__(self):
        self.close_connection()
