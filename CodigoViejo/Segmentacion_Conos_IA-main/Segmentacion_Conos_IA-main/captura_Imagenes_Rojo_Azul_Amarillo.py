import cv2 
import numpy as np
import os
import time

# Crear carpetas organizadas si no existen
os.makedirs("dataset_entrenamiento/rojo", exist_ok=True)
os.makedirs("dataset_entrenamiento/amarillo", exist_ok=True)
os.makedirs("dataset_entrenamiento/azul", exist_ok=True)

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

    # 🎯 --- CONOS ROJOS ---
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])
    mask_red = cv2.inRange(hsv, lower_red, upper_red)

    # 🟡 --- CONOS AMARILLOS ---
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([30, 255, 255])
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

    # 🔵 --- CONOS AZULES ---
    lower_blue = np.array([100, 150, 0])
    upper_blue = np.array([140, 255, 255])
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

    # Contadores
    conteo_rojo = 0
    conteo_amarillo = 0
    conteo_azul = 0

    timestamp = int(time.time() * 1000)  # Para nombres únicos

    # 🔴 Conos rojos
    contours_red, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for i, cnt in enumerate(contours_red):
        area = cv2.contourArea(cnt)
        if area > 300:
            conteo_rojo += 1
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.putText(frame, 'Cono Rojo', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            recorte = frame[y:y+h, x:x+w]
            nombre = f"dataset_entrenamiento/rojo/rojo_{timestamp}_{i}.png"
            cv2.imwrite(nombre, recorte)

    # 🟡 Conos amarillos
    contours_yellow, _ = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for i, cnt in enumerate(contours_yellow):
        area = cv2.contourArea(cnt)
        if area > 300:
            conteo_amarillo += 1
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
            cv2.putText(frame, 'Cono Amarillo', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            recorte = frame[y:y+h, x:x+w]
            nombre = f"dataset_entrenamiento/amarillo/amarillo_{timestamp}_{i}.png"
            cv2.imwrite(nombre, recorte)

    # 🔵 Conos azules
    contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for i, cnt in enumerate(contours_blue):
        area = cv2.contourArea(cnt)
        if area > 300:
            conteo_azul += 1
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(frame, 'Cono Azul', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            recorte = frame[y:y+h, x:x+w]
            nombre = f"dataset_entrenamiento/azul/azul_{timestamp}_{i}.png"
            cv2.imwrite(nombre, recorte)

    # Mostrar conteos en pantalla
    cv2.putText(frame, f'Rojos: {conteo_rojo}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.putText(frame, f'Amarillos: {conteo_amarillo}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.putText(frame, f'Azules: {conteo_azul}', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    # 🎯 --- LÍNEAS NEGRAS ---
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, mask_black = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)

    contours_black, _ = cv2.findContours(mask_black, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours_black:
        area = cv2.contourArea(cnt)
        if area > 500:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 255), 2)
            cv2.putText(frame, 'Linea Negra', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Muestra el resultado
    cv2.imshow('Segmentacion en tiempo real', frame)

    # Salir con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera recursos
cap.release()
cv2.destroyAllWindows()
