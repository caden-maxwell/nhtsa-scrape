from typing import List
from sqlalchemy import ForeignKey, UniqueConstraint, inspect
from sqlalchemy.orm import (
    relationship,
    DeclarativeBase,
    Mapped,
    mapped_column,
)
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy


class Base(DeclarativeBase):
    pass


class Profile(Base):
    __tablename__ = "profile"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    make: Mapped[str] = mapped_column()
    model: Mapped[str] = mapped_column()
    start_year: Mapped[int] = mapped_column()
    end_year: Mapped[int] = mapped_column()
    primary_dmg: Mapped[str] = mapped_column()
    secondary_dmg: Mapped[str] = mapped_column()
    min_dv: Mapped[int] = mapped_column()
    max_dv: Mapped[int] = mapped_column()
    created: Mapped[int] = mapped_column()
    modified: Mapped[int] = mapped_column()

    profile_event_associations: Mapped[List["ProfileEvent"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )

    events: AssociationProxy[List["Event"]] = association_proxy(
        "profile_event_associations",
        "event",
        creator=lambda event_obj: ProfileEvent(event=event_obj),
    )


class Event(Base):
    __tablename__ = "event"
    __table_args__ = (UniqueConstraint("case_id", "vehicle_num", "event_num"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    scraper_type: Mapped[str] = mapped_column()
    summary: Mapped[str] = mapped_column()
    case_num: Mapped[str] = mapped_column()
    case_id: Mapped[int] = mapped_column()
    vehicle_num: Mapped[int] = mapped_column()
    event_num: Mapped[int] = mapped_column()
    make: Mapped[str] = mapped_column()
    model: Mapped[str] = mapped_column()
    model_year: Mapped[int] = mapped_column()
    curb_wgt: Mapped[int] = mapped_column()
    dmg_loc: Mapped[str] = mapped_column()
    underride: Mapped[str] = mapped_column()
    edr: Mapped[str] = mapped_column()
    total_dv: Mapped[int] = mapped_column()
    long_dv: Mapped[int] = mapped_column()
    lat_dv: Mapped[int] = mapped_column()
    smashl: Mapped[int] = mapped_column()
    crush1: Mapped[int] = mapped_column()
    crush2: Mapped[int] = mapped_column()
    crush3: Mapped[int] = mapped_column()
    crush4: Mapped[int] = mapped_column()
    crush5: Mapped[int] = mapped_column()
    crush6: Mapped[int] = mapped_column()
    a_veh_num: Mapped[int] = mapped_column()
    a_veh_desc: Mapped[str] = mapped_column()
    a_make: Mapped[str] = mapped_column()
    a_model: Mapped[str] = mapped_column()
    a_year: Mapped[str] = mapped_column()
    a_curb_wgt: Mapped[int] = mapped_column()
    a_dmg_loc: Mapped[str] = mapped_column()
    c_bar: Mapped[int] = mapped_column()
    NASS_dv: Mapped[int] = mapped_column()
    NASS_vc: Mapped[int] = mapped_column()
    e: Mapped[int] = mapped_column()
    TOT_dv: Mapped[int] = mapped_column()

    event_profile_associations: Mapped[List["ProfileEvent"]] = relationship(
        back_populates="event"
    )

    profiles: AssociationProxy[List["Profile"]] = association_proxy(
        "event_profile_associations",
        "profile",
        creator=lambda profile_obj: ProfileEvent(profile=profile_obj),
    )

    def __iter__(self):
        for column in inspect(self).mapper.columns:
            yield (column.key, getattr(self, column.key))

    def to_tuple(self):
        """Get tuple of all values of attributes"""
        return tuple(value for key, value in self)

    def update(self, event: "Event"):
        for key, value in event:
            if key != "id":
                setattr(self, key, value)


class ProfileEvent(Base):
    __tablename__ = "profile_event"

    profile_id: Mapped[int] = mapped_column(ForeignKey("profile.id"), primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"), primary_key=True)
    ignored: Mapped[bool] = mapped_column(default=False)

    profile: Mapped[Profile] = relationship(back_populates="profile_event_associations")
    event: Mapped[Event] = relationship(back_populates="event_profile_associations")
