import customtkinter as ctk
import pandas as pd
from datetime import datetime
import tkinter as tk

class DashboardWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("FlowClock Dashboard")
        self.geometry("600x950")
        self.attributes("-topmost", True)
        self.configure(fg_color="#242424")
        
        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="#242424")
        self.main_scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(self.main_scroll, text="DAILY SUMMARY", 
                     font=("Helvetica", 22, "bold"), text_color="#3a7ebf").pack(pady=(30, 10))

        self.load_today_data()

    def load_today_data(self):
        try:
            df = pd.read_csv("focus_sessions.csv")
            today_str = datetime.now().strftime("%Y-%m-%d")
            today_data = df[df['Date'].str.contains(today_str)].copy()
            
            data_to_render = today_data if not today_data.empty else df
            self.render_dashboard(data_to_render)
        except Exception as e:
            ctk.CTkLabel(self.main_scroll, text=f"Error: {e}").pack(pady=20)

    def render_dashboard(self, data):
        # 1. KPI SECTION
        total_mins = data['Actual_Mins'].sum()
        avg_focus = data['Focus_Level'].mean()
        
        metrics_frame = ctk.CTkFrame(self.main_scroll, fg_color="#2b2b2b", corner_radius=10)
        metrics_frame.pack(pady=10, padx=30, fill="x")
        self.create_metric_row(metrics_frame, "Total Time", f"{total_mins:.1f}m")
        self.create_metric_row(metrics_frame, "Focus Score", f"{avg_focus:.1f}/5")

        # 2. NATIVE PIE/DONUT
        ctk.CTkLabel(self.main_scroll, text="Time Distribution", 
                     font=("Helvetica", 16, "bold"), text_color="#eeeeee").pack(pady=(20, 10))
        self.draw_native_donut(data)

        # 3. NATIVE BAR CHART (NEW)
        ctk.CTkLabel(self.main_scroll, text="Hourly Focus Quality", 
                     font=("Helvetica", 16, "bold"), text_color="#eeeeee").pack(pady=(30, 10))
        self.draw_native_bars(data)

        # 4. WINS SECTION
        ctk.CTkLabel(self.main_scroll, text="Session Notes", 
                     font=("Helvetica", 16, "bold"), text_color="#eeeeee").pack(pady=(30, 10))
        for note in data['Notes'].tolist():
            if note and note != "No notes provided.":
                ctk.CTkLabel(self.main_scroll, text=f"• {note}", font=("Helvetica", 13),
                             wraplength=450, justify="left", text_color="#bbbbbb").pack(anchor="w", padx=50, pady=2)

    def draw_native_donut(self, data):
        cat_data = data.groupby('Category')['Actual_Mins'].sum()
        total = cat_data.sum()
        colors = ['#3a7ebf', '#16a085', '#f1c40f', '#e67e22', '#9b59b6']
        
        chart_container = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        chart_container.pack(pady=10)

        canvas = tk.Canvas(chart_container, width=200, height=200, bg="#242424", highlightthickness=0)
        canvas.pack(side="left", padx=20)

        legend_frame = ctk.CTkFrame(chart_container, fg_color="transparent")
        legend_frame.pack(side="left", padx=10)

        start_angle = 90
        for i, (cat, val) in enumerate(cat_data.items()):
            extent = (val / total) * 360
            color = colors[i % len(colors)]
            canvas.create_arc((10, 10, 190, 190), start=start_angle, extent=extent, 
                             fill=color, outline="#242424", width=2)
            
            leg_row = ctk.CTkFrame(legend_frame, fg_color="transparent")
            leg_row.pack(anchor="w", pady=2)
            ctk.CTkFrame(leg_row, width=12, height=12, fg_color=color).pack(side="left", padx=(0, 5))
            ctk.CTkLabel(leg_row, text=f"{cat}", font=("Helvetica", 12), text_color="#eeeeee").pack(side="left")
            start_angle += extent

        canvas.create_oval((65, 65, 135, 135), fill="#242424", outline="#242424") # Thinner hole

    def draw_native_bars(self, data):
        # Data Prep
        data['Timestamp'] = pd.to_datetime(data['Date'])
        data['Hour'] = data['Timestamp'].dt.hour
        hourly_avg = data.groupby('Hour')['Focus_Level'].mean()

        # Layout Constants
        c_width = 450
        c_height = 200
        padding = 30
        
        canvas = tk.Canvas(self.main_scroll, width=c_width, height=c_height, bg="#242424", highlightthickness=0)
        canvas.pack(pady=10)

        # Draw Y-Axis Grid Lines (Focus 1 to 5)
        for i in range(1, 6):
            y_pos = c_height - (i * (c_height / 6))
            canvas.create_line(padding, y_pos, c_width-padding, y_pos, fill="#333333", dash=(4, 4))
            canvas.create_text(padding-15, y_pos, text=str(i), fill="#888888", font=("Helvetica", 8))

        # Draw Bars
        hours = hourly_avg.index.tolist()
        vals = hourly_avg.values.tolist()
        
        bar_gap = 10
        total_gaps = (len(hours) - 1) * bar_gap
        bar_width = (c_width - (padding * 2) - total_gaps) / len(hours)

        for i, (hour, val) in enumerate(zip(hours, vals)):
            x0 = padding + (i * (bar_width + bar_gap))
            y0 = c_height - (val * (c_height / 6))
            x1 = x0 + bar_width
            y1 = c_height - 5 # Small baseline offset

            # Draw the bar
            canvas.create_rectangle(x0, y0, x1, y1, fill="#3a7ebf", outline="", width=0)
            
            # Label the Hour below
            canvas.create_text((x0 + x1)/2, c_height + 15, text=f"{hour}h", fill="#eeeeee", font=("Helvetica", 10))
            
            # Label the Value on top
            canvas.create_text((x0 + x1)/2, y0 - 10, text=f"{val:.1f}", fill="white", font=("Helvetica", 9, "bold"))

    def create_metric_row(self, master, label, value):
        row = ctk.CTkFrame(master, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=8)
        ctk.CTkLabel(row, text=label.upper(), font=("Helvetica", 11, "bold"), text_color="#888888").pack(side="left")
        ctk.CTkLabel(row, text=str(value), font=("Helvetica", 16, "bold"), text_color="white").pack(side="right")

if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()
    dash = DashboardWindow(root)
    dash.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()