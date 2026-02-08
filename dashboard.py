import customtkinter as ctk
import pandas as pd
import tkinter as tk
from datetime import datetime, timedelta

class DashboardWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("FlowClock")
        self.geometry("550x850") 
        self.attributes("-topmost", True)
        self.configure(fg_color="#121212") 
        
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=25, pady=20)

        # Updated title: Smaller font and new text
        header_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header_frame, text="DAILY FLOW DASHBOARD", 
                     font=("Helvetica", 20, "bold"), text_color="#BBD1E5").pack(expand=True, fill="x")

        self.load_today_data()

    def load_today_data(self):
        try:
            df = pd.read_csv("focus_sessions.csv")
            today_str = datetime.now().strftime("%Y-%m-%d")
            today_data = df[df['Date'].str.contains(today_str)].copy()
            data_to_render = today_data if not today_data.empty else df
            self.render_dashboard(data_to_render)
        except Exception as e:
            ctk.CTkLabel(self.container, text=f"No data yet. Keep flowing!", text_color="#888888").pack(pady=40)

    def render_dashboard(self, data):
        # 1. KPI SECTION
        kpi_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 20))
        
        # Time Formatting
        total_mins_raw = data['Actual_Mins'].sum()
        h = int(total_mins_raw // 60)
        m = int(total_mins_raw % 60)
        time_display = f"{h}h {m}min" if h > 0 else f"{m}min"
        
        # Focus Score Formatting
        avg_focus = data['Focus_Level'].mean()
        focus_display = f"{avg_focus:.1f} / 5"
        
        # Updated Stats: Both use #FFFFFF (Pure White)
        stats_data = [
            ("TOTAL TIME", time_display, "#FFFFFF"), 
            ("AVG FOCUS", focus_display, "#FFFFFF")
        ]

        for label, val, color in stats_data:
            card = ctk.CTkFrame(kpi_frame, fg_color="#1E1E1E", corner_radius=12, width=240, height=80)
            card.pack(side="left", expand=True, padx=5)
            card.pack_propagate(False)
            ctk.CTkLabel(card, text=label, font=("Helvetica", 10, "bold"), text_color="#AAAAAA").pack(pady=(15, 2))
            ctk.CTkLabel(card, text=val, font=("Helvetica", 18, "bold"), text_color=color).pack()

        # 2. CATEGORY CHART
        ctk.CTkLabel(self.container, text="TIME DISTRIBUTION", font=("Helvetica", 11, "bold"), 
                     text_color="#AAAAAA").pack(anchor="w", padx=5, pady=(10, 5))
        self.draw_native_donut(data)

        # 3. HOURLY CHART
        ctk.CTkLabel(self.container, text="FOCUS BY HOUR", font=("Helvetica", 11, "bold"), 
                     text_color="#AAAAAA").pack(anchor="w", padx=5, pady=(20, 5))
        self.draw_native_bars(data)

    def draw_native_donut(self, data):
        cat_data = data.groupby('Category')['Actual_Mins'].sum()
        total = cat_data.sum()
        colors = ['#3a7ebf', '#16a085', '#f1c40f', '#e67e22', '#9b59b6']
        
        chart_container = ctk.CTkFrame(self.container, fg_color="#1E1E1E", corner_radius=12)
        chart_container.pack(fill="x", pady=5)

        canvas = tk.Canvas(chart_container, width=150, height=150, bg="#1E1E1E", highlightthickness=0)
        canvas.pack(side="left", padx=20, pady=15)

        legend_frame = ctk.CTkFrame(chart_container, fg_color="transparent")
        legend_frame.pack(side="left", fill="y", pady=15)

        start_angle = 90
        for i, (cat, val) in enumerate(cat_data.items()):
            extent = (val / total) * 360
            color = colors[i % len(colors)]
            canvas.create_arc((5, 5, 145, 145), start=start_angle, extent=extent, fill=color, outline="#1E1E1E", width=2)
            
            row = ctk.CTkFrame(legend_frame, fg_color="transparent")
            row.pack(anchor="w", pady=1)
            ctk.CTkFrame(row, width=8, height=8, fg_color=color, corner_radius=4).pack(side="left", padx=(0, 8))
            ctk.CTkLabel(row, text=cat, font=("Helvetica", 11), text_color="#DDDDDD").pack(side="left")
            start_angle += extent
        canvas.create_oval((50, 50, 100, 100), fill="#1E1E1E", outline="#1E1E1E")

    def draw_native_bars(self, data):
        df = data.copy()
        df['End_TS'] = pd.to_datetime(df['Date'])
        df['Start_TS'] = df.apply(lambda row: row['End_TS'] - timedelta(minutes=row['Actual_Mins']), axis=1)
        min_hour, max_hour = int(df['Start_TS'].min().hour), int(df['End_TS'].max().hour)
        full_range = list(range(min_hour, max_hour + 1))

        hourly_val = {}
        for hour in full_range:
            h_start = datetime.combine(df['Start_TS'].min().date(), datetime.min.time()).replace(hour=hour)
            h_end = h_start + timedelta(hours=1)
            points, mins = 0, 0
            for _, s in df.iterrows():
                o_start, o_end = max(s['Start_TS'], h_start), min(s['End_TS'], h_end)
                if o_start < o_end:
                    d = (o_end - o_start).total_seconds() / 60
                    points += (s['Focus_Level'] * d)
                    mins += d
            if mins > 0: hourly_val[hour] = points / mins

        chart_bg = ctk.CTkFrame(self.container, fg_color="#1E1E1E", corner_radius=12)
        chart_bg.pack(fill="x", pady=5)
        
        c_w, c_h = 480, 200
        px, py = 40, 30
        canvas = tk.Canvas(chart_bg, width=c_w, height=c_h, bg="#1E1E1E", highlightthickness=0)
        canvas.pack(pady=(15, 5))

        for i in range(1, 6):
            y = (c_h - py) - (i * ((c_h - 2*py) / 5))
            canvas.create_line(px, y, c_w - px, y, fill="#2A2A2A", dash=(2, 2))
            canvas.create_text(px - 15, y, text=str(i), fill="#666666", font=("Helvetica", 9))

        num = len(full_range)
        gap = 12
        bw = ((c_w - 2*px) - (num * gap)) / num
        for i, h in enumerate(full_range):
            x0 = px + (i * (bw + gap))
            x1 = x0 + bw
            y_base = c_h - py
            canvas.create_text((x0+x1)/2, y_base + 15, text=f"{h}h", fill="#666666", font=("Helvetica", 8))
            if h in hourly_val:
                val = hourly_val[h]
                hp = (val / 5) * (c_h - 2 * py)
                canvas.create_rectangle(x0, y_base - hp, x1, y_base, fill="#3a7ebf", outline="")
                canvas.create_text((x0+x1)/2, y_base - hp - 10, text=f"{val:.1f}", fill="#FFFFFF", font=("Helvetica", 9, "bold"))

        legend = ctk.CTkFrame(chart_bg, fg_color="transparent")
        legend.pack(pady=(0, 10))
        ctk.CTkFrame(legend, width=10, height=10, fg_color="#3a7ebf", corner_radius=2).pack(side="left", padx=5)
        ctk.CTkLabel(legend, text="Focus Quality (1-5)", font=("Helvetica", 10), text_color="#888888").pack(side="left")

if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()
    DashboardWindow(root).protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()