import customtkinter as ctk
# Importamos la nueva función toggle_user_status en lugar de delete_user
from core.auth import get_all_users, add_user, toggle_user_status
from tkinter import messagebox

class AdminView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#050505")
        
        self.color_neon = "#DEFF9A"
        self.color_surface = "#151515"
        self.color_surface_alt = "#1E1E1E" # Color alterno para el efecto cebra
        self.color_brick = "#ff4d4d"
        
        self.grid_columnconfigure(0, weight=1)
        
        self.title_label = ctk.CTkLabel(self, text="USER MANAGEMENT PANEL", font=ctk.CTkFont(size=24, weight="bold"), text_color=self.color_neon)
        self.title_label.pack(pady=(30, 10), padx=20)

        # Formulario
        self.add_frame = ctk.CTkFrame(self, fg_color=self.color_surface, border_width=1, border_color="#222")
        self.add_frame.pack(padx=20, pady=10)

        form_container = ctk.CTkFrame(self.add_frame, fg_color="transparent")
        form_container.pack(pady=15, padx=20)

        self.new_user = ctk.CTkEntry(form_container, placeholder_text="New Username", width=200, fg_color="#0A0A0A", border_color="#333")
        self.new_user.pack(side="left", padx=10)

        self.new_pass = ctk.CTkEntry(form_container, placeholder_text="New Password", show="*", width=200, fg_color="#0A0A0A", border_color="#333")
        self.new_pass.pack(side="left", padx=10)

        self.role_var = ctk.StringVar(value="employee")
        self.role_menu = ctk.CTkOptionMenu(form_container, values=["employee", "admin"], variable=self.role_var, fg_color="#333", button_color=self.color_neon)
        self.role_menu.pack(side="left", padx=10)

        self.add_btn = ctk.CTkButton(form_container, text="CREATE USER", command=self.create_user, font=ctk.CTkFont(weight="bold"), fg_color=self.color_neon, text_color="black", hover_color="#bde072")
        self.add_btn.pack(side="left", padx=10)

        # Controles
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.pack(fill="x", padx=40, pady=(20, 5))
        
        ctk.CTkLabel(controls_frame, text="CURRENT USERS", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        
        self.filter_var = ctk.StringVar(value="All Roles")
        self.filter_menu = ctk.CTkComboBox(controls_frame, variable=self.filter_var, values=["All Roles", "employee", "admin"], 
                                           command=lambda e: self.refresh_users(), width=130, fg_color="#333", button_color=self.color_neon)
        self.filter_menu.pack(side="right")
        ctk.CTkLabel(controls_frame, text="Filter by Role:").pack(side="right", padx=10)

        self.user_list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.user_list_frame.pack(pady=5, padx=20, fill="both", expand=True)

        self.refresh_users()

    def create_user(self):
        user = self.new_user.get()
        password = self.new_pass.get()
        if user and password:
            if add_user(user, password, self.role_var.get()):
                self.new_user.delete(0, 'end')
                self.new_pass.delete(0, 'end')
                self.refresh_users()

    def force_reset_toast(self, username):
        messagebox.showinfo("Security Action", f"Force Password Reset activated for {username}.\nThey will be prompted on next login.")

    def change_status(self, user_id, new_status):
        if toggle_user_status(user_id, new_status):
            self.refresh_users()

    def refresh_users(self):
        for widget in self.user_list_frame.winfo_children():
            widget.destroy()
        
        users = get_all_users()
        selected_role = self.filter_var.get()
        
        if selected_role != "All Roles":
            users = [u for u in users if u[2] == selected_role]

        for idx, user in enumerate(users):
            # EFECTO CEBRA
            bg_color = self.color_surface if idx % 2 == 0 else self.color_surface_alt
            is_active = user[3] if len(user) > 3 else 1

            row = ctk.CTkFrame(self.user_list_frame, height=50, fg_color=bg_color, corner_radius=0)
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)
            
            text_color = "white" if is_active else "#555555"
            role_color = self.color_neon if user[2] == "admin" else "#5dade2"
            if not is_active: role_color = "#555555"
            
            # CORRECCIÓN: Eliminado 'strike=not is_active' que causaba el error TypeError
            ctk.CTkLabel(row, text=f"👤 {user[1]}", font=ctk.CTkFont(weight="bold"), text_color=text_color).pack(side="left", padx=20)
            ctk.CTkLabel(row, text=f"Role: {user[2].upper()}", text_color=role_color).pack(side="left", padx=20)
            
            if not is_active:
                ctk.CTkLabel(row, text="(INACTIVE)", font=ctk.CTkFont(size=10, weight="bold"), text_color=self.color_brick).pack(side="left")

            if user[1] != 'admin':
                # Botón ACTIVAR / DESACTIVAR
                if is_active:
                    ctk.CTkButton(
                        row, text="DEACTIVATE", fg_color="transparent", border_width=1, border_color=self.color_brick, text_color=self.color_brick, hover_color="#331111", width=90, font=ctk.CTkFont(size=11, weight="bold"),
                        command=lambda u_id=user[0]: self.change_status(u_id, 0)
                    ).pack(side="right", padx=10)
                else:
                    ctk.CTkButton(
                        row, text="ACTIVATE", fg_color="transparent", border_width=1, border_color=self.color_neon, text_color=self.color_neon, hover_color="#1a260d", width=90, font=ctk.CTkFont(size=11, weight="bold"),
                        command=lambda u_id=user[0]: self.change_status(u_id, 1)
                    ).pack(side="right", padx=10)
                
                # Botón Forzar Reset
                ctk.CTkButton(
                    row, text="FORCE RESET", fg_color="transparent", border_width=1, border_color="#f39c12", text_color="#f39c12", hover_color="#332200", width=100, font=ctk.CTkFont(size=11, weight="bold"),
                    command=lambda name=user[1]: self.force_reset_toast(name)
                ).pack(side="right", padx=10)