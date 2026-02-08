import customtkinter as ctk
from logger import log_session
from audio_player import play_alarm, stop_alarm
import tkinter as tk

class FlowClock(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("FlowClock v5.2 - Focus & Review")
        self.geometry("450x800")
        ctk.set_appearance_mode("dark")
        
        self.remaining_seconds = 0
        self.total_initial_seconds = 0
        self.elapsed_seconds = 0
        self.is_running = False
        self.mode = "countdown"
        
        self.setup_ui()

    def setup_ui(self):
        self.status_label = ctk.CTkLabel(self, text="Ready to Focus", font=("Helvetica", 24, "bold"))
        self.status_label.pack(pady=(40, 10))

        # --- PAGE 1: INPUT ---
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="both", expand=True)

        self.category_var = ctk.StringVar(value="Work")
        self.category_menu = ctk.CTkOptionMenu(self.input_frame, values=["Work", "Study", "Code", "Admin", "Personal"], variable=self.category_var)
        self.category_menu.pack(pady=10)

        self.task_entry = ctk.CTkEntry(self.input_frame, placeholder_text="What are you working on?", width=350, height=45)
        self.task_entry.pack(pady=10)

        self.est_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Estimated Minutes (e.g. 25)", width=350, height=45)
        self.est_entry.pack(pady=10)

        self.start_btn = ctk.CTkButton(self.input_frame, text="Start Session", command=self.handle_start, width=250, height=50, font=("Helvetica", 16, "bold"))
        self.start_btn.pack(pady=30)

        # --- PAGE 2: TIMER ---
        self.timer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.canvas_size = 260
        self.canvas = tk.Canvas(self.timer_frame, width=self.canvas_size, height=self.canvas_size, bg="#242424", highlightthickness=0)
        self.canvas.pack(pady=20)
        
        padding = 15
        self.coord = (padding, padding, self.canvas_size - padding, self.canvas_size - padding)
        self.canvas.create_oval(self.coord, outline="#333333", width=12)
        self.progress_arc = self.canvas.create_arc(self.coord, start=90, extent=0, outline="#3a7ebf", width=12, style="arc")
        self.timer_text = self.canvas.create_text(self.canvas_size/2, self.canvas_size/2, text="00:00", fill="white", font=("Helvetica", 50, "bold"))

        btn_container = ctk.CTkFrame(self.timer_frame, fg_color="transparent")
        btn_container.pack(pady=20)
        self.pause_btn = ctk.CTkButton(btn_container, text="Pause", command=self.toggle_pause, width=140, height=45, fg_color="orange")
        self.pause_btn.pack(side="left", padx=10)
        self.finish_btn = ctk.CTkButton(btn_container, text="Finish", command=self.initiate_review, width=120, height=45, fg_color="#2ecc71")
        self.finish_btn.pack(side="left", padx=10)

        # --- PAGE 3: REVIEW ---
        self.review_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctk.CTkLabel(self.review_frame, text="What did you accomplish?", font=("Helvetica", 16)).pack(pady=10)
        self.notes_text = ctk.CTkTextbox(self.review_frame, width=350, height=120)
        self.notes_text.pack(pady=10)
        self.rating_btn_frame = ctk.CTkFrame(self.review_frame, fg_color="transparent")
        self.rating_btn_frame.pack(pady=10)
        for i in range(1, 6):
            ctk.CTkButton(self.rating_btn_frame, text=str(i), width=50, command=lambda val=i: self.finalize_data(val)).grid(row=0, column=i-1, padx=4)

        # --- PAGE 4: SUCCESS SUMMARY ---
        self.success_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.success_label = ctk.CTkLabel(self.success_frame, text="", font=("Helvetica", 18), wraplength=350, justify="center")
        self.success_label.pack(pady=40)
        self.next_task_btn = ctk.CTkButton(self.success_frame, text="Start Next Task", fg_color="#3a7ebf", height=50, width=250, command=self.reset_timer)
        self.next_task_btn.pack(pady=10)

    # --- LOGIC ---

    def handle_start(self):
        try:
            mins = int(self.est_entry.get())
            self.input_frame.pack_forget()
            self.timer_frame.pack(fill="both", expand=True)
            self.start_countdown()
        except:
            self.status_label.configure(text="Invalid Minutes!", text_color="red")
            self.after(1000, lambda: self.status_label.configure(text="Ready to Focus", text_color="white"))

    def start_countdown(self):
        if not self.is_running:
            if self.remaining_seconds == 0:
                self.remaining_seconds = int(self.est_entry.get()) * 60
                self.total_initial_seconds = self.remaining_seconds
            self.is_running = True
            self.update_clock()

    def toggle_pause(self):
        try: stop_alarm()
        except: pass
        if self.mode == "stopwatch" and not self.is_running:
            self.is_running = True
            self.pause_btn.configure(text="Pause", fg_color="orange")
            self.update_clock()
            return
        if self.is_running:
            self.is_running = False
            self.pause_btn.configure(text="Resume", fg_color="#2ecc71")
        else:
            self.is_running = True
            self.pause_btn.configure(text="Pause", fg_color="orange")
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
            self.canvas.itemconfig(self.progress_arc, extent=359.9, outline="#16a085")
            self.after(1000, self.update_clock)

    def display_time(self, total_seconds):
        mins, secs = divmod(total_seconds, 60)
        self.canvas.itemconfig(self.timer_text, text=f"{mins:02d}:{secs:02d}")

    def trigger_alarm_state(self):
        self.is_running = False 
        play_alarm()
        self.mode = "stopwatch"
        self.status_label.configure(text="Goal Reached!", text_color="#3498db")
        self.pause_btn.configure(text="Silence & Continue", fg_color="#3498db")
        self.canvas.itemconfig(self.timer_text, fill="#3498db")

    def initiate_review(self):
        self.is_running = False
        try: stop_alarm()
        except: pass
        self.timer_frame.pack_forget()
        self.review_frame.pack(fill="both", expand=True)
        self.status_label.configure(text="Session Review", text_color="#f1c40f")

    def finalize_data(self, focus_score):
        # Calculation
        est_mins = int(self.est_entry.get())
        actual_mins = round(est_mins + (self.elapsed_seconds / 60), 2)
        task_name = self.task_entry.get() or "Unnamed Task"
        
        # Log to CSV
        log_session(self.category_var.get(), task_name, est_mins, actual_mins, "Yes", self.notes_text.get("1.0", "end-1c"), focus_score)
        
        # Show Success Screen
        self.review_frame.pack_forget()
        self.success_frame.pack(fill="both", expand=True)
        self.status_label.configure(text="Well Done!", text_color="#2ecc71")
        
        summary = f"Session Complete!\n\nTask: {task_name}\nTime: {actual_mins} minutes\nFocus Score: {focus_score}/5"
        self.success_label.configure(text=summary)

    def reset_timer(self):
        self.is_running = False
        self.remaining_seconds = 0
        self.elapsed_seconds = 0
        self.mode = "countdown"
        self.success_frame.pack_forget()
        self.input_frame.pack(fill="both", expand=True)
        self.canvas.itemconfig(self.progress_arc, extent=0, outline="#3a7ebf")
        self.canvas.itemconfig(self.timer_text, fill="white", text="00:00")
        self.status_label.configure(text="Ready to Focus", text_color="white")
        self.notes_text.delete("1.0", "end")

if __name__ == "__main__":
    app = FlowClock()
    app.mainloop()