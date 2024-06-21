from datetime import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from schema import Base, Profile, Event

db_path = "sqlite:///app.db"  # or use Path object if needed
engine = create_engine(db_path, echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

new_profile = Profile(
    name="Blah blah blah",
    make="Ford",
    model="F-150",
    start_year=2020,
    end_year=2021,
    primary_dmg="Front",
    secondary_dmg="Front Right",
    min_dv=0,
    max_dv=100,
    created=datetime.now().timestamp(),
    modified=datetime.now().timestamp(),
)
session.add(new_profile)
session.commit()

new_event = Event(
    case_id=0,
    vehicle_num=0,
    event_num=1,
    make="Ford",
    model="F-150",
    model_year=2020,
    curb_weight=5000,
    dmg_loc="Front",
    underride="None",
    edr="Yes",
    total_dv=50,
    long_dv=25,
    lat_dv=25,
    smashl=0,
    crush1=0,
    crush2=0,
    crush3=0,
    crush4=0,
    crush5=0,
    crush6=0,
    a_veh_num="1",
    a_make="Ford",
    a_model="F-150",
    a_year="2020",
    a_curb_weight=5000,
    a_dmg_loc="Front",
    c_bar=0,
    NASS_dv=0,
    NASS_vc=0,
    e=0,
    TOT_dv=0,
)

try:
    new_profile.events.append(new_event)
    session.add(new_event)
    session.commit()
except IntegrityError as e:
    print(e.orig)
    session.rollback()

# Don't forget to close the session when done
# session.close()
