from PIL import Image
import numpy as np
import tensorflow as tf

# Load the TensorFlow model
try:
    MODEL = tf.keras.models.load_model(
        r"C:\Users\ACER\Code\vitato-disease\saved_models\1.keras")
except Exception as e:
    raise Exception(f"Error loading model: {e}")

CLASS_NAMES = ["Caterpillar", "Healthy",
               "Infected", "Leaf_Miners", "Sap_Sucking_Insect"]


def read_file_as_image(file_path) -> np.ndarray:
    image = np.array(Image.open(file_path).convert('RGB'))
    return image
