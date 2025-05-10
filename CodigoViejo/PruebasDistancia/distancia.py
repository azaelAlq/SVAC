import cv2
import numpy as np

# Dirección IP del ESP32-CAM
ESP32_CAM_VIDEO_URL = "http://192.168.2.94/video"

# Medidas del cono (en cm)
ALTURA_REAL_CONO = 9  # cambia si tu cono mide más o menos
FOCAL_APROX = 600      # calcula esto bien como te explico arriba

# Conectar al stream
cap = cv2.VideoCapture(ESP32_CAM_VIDEO_URL)

if not cap.isOpened():
    print("No se pudo conectar al stream de la ESP32-CAM.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    frame = cv2.resize(frame, (640, 480))
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_yellow = np.array([0, 50, 87])
    upper_yellow = np.array([35, 255, 255])
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

    contours, _ = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    conteo = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 300:
            conteo += 1
            x, y, w, h = cv2.boundingRect(cnt)

            # Estimar la distancia
            if h != 0:
                distancia_cm = (ALTURA_REAL_CONO * FOCAL_APROX) / h
            else:
                distancia_cm = 0

            # Dibujar
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
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
