import customtkinter as ctk
from core.auth import get_all_users, add_user, delete_user

class AdminView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="gray20")
        print("Admin view init")
        self.grid_columnconfigure(0, weight=1)
        
        self.title_label = ctk.CTkLabel(self, text="User Management Panel", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=20, padx=20)


        #Formulario para añadir usuario
        self.add_frame = ctk.CTkFrame(self)
        self.add_frame.pack(padx=20, pady=10, fill="x")

        self.new_user = ctk.CTkEntry(self.add_frame, placeholder_text="New Username")
        self.new_user.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        self.new_pass = ctk.CTkEntry(self.add_frame, placeholder_text="New Password", show="*")
        self.new_pass.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        self.role_var = ctk.StringVar(value="employee")
        self.role_menu = ctk.CTkOptionMenu(self.add_frame, values=["employee", "admin"], variable=self.role_var)
        self.role_menu.pack(side="left", padx=10, pady=10)

        self.add_btn = ctk.CTkButton(self.add_frame, text="Create User", command=self.create_user)
        self.add_btn.pack(side="left", padx=10, pady=10)

        # user table
        self.user_list_frame = ctk.CTkScrollableFrame(self, label_text="Current Users")
        self.user_list_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.refresh_users()

    def create_user(self):
        user = self.new_user.get()
        password = self.new_pass.get()
        if user and password:
            if add_user(user, password, self.role_var.get()):
                self.new_user.delete(0, 'end')
                self.new_pass.delete(0, 'end')
                self.refresh_users()

    def refresh_users(self):
        for widget in self.user_list_frame.winfo_children():
            widget.destroy()
        
        users = get_all_users()
        for user in users:
            row = ctk.CTkFrame(self.user_list_frame)
            row.pack(fill="x", pady=5, padx=5)
            
            ctk.CTkLabel(row, text=f"👤 {user[1]}").pack(side="left", padx=10)
            ctk.CTkLabel(row, text=f"Role: {user[2]}", text_color="gray").pack(side="left", padx=10)
            
            if user[1] != 'admin':
                ctk.CTkButton(
                    row, text="Delete", fg_color="#A30000", width=60,
                    command=lambda u_id=user[0]: self.remove_user(u_id)
                ).pack(side="right", padx=10)

    def remove_user(self, user_id):
        if delete_user(user_id):
            self.refresh_users()