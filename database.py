import sqlite3
import os

DB_NAME = "citas_medicas.db"

def crear_base_datos():
    if not os.path.exists(DB_NAME):  # Verificar si la BD ya existe
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Crear tabla de Usuarios
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT CHECK(tipo IN ('Paciente', 'Admin')) NOT NULL
        )''')

        # Crear tabla de Médicos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Medicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            especialidad TEXT NOT NULL
        )''')

        # Crear tabla de Citas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            medico_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            estado TEXT CHECK(estado IN ('Confirmada', 'Cancelada')) NOT NULL,
            FOREIGN KEY(usuario_id) REFERENCES Usuarios(id),
            FOREIGN KEY(medico_id) REFERENCES Medicos(id)
        )''')

        # Insertar datos de médicos solo si la tabla está vacía
        cursor.execute("SELECT COUNT(*) FROM Medicos")
        if cursor.fetchone()[0] == 0:
            medicos = [
                ("Dr. Juan Perez", "Cardiologo"),
                ("Dra. Ana Gomez", "Pediatra"),
                ("Dr. Carlos Lopez", "Dermatologo")
            ]
            cursor.executemany('''
                INSERT INTO Medicos (nombre, especialidad) VALUES (?, ?)
            ''', medicos)

        # Insertar datos de usuarios solo si la tabla está vacía
        cursor.execute("SELECT COUNT(*) FROM Usuarios")
        if cursor.fetchone()[0] == 0:
            usuarios = [
                ("Pedro Martínez", "Paciente"),
                ("Lucía Fernández", "Paciente"),
                ("Carlos Ramírez", "Paciente"),
                ("Admin", "Admin")
            ]
            cursor.executemany('''
                INSERT INTO Usuarios (nombre, tipo) VALUES (?, ?)
            ''', usuarios)

        conn.commit()
        conn.close()
        print("✅ Base de datos creada correctamente.")
    else:
        print("⚠️ La base de datos ya existe. No es necesario crearla nuevamente.")
