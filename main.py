from core.database import initialize_db
from core.auth import verify_login
from gui.login_frame import LoginFrame
from gui.main_window import MainWindow
import customtkinter as ctk


class CRMApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        # Config de la ventana princpal
        self.title("CRM FDT - Management System")
        self.geometry("1000x700")

        initialize_db()

        # Pantalla de login al iniciar
        self.show_login()

    def show_login(self):
        self.login_screen = LoginFrame(self, self.on_login_success)
        self.login_screen.pack(expand=True) # Centrar en la ventana

    def on_login_success(self, user_data):
        self.login_screen.destroy() # Borra la pantnalla de login

        # crear ventana principal pasando los datos de user
        self.main_ui = MainWindow(self, user_data)
        self.main_ui.pack(expand=True, fill="both")



if __name__ == "__main__":
    app = CRMApp()
    app.mainloop()