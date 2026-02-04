import customtkinter as ctk
import pandas as pd
import tkinter as tk
from datetime import datetime, timedelta

class HybridTimelineChart(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FlowClock: Hybrid Density Dashboard")
        self.geometry("900x600")
        self.configure(fg_color="#242424")

        self.header = ctk.CTkLabel(self, text="HOURLY FOCUS QUALITY", 
                                   font=("Helvetica", 20, "bold"), text_color="#eeeeee")
        self.header.pack(pady=(30, 10))

        try:
            # Note: Ensure you run your simulate_data.py first to create this file!
            df = pd.read_csv("test_sessions.csv")
            self.render_chart(df)
        except Exception as e:
            # This captures the error you saw in your screenshot
            ctk.CTkLabel(self, text=f"Error: {e}", text_color="red").pack(pady=20)

    def render_chart(self, df):
        # --- 1. DATA PRE-PROCESSING ---
        df['End_TS'] = pd.to_datetime(df['Date'])
        df['Start_TS'] = df.apply(lambda row: row['End_TS'] - timedelta(minutes=row['Actual_Mins']), axis=1)
        
        # Determine day start/end based on your data
        min_hour = int(df['Start_TS'].min().hour)
        max_hour = int(df['End_TS'].max().hour)
        full_range = list(range(min_hour, max_hour + 1))

        # --- 2. HYBRID LOGIC CALCULATION ---
        hourly_display_val = {}
        base_date = df['Start_TS'].min().date()
        
        for hour in full_range:
            # Define hour window using datetime.combine
            h_start = datetime.combine(base_date, datetime.min.time()).replace(hour=hour)
            h_end = h_start + timedelta(hours=1)
            
            total_weighted_focus = 0
            total_active_mins = 0
            
            for _, session in df.iterrows():
                overlap_start = max(session['Start_TS'], h_start)
                overlap_end = min(session['End_TS'], h_end)
                
                if overlap_start < overlap_end:
                    duration_in_hour = (overlap_end - overlap_start).total_seconds() / 60
                    total_weighted_focus += (session['Focus_Level'] * duration_in_hour)
                    total_active_mins += duration_in_hour
            
            # Hybrid Rule: Quality average over active time only
            if total_active_mins > 0:
                hourly_display_val[hour] = total_weighted_focus / total_active_mins

        # --- 3. RENDERING ---
        c_width, c_height = 800, 350
        padding_x, padding_y = 60, 60
        canvas = tk.Canvas(self, width=c_width, height=c_height, bg="#242424", highlightthickness=0)
        canvas.pack(pady=20)

        # Draw Grid Lines
        for i in range(1, 6):
            y_pos = (c_height - padding_y) - (i * ((c_height - 2*padding_y) / 5))
            canvas.create_line(padding_x, y_pos, c_width - padding_x, y_pos, fill="#333333", dash=(2, 2))
            canvas.create_text(padding_x - 25, y_pos, text=str(i), fill="#888888")

        # Draw X-axis
        canvas.create_line(padding_x, c_height-padding_y, c_width-padding_x, c_height-padding_y, fill="#444444")

        # --- 4. BARS ---
        num_slots = len(full_range)
        bar_width = ((c_width - 2*padding_x) - (num_slots * 10)) / num_slots

        for i, hour in enumerate(full_range):
            x0 = padding_x + (i * (bar_width + 10))
            x1 = x0 + bar_width
            y_base = c_height - padding_y
            
            canvas.create_text((x0+x1)/2, y_base + 25, text=f"{hour}:00", fill="#888888")

            if hour in hourly_display_val:
                val = hourly_display_val[hour]
                h_pix = (val / 5) * (c_height - 2 * padding_y)
                canvas.create_rectangle(x0, y_base - h_pix, x1, y_base, fill="#3a7ebf", outline="")
                canvas.create_text((x0+x1)/2, y_base - h_pix - 15, text=f"{val:.1f}", fill="white", font=("Arial", 9, "bold"))

if __name__ == "__main__":
    app = HybridTimelineChart()
    app.mainloop()