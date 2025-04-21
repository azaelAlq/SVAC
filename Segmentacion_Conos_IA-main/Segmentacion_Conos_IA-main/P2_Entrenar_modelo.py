import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Definir el generador de datos de entrenamiento
datagen = ImageDataGenerator(rescale=1./255)

train_generator = datagen.flow_from_directory(
    'dataset_entrenamiento',        # Asegúrate de que tenga subcarpetas como 'amarillo' y 'otros'
    target_size=(64, 64),
    batch_size=32,
    class_mode='binary'             # Solo dos clases: amarillo vs no amarillo
)

# Construir el modelo
model = Sequential()

# Primera capa
model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(64, 64, 3)))
model.add(MaxPooling2D(pool_size=(2, 2)))

# Segunda capa
model.add(Conv2D(32, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

# Capa de flatten
model.add(Flatten())

# Capa densa oculta
model.add(Dense(128, activation='relu'))

# Capa de salida para clasificación binaria
model.add(Dense(1, activation='sigmoid'))

# Compilar el modelo
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Entrenar el modelo
model.fit(train_generator, epochs=10, steps_per_epoch=100)

# Guardar el modelo
model.save('modelo_conos_amarillos.h5')
