import time
import csv
import os
import subprocess
from datetime import datetime

class Task:
    def __init__(self, name, category, estimated_mins):
        self.name = name
        self.category = category  # New: School, Work, Side Project, etc.
        self.estimated_mins = estimated_mins
        self.actual_mins = 0  
        self.completed = False
        self.notes = ""        

def get_user_tasks():
    tasks_list = []
    print("--- 🌊 FlowClock v2.5: Define Your Day ---")
    while True:
        name = input("\nTask name (or type 'done' to finish): ")
        if name.lower() == 'done':
            break
        
        # New: Category prompt for better dashboarding later
        print("Categories: [S]chool, [W]ork, [P]roject, [A]dmin, [H]ealth")
        cat_input = input(f"Category for '{name}': ").upper()
        
        try:
            mins = int(input(f"Estimated minutes for '{name}': "))
            tasks_list.append(Task(name, cat_input, mins))
        except ValueError:
            print("Oops! Please enter a whole number for minutes.")
    return tasks_list

def run_timer(task):
    sound_high = "/System/Library/Sounds/Glass.aiff"
    sound_low = "/System/Library/Sounds/Basso.aiff"
    
    seconds = task.estimated_mins * 60
    print(f"\n>>> Starting: [{task.category}] {task.name} ({task.estimated_mins}m)")
    
    while seconds > 0:
        m, s = divmod(seconds, 60)
        print(f"⏳ Countdown: {m:02d}:{s:02d}", end="\r")
        time.sleep(1)
        seconds -= 1
    
    task.actual_mins += task.estimated_mins 
    
    print(f"\n\n{'!'*25}\n⏰ TIME IS UP: {task.name.upper()}\n{'!'*25}")
    
    alarm_loop = subprocess.Popen(
        ['/bin/bash', '-c', f'while true; do afplay -v 255 {sound_high} & afplay -v 255 {sound_low}; sleep 1; done']
    )

    input("👉 PRESS [ENTER] TO SILENCE ALARM...")
    alarm_loop.terminate()

    finished = input(f"\nDid you finish '{task.name}'? (y/n): ").lower()
    
    if finished != 'y':
        print("🚀 Entering Overtime... Press Ctrl+C when finished!")
        start_time = time.time() 
        try:
            while True:
                elapsed = int(time.time() - start_time)
                m, s = divmod(elapsed, 60)
                total_so_far = round(task.actual_mins + (elapsed/60), 2)
                print(f"⏱️ Overtime: {m:02d}:{s:02d} (Total: {total_so_far}m)", end="\r")
                time.sleep(1)
        except KeyboardInterrupt:
            end_time = time.time()
            actual_overtime_mins = (end_time - start_time) / 60
            task.actual_mins += round(actual_overtime_mins, 2)
            print(f"\n✅ Added {round(actual_overtime_mins, 2)}m.")
            task.completed = True
    else:
        task.completed = True

    task.notes = input("Quick note/reflection: ")

def save_results(tasks):
    file_exists = os.path.isfile('work_log.csv')
    with open('work_log.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        
        # Updated header to include Category and clear up column confusion
        if not file_exists:
            writer.writerow(["Date", "Category", "Task", "Est_Mins", "Actual_Mins", "Completed", "Notes"])
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        for t in tasks:
            writer.writerow([timestamp, t.category, t.name, t.estimated_mins, t.actual_mins, t.completed, t.notes])
            
    print(f"\n📊 Data saved. Your dashboard will look great with this!")

def main():
    my_tasks = get_user_tasks()
    if not my_tasks: return
    for t in my_tasks:
        run_timer(t)
    save_results(my_tasks)

if __name__ == "__main__":
    main()