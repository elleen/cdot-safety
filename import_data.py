import db
import csv

from coords_to_intersection import get_intersection


def import_ped_crashes():
    # we only want to import this file once, so wipe the table before running
    db.reset_ped_crashes_table()

    with open("data/crashes-people.csv") as crashes_people_csv:
        cp_reader = csv.DictReader(crashes_people_csv)
        for row in cp_reader:
            if row["PERSON_TYPE"] != "PEDESTRIAN":
                continue

            crash_id = row["CRASH_RECORD_ID"]

            crashes_row = db.find_crash(crash_id)
            if crashes_row:
                lat = float(crashes_row[0])
                long = float(crashes_row[1])
                intersection = get_intersection(lat, long)

                db.increment_ped_crash(intersection)


def import_non_ped_crashes():
    db.reset_features("non_ped_crashes")

    with open("data/crashes-people.csv") as crashes_people_csv:
        cp_reader = csv.DictReader(crashes_people_csv)
        for row in cp_reader:
            if row["PERSON_TYPE"] == "PEDESTRIAN":
                continue

            crash_id = row["CRASH_RECORD_ID"]

            crashes_row = db.find_crash(crash_id)
            if crashes_row:
                lat = float(crashes_row[0])
                long = float(crashes_row[1])

                # we don't care about this if it's not in the ped_crashes table
                intersection = db.get_intersection_if_ped_crash(lat, long)
                
                if intersection:
                    db.increment_features(intersection, "non_ped_crashes", 1)
                    print(f"[non_ped_crashes] incremented {intersection}")


def import_red_light_violations():
    db.reset_features("red_light_viol")
    with open("data/red-light-violations.csv") as rlv_csv:
        rlv_reader = csv.DictReader(rlv_csv)
        for row in rlv_reader:
            lat = row["LATITUDE"]
            long = row["LONGITUDE"]

            # we don't care about this if it's not in the ped_crashes table
            intersection = db.get_intersection_if_ped_crash(lat, long)
            if intersection:
                num_viols = row["VIOLATIONS"]
                db.increment_features(intersection, "red_light_viol", num_viols)
                print(f"[red_light_viol] incremented {intersection}")


def import_speed_cam_violations():
    db.reset_features("speed_cam_viol")
    with open("data/speed-camera-violations.csv") as scv_csv:
        scv_reader = csv.DictReader(scv_csv)
        for row in scv_reader:
            lat = row["LATITUDE"]
            long = row["LONGITUDE"]

            # we don't care about this if it's not in the ped_crashes table
            intersection = db.get_intersection_if_ped_crash(lat, long)

            if intersection:
                num_viols = row["VIOLATIONS"]
                db.increment_features(intersection, "speed_cam_viol", num_viols)
                print(f"[speed_cam_viol] incremented {intersection}")


def import_traffic_counts():
    db.reset_features("daily_traffic_counts")
    with open("data/traffic-counts.csv") as t_csv:
        t_reader = csv.DictReader(t_csv)
        for row in t_reader:
            lat = row["Latitude"]
            long = row["Longitude"]

            # we don't care about this if it's not in the ped_crashes table
            intersection = db.get_intersection_if_ped_crash(lat, long)

            if intersection:
                num_traffic = row["Total Passing Vehicle Volume"]
                db.increment_features(intersection, "daily_traffic_counts", num_traffic)
                print(f"[daily_traffic_counts] incremented {intersection}")


def import_potholes():
    db.reset_features("potholes_patched")

    with open("data/potholes.csv") as p_csv:
        p_reader = csv.DictReader(p_csv)
        for row in p_reader:
            lat = row["LATITUDE"]
            long = row["LONGITUDE"]

            # we don't care about this if it's not in the ped_crashes table
            intersection = db.get_intersection_if_ped_crash(lat, long)

            if intersection:
                num_potholes = row["NUMBER OF POTHOLES FILLED ON BLOCK"]
                db.increment_features(intersection, "potholes_patched", num_potholes)
                print(f"[potholes_patched] incremented {intersection}")


def import_features():
    # import_non_ped_crashes()
    # import_red_light_violations()
    # import_speed_cam_violations()
    import_traffic_counts()
    import_potholes()


import_features()

# import_ped_crashes()
