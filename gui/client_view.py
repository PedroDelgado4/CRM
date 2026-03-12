import customtkinter as ctk
from core.clients import add_client, get_all_clients, search_clients, delete_client

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

        # Buscador
        self.search_entry = ctk.CTkEntry(self, placeholder_text="Search clients by name or company...")
        self.search_entry.pack(padx=20, pady=10, fill="x")
        self.search_entry.bind("<KeyRelease>", lambda event: self.refresh_list())

        # Lista de clientes
        self.list_frame = ctk.CTkScrollableFrame(self, label_text="Client List")
        self.list_frame.pack(pady=10, padx=20, fill="both", expand=True)

        #self.display_area = ctk.CTkTextbox(self, height=200)
        #self.display_area.pack(padx=20, pady=10, fill="both", expand=True)

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
        # limpiar lista actual
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        # obtener datos con o sin filtrar
        search_term = self.search_entry.get()
        if search_term:
            clients = search_clients(search_term)
        else:
            clients = get_all_clients()

        # mostrar cada cliente como una "fila"
        for c in clients:
            row = ctk.CTkFrame(self.list_frame)
            row.pack(fill="x", pady=2, padx=5)

            # etiquet con datos
            ctk.CTkLabel(row, text=f"{c[1]} ({c[2]})").pack(side="left", padx=10)
            
            # badge de estado
            color = "green" if c[3] == "client" else "orange"
            ctk.CTkLabel(row, text=c[3].upper(), text_color=color, font=ctk.CTkFont(size=10, weight="bold")).pack(side="left", padx=5)

            # boton eliminar
            ctk.CTkButton(row, text="Delete", fg_color="#A30000", width=60, height=20, command=lambda c_id=c[0]: self.remove_client(c_id)).pack(side="right", padx=10)
        
    def remove_client(self, client_id):
        if delete_client(client_id):
            self.refresh_list()
            





        


        