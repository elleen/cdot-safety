import csv
import sqlite3

connection = sqlite3.connect("cdot_safety.db")
cursor = connection.cursor()


def setup_coords_to_is_table():
    cursor.execute(
        f"CREATE TABLE IF NOT EXISTS coords_to_is (coord TEXT, intersection TEXT)"
    )
    connection.commit()


def create_new_coord(coord, intersection):
    cursor.execute(f"INSERT INTO coords_to_is VALUES ('{coord}', '{intersection}')")
    connection.commit()


def query_coord(coord):
    rows = cursor.execute(
        f"SELECT intersection FROM coords_to_is WHERE coord = '{coord}'"
    ).fetchone()
    connection.commit()
    return rows


def setup_crashes_table():
    cursor.execute(
        f"CREATE TABLE IF NOT EXISTS crashes (crash_id TEXT PRIMARY KEY, lat FLOAT, long FLOAT)"
    )
    with open("data/crashes.csv") as c_csv:
        c_reader = csv.DictReader(c_csv)
        for row in c_reader:
            lat = round(float(row["LATITUDE"]), 4)
            long = round(float(row["LONGITUDE"]), 4)
            crash_id = row["CRASH_RECORD_ID"]
            if lat and long:
                cursor.execute(
                    f"INSERT INTO crashes VALUES ('{crash_id}', {lat}, {long})"
                )
    connection.commit()


def find_crash(crash_id):
    rows = cursor.execute(
        f"SELECT lat, long FROM crashes WHERE crash_id = '{crash_id}'"
    ).fetchone()
    connection.commit()
    return rows


def setup_ped_crashes_table():
    """
    Table consisting of intersection and # of ped crashes
    """
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS ped_crashes (intersection TEXT, num_crashes INTEGER)"
    )
    connection.commit()


def reset_ped_crashes_table():
    cursor.execute("DELETE from ped_crashes")
    connection.commit()


def increment_ped_crash(intersection):
    rows = cursor.execute(
        f"SELECT * from ped_crashes WHERE intersection = '{intersection}'"
    ).fetchall()
    if not rows:
        cursor.execute(f"INSERT INTO ped_crashes VALUES ('{intersection}', 1)")
    else:
        cursor.execute(
            f"UPDATE ped_crashes SET num_crashes = num_crashes + 1 WHERE intersection = '{intersection}'"
        )
    connection.commit()


def get_intersection_if_ped_crash(lat, long):
    """
    If there was a ped crash in the intersection, return the intersection.
    Otherwise, return None, we don't care about it and don't want to include it in our features.
    """
    if lat and long:
        coord = "{}, {}".format(round(float(lat), 4), round(float(long), 4))
        intersection = cursor.execute(
            f"SELECT intersection FROM coords_to_is WHERE coord = '{coord}'"
        ).fetchone()
        if intersection:
            rows = cursor.execute(
                f"SELECT * from ped_crashes WHERE intersection = '{intersection[0]}'"
            ).fetchone()
            if rows:
                return intersection[0]

    return None


def setup_features_table():
    """
    Table consisting of intersection and:
      - # of non-ped crashes
      - # of red light violations
      - # of speed cam violations
      - average daily traffic counts
      - # potholes patched
    """
    cursor.execute(
        f"CREATE TABLE IF NOT EXISTS cdot_data (intersection TEXT, non_ped_crashes INTEGER, red_light_viol INTEGER, speed_cam_viol INTEGER, daily_traffic_counts INTEGER, potholes_patched INTEGER)"
    )
    cursor.execute(
        f"INSERT INTO cdot_data (intersection) SELECT intersection FROM ped_crashes"
    )
    connection.commit()


def reset_features(feature):
    cursor.execute(f"UPDATE cdot_data SET {feature} = 0")
    connection.commit()


def increment_features(intersection, feature, incr_val):
    rows = cursor.execute(
        f"SELECT * from cdot_data WHERE intersection = '{intersection}'"
    ).fetchone()
    if rows:
        cursor.execute(
            f"UPDATE cdot_data SET {feature} = {feature} + {incr_val} WHERE intersection = '{intersection}'"
        )

    connection.commit()

# setup_features_table()