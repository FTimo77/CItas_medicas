import login
import database

if __name__ == "__main__":
    database.crear_base_datos()
    app = login.LoginApp()  # Crear instancia
    app.mainloop()  # Asegurar que la ventana se ejecute correctamente
