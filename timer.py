import customtkinter as ctk
import csv
from datetime import datetime

class FlowClock(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("FlowClock v4.1")
        self.geometry("450x550")
        ctk.set_appearance_mode("dark")
        
        # --- State Variables ---
        self.remaining_seconds = 0
        self.is_running = False
        self.current_task = ""
        self.start_time_str = ""

        # --- UI Layout ---
        self.setup_ui()

    def setup_ui(self):
        # Header
        self.label = ctk.CTkLabel(self, text="Focus Session", font=("Helvetica", 24, "bold"))
        self.label.pack(pady=(30, 20))

        # Inputs
        self.task_entry = ctk.CTkEntry(self, placeholder_text="Mission Name", width=300, height=40)
        self.task_entry.pack(pady=10)

        self.time_entry = ctk.CTkEntry(self, placeholder_text="Minutes", width=300, height=40)
        self.time_entry.pack(pady=10)

        # Timer Display
        self.timer_display = ctk.CTkLabel(self, text="00:00", font=("Helvetica", 80, "bold"))
        self.timer_display.pack(pady=40)

        # Button Container (Horizontal)
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=20)

        self.start_btn = ctk.CTkButton(self.btn_frame, text="Start", command=self.start_timer, width=100)
        self.start_btn.grid(row=0, column=0, padx=10)

        self.pause_btn = ctk.CTkButton(self.btn_frame, text="Pause", command=self.toggle_pause, 
                                      state="disabled", width=100, fg_color="orange")
        self.pause_btn.grid(row=0, column=1, padx=10)

        self.reset_btn = ctk.CTkButton(self.btn_frame, text="Reset", command=self.reset_timer, 
                                      width=100, fg_color="#d9534f")
        self.reset_btn.grid(row=0, column=2, padx=10)

    # --- Logic Methods ---

    def start_timer(self):
        if not self.is_running:
            try:
                if self.remaining_seconds == 0: # New session
                    mins = int(self.time_entry.get())
                    self.remaining_seconds = mins * 60
                    self.current_task = self.task_entry.get() or "Deep Work"
                    self.start_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                self.is_running = True
                self.pause_btn.configure(state="normal", text="Pause")
                self.update_clock()
            except ValueError:
                self.timer_display.configure(text="Error", text_color="red")

    def toggle_pause(self):
        if self.is_running:
            self.is_running = False
            self.pause_btn.configure(text="Resume")
        else:
            self.is_running = True
            self.pause_btn.configure(text="Pause")
            self.update_clock()

    def update_clock(self):
        if self.is_running and self.remaining_seconds > 0:
            mins, secs = divmod(self.remaining_seconds, 60)
            self.timer_display.configure(text=f"{mins:02d}:{secs:02d}", text_color="white")
            self.remaining_seconds -= 1
            self.after(1000, self.update_clock)
        elif self.remaining_seconds <= 0 and self.is_running:
            self.finish_session()

    def reset_timer(self):
        self.is_running = False
        self.remaining_seconds = 0
        self.timer_display.configure(text="00:00", text_color="white")
        self.pause_btn.configure(state="disabled", text="Pause")

    def finish_session(self):
        self.is_running = False
        self.timer_display.configure(text="Done!", text_color="#5cb85c")
        self.log_to_csv()

    def log_to_csv(self):
        # The logic from your v3.0
        data = [self.start_time_str, self.current_task, "Completed"]
        with open("work_log.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(data)
        print("Logged to CSV.")

if __name__ == "__main__":
    app = FlowClock()
    app.mainloop()