[Back to SDP Overview](README.md)

---

# Database Design Document

## Data Entities

1. **Cases**
    - **Description:** Represents a CrashViewer case from the NASS/CDS database
    - **Attributes:** Case ID, case number, summary, case profiles that this case might be associated with
    - **Relationships:** Has a many-to-many relationship with Case Profiles. Has a one-to-many relationship with Vehicles.
2. **Event**
    - **Description:** Represents an event in a CrashViewer case from the NASS/CDS database
    - **Attributes:** Case id, vehicle number, year, make, model, curb weight, damage location, underride, EDR report, total delta-v (kmph), longitudinal delta-v, lateral delta-v, smash l, crush, alt vehicle number, alt vehicle year, alt vehicle make, alt vehicle model, alt vehicle curb weight, average crush in inches, total delta-v (mph), NASS_vc, e, tot_dv (I am unsure of what NASS_vc, e, and tot_dv actually mean as of now)
    - **Relationships:** Has a many-to-one relationship with Cases. Has a one-to-many relationship with Case Images.
2. **Case Profiles**
    - **Description:** Represents a case profile that is created by a user.
    - **Attributes:** profile_id, name, description, date_created, date_modified, cases
    - **Relationships:** Has a many-to-many relationship with Cases.
4. **Case Images**
    - **Description:** Represents an image associated with a case.
    - **Attributes:** image_id, case_id, image_name, image_path, date_created, date_modified
    - **Relationships:** Has a many-to-one relationship with Vehicles.

## Database SQL Schema

```sql
CREATE TABLE Cases (
    case_id INTEGER PRIMARY KEY,
    case_num TEXT,
    summary TEXT
);

CREATE TABLE Events (
    case_id INTEGER,
    event_num INTEGER.
    vehicle_num INTEGER,
    year INTEGER,
    make TEXT,
    model TEXT,
    curb_weight INTEGER,
    dmg_location TEXT,
    underride TEXT,
    edr TEXT,
    total_dv INTEGER,
    long_dv INTEGER,
    lateral_dv INTEGER,
    smashl INTEGER,
    crush0 INTEGER,
    crush1 INTEGER,
    crush2 INTEGER,
    crush3 INTEGER,
    crush4 INTEGER,
    a_vehicle_num INTEGER,
    a_year INTEGER,
    a_make TEXT,
    a_model TEXT,
    a_curb_weight INTEGER,
    c_bar INTEGER,
    NASS_dv INTEGER,
    NASS_vc INTEGER,
    e INTEGER,
    TOT_dv INTEGER,
    PRIMARY KEY (case_id, event_num, vehicle_num),
    FOREIGN KEY (case_id) REFERENCES Cases(case_id)
);

CREATE TABLE CaseProfiles (
    profile_id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    date_created TEXT,
    date_modified TEXT
);

CREATE TABLE CaseImages (
    image_id INTEGER PRIMARY KEY,
    vehicle_num INTEGER,
    case_id INTEGER,
    image_name TEXT,
    image_path TEXT,
    date_created TEXT,
    date_modified TEXT,
    FOREIGN KEY (case_id) REFERENCES Cases(case_id)
);

CREATE TABLE CaseProfileCasesMapping (
    profile_id INTEGER,
    case_id INTEGER,
    PRIMARY KEY (profile_id, case_id),
    FOREIGN KEY (profile_id) REFERENCES CaseProfiles(profile_id),
    FOREIGN KEY (case_id) REFERENCES Cases(case_id)
);
```

---

[Back to SDP Overview](README.md)