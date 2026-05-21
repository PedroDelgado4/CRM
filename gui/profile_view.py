import customtkinter as ctk
from core.auth import update_password

class ProfileView(ctk.CTkFrame):
    def __init__(self, master, user_data):
        super().__init__(master, fg_color="#050505")
        self.user_data = user_data  # [id, username, role]

        self.color_neon = "#DEFF9A"
        self.color_surface = "#151515"

        self.grid_columnconfigure(0, weight=1)

        # Titulo
        ctk.CTkLabel(self, text="MY PROFILE", font=ctk.CTkFont(size=24, weight="bold"), text_color=self.color_neon).pack(pady=(40, 20))

        # Panel info user
        info_frame = ctk.CTkFrame(self, fg_color=self.color_surface, border_width=1, border_color="#222")
        info_frame.pack(padx=20, pady=10)

        ctk.CTkLabel(info_frame, text=f"Username: {self.user_data[1]}", font=ctk.CTkFont(size=14)).pack(pady=(20, 5), padx=40)
        role_color = self.color_neon if self.user_data[2] == "admin" else "#5dade2"
        ctk.CTkLabel(info_frame, text=f"Role: {self.user_data[2].upper()}", text_color=role_color, font=ctk.CTkFont(weight="bold")).pack(pady=(5, 20), padx=40)

        # NUEVO: Selector de Tema
        theme_frame = ctk.CTkFrame(self, fg_color="transparent")
        theme_frame.pack(pady=10)
        ctk.CTkLabel(theme_frame, text="Appearance:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        
        self.theme_var = ctk.StringVar(value=ctk.get_appearance_mode())
        self.theme_menu = ctk.CTkOptionMenu(theme_frame, variable=self.theme_var, values=["Dark", "Light", "System"],
                                            command=self.change_theme, fg_color="#333", button_color=self.color_neon)
        self.theme_menu.pack(side="left", padx=10)

        # Seccion cambio de pass
        change_pw_frame = ctk.CTkFrame(self, fg_color=self.color_surface, border_width=1, border_color="#222")
        change_pw_frame.pack(padx=20, pady=20)

        ctk.CTkLabel(change_pw_frame, text="Security Settings", font=ctk.CTkFont(weight="bold", size=16)).pack(pady=(20, 10), padx=40)

        self.new_pass_entry = ctk.CTkEntry(change_pw_frame, placeholder_text="New Password", show="*", width=250, height=35, fg_color="#0A0A0A", border_color="#333")
        self.new_pass_entry.pack(pady=10, padx=40)

        self.confirm_btn = ctk.CTkButton(change_pw_frame, text="UPDATE PASSWORD", command=self.save_new_password, 
                                         fg_color=self.color_neon, text_color="black", hover_color="#bde072", font=ctk.CTkFont(weight="bold"))
        self.confirm_btn.pack(pady=10, padx=40)

        self.msg_label = ctk.CTkLabel(change_pw_frame, text="")
        self.msg_label.pack(pady=(5, 20))

    def change_theme(self, new_theme):
        ctk.set_appearance_mode(new_theme)

    def save_new_password(self):
        new_pw = self.new_pass_entry.get()
        if len(new_pw) >= 4: 
            if update_password(self.user_data[0], new_pw):
                self.msg_label.configure(text="Password updated successfully!", text_color=self.color_neon)
                self.new_pass_entry.delete(0, 'end')
            else:
                self.msg_label.configure(text="Error updating password", text_color="#ff4d4d")
        else:
            self.msg_label.configure(text="Password too short (min 4 chars)", text_color="#f39c12")