import time
import csv
import os
from datetime import datetime

class Task:
    def __init__(self, name, duration_mins):
        self.name = name
        self.duration_mins = duration_mins
        self.completed = False  
        self.notes = ""         

def get_user_tasks():
    tasks_list = []
    print("--- Define your workday tasks ---")
    while True:
        name = input("Task name (or type 'done' to finish): ")
        if name.lower() == 'done':
            break
        try:
            mins = int(input(f"How many minutes for '{name}'? "))
            tasks_list.append(Task(name, mins))
        except ValueError:
            print("Oops! Please enter a whole number for minutes.")
    return tasks_list

def run_timer(task):
    seconds = task.duration_mins * 60
    print(f"\n>>> Starting: {task.name}")
    while seconds > 0:
        m, s = divmod(seconds, 60) # A shortcut for // and %
        print(f"Time remaining: {m:02d}:{s:02d}", end="\r")
        time.sleep(1)
        seconds -= 1
    print(f"\nDone with {task.name}!")

    alarm_sound = "/System/Library/Sounds/Funk.aiff"
    
    # 2. The 5-second Loop
    print("\n⏰ TIME IS UP!")
    for _ in range(5):
        os.system(f'afplay {alarm_sound}')
        time.sleep(1)

# NEW FUNCTION: The Guardrail
def check_off_task(task):
    while True:
        status = input(f"Did you finish '{task.name}'? (y/n): ").lower()
        if status == 'y':
            task.completed = True
            task.notes = input("Quick note on what you did: ")
            break
        else:
            print("No problem! Keep working. Type 'y' when you are actually done.")

def save_results(tasks):
    # Check if file exists so we know if we need to write the header
    import os
    file_exists = os.path.isfile('work_log.csv')

    with open('work_log.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        
        # Write the header only once
        if not file_exists:
            writer.writerow(["Date", "Task", "Minutes", "Completed", "Notes"])
        
        # Get the current date and time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        for t in tasks:
            writer.writerow([timestamp, t.name, t.duration_mins, t.completed, t.notes])
            
    print(f"\n✅ Progress saved to work_log.csv")

def main():
    # 1. Plan the day
    my_tasks = get_user_tasks()
    
    # 2. Execute the day
    for t in my_tasks:
        run_timer(t)
        check_off_task(t) # Forces you to finish before the next timer starts
        save_results(my_tasks)
    print("\n🚀 All tasks for today are finished!")

if __name__ == "__main__":
    main()