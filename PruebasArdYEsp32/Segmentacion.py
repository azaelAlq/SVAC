import cv2
import numpy as np
import socket

# Configuración de red para recibir datos UDP
UDP_IP = "0.0.0.0"  # Acepta conexiones desde cualquier IP
UDP_PORT = 5005
CHUNK_SIZE = 1024

# Función para imprimir los valores actuales de los sliders
def imprimir_valores():
    h_min = cv2.getTrackbarPos("H Min", "Ajustes Amarillo")
    s_min = cv2.getTrackbarPos("S Min", "Ajustes Amarillo")
    v_min = cv2.getTrackbarPos("V Min", "Ajustes Amarillo")
    h_max = cv2.getTrackbarPos("H Max", "Ajustes Amarillo")
    s_max = cv2.getTrackbarPos("S Max", "Ajustes Amarillo")
    v_max = cv2.getTrackbarPos("V Max", "Ajustes Amarillo")
    print(f"lower_yellow = np.array([{h_min}, {s_min}, {v_min}])")
    print(f"upper_yellow = np.array([{h_max}, {s_max}, {v_max}])")

# Callback vacío para los trackbars
def nothing(x):
    imprimir_valores()

# Crear ventana con controles de color (para ajuste manual del rango de color amarillo)
cv2.namedWindow("Ajustes Amarillo")
cv2.createTrackbar("H Min", "Ajustes Amarillo", 20, 179, nothing)
cv2.createTrackbar("S Min", "Ajustes Amarillo", 100, 255, nothing)
cv2.createTrackbar("V Min", "Ajustes Amarillo", 100, 255, nothing)
cv2.createTrackbar("H Max", "Ajustes Amarillo", 35, 179, nothing)
cv2.createTrackbar("S Max", "Ajustes Amarillo", 255, 255, nothing)
cv2.createTrackbar("V Max", "Ajustes Amarillo", 255, 255, nothing)

# Crear socket UDP para recibir datos de la cámara
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(5)

print(f"Escuchando en {UDP_IP}:{UDP_PORT}...")

image_data = b""

while True:
    try:
        # Recibir fragmentos de la imagen por UDP
        data, _ = sock.recvfrom(CHUNK_SIZE)
        image_data += data

        # Si el fragmento recibido es menor que el tamaño máximo, asumimos que es el final de una imagen
        if len(data) < CHUNK_SIZE:
            np_arr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if img is not None:
                # Rotar y redimensionar la imagen
                img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

                # Convertir la imagen a HSV
                hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

                # Leer los valores de los sliders para el rango de color amarillo
                h_min = cv2.getTrackbarPos("H Min", "Ajustes Amarillo")
                s_min = cv2.getTrackbarPos("S Min", "Ajustes Amarillo")
                v_min = cv2.getTrackbarPos("V Min", "Ajustes Amarillo")
                h_max = cv2.getTrackbarPos("H Max", "Ajustes Amarillo")
                s_max = cv2.getTrackbarPos("S Max", "Ajustes Amarillo")
                v_max = cv2.getTrackbarPos("V Max", "Ajustes Amarillo")

                # Definir los rangos de color amarillo
                lower_yellow = np.array([h_min, s_min, v_min])
                upper_yellow = np.array([h_max, s_max, v_max])

                # Crear la máscara para detectar el color amarillo
                mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
                result = cv2.bitwise_and(img, img, mask=mask)

                # Mostrar las dos imágenes (original y resultado de la detección)
                cv2.imshow("Detección Amarillo", result)
                cv2.imshow("Original", img)

            else:
                print("Error al decodificar la imagen")

            image_data = b""  # Reiniciar el buffer para la siguiente imagen
    except socket.timeout:
        print("[!] Tiempo de espera agotado, reiniciando buffer...")
        image_data = b""
    except Exception as e:
        print(f"Error: {e}")
        image_data = b""

    # Salir si presionas 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cerrar conexiones
sock.close()
cv2.destroyAllWindows()
