import customtkinter as ctk
from core.auth import update_password

class ProfileView(ctk.CTkFrame):
    def __init__(self, master, user_data):
        super().__init__(master, fg_color="transparent")
        self.user_data = user_data  # [id, username, role]

        self.grid_columnconfigure(0, weight=1)

        # Titulo
        self.title_label = ctk.CTkLabel(self, text="My Profile", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        # panel info user
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(padx=20, pady=10, fill="x")

        ctk.CTkLabel(info_frame, text=f"Username: {self.user_data[1]}").pack(pady=5)
        ctk.CTkLabel(info_frame, text=f"Role: {self.user_data[2]}", text_color="gray").pack(pady=5)


        # seccion cambio de pass
        change_pw_frame = ctk.CTkFrame(self)
        change_pw_frame.pack(padx=20, pady=20, fill="x")

        ctk.CTkLabel(change_pw_frame, text="Change Password", font=ctk.CTkFont(weight="bold")).pack(pady=10)

        self.new_pass_entry = ctk.CTkEntry(change_pw_frame, placeholder_text="New Password", show="*")
        self.new_pass_entry.pack(pady=10)

        self.confirm_btn = ctk.CTkButton(change_pw_frame, text="Update password", command=self.save_new_password)
        self.confirm_btn.pack(pady=10)


        self.msg_label = ctk.CTkLabel(change_pw_frame, text="")
        self.msg_label.pack(pady=5)

    def save_new_password(self):
        new_pw = self.new_pass_entry.get()
        if len(new_pw) >= 4: # validacion de seguridad de minimo 4 caracteres
            if update_password(self.user_data[0], new_pw):
                self.msg_label.configure(text="Password updated successfully!", text_color="green")
                self.new_pass_entry.delete(0, 'end')
            else:
                self.msg_label.configure(text="Error updating password", text_color="red")
        else:
            self.msg_label.configure(text="Password too short (min 4 chars)", text_color="orange")