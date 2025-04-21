import cv2
import numpy as np
import os
import time

# Crear carpetas organizadas para el dataset de entrenamiento
os.makedirs('dataset_entrenamiento/amarillo', exist_ok=True)
# Si luego vas a agregar otros colores como rojo o azul, puedes agregarlos aquí
# os.makedirs('dataset_entrenamiento/rojo', exist_ok=True)
# os.makedirs('dataset_entrenamiento/azul', exist_ok=True)

# Inicializa la webcam
cap = cv2.VideoCapture(0)  # Usa 0 para la cámara por defecto

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Redimensiona si la imagen es muy grande
    frame = cv2.resize(frame, (640, 480))

    # Convertir a HSV para detectar colores
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 🎯 --- CONOS AMARILLOS ---
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([30, 255, 255])
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

    conteo_amarillo = 0
    timestamp = int(time.time() * 1000)  # Para nombres únicos

    contours_yellow, _ = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for i, cnt in enumerate(contours_yellow):
        area = cv2.contourArea(cnt)
        if area > 300:
            conteo_amarillo += 1
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
            cv2.putText(frame, 'Cono Amarillo', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            # Recorta y guarda directamente en la carpeta correspondiente
            recorte = frame[y:y+h, x:x+w]
            nombre = f"dataset_entrenamiento/amarillo/amarillo_{timestamp}_{i}.png"
            cv2.imwrite(nombre, recorte)

    # Mostrar conteo en pantalla
    cv2.putText(frame, f'Amarillos: {conteo_amarillo}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # Muestra el resultado
    cv2.imshow('Segmentacion en tiempo real', frame)

    # Salir con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera recursos
cap.release()
cv2.destroyAllWindows()
