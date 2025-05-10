import socket
import cv2
import numpy as np
import tkinter as tk
from threading import Thread, Lock
import threading
import requests
import time

# Configuración de red
UDP_IP = "0.0.0.0"
UDP_PORT = 5005
CHUNK_SIZE = 1024
ESP32_MOTORES_BASE_URL = "http://192.168.134.104"

lower_yellow = np.array([18, 80, 78])
upper_yellow = np.array([43, 255, 255])

# Variables globales
log_console = None
video_frame = None
entry_duracion = None
sock = None

# Variables automáticas
modo_automatico = False
tiempo_espera_movimiento = 1.5  # segundos
frame_actual = None
mutex = Lock()
s
# Inicializa socket UDP
def iniciar_socket_udp():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.settimeout(5)
    print(f"[INFO] Escuchando en {UDP_IP}:{UDP_PORT}")

# Enviar comando HTTP a ESP32 motores
def enviar_comando_motores(ruta):
    url = f"{ESP32_MOTORES_BASE_URL}/{ruta}"
    try:
        requests.get(url, timeout=0.7)
        log_evento(f"Comando enviado: {ruta}")
    except Exception as e:
        log_evento(f"Error al enviar comando: {ruta} - {e}")

def mover(accion, duracion):
    ruta = f"motor/{accion}?duracion={duracion}"
    enviar_comando_motores(ruta)

def log_evento(texto):
    log_console.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {texto}\n")
    log_console.yview(tk.END)

# Mostrar video en Tkinter y actualizar frame_actual
def mostrar_video_udp():
    global frame_actual
    image_data = b""
    while True:
        try:
            data, _ = sock.recvfrom(CHUNK_SIZE)
            image_data += data

            if len(data) < CHUNK_SIZE:
                np_arr = np.frombuffer(image_data, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                if frame is not None:
                    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    frame = cv2.resize(frame, (640, 480))

                    with mutex:
                        frame_actual = frame.copy()

                    # Detección de color amarillo
                    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

                    kernel = np.ones((5, 5), np.uint8)
                    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

                    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                    for cnt in contours:
                        area = cv2.contourArea(cnt)
                        if area > 300:
                            x, y, w, h = cv2.boundingRect(cnt)
                            ALTURA_CONO_REAL_CM = 9
                            DISTANCIA_FOCAL = 550
                            h_corregida = h * 1.10
                            distancia_cm = (ALTURA_CONO_REAL_CM * DISTANCIA_FOCAL) / h_corregida

                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
                            cv2.putText(frame, "Cono", (x, y - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                            cv2.putText(frame, f"h={h}, w={w}", (x, y - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 200), 1)
                            cv2.putText(frame, f"d={distancia_cm:.1f} cm", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                    img_rgb = frame.copy()
                    img_tk = cv2.imencode('.ppm', img_rgb)[1].tobytes()
                    photo = tk.PhotoImage(data=img_tk)
                    video_frame.configure(image=photo)
                    video_frame.image = photo

                else:
                    log_evento("Error al decodificar imagen")
                image_data = b""

        except socket.timeout:
            image_data = b""
        except Exception as e:
            log_evento(f"Error de recepción: {e}")
            image_data = b""

# Funciones automáticas
def activar_modo_automatico():
    global modo_automatico
    if not modo_automatico:
        modo_automatico = True
        log_evento("Modo automático ACTIVADO")
        Thread(target=modo_autonomo, daemon=True).start()

def desactivar_modo_automatico():
    global modo_automatico
    modo_automatico = False
    log_evento("Modo automático DESACTIVADO")

def modo_autonomo():
    global modo_automatico
    while modo_automatico:
        with mutex:
            if frame_actual is None:
                time.sleep(0.5)
                continue
            frame = frame_actual.copy()

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            mover("giro", 350)
            time.sleep(tiempo_espera_movimiento)
            continue

        cnt = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(cnt)
        cx = x + w // 2

        ALTURA_CONO_REAL_CM = 9
        DISTANCIA_FOCAL = 550
        distancia_cm = (ALTURA_CONO_REAL_CM * DISTANCIA_FOCAL) / (h * 1.10)

        if 18 <= distancia_cm <= 19:
            log_evento("¡Cono alcanzado! Quitar cono")
            modo_automatico = False
            return

        if cx < 220:
            mover("izquierda", 150)
        elif cx > 420:
            mover("derecha", 150)
        else:
            if distancia_cm > 25:
                mover("adelante", 500)
            else:
                mover("adelante", 300)

        time.sleep(tiempo_espera_movimiento)

# Interfaz principal
def iniciar_interfaz():
    global log_console, video_frame, entry_duracion

    root = tk.Tk()
    root.title("Robot - Control Manual con Video UDP")

    video_frame = tk.Label(root)
    video_frame.pack()

    log_console = tk.Text(root, height=10, width=80)
    log_console.pack(padx=10, pady=10)

    control_frame = tk.Frame(root)
    control_frame.pack()

    tk.Label(control_frame, text="Duración (ms):").grid(row=0, column=0)
    entry_duracion = tk.Entry(control_frame, width=5)
    entry_duracion.insert(0, "1000")
    entry_duracion.grid(row=0, column=1)

    tk.Button(control_frame, text="Adelante", command=lambda: mover("adelante", entry_duracion.get())).grid(row=1, column=1)
    tk.Button(control_frame, text="Izquierda", command=lambda: mover("izquierda", entry_duracion.get())).grid(row=2, column=0)
    tk.Button(control_frame, text="Derecha", command=lambda: mover("derecha", entry_duracion.get())).grid(row=2, column=2)
    tk.Button(control_frame, text="Atrás", command=lambda: mover("atras", entry_duracion.get())).grid(row=3, column=1)
    tk.Button(control_frame, text="Giro", command=lambda: mover("giro", entry_duracion.get())).grid(row=4, column=1)

    tk.Button(control_frame, text="Auto ON", command=activar_modo_automatico).grid(row=5, column=0, pady=10)
    tk.Button(control_frame, text="Auto OFF", command=desactivar_modo_automatico).grid(row=5, column=2, pady=10)

    Thread(target=mostrar_video_udp, daemon=True).start()

    root.mainloop()

# Inicio del programa
if __name__ == "__main__":
    iniciar_socket_udp()
    iniciar_interfaz()
