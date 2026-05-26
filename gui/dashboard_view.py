import customtkinter as ctk
from core.analytics import generate_html_report, get_cross_selling_suggestions 
from core.finances import get_finance_summary
from core.opportunities import get_connection 
from core.sales_report import generate_sales_csv
from tkinter import messagebox
import os


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, user_data):
        super().__init__(master, fg_color="transparent")
        self.user_data = user_data
        
        self.color_neon = "#DEFF9A"
        self.color_green = "#2E8D1B"
        self.color_header = "#3F3F3F"
        self.color_silver = "#D9D9D9"

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- CABECERA DE BIENVENIDA ---
        self.welcome_label = ctk.CTkLabel(
            self, 
            text=f"Welcome back, {self.user_data[1]}!", 
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=self.color_neon
        )
        self.welcome_label.grid(row=0, column=0, pady=(30, 20), padx=20, sticky="w")

        # --- CONTENEDOR PRINCIPAL (SCROLL) ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=20)
        self.scroll_frame.grid_columnconfigure((0, 1), weight=1)

        # --- SECCIÓN 1: MÉTRICAS DE CRECIMIENTO ---
        self.stats_label = ctk.CTkLabel(self.scroll_frame, text="Growth & Performance", font=ctk.CTkFont(size=18, weight="bold"), text_color="white")
        self.stats_label.grid(row=0, column=0, columnspan=2, pady=(10, 15), sticky="w")
        
        self.render_growth_stats()

        # --- SECCIÓN 2: HUB DE ACCIONES RÁPIDAS Y REPORTES ---
        actions_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        actions_frame.grid(row=2, column=0, columnspan=2, pady=(20, 30), sticky="w")

        # Botón 1: Finanzas
        self.finance_btn = ctk.CTkButton(
            actions_frame, 
            text="💰 VIEW FINANCES", 
            fg_color="#151515",
            hover_color="#2A2A2A",
            border_width=1,
            border_color="#333",
            text_color="white",
            height=40,
            font=ctk.CTkFont(weight="bold"),
            command=lambda: self.master.master.change_view("Finances")
        )
        self.finance_btn.pack(side="left", padx=(0, 15))

        # Botón 2: Generar Reporte Completo (HTML con Gráfico)
        self.html_report_btn = ctk.CTkButton(
            actions_frame, 
            text="GENERATE DETAILED SALES REPORT", 
            fg_color=self.color_neon, 
            text_color="black", 
            hover_color="#bde072",
            height=40,
            font=ctk.CTkFont(weight="bold"),
            command=generate_html_report 
        )
        self.html_report_btn.pack(side="left", padx=(0, 15))

        # Botón 3: Exportar solo datos (CSV)
        self.csv_export_btn = ctk.CTkButton(
            actions_frame, 
            text="EXPORT SALES CSV", 
            fg_color="transparent", 
            border_width=1,
            border_color=self.color_neon,
            text_color=self.color_neon, 
            hover_color="#1a260d",
            height=40,
            font=ctk.CTkFont(weight="bold"),
            command=self.export_sales_csv
        )
        self.csv_export_btn.pack(side="left")

        # --- SECCIÓN 3: POSIBILIDADES DE CRECIMIENTO (IA) ---
        self.suggestions_label = ctk.CTkLabel(self.scroll_frame, text="💡 AI Insights: Growth Opportunities", font=ctk.CTkFont(size=18, weight="bold"), text_color="#f39c12")
        self.suggestions_label.grid(row=3, column=0, columnspan=2, pady=(20, 15), sticky="w")

        self.render_suggestions()

    def render_suggestions(self):

        suggestions = get_cross_selling_suggestions() 
        
        container = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        container.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 20))
        
        if not suggestions:
            ctk.CTkLabel(container, text="Excellent work! All your clients with contacts have active opportunities.", text_color=self.color_silver, font=ctk.CTkFont(slant="italic")).pack(anchor="w", pady=10)
            return

        for s in suggestions:
            card = ctk.CTkFrame(container, fg_color="#151515", border_width=1, border_color="#333", corner_radius=8)
            card.pack(fill="x", pady=5)
            
            text_info = f"Target Account: {s[1]} (Has {s[2]} contact/s, but 0 active opportunities)"
            ctk.CTkLabel(card, text=text_info, text_color="white", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=15, pady=15)
            
            action_btn = ctk.CTkButton(card, text="Create Opportunity", width=120, height=30, fg_color=self.color_neon, text_color="black", hover_color="#bde072", font=ctk.CTkFont(weight="bold"),
                                       command=lambda: self.master.master.change_view("Opportunities"))
            action_btn.pack(side="right", padx=15, pady=15)

    def render_growth_stats(self):
        growth_data = self.get_growth_comparison()
        
        self.create_stat_card(self.scroll_frame, "Sales This Year", f"{growth_data['current']:,.2f} €", 1, 0)
        
        growth_pct = growth_data['percentage']
        color = self.color_neon if growth_pct >= 0 else "#ff4d4d" # Adaptado a colores Neon/Void
        prefix = "+" if growth_pct >= 0 else ""
        self.create_stat_card(self.scroll_frame, "YoY Growth", f"{prefix}{growth_pct:.1f}%", 1, 1, color)

    def create_stat_card(self, master, title, value, row, col, val_color=None):
        card = ctk.CTkFrame(master, fg_color="#151515", border_width=1, border_color="#333", corner_radius=12)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=13), text_color=self.color_silver).pack(pady=(15, 0))
        ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=24, weight="bold"), text_color=val_color or "white").pack(pady=(5, 15))

    def get_growth_comparison(self):
        conn = get_connection()
        stats = {"current": 0.0, "previous": 0.0, "percentage": 0.0}
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(estimated_value) FROM opportunities WHERE status='closed_won' AND strftime('%Y', expected_close_date) = strftime('%Y', 'now')")
            stats["current"] = cursor.fetchone()[0] or 0.0
            
            cursor.execute("SELECT SUM(estimated_value) FROM opportunities WHERE status='closed_won' AND strftime('%Y', expected_close_date) = strftime('%Y', 'now', '-1 year')")
            stats["previous"] = cursor.fetchone()[0] or 0.0
            
            if stats["previous"] > 0:
                stats["percentage"] = ((stats["current"] - stats["previous"]) / stats["previous"]) * 100
            elif stats["current"] > 0:
                stats["percentage"] = 100.0
                
            conn.close()
        return stats
    
    def export_sales_csv(self):
        """Ejecuta la extracción de datos y genera el archivo CSV en la raíz del proyecto."""
        filepath = "sales_data.csv"
        
        if generate_sales_csv(filepath):
            ruta_completa = os.path.abspath(filepath)
            messagebox.showinfo(
                "Export Success", 
                f"Sales data successfully exported to CSV!\n\nLocation:\n{ruta_completa}"
            )
        else:
            messagebox.showerror(
                "Export Error", 
                "Could not export sales data.\nEnsure you have opportunities marked as 'Closed Won' with products linked."
            )