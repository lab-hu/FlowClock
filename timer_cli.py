import time
import csv
import os
import subprocess
import sys
from datetime import datetime

class Task:
    def __init__(self, name, category, estimated_mins):
        self.name = name
        self.category = category
        self.estimated_mins = estimated_mins
        self.actual_mins = 0.0  
        self.completed = False
        self.notes = ""

def get_single_task():
    print("\n" + "="*40)
    print("🌊 FLOWCLOCK v3.0: SINGLE-TASK FOCUS")
    print("="*40)
    
    name = input("\nWhat is the mission? ")
    print("\nCategories: [S]chool, [W]ork, [P]roject, [A]dmin, [H]ealth")
    category = input(f"Select category for '{name}': ").upper()
    
    try:
        mins = int(input(f"Minutes allocated for '{name}': "))
        task = Task(name, category, mins)
        
        # THE READY GATE
        print(f"\n✅ SETUP COMPLETE: [{category}] {name} ({mins}m)")
        print("-" * 40)
        input("👉 Press [ENTER] when you are officially ready to start...")
        return task
    except ValueError:
        print("\n❌ Error: Please enter a whole number for minutes.")
        sys.exit()

def run_timer(task):
    seconds_remaining = task.estimated_mins * 60
    
    while seconds_remaining > 0:
        try:
            m, s = divmod(int(seconds_remaining), 60)
            # Live countdown display
            print(f"⏳ FOCUSING: {m:02d}:{s:02d} | (Ctrl+C to Pause/Exit)", end="\r")
            time.sleep(1)
            seconds_remaining -= 1
            task.actual_mins += (1/60) # Log progress incrementally
            
        except KeyboardInterrupt:
            # THE EMERGENCY BRAKE (Pause Menu)
            print(f"\n\n⏸  SYSTEM PAUSED at {m:02d}:{s:02d}")
            print("---------------------------------")
            choice = input("Option: (R)esume, (S)ave & Exit, (D)iscard: ").lower()
            
            if choice == 'r':
                print("\n▶️ Resuming focus...")
                continue 
            elif choice == 's':
                task.notes = input("\nQuick note on partial progress: ")
                save_results([task])
                print("✅ Progress saved. Session ended.")
                sys.exit()
            else:
                print("🚫 Session discarded. No data saved.")
                sys.exit()

    # Trigger alarm once loop completes naturally
    trigger_alarm_and_overtime(task)

def trigger_alarm_and_overtime(task):
    sound_high = "/System/Library/Sounds/Glass.aiff"
    sound_low = "/System/Library/Sounds/Basso.aiff"
    
    print(f"\n\n{'!'*30}\n⏰ TIME IS UP: {task.name.upper()}\n{'!'*30}")
    
    # Start persistent alarm loop
    alarm_process = subprocess.Popen(
        ['/bin/bash', '-c', f'while true; do afplay -v 255 {sound_high} & afplay -v 255 {sound_low}; sleep 1; done']
    )
    input("\n👉 PRESS [ENTER] TO SILENCE ALARM...")
    alarm_process.terminate()

    finished = input(f"\nDid you finish '{task.name}'? (y/n): ").lower()
    
    if finished == 'y':
        task.completed = True
    else:
        # OVERTIME STOPWATCH
        print("\n🚀 ENTERING OVERTIME... (Press Ctrl+C when actually finished)")
        ot_start = time.time()
        try:
            while True:
                elapsed = time.time() - ot_start
                m, s = divmod(int(elapsed), 60)
                print(f"⏱️ Overtime: {m:02d}:{s:02d}", end="\r")
                time.sleep(1)
        except KeyboardInterrupt:
            ot_mins = (time.time() - ot_start) / 60
            task.actual_mins += ot_mins
            task.completed = True
            print(f"\n\n✅ Overtime ended. Added {round(ot_mins, 2)}m.")

    task.notes = input("\nFinal reflection/note: ")

def save_results(tasks):
    file_path = 'work_log.csv'
    file_exists = os.path.isfile(file_path)
    
    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Date", "Category", "Task", "Est_Mins", "Actual_Mins", "Completed", "Notes"])
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        for t in tasks:
            writer.writerow([
                timestamp, 
                t.category, 
                t.name, 
                t.estimated_mins, 
                round(t.actual_mins, 2), 
                t.completed, 
                t.notes
            ])
    print(f"\n📊 DATA LOGGED. Total time for this session: {round(tasks[0].actual_mins, 2)}m.")

def main():
    try:
        current_task = get_single_task()
        run_timer(current_task)
        save_results([current_task])
        print("\n✨ Session Complete. Go take a real break!")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()