import cv2
import numpy as np
import tkinter as tk
from threading import Thread
import requests

# ========================
# Configuración del ESP32-CAM
# ========================
ESP32_CAM_VIDEO_URL = "http://10.247.102.94/video"
ESP32_CAM_BASE_URL = "http://10.247.102.94"

# ========================
# Parámetros de visión
# ========================
ALTURA_REAL_CONO = 9  # en cm
FOCAL_APROX = 600

# ========================
# Funciones de control de motores
# ========================
def enviar_comando(ruta):
    url = f"{ESP32_CAM_BASE_URL}/{ruta}"
    try:
        requests.get(url)
        print(f"Comando enviado: {ruta}")
    except Exception as e:
        print(f"Error al enviar comando: {e}")

def mover(accion, segundos):
    ruta = f"motor/{accion}?segundos={segundos}"
    enviar_comando(ruta)

# ========================
# Interfaz gráfica para los botones
# ========================
def iniciar_interfaz():
    root = tk.Tk()
    root.title("Control de Motores - ESP32-CAM")

    frame = tk.Frame(root)
    frame.pack(pady=10)

    tk.Label(frame, text="Acciones de Movimiento", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=3, pady=5)

    duracion = tk.StringVar(value="1")

    tk.Label(frame, text="Duración (s):").grid(row=1, column=0)
    entry_duracion = tk.Entry(frame, width=5, textvariable=duracion)
    entry_duracion.grid(row=1, column=1)

    # Botones de movimiento
    tk.Button(frame, text="Adelante", width=20, command=lambda: mover("adelante", duracion.get())).grid(row=2, column=0, columnspan=3)
    tk.Button(frame, text="Atrás", width=20, command=lambda: mover("atras", duracion.get())).grid(row=3, column=0, columnspan=3)
    tk.Button(frame, text="Izquierda", width=20, command=lambda: mover("izquierda", duracion.get())).grid(row=4, column=0, columnspan=3)
    tk.Button(frame, text="Derecha", width=20, command=lambda: mover("derecha", duracion.get())).grid(row=5, column=0, columnspan=3)
    tk.Button(frame, text="Giro sobre eje", width=20, command=lambda: mover("giro", duracion.get())).grid(row=6, column=0, columnspan=3)

    # Control de velocidad
    tk.Label(frame, text="Velocidad", font=('Arial', 12, 'bold')).grid(row=7, column=0, columnspan=3, pady=5)
    tk.Button(frame, text="Lenta", width=20, command=lambda: enviar_comando("motor/velocidad/lenta")).grid(row=8, column=0, columnspan=1)
    tk.Button(frame, text="Normal", width=20, command=lambda: enviar_comando("motor/velocidad/normal")).grid(row=8, column=1, columnspan=1)

    root.mainloop()

# ========================
# Detección de conos (OpenCV)
# ========================
def deteccion_conos():
    cap = cv2.VideoCapture(ESP32_CAM_VIDEO_URL)

    if not cap.isOpened():
        print("No se pudo conectar al stream de la ESP32-CAM.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        frame = cv2.resize(frame, (640, 480))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        #Ajuste de parametros de color
        lower_yellow = np.array([28, 69, 100])
        upper_yellow = np.array([35, 255, 255])
        
        mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

        contours, _ = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        conteo = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 300:
                conteo += 1
                x, y, w, h = cv2.boundingRect(cnt)

                distancia_cm = (ALTURA_REAL_CONO * FOCAL_APROX) / h if h != 0 else 0

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
                cv2.putText(frame, f"{distancia_cm:.1f} cm", (x, y - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(frame, "Cono Amarillo", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        cv2.putText(frame, f"Detectados: {conteo}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        cv2.imshow("Detección de Conos Amarillos", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# ========================
# Iniciar ambos procesos
# ========================
if __name__ == "__main__":
    # Ejecutar interfaz de botones en un hilo
    Thread(target=iniciar_interfaz, daemon=True).start()

    # Ejecutar detección con OpenCV
    deteccion_conos()
