import cv2
import numpy as np
import tensorflow as tf

# Cargar el modelo
model = tf.keras.models.load_model('modelo_conos_amarillos.h5')

# Webcam
cap = cv2.VideoCapture(0)

# Preprocesamiento
def preprocess_image(image):
    # Redimensionar la imagen a 64x64 (el tamaño esperado por el modelo)
    image_resized = cv2.resize(image, (64, 64))
    image_normalized = image_resized / 255.0
    image_expanded = np.expand_dims(image_normalized, axis=0)
    return image_expanded

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Redimensionar para visualización (opcional)
    frame_resized = cv2.resize(frame, (640, 480))
    hsv = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2HSV)

    # 🎯 Filtrar color amarillo (para detectar conos amarillos)
    lower_yellow = np.array([20, 100, 100])  # Límite inferior del color amarillo
    upper_yellow = np.array([30, 255, 255])  # Límite superior del color amarillo
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)  # Crear la máscara

    # Encontrar contornos en la máscara de color amarillo
    contours_yellow, _ = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours_yellow:
        area = cv2.contourArea(cnt)
        if area > 300:  # Solo detectar áreas grandes (evitar ruidos pequeños)
            # Dibujar un rectángulo alrededor de los contornos
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame_resized, (x, y), (x+w, y+h), (0, 255, 255), 2)
            
            # Recortar la región que contiene el posible cono
            recorte = frame_resized[y:y+h, x:x+w]
            input_image = preprocess_image(recorte)

            # Hacer la predicción
            pred = model.predict(input_image, verbose=0)
            if pred[0][0] > 0.5:  # Probabilidad alta de ser cono amarillo
                cv2.putText(frame_resized, 'Cono Amarillo', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    # Mostrar la imagen con los contornos y las predicciones
    cv2.imshow('Predicciones en tiempo real', frame_resized)

    # Salir con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
