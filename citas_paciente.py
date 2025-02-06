from datetime import datetime

import customtkinter as ctk
import sqlite3
from tkcalendar import Calendar
from tkinter import messagebox, Listbox, Scrollbar
import time

class CitasApp(ctk.CTk):
    def __init__(self, usuario_logueado):
        super().__init__()
        self.usuario_logueado = usuario_logueado
        self.title("Calendario de Citas")
        self.geometry("600x600")

        # Crear calendario
        self.calendario = Calendar(self, selectmode='day', date_pattern='yyyy-mm-dd')
        self.calendario.pack(fill="both", expand=True, padx=20, pady=20)

        # Botón para cargar citas
        self.btn_cargar_citas = ctk.CTkButton(self, text="Cargar Citas", command=self.mostrar_citas)
        self.btn_cargar_citas.pack(pady=10)

        # Lista de citas (Usando Listbox para permitir selección)
        self.lista_citas_frame = ctk.CTkFrame(self)
        self.lista_citas_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.listbox = Listbox(self.lista_citas_frame, height=10, selectmode="single")
        self.listbox.pack(side="left", fill="both", expand=True)

        self.lista_scroll = Scrollbar(self.lista_citas_frame, command=self.listbox.yview)
        self.lista_scroll.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=self.lista_scroll.set)

        # Botón para abrir la ventana de agendar citas
        self.btn_abrir_agendar = ctk.CTkButton(self, text="Agendar Cita", command=self.abrir_ventana_agendar)
        self.btn_abrir_agendar.pack(pady=10)

        self.btn_eliminar = ctk.CTkButton(self, text="Eliminar Cita", command=self.eliminar_cita)
        self.btn_eliminar.pack(pady=5)

        self.pintar_dias_con_citas()

    def pintar_dias_con_citas(self):
        """Resalta los días con citas en el calendario."""
        try:
            with sqlite3.connect("citas_medicas.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT fecha FROM Citas WHERE estado='Confirmada'")
                fechas_con_citas = [fila[0] for fila in cursor.fetchall()]

            # Limpiar etiquetas previas
            self.calendario.calevent_remove('all')

            for fecha in fechas_con_citas:
                fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()  # Convertir string a datetime.date
                self.calendario.calevent_create(fecha_dt, 'Cita', 'citas')

            self.calendario.tag_config('citas', background='blue', foreground='white')

        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"Error al obtener citas: {e}")

    def abrir_ventana_agendar(self):
        ventana_agendar = AgendarCita(self.usuario_logueado, self)
        ventana_agendar.mainloop()

    def mostrar_citas(self):
        fecha_seleccionada = self.calendario.get_date()  # Obtener la fecha seleccionada del calendario
        self.listbox.delete(0, "end")  # Limpiar lista de citas
        self.pintar_dias_con_citas()

        usuario_logueado = self.usuario_logueado  # Asegúrate de tener el usuario logueado disponible

        try:
            with sqlite3.connect("citas_medicas.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT Citas.id, Medicos.nombre, Citas.hora 
                    FROM Citas
                    JOIN Usuarios ON Citas.usuario_id = Usuarios.id
                    JOIN Medicos ON Citas.medico_id = Medicos.id
                    WHERE Citas.fecha=? AND Citas.estado='Confirmada' AND Usuarios.nombre=?
                """, (fecha_seleccionada, usuario_logueado))
                citas = cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"Error al obtener citas: {e}")
            return

        if citas:
            for cita in citas:
                self.listbox.insert("end", f"{cita[0]} - Médico: {cita[1]}, Hora: {cita[2]}")
        else:
            self.listbox.insert("end", "No hay citas para esta fecha.")

    def eliminar_cita(self):
        try:
            seleccion = self.listbox.curselection()
            if not seleccion:
                messagebox.showwarning("Selección Vacía", "Por favor seleccione una cita para eliminar.")
                return

            cita_id = self.listbox.get(seleccion[0]).split(" - ")[0]
            with sqlite3.connect("citas_medicas.db") as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Citas WHERE id=?", (cita_id,))
                conn.commit()

            messagebox.showinfo("Éxito", "Cita eliminada correctamente.")
            self.mostrar_citas()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar la cita: {e}")

class AgendarCita(ctk.CTk):
    def __init__(self, usuario_logueado, parent):
        super().__init__()
        self.usuario_logueado = usuario_logueado
        self.parent = parent
        self.title("Agendar Cita")
        self.geometry("400x300")

        # Campo Paciente
        ctk.CTkLabel(self, text="Paciente:").pack()
        self.entry_paciente = ctk.CTkEntry(self)
        self.entry_paciente.insert(0, self.usuario_logueado)
        self.entry_paciente.configure(state="disabled")
        self.entry_paciente.pack(pady=5)

        # Campo Especialidad
        ctk.CTkLabel(self, text="Especialidad:").pack()
        especialidades = self.obtener_especialidades()
        self.combo_especialidad = ctk.CTkComboBox(self, values=especialidades)
        self.combo_especialidad.pack(pady=5)

        # Campo Médico
        ctk.CTkLabel(self, text="Médico:").pack()
        self.combo_medico = ctk.CTkComboBox(self, values=[])
        self.combo_medico.pack(pady=5)

        # Campo Hora
        ctk.CTkLabel(self, text="Hora (HH:MM):").pack()
        self.entry_hora = ctk.CTkComboBox(self, values=["12:00", "13:00", "14:00", "15:00", "16:00"])
        self.entry_hora.pack(pady=5)

        # Botón Agendar
        self.btn_agendar = ctk.CTkButton(self, text="Agendar", command=self.agendar_cita)
        self.btn_agendar.pack(pady=10)

        # Vincular cambio en especialidad con actualización de médicos
        self.combo_especialidad.bind("<<ComboboxSelected>>", self.actualizar_medicos)

        # Inicializar médicos según la especialidad seleccionada
        if especialidades:
            self.combo_especialidad.set(especialidades[0])
            self.actualizar_medicos()

    def obtener_especialidades(self):
        """Obtiene las especialidades únicas de la base de datos"""
        try:
            with sqlite3.connect("citas_medicas.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT especialidad FROM Medicos")
                especialidades = [row[0] for row in cursor.fetchall()]
                return especialidades if especialidades else ["Sin especialidades"]
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"Error al obtener especialidades: {e}")
            return ["Error"]

    def actualizar_medicos(self, event=None):
        """Actualiza la lista de médicos sin filtrar por especialidad"""
        medicos = self.obtener_medicos()
        self.combo_medico.configure(values=medicos if medicos else ["No hay médicos"])
        self.combo_medico.set(medicos[0] if medicos else "No hay médicos")

    def obtener_medicos(self):
        """Obtiene todos los médicos disponibles en la base de datos"""
        try:
            with sqlite3.connect("citas_medicas.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nombre FROM Medicos")
                medicos = [row[0] for row in cursor.fetchall()]
                return medicos
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"Error al obtener médicos: {e}")
            return ["Error"]

    def agendar_cita(self):
        """Registra la cita en la base de datos"""
        medico = self.combo_medico.get()
        hora = self.entry_hora.get()
        fecha = self.parent.calendario.get_date()

        if not medico or not hora or medico == "No hay médicos":
            messagebox.showwarning("Campos Vacíos", "Por favor complete todos los campos correctamente.")
            return

        try:
            with sqlite3.connect("citas_medicas.db") as conn:
                cursor = conn.cursor()

                # Obtener usuario_id
                cursor.execute("SELECT id FROM Usuarios WHERE nombre=?", (self.usuario_logueado,))
                usuario_id = cursor.fetchone()
                if not usuario_id:
                    messagebox.showerror("Error", "Usuario no encontrado en la base de datos.")
                    return
                usuario_id = usuario_id[0]

                # Insertar cita con subconsulta para obtener medico_id
                cursor.execute("""
                    INSERT INTO Citas (usuario_id, medico_id, fecha, hora, estado)
                    VALUES (?, (SELECT id FROM Medicos WHERE nombre=?), ?, ?, 'Confirmada')
                """, (usuario_id, medico, fecha, hora))
                conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"Error al agendar cita: {e}")
            return

        messagebox.showinfo("Éxito", "Cita agendada correctamente.")
        self.parent.mostrar_citas()
        self.destroy()

