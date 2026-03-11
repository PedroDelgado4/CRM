import customtkinter as ctk
from core.clients import add_client, get_all_clients

class ClientView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)

        # Titulo
        self.label = ctk.CTkLabel(self, text="Client Management", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.pack(pady=20)

        # Formulario
        self.from_frame = ctk.CTkFrame(self)
        self.from_frame.pack(padx=20, pady=10, fill="x")

        self.name_entry = ctk.CTkEntry(self.from_frame, placeholder_text="Full name")
        self.name_entry.grid(row=0, column=0, padx=10, pady=10)

        self.company_entry = ctk.CTkEntry(self.from_frame, placeholder_text="Company")
        self.company_entry.grid(row=0, column=1, padx=10, pady=10)

        self.email_entry = ctk.CTkEntry(self.from_frame, placeholder_text="Email")
        self.email_entry.grid(row=1, column=0, padx=10, pady=10)

        self.phone_entry = ctk.CTkEntry(self.from_frame, placeholder_text="Phone")
        self.phone_entry.grid(row=1, column=1, padx=10, pady=10)

        self.status_var = ctk.StringVar(value="lead")
        self.status_menu = ctk.CTkOptionMenu(self.from_frame, values=["lead", "client"], variable=self.status_var)
        self.status_menu.grid(row=2, column=0, padx=10, pady=10)

        self.save_btn = ctk.CTkButton(self.from_frame, text="Add Client", command=self.save_client)
        self.save_btn.grid(row=2, column=1, padx=10, pady=10)

        # Lista de clientes
        self.list_label = ctk.CTkLabel(self, text="Recent Clients:", font=ctk.CTkFont(weight="bold"))
        self.list_label.pack(pady=(20, 0))

        self.display_area = ctk.CTkTextbox(self, height=200)
        self.display_area.pack(padx=20, pady=10, fill="both", expand=True)

        self.refresh_list()
    
    def save_client(self):
        name = self.name_entry.get()
        company = self.company_entry.get()
        email = self.email_entry.get()
        phone = self.phone_entry.get()
        status = self.status_var.get()

        if name:
            if add_client(name, company, email, phone, status):
                # Borrar datos en los campos del form
                self.name_entry.delete(0, 'end')
                self.company_entry.delete(0, 'end')
                self.email_entry.delete(0, 'end')
                self.phone_entry.delete(0, 'end')
                # Actualizar list
                self.refresh_list()
    
    def refresh_list(self):
        self.display_area.delete(0.0, 'end')
        clients = get_all_clients()
        for c in clients:
            self.display_area.insert('end', f"ID: {c[0]} | Name: {c[1]} | Co: {c[2]} | Status: {c[3]}\n")





        


        