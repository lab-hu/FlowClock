import pandas as pd
from datetime import datetime, timedelta

def generate_mock_data():
    # Use today's date for all entries
    today = datetime.now().strftime("%Y-%m-%d")
    
    data = [
        # Date, Category, Task, Est, Actual, Completed, Notes, Focus
        [f"{today} 09:15", "Work", "Emails", 30, 35, "Yes", "Cleared inbox", 4],
        [f"{today} 10:30", "Study", "Math", 60, 65, "Yes", "Calculus", 5],
        [f"{today} 11:00", "Study", "Math", 30, 25, "Yes", "Review", 3], # Testing 2 entries in hour 11
        [f"{today} 14:20", "Code", "UI Fix", 45, 50, "Yes", "Dashboard logic", 4],
        [f"{today} 15:45", "Admin", "Planning", 15, 20, "Yes", "Next week", 2],
        [f"{today} 21:10", "Personal", "Reading", 60, 60, "Yes", "New book", 4]
    ]
    
    columns = ["Date", "Category", "Task", "Est_Mins", "Actual_Mins", "Completed", "Notes", "Focus_Level"]
    df = pd.DataFrame(data, columns=columns)
    
    # Save to a specific test file
    df.to_csv("test_sessions.csv", index=False)
    print("✅ 'test_sessions.csv' created successfully with 6 entries.")

if __name__ == "__main__":
    generate_mock_data()