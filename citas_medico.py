from datetime import datetime

import customtkinter as ctk
import sqlite3
from tkcalendar import Calendar
from tkinter import Listbox, messagebox
from tkinter import Toplevel


class AdminApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Administración de Citas")
        self.geometry("700x700")

        # Crear calendario
        self.calendario = Calendar(self, selectmode='day', date_pattern='yyyy-mm-dd')
        self.calendario.pack(fill="both", expand=True, padx=20, pady=20)

        # Botón para cargar citas por fecha
        self.btn_cargar_por_fecha = ctk.CTkButton(self, text="Cargar Citas por Fecha",
                                                  command=self.mostrar_citas_por_fecha)
        self.btn_cargar_por_fecha.pack(pady=10)

        # Lista de citas con Listbox para seleccionar
        self.lista_citas = Listbox(self, selectmode="single", height=10)
        self.lista_citas.pack(fill="both", expand=True, padx=20, pady=10)

        # Entrada y botón para cargar citas por médico
        ctk.CTkLabel(self, text="Médico:").pack()
        self.combo_medico = ctk.CTkComboBox(self, values=self.obtener_medicos())
        self.combo_medico.pack(pady=5)

        self.btn_cargar_por_medico = ctk.CTkButton(self, text="Cargar Citas por Médico",
                                                   command=self.mostrar_citas_por_medico)
        self.btn_cargar_por_medico.pack(pady=10)

        # Botón para abrir la ventana de agendar citas
        self.btn_abrir_agendar = ctk.CTkButton(self, text="Agendar Cita para Paciente",
                                               command=self.abrir_ventana_agendar)
        self.btn_abrir_agendar.pack(pady=10)

        # Contenedor para los botones de la parte inferior
        self.frame_botones = ctk.CTkFrame(self)
        self.frame_botones.pack(pady=10)

        # Botones para editar/eliminar citas
        self.btn_editar = ctk.CTkButton(self.frame_botones, text="Editar Cita", command=self.editar_cita)
        self.btn_editar.pack(side="left", padx=5)

        self.btn_eliminar = ctk.CTkButton(self.frame_botones, text="Eliminar Cita", command=self.eliminar_cita)
        self.btn_eliminar.pack(side="left", padx=5)

        # Pintar los días con citas confirmadas
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

    def mostrar_citas_por_fecha(self):
        fecha_seleccionada = self.calendario.get_date()
        self.mostrar_citas("SELECT Citas.id, Usuarios.nombre, Medicos.nombre, Citas.hora FROM Citas \
                           JOIN Usuarios ON Citas.usuario_id = Usuarios.id \
                           JOIN Medicos ON Citas.medico_id = Medicos.id \
                           WHERE Citas.fecha=? AND Citas.estado='Confirmada'", (fecha_seleccionada,))

    def mostrar_citas_por_medico(self):
        nombre_medico = self.combo_medico.get().strip()
        if not nombre_medico:
            messagebox.showwarning("Campos Vacíos", "Por favor ingrese el nombre del médico.")
            return
        self.mostrar_citas("SELECT Citas.id, Usuarios.nombre, Medicos.nombre, Citas.hora FROM Citas \
                           JOIN Usuarios ON Citas.usuario_id = Usuarios.id \
                           JOIN Medicos ON Citas.medico_id = Medicos.id \
                           WHERE Medicos.nombre=? AND Citas.estado='Confirmada'", (nombre_medico,))

    def mostrar_citas(self, query, params):
        try:
            with sqlite3.connect("citas_medicas.db") as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                citas = cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"Error al obtener citas: {e}")
            return

        self.lista_citas.delete(0, "end")
        if citas:
            for cita in citas:
                self.lista_citas.insert("end", f"ID: {cita[0]} - Paciente: {cita[1]}, Médico: {cita[2]}, Hora: {cita[3]}")
        else:
            self.lista_citas.insert("end", "No hay citas para esta consulta.")

    def abrir_ventana_agendar(self):
        ventana_agendar = AgendarCita(self)
        ventana_agendar.mainloop()

    def obtener_medicos(self):
        try:
            with sqlite3.connect("citas_medicas.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nombre FROM Medicos")
                medicos = [row[0] for row in cursor.fetchall()]
            return medicos
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"Error al obtener médicos: {e}")
            return []

    def eliminar_cita(self):
        selected_index = self.lista_citas.curselection()
        if not selected_index:
            messagebox.showwarning("Selección de Cita", "Por favor seleccione una cita para eliminar.")
            return

        cita_seleccionada = self.lista_citas.get(selected_index[0]).split(" - ")[0].replace("ID: ", "")
        try:
            with sqlite3.connect("citas_medicas.db") as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Citas WHERE id=?", (cita_seleccionada,))
                conn.commit()
            messagebox.showinfo("Cita Eliminada", f"La cita con ID {cita_seleccionada} ha sido eliminada.")
            self.mostrar_citas_por_fecha()  # Recargar citas
        except sqlite3.Error as e:
            messagebox.showerror("Error al Eliminar Cita", f"Error al eliminar la cita: {e}")
        self.pintar_dias_con_citas()

    def editar_cita(self):
        selected_index = self.lista_citas.curselection()
        if not selected_index:
            messagebox.showwarning("Selección de Cita", "Por favor seleccione una cita para editar.")
            return

        cita_seleccionada = self.lista_citas.get(selected_index[0]).split(" - ")[0].replace("ID: ", "")
        # Abrir ventana de edición de cita
        self.ventana_editar_cita(cita_seleccionada)

    def ventana_editar_cita(self, cita_id):
        """Abrir una nueva ventana para editar los datos de la cita seleccionada."""
        # Crear ventana emergente
        ventana_editar = Toplevel(self)
        ventana_editar.title("Editar Cita")
        ventana_editar.geometry("400x300")

        # Etiquetas y campos de entrada para los nuevos valores
        ctk.CTkLabel(ventana_editar, text="Hora de la Cita:", text_color="black").pack(pady=5)
        entry_hora = ctk.CTkEntry(ventana_editar)
        entry_hora.pack(pady=5)

        ctk.CTkLabel(ventana_editar, text="Nuevo Médico:", text_color="black").pack(pady=5)
        combo_medico = ctk.CTkComboBox(ventana_editar, values=self.obtener_medicos())
        combo_medico.pack(pady=5)

        # Botón para guardar cambios
        def guardar_edicion():
            nueva_hora = entry_hora.get()
            nuevo_medico = combo_medico.get()

            if not nueva_hora or not nuevo_medico:
                messagebox.showwarning("Campos Vacíos", "Por favor complete todos los campos.")
                return

            try:
                with sqlite3.connect("citas_medicas.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Citas SET hora=?, medico_id=(SELECT id FROM Medicos WHERE nombre=?) WHERE id=?",
                                   (nueva_hora, nuevo_medico, cita_id))
                    conn.commit()
                messagebox.showinfo("Cita Editada", "La cita se ha editado correctamente.")
                ventana_editar.destroy()
                self.mostrar_citas_por_fecha()  # Recargar las citas
            except sqlite3.Error as e:
                messagebox.showerror("Error al Editar Cita", f"Error al editar la cita: {e}")

        # Botón para guardar los cambios
        btn_guardar = ctk.CTkButton(ventana_editar, text="Guardar Cambios", command=guardar_edicion)
        btn_guardar.pack(pady=20)






class AgendarCita(ctk.CTk):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.title("Agendar Cita para Paciente")
        self.geometry("400x300")

        # Selección del paciente
        ctk.CTkLabel(self, text="Paciente:").pack()
        self.combo_paciente = ctk.CTkComboBox(self, values=self.obtener_pacientes())
        self.combo_paciente.pack(pady=5)

        # Selección de especialidad
        ctk.CTkLabel(self, text="Especialidad:").pack()
        self.combo_especialidad = ctk.CTkComboBox(self, values=self.obtener_especialidades())
        self.combo_especialidad.pack(pady=5)

        # Selección del médico
        ctk.CTkLabel(self, text="Médico:").pack()
        self.combo_medico = ctk.CTkComboBox(self, values=[])
        self.combo_medico.pack(pady=5)

        # Hora de la cita
        ctk.CTkLabel(self, text="Hora (HH:MM):").pack()
        self.entry_hora = ctk.CTkComboBox(self, values=["12:00", "13:00", "14:00"])
        self.entry_hora.pack(pady=5)

        # Botón para agendar la cita
        self.btn_agendar = ctk.CTkButton(self, text="Agendar", command=self.agendar_cita)
        self.btn_agendar.pack(pady=10)

        # Conectar el cambio de especialidad con la actualización de médicos
        self.combo_especialidad.bind("<Configure>", self.actualizar_medicos)

    @staticmethod
    def obtener_pacientes():
        try:
            with sqlite3.connect("citas_medicas.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nombre FROM Usuarios WHERE tipo = 'Paciente'")
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"Error al obtener pacientes: {e}")
            return []

    @staticmethod
    def obtener_especialidades():
        try:
            with sqlite3.connect("citas_medicas.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT especialidad FROM Medicos")
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"Error al obtener especialidades: {e}")
            return []

    def actualizar_medicos(self, event=None):
        especialidad = self.combo_especialidad.get()
        if especialidad:
            medicos = self.obtener_medicos(especialidad)
            self.combo_medico.configure(values=medicos)

    @staticmethod
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

    def validar_cita_existente(self, medico, fecha, hora):
        """Verifica si ya existe una cita para el médico, en la fecha y hora dadas."""
        try:
            with sqlite3.connect("citas_medicas.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM Citas
                    WHERE medico_id = (SELECT id FROM Medicos WHERE nombre = ?)
                    AND fecha = ? AND hora = ?
                """, (medico, fecha, hora))
                resultado = cursor.fetchone()
                return resultado[0] > 0
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"Error al verificar citas existentes: {e}")
            return False

    def agendar_cita(self):
        paciente = self.combo_paciente.get().strip()
        medico = self.combo_medico.get()
        hora = self.entry_hora.get()
        fecha = self.parent.calendario.get_date()

        if not paciente or not medico or not hora:
            messagebox.showwarning("Campos Vacíos", "Por favor complete todos los campos.")
            return

        # Validar si ya existe una cita para el médico en esa fecha y hora
        if self.validar_cita_existente(medico, fecha, hora):
            messagebox.showwarning("Cita ya agendada", f"Ya existe una cita para el médico {medico} en esa fecha y hora.")
            return

        try:
            with sqlite3.connect("citas_medicas.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Citas (usuario_id, medico_id, fecha, hora, estado)
                    VALUES ((SELECT id FROM Usuarios WHERE nombre=?),
                            (SELECT id FROM Medicos WHERE nombre=?), ?, ?, 'Confirmada')
                """, (paciente, medico, fecha, hora))
                conn.commit()

            messagebox.showinfo("Éxito", "Cita agendada correctamente.")
            self.parent.pintar_dias_con_citas()
            self.destroy()

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo agendar la cita: {e}")


