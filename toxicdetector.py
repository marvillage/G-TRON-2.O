from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
from PIL import Image
import io
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
# Load the trained model
model = tf.keras.models.load_model("best_resnet_fold_5.h5")

# Define image preprocessing function
def preprocess_image(image):
    image = image.resize((224, 224))  # Resize image to match model input
    image = np.array(image) / 255.0   # Normalize
    image = np.expand_dims(image, axis=0)  # Add batch dimension
    return image
label_mapping = {
    0: "Non-Toxic",
    1: "Toxic"
}

@app.route('/predict', methods=['POST'])
def predict():
    file = request.files['file']
    img = Image.open(file).resize((224, 224))  # Adjust size as per your model
    img_array = np.array(img) / 255.0  # Normalize if required
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension

    prediction = model.predict(img_array)
    predicted_class = np.argmax(prediction)  # Get the index of the highest probability
    confidence = float(np.max(prediction))  # Confidence score

    result = {
        "prediction": label_mapping[predicted_class],  # Convert number to label
        "confidence": confidence
    }

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
