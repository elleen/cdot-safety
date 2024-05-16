import sqlite3
import numpy as np

connection = sqlite3.connect("cdot_safety.db")
cursor = connection.cursor()

def get_y_labels():
  rows = cursor.execute("SELECT num_crashes FROM ped_crashes ORDER BY intersection ASC").fetchall()
  return np.array(rows)

def get_X_features():
  rows = cursor.execute("SELECT non_ped_crashes, red_light_viol, speed_cam_viol, daily_traffic_counts, potholes_patched FROM cdot_data ORDER BY intersection ASC").fetchall()
  return np.array(rows)