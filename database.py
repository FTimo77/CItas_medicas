import sqlite3


def crear_base_datos():
    conn = sqlite3.connect("citas_medicas.db")
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

    # Insertar datos de médicos
    medicos = [
        ("Dr. Juan Perez", "Cardiologo"),
        ("Dra. Ana Gomez", "Pediatra"),
        ("Dr. Carlos Lopez", "Dermatologo")
    ]
    cursor.executemany('''
            INSERT INTO Medicos (nombre, especialidad) VALUES (?, ?)
        ''', medicos)

    # Insertar datos de usuarios (pacientes)
    usuarios = [
        ("Pedro Martínez", "Paciente"),
        ("Lucía Fernández", "Paciente"),
        ("Carlos Ramírez", "Paciente"),
        ("Juan_Gonzalez", "Admin")
    ]
    cursor.executemany('''
            INSERT INTO Usuarios (nombre, tipo) VALUES (?, ?)
        ''', usuarios)

    conn.commit()
    conn.close()

