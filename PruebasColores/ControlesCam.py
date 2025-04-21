import cv2
import tkinter as tk
from threading import Thread
import requests
import time  # Para usar time.sleep
from PIL import Image, ImageTk

# Dirección IP del ESP32-CAM
ESP32_CAM_VIDEO_URL = "http://192.168.2.94/video"
ESP32_CAM_BASE_URL = "http://192.168.2.94"

# Función para enviar comando al ESP32
def enviar_comando(ruta):
    url = f"{ESP32_CAM_BASE_URL}/{ruta}"
    try:
        requests.get(url)
        print(f"Comando enviado: {ruta}")
    except Exception as e:
        print(f"Error al enviar comando: {e}")

# Función para enviar los comandos con un retraso para sincronización
def enviar_comando_sincronizado(ruta_izq, ruta_der, delay=0.1):
    # Enviar comando para motor izquierdo
    requests.get(f"{ESP32_CAM_BASE_URL}/{ruta_izq}")
    print(f"Comando enviado: {ruta_izq}")
    
    # Esperar un poco antes de enviar el comando para el motor derecho
    time.sleep(delay)
    
    # Enviar comando para motor derecho
    requests.get(f"{ESP32_CAM_BASE_URL}/{ruta_der}")
    print(f"Comando enviado: {ruta_der}")

# Clase de la interfaz
class ControlESP32CAM:
    def __init__(self, master):
        self.master = master
        self.master.title("Control Individual de Motores - ESP32-CAM")

        # Canvas para mostrar video
        self.label_video = tk.Label(master)
        self.label_video.pack()

        # Controles por motor
        frame = tk.Frame(master)
        frame.pack(pady=10)

        # Botones para motor izquierdo
        tk.Label(frame, text="Motor Izquierdo", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=5)
        tk.Button(frame, text="Adelante ON", width=20, command=lambda: enviar_comando("motor/izq/adelante/on")).grid(row=1, column=0)
        tk.Button(frame, text="Adelante OFF", width=20, command=lambda: enviar_comando("motor/izq/adelante/off")).grid(row=1, column=1)
        tk.Button(frame, text="Atrás ON", width=20, command=lambda: enviar_comando("motor/izq/atras/on")).grid(row=2, column=0)
        tk.Button(frame, text="Atrás OFF", width=20, command=lambda: enviar_comando("motor/izq/atras/off")).grid(row=2, column=1)

        # Botones para motor derecho
        tk.Label(frame, text="Motor Derecho", font=('Arial', 12, 'bold')).grid(row=3, column=0, columnspan=2, pady=5)
        tk.Button(frame, text="Adelante ON", width=20, command=lambda: enviar_comando("motor/der/adelante/on")).grid(row=4, column=0)
        tk.Button(frame, text="Adelante OFF", width=20, command=lambda: enviar_comando("motor/der/adelante/off")).grid(row=4, column=1)
        tk.Button(frame, text="Atrás ON", width=20, command=lambda: enviar_comando("motor/der/atras/on")).grid(row=5, column=0)
        tk.Button(frame, text="Atrás OFF", width=20, command=lambda: enviar_comando("motor/der/atras/off")).grid(row=5, column=1)

        # Control de velocidad
        tk.Label(frame, text="Velocidad", font=('Arial', 12, 'bold')).grid(row=6, column=0, columnspan=2, pady=5)
        tk.Button(frame, text="Lenta", width=20, command=lambda: enviar_comando("motor/velocidad/lenta")).grid(row=7, column=0)
        tk.Button(frame, text="Normal", width=20, command=lambda: enviar_comando("motor/velocidad/normal")).grid(row=7, column=1)

        # Hilo para mostrar el video
        self.thread = Thread(target=self.mostrar_video)
        self.thread.daemon = True
        self.thread.start()

        # Asociar teclas con funciones
        self.master.bind("<KeyPress>", self.tecla_presionada)
        self.master.bind("<KeyRelease>", self.tecla_liberada)

        self.teclas_activas = set()

    def mostrar_video(self):
        stream = cv2.VideoCapture(ESP32_CAM_VIDEO_URL)
        if not stream.isOpened():
            print("No se pudo conectar al stream de la ESP32-CAM.")
            return

        while True:
            ret, frame = stream.read()
            if not ret:
                continue

            # Rotar la imagen 90 grados en sentido horario
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

            # Convertir el frame a formato compatible con Tkinter
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imagen = ImageTk.PhotoImage(Image.fromarray(frame))

            self.label_video.configure(image=imagen)
            self.label_video.image = imagen

    def tecla_presionada(self, evento):
        tecla = evento.keysym.lower()
        if tecla in self.teclas_activas:
            return  # Evita repetir si ya está presionada

        self.teclas_activas.add(tecla)

        if tecla == "w":
            enviar_comando_sincronizado("motor/izq/adelante/on", "motor/der/adelante/on")
        elif tecla == "s":
            enviar_comando_sincronizado("motor/izq/atras/on", "motor/der/atras/on")
        elif tecla == "a":
            # Solo activar motor izquierdo para ir a la izquierda
            enviar_comando_sincronizado("motor/izq/atras/on", "motor/der/adelante/off")
        elif tecla == "d":
            # Solo activar motor derecho para ir a la derecha
            enviar_comando_sincronizado("motor/izq/adelante/off", "motor/der/atras/on")
        elif tecla == "q":
            self.parar_motores()

    def tecla_liberada(self, evento):
        tecla = evento.keysym.lower()
        if tecla in self.teclas_activas:
            self.teclas_activas.remove(tecla)
            self.parar_motores()

    def parar_motores(self):
        enviar_comando_sincronizado("motor/izq/adelante/off", "motor/der/adelante/off")
        enviar_comando_sincronizado("motor/izq/atras/off", "motor/der/atras/off")

# Ejecutar la interfaz
if __name__ == "__main__":
    root = tk.Tk()
    app = ControlESP32CAM(root)
    root.mainloop()
