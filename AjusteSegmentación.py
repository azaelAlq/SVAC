import cv2
import numpy as np

# URL del stream de la ESP32-CAM
ESP32_CAM_URL = "http://192.168.2.94/video"

# Función para imprimir los valores actuales
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

# Crear ventana con controles
cv2.namedWindow("Ajustes Amarillo")
cv2.createTrackbar("H Min", "Ajustes Amarillo", 20, 179, nothing)
cv2.createTrackbar("S Min", "Ajustes Amarillo", 100, 255, nothing)
cv2.createTrackbar("V Min", "Ajustes Amarillo", 100, 255, nothing)
cv2.createTrackbar("H Max", "Ajustes Amarillo", 35, 179, nothing)
cv2.createTrackbar("S Max", "Ajustes Amarillo", 255, 255, nothing)
cv2.createTrackbar("V Max", "Ajustes Amarillo", 255, 255, nothing)

# Abrir el stream
cap = cv2.VideoCapture(ESP32_CAM_URL)

if not cap.isOpened():
    print("No se pudo abrir el stream de la ESP32-CAM.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # Rotar para que coincida con la orientación correcta (si es necesario)
    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

    # Convertir a HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Leer los valores de los sliders
    h_min = cv2.getTrackbarPos("H Min", "Ajustes Amarillo")
    s_min = cv2.getTrackbarPos("S Min", "Ajustes Amarillo")
    v_min = cv2.getTrackbarPos("V Min", "Ajustes Amarillo")
    h_max = cv2.getTrackbarPos("H Max", "Ajustes Amarillo")
    s_max = cv2.getTrackbarPos("S Max", "Ajustes Amarillo")
    v_max = cv2.getTrackbarPos("V Max", "Ajustes Amarillo")

    lower_yellow = np.array([h_min, s_min, v_min])
    upper_yellow = np.array([h_max, s_max, v_max])

    # Crear la máscara y mostrarla
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    result = cv2.bitwise_and(frame, frame, mask=mask)

    # Mostrar ambas ventanas
    cv2.imshow("Detección Amarillo", result)
    cv2.imshow("Original", frame)

    # Salir con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
