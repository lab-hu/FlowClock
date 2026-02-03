import customtkinter as ctk

class TaskDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FlowClock v4.0 Preview")
        self.geometry("500x400")
        
        # --- 1. DATA STATE ---
        self.task_count = 0

        # --- 2. THE UI (Shiny fluidPage) ---
        # Sidebar Frame
        self.sidebar = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        self.logo = ctk.CTkLabel(self.sidebar, text="DASHBOARD", font=("Helvetica", 16, "bold"))
        self.logo.pack(pady=20, padx=10)

        # Main Content Frame
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # Input Area
        self.entry = ctk.CTkEntry(self.main_view, placeholder_text="Enter a new task...", width=250)
        self.entry.pack(pady=(0, 10))

        # Buttons with different "Personalities"
        self.add_button = ctk.CTkButton(self.main_view, text="Add Task", command=self.add_task_logic)
        self.add_button.pack(pady=5)

        self.warn_button = ctk.CTkButton(self.main_view, text="Toggle Danger Mode", 
                                        fg_color="transparent", border_width=2, 
                                        text_color=("gray10", "#DCE4EE"),
                                        command=self.toggle_danger)
        self.warn_button.pack(pady=5)

        # Scrollable List (Like a reactive UI output)
        self.scrollable_frame = ctk.CTkScrollableFrame(self.main_view, label_text="Your Active Tasks")
        self.scrollable_frame.pack(fill="both", expand=True, pady=10)

    # --- 3. THE "SERVER" LOGIC ---
    def add_task_logic(self):
        task_text = self.entry.get()
        if task_text != "":
            self.task_count += 1
            # Create a new widget dynamically
            new_task = ctk.CTkCheckBox(self.scrollable_frame, text=f"{self.task_count}. {task_text}")
            new_task.pack(pady=5, anchor="w")
            # Clear input box (like resetInput)
            self.entry.delete(0, 'end')
        else:
            self.entry.configure(placeholder_text="CANNOT BE EMPTY!", placeholder_text_color="red")

    def toggle_danger(self):
        # Change UI state dynamically
        current_color = self.warn_button.cget("fg_color")
        if current_color == "transparent":
            self.warn_button.configure(fg_color="#ff4d4d", text="DANGER ACTIVE")
            self.main_view.configure(fg_color="#2b1b1b") # Dark red tint
        else:
            self.warn_button.configure(fg_color="transparent", text="Toggle Danger Mode")
            self.main_view.configure(fg_color="transparent")

if __name__ == "__main__":
    app = TaskDashboard()
    app.mainloop()