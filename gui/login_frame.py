import customtkinter as ctk
from core.auth import verify_login

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, login_callback):
        super().__init__(master)

        self.login_callback = login_callback
        # Layout
        self.grid_columnconfigure(0, weight=1)
        
        # Titulo
        self.title_label = ctk.CTkLabel(
            self, text="CRM FDT - Access",
            font= ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(40, 20))

        # Campo de usuario
        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username", width=250)
        self.username_entry.grid(row=1, column=0, padx=20, pady=10)

        self.username_entry.bind("<Return>", lambda event: self.attempt_login)


        # Campo de contraseña
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=250)
        self.password_entry.grid(row=2, column=0, padx=20, pady=10)

        self.password_entry.bind("<Return>", self.attempt_login)


        # Botón entrar
        self.login_button = ctk.CTkButton(self, text="Login", command=self.attempt_login)
        self.login_button.grid(row=3, column=0, padx=20, pady=20)

        # Etiqueta de error
        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.grid(row=4, column=0, padx=20, pady=5)

    def attempt_login(self, event=None):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Comprobacion de credenciales
        user_data = verify_login(username, password)

        if user_data:
            print(f"UI: Access granted for {username}")
            self.error_label.configure(text="")
            self.login_callback(user_data)
        else:
            print("Invalid credentials!")
            self.error_label.configure(text="Invalid username or password. Please check your credentials!")













       