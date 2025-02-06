import customtkinter as ctk
import sqlite3
import citas_paciente
import citas_medico

class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.title("Inicio de Sesión")
        self.geometry("400x300")

        self.entry_usuario = None
        self.tipo_usuario = None

        # Etiqueta y entrada para usuario
        ctk.CTkLabel(self, text="Usuario:").pack(pady=5)
        self.entry_usuario = ctk.CTkEntry(self)
        self.entry_usuario.pack(pady=5)

        # Etiqueta y selección de tipo de usuario
        ctk.CTkLabel(self, text="Tipo de Usuario:").pack(pady=5)
        self.tipo_usuario = ctk.CTkComboBox(self, values=["Paciente", "Admin"])
        self.tipo_usuario.pack(pady=5)

        # Botón para iniciar sesión
        self.btn_login = ctk.CTkButton(self, text="Ingresar", command=self.verificar_usuario)
        self.btn_login.pack(pady=20)

        # Etiqueta para mostrar mensajes (Acceso concedido/denegado)
        self.lbl_mensaje = ctk.CTkLabel(self, text="")
        self.lbl_mensaje.pack(pady=10)

        # Guardar la ID del evento 'after' para cancelarlo cuando sea necesario
        self.after_event_id = None

    def verificar_usuario(self):
        usuario = self.entry_usuario.get().strip()
        tipo = self.tipo_usuario.get()

        if not usuario:
            self.lbl_mensaje.configure(text="Ingrese un usuario", text_color="orange")
            return

        resultado = None
        with sqlite3.connect("citas_medicas.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Usuarios WHERE nombre=? AND tipo=?", (usuario, tipo))
            resultado = cursor.fetchone()

        if resultado:
            self.lbl_mensaje.configure(text="Acceso concedido", text_color="green")
            # Usamos 'after' para asegurar el flujo controlado
            self.after_event_id = self.after(100, self.cerrar_y_abrir_citas, usuario, tipo)  # Agregar el evento a cancelar
        else:
            self.lbl_mensaje.configure(text="Acceso denegado", text_color="red")

    def cerrar_y_abrir_citas(self, usuario, tipo):
        # Cancelamos cualquier evento pendiente antes de destruir la ventana
        if self.after_event_id:
            self.after_cancel(self.after_event_id)

        # Cerramos la ventana de login
        self.quit()
        self.destroy()

        # Ahora abrimos la ventana de citas correspondiente
        if tipo == "Paciente":
            citas_app = citas_paciente.CitasApp(usuario)
            citas_app.mainloop()
        elif tipo == "Admin":
            citas_ad = citas_medico.AdminApp()
            citas_ad.mainloop()


