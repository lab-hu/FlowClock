import customtkinter as ctk
from logger import log_session
from audio_player import play_alarm, stop_alarm
import tkinter as tk

class FlowClock(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window Configuration
        self.title("FlowClock v4.8.9 - Final Release")
        self.geometry("450x800")
        ctk.set_appearance_mode("dark")
        
        # --- State Variables ---
        self.remaining_seconds = 0
        self.total_initial_seconds = 0
        self.elapsed_seconds = 0
        self.is_running = False
        self.mode = "countdown"
        
        self.setup_ui()

    def setup_ui(self):
        # Header
        self.status_label = ctk.CTkLabel(self, text="Ready to Focus", font=("Helvetica", 24, "bold"))
        self.status_label.pack(pady=(30, 10))

        # --- 1. MAIN INPUT GROUP ---
        self.main_input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_input_frame.pack()

        self.category_var = ctk.StringVar(value="Work")
        self.category_menu = ctk.CTkOptionMenu(self.main_input_frame, values=["Work", "Study", "Code", "Admin", "Personal"], variable=self.category_var)
        self.category_menu.pack(pady=5)

        self.task_entry = ctk.CTkEntry(self.main_input_frame, placeholder_text="What are you working on?", width=350, height=40)
        self.task_entry.pack(pady=10)

        self.est_entry = ctk.CTkEntry(self.main_input_frame, placeholder_text="Estimated Minutes (e.g. 25)", width=350, height=40)
        self.est_entry.pack(pady=10)

        # --- 2. CANVAS CIRCLE ---
        self.canvas_size = 220
        self.canvas = tk.Canvas(self, width=self.canvas_size, height=self.canvas_size, 
                               bg="#242424", highlightthickness=0)
        self.canvas.pack(pady=20)
        
        padding = 10
        self.coord = (padding, padding, self.canvas_size - padding, self.canvas_size - padding)
        self.canvas.create_oval(self.coord, outline="#333333", width=12)
        self.progress_arc = self.canvas.create_arc(self.coord, start=90, extent=0, 
                                                 outline="#3a7ebf", width=12, style="arc")

        # Main Timer Display
        self.timer_display = ctk.CTkLabel(self, text="00:00", font=("Helvetica", 60, "bold"))
        self.timer_display.pack(pady=(0, 20))

        # --- 3. MAIN BUTTON GROUP ---
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=10)

        self.start_btn = ctk.CTkButton(self.btn_frame, text="Start", command=self.handle_start, width=120)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.pause_btn = ctk.CTkButton(self.btn_frame, text="Pause", command=self.toggle_pause, 
                                      width=120, fg_color="orange", state="disabled")
        self.pause_btn.grid(row=0, column=1, padx=5)

        # --- 4. REVIEW SECTION ---
        self.review_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.notes_text = ctk.CTkTextbox(self.review_frame, width=350, height=100)
        self.rating_btn_frame = ctk.CTkFrame(self.review_frame, fg_color="transparent")
        self.setup_review_elements()

        # --- 5. SUCCESS SECTION ---
        self.success_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.success_msg = ctk.CTkLabel(self.success_frame, text="", font=("Helvetica", 18, "bold"), wraplength=350)
        self.success_msg.pack(pady=20)
        self.next_task_btn = ctk.CTkButton(self.success_frame, text="Start Next Task", fg_color="green", height=50, command=self.reset_timer)
        self.next_task_btn.pack(pady=10)
        
        # Reset Button
        self.reset_btn = ctk.CTkButton(self, text="Reset & Clear", fg_color="#d9534f", command=self.reset_timer, width=250)
        self.reset_btn.pack(pady=20)

    def setup_review_elements(self):
        ctk.CTkLabel(self.review_frame, text="What did you accomplish?", font=("Helvetica", 14)).pack(pady=5)
        self.notes_text.pack(pady=10)
        ctk.CTkLabel(self.review_frame, text="Rate Focus (1-5)", font=("Helvetica", 14)).pack(pady=5)
        self.rating_btn_frame.pack()
        for i in range(1, 6):
            ctk.CTkButton(self.rating_btn_frame, text=str(i), width=40, 
                         command=lambda val=i: self.finalize_data(val)).grid(row=0, column=i-1, padx=2)

    def handle_start(self):
        if self.mode == "countdown": self.start_countdown()
        else: self.start_stopwatch()

    def start_countdown(self):
        if not self.is_running:
            try:
                if self.remaining_seconds == 0:
                    mins = int(self.est_entry.get())
                    self.remaining_seconds = mins * 60
                    self.total_initial_seconds = self.remaining_seconds
                self.is_running = True
                self.pause_btn.configure(state="normal", text="Pause")
                self.status_label.configure(text="Deep Work...", text_color="white")
                self.update_clock()
            except ValueError:
                self.timer_display.configure(text="Err: Num", text_color="red")

    def toggle_pause(self):
        stop_alarm()
        
        # KEY CHANGE: If we are at 00:00 in stopwatch mode, silence and disable button
        if self.mode == "stopwatch" and self.elapsed_seconds == 0:
            self.is_running = False
            self.pause_btn.configure(state="disabled", text="Pause")
            return 

        if self.is_running:
            self.is_running = False
            self.pause_btn.configure(text="Resume")
        else:
            self.is_running = True
            self.pause_btn.configure(text="Pause")
            self.update_clock()

    def update_clock(self):
        if not self.is_running: return
        if self.mode == "countdown":
            if self.remaining_seconds > 0:
                self.remaining_seconds -= 1
                self.display_time(self.remaining_seconds)
                extent = (self.remaining_seconds / self.total_initial_seconds) * 360
                self.canvas.itemconfig(self.progress_arc, extent=extent)
                self.after(1000, self.update_clock)
            else:
                self.trigger_alarm_state()
        elif self.mode == "stopwatch":
            self.elapsed_seconds += 1
            self.display_time(self.elapsed_seconds)
            self.canvas.itemconfig(self.progress_arc, extent=0)
            self.after(1000, self.update_clock)

    def display_time(self, total_seconds):
        mins, secs = divmod(total_seconds, 60)
        self.timer_display.configure(text=f"{mins:02d}:{secs:02d}")

    def trigger_alarm_state(self):
        self.is_running = False 
        self.display_time(0)
        self.canvas.itemconfig(self.progress_arc, extent=0)
        play_alarm()
        self.mode = "stopwatch"
        self.status_label.configure(text="Time's Up! Still working?", text_color="#3498db")
        self.start_btn.configure(text="Keep Going", fg_color="#3498db")
        self.pause_btn.configure(state="normal", text="Pause") 
        self.reset_btn.configure(text="Log Results", fg_color="green", command=self.initiate_review)

    def start_stopwatch(self):
        stop_alarm()
        self.is_running = True
        self.pause_btn.configure(state="normal", text="Pause")
        self.update_clock()

    def initiate_review(self):
        self.is_running = False
        stop_alarm()
        self.main_input_frame.pack_forget()
        self.btn_frame.pack_forget()
        self.canvas.pack_forget()
        self.reset_btn.pack_forget()
        self.review_frame.pack(pady=10)
        self.status_label.configure(text="Session Review", text_color="#f1c40f")

    def finalize_data(self, focus_score):
        try: est_mins = int(self.est_entry.get())
        except: est_mins = 0
        actual_mins = round(est_mins + (self.elapsed_seconds / 60), 2)
        notes = self.notes_text.get("1.0", "end-1c").strip() or "No notes provided."
        log_session(self.category_var.get(), self.task_entry.get() or "Unnamed Task", est_mins, actual_mins, "Yes", notes, focus_score)
        self.show_success_page(actual_mins)

    def show_success_page(self, actual_mins):
        self.review_frame.pack_forget()
        task_name = self.task_entry.get() or "your task"
        message = f"Great job!\nYou worked on '{task_name}'\nfor {actual_mins} minutes."
        self.success_msg.configure(text=message)
        self.success_frame.pack(pady=20)
        self.status_label.configure(text="Goal Achieved!", text_color="#2ecc71")

    def reset_timer(self):
        self.is_running = False
        self.remaining_seconds = 0
        self.elapsed_seconds = 0
        self.mode = "countdown"
        stop_alarm()
        self.success_frame.pack_forget()
        self.review_frame.pack_forget()
        self.notes_text.delete("1.0", "end")
        self.main_input_frame.pack()
        self.canvas.pack(pady=20)
        self.canvas.itemconfig(self.progress_arc, extent=0)
        self.btn_frame.pack(pady=10)
        self.reset_btn.pack(pady=20)
        self.status_label.configure(text="Ready to Focus", text_color="white")
        self.timer_display.configure(text="00:00", text_color="white")
        self.start_btn.configure(text="Start", fg_color=["#3a7ebf", "#1f538d"], command=self.handle_start)
        self.pause_btn.configure(state="disabled", text="Pause")
        self.reset_btn.configure(text="Reset & Clear", fg_color="#d9534f", command=self.reset_timer)

if __name__ == "__main__":
    app = FlowClock()
    app.mainloop()