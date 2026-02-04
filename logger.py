import csv
from datetime import datetime
import os

def log_session(category, task, est_mins, actual_mins, completed, notes, focus_level):
    file_name = "focus_sessions.csv"
    # Added Focus_Level to headers
    headers = ["Date", "Category", "Task", "Est_Mins", "Actual_Mins", "Completed", "Notes", "Focus_Level"]
    
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.isfile(file_name)
    
    with open(file_name, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        
        # Added focus_level to the data row
        writer.writerow([date_str, category, task, est_mins, actual_mins, completed, notes, focus_level])