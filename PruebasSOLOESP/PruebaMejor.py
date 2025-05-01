import cv2
import numpy as np
import tkinter as tk
from threading import Thread
import requests
import time

ESP32_CAM_VIDEO_URL = "http://10.29.60.94/video"
ESP32_CAM_BASE_URL = "http://10.29.60.94"

ALTURA_REAL_CONO = 9  # cm
FOCAL_APROX = 600

# Variables globales
modo_autonomo_activado = False
ultima_frame = None

def enviar_comando(ruta):
    url = f"{ESP32_CAM_BASE_URL}/{ruta}"
    try:
        requests.get(url, timeout=0.1)
        log_evento(f"Comando: {ruta}")
    except Exception as e:
        log_evento(f"Comando: {ruta}")

def mover(accion, segundos):
    ruta = f"motor/{accion}?segundos={segundos}"
    enviar_comando(ruta)

def log_evento(texto):
    log_console.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {texto}\n")
    log_console.yview(tk.END)

def iniciar_modo_autonomo():
    global modo_autonomo_activado
    modo_autonomo_activado = True
    log_evento("Modo autónomo ACTIVADO")

def iniciar_interfaz():
    global log_console, video_frame, entry_duracion

    root = tk.Tk()
    root.title("Robot - Vista, Movimiento y Control")

    # Frame video
    video_frame = tk.Label(root)
    video_frame.pack()

    # Logs
    log_console = tk.Text(root, height=10, width=80)
    log_console.pack(padx=10, pady=10)

    # Botones de control manual
    control_frame = tk.Frame(root)
    control_frame.pack()

    tk.Label(control_frame, text="Duración (s):").grid(row=0, column=0)
    entry_duracion = tk.Entry(control_frame, width=5)
    entry_duracion.insert(0, "1")
    entry_duracion.grid(row=0, column=1)

    tk.Button(control_frame, text="Adelante", command=lambda: mover("adelante", entry_duracion.get())).grid(row=1, column=1)
    tk.Button(control_frame, text="Izquierda", command=lambda: mover("izquierda", entry_duracion.get())).grid(row=2, column=0)
    tk.Button(control_frame, text="Derecha", command=lambda: mover("derecha", entry_duracion.get())).grid(row=2, column=2)
    tk.Button(control_frame, text="Atrás", command=lambda: mover("atras", entry_duracion.get())).grid(row=3, column=1)
    tk.Button(control_frame, text="Giro", command=lambda: mover("giro", entry_duracion.get())).grid(row=4, column=1)

    tk.Button(control_frame, text="Velocidad Lenta", command=lambda: enviar_comando("motor/velocidad/lenta")).grid(row=5, column=0)
    tk.Button(control_frame, text="Velocidad Normal", command=lambda: enviar_comando("motor/velocidad/normal")).grid(row=5, column=2)

    # Botón de iniciar modo autónomo
    tk.Button(root, text="Iniciar Modo Autónomo", font=('Arial', 12, 'bold'), bg='green', fg='white',
              command=iniciar_modo_autonomo).pack(pady=10)

    # Ejecutar video + detección
    Thread(target=detectar_conos_y_control, daemon=True).start()

    root.mainloop()

def imagen_diferente(img1, img2, umbral=200000):
    if img1 is None or img2 is None:
        return True
    diff = cv2.absdiff(img1, img2)
    non_zero = np.count_nonzero(diff)
    return non_zero > umbral

def detectar_conos_y_control():
    global ultima_frame, modo_autonomo_activado

    cap = cv2.VideoCapture(ESP32_CAM_VIDEO_URL)
    if not cap.isOpened():
        log_evento("No se pudo conectar al stream.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        frame = cv2.resize(frame, (640, 480))

        # Solo si la imagen cambia
        if not imagen_diferente(ultima_frame, frame):
            time.sleep(0.1)
            continue
        ultima_frame = frame.copy()

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([35, 255, 255])

        mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
        contours, _ = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        cono_mas_cercano = None
        distancia_min = float('inf')

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 300:
                x, y, w, h = cv2.boundingRect(cnt)
                distancia_cm = (ALTURA_REAL_CONO * FOCAL_APROX) / h if h != 0 else 0
                if distancia_cm < distancia_min:
                    distancia_min = distancia_cm
                    cono_mas_cercano = (x, y, w, h)

        if cono_mas_cercano:
            x, y, w, h = cono_mas_cercano
            distancia_cm = (ALTURA_REAL_CONO * FOCAL_APROX) / h if h != 0 else 0
            centro_cono = x + w // 2

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
            cv2.putText(frame, f"{distancia_cm:.1f} cm", (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            if modo_autonomo_activado:
                if 14 <= distancia_cm <= 17:
                    mover("detener", 0)
                    log_evento("¡Cono cercano! Detenerse y retirar.")
                    time.sleep(3)
                elif centro_cono < 250:
                    mover("izquierda", 0.0)
                elif centro_cono > 390:
                    mover("derecha", 0.0)
                else:
                    mover("adelante", 0)
        else:
            if modo_autonomo_activado:
                mover("giro", 0.0)

        # Mostrar video
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_tk = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        img_tk = cv2.imencode('.ppm', img_tk)[1].tobytes()
        photo = tk.PhotoImage(data=img_tk)
        video_frame.configure(image=photo)
        video_frame.image = photo

        time.sleep(0.1)  # Control de ciclo

if __name__ == "__main__":
    iniciar_interfaz()
