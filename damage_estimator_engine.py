import numpy as np
import json
import requests
import urllib.request
import io
from PIL import Image as PILImage
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import get_file
from IPython.display import display, Image, clear_output
import pickle as pk
import matplotlib.pyplot as plt
# Updated imports for TensorFlow 2.x
import tensorflow as tf
from tensorflow.keras.applications import VGG16
from tensorflow.keras.applications.imagenet_utils import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.utils import get_file
# Load models
first_gate = VGG16(weights='imagenet')
second_gate = load_model('models/damage.keras')
severity_model = load_model('models/severity.h5')

with open('models/car_counter.pk', 'rb') as f:
    cat_list = pk.load(f)

# ImageNet class index for predictionss
CLASS_INDEX = None
CLASS_INDEX_PATH = 'https://s3.amazonaws.com/deep-learning-models/image-models/imagenet_class_index.json'

def get_predictions(preds, top=5):
    global CLASS_INDEX
    if len(preds.shape) != 2 or preds.shape[1] != 1000:
        raise ValueError('`decode_predictions` expects a batch of predictions (i.e. a 2D array of shape (samples, 1000)). '
                         'Found array with shape: ' + str(preds.shape))
    if CLASS_INDEX is None:
        fpath = get_file('imagenet_class_index.json',
                         CLASS_INDEX_PATH,
                         cache_subdir='models')
        CLASS_INDEX = json.load(open(fpath))
    results = []
    for pred in preds:
        top_indices = pred.argsort()[-top:][::-1]
        result = [tuple(CLASS_INDEX[str(i)]) + (pred[i],) for i in top_indices]
        result.sort(key=lambda x: x[2], reverse=True)
        results.append(result)
    return results

def get_image_from_url(img_url):
    """Get image data from URL without saving to disk"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(img_url, headers=headers, stream=True)
    response.raise_for_status()

    img_data = io.BytesIO(response.content)
    return img_data

def display_image(img_data_or_path):
    """Display image from either BytesIO or file path without saving to disk"""
    try:
        if isinstance(img_data_or_path, io.BytesIO):
            # Reset the pointer to the start of the BytesIO object
            img_data_or_path.seek(0)
            img = PILImage.open(img_data_or_path)

        elif isinstance(img_data_or_path, str):
            # It's a file path, could be local or URL
            if img_data_or_path.startswith(('http://', 'https://')):
                img_data = get_image_from_url(img_data_or_path)
                img = PILImage.open(img_data)

            else:
                # Local file
                img = PILImage.open(img_data_or_path)
    except Exception as e:
        print(f"Error displaying image: {str(e)}")

def prepare_image_from_data(img_data, target_size=(224, 224)):
    """Prepare image from data without saving to disk"""
    # Reset the pointer to the start of the BytesIO object
    img_data.seek(0)
    img = PILImage.open(img_data)
    # Convert to RGB mode to ensure 3 channels
    img = img.convert('RGB')
    img = img.resize(target_size)
    img_array = np.array(img)
    x = np.expand_dims(img_array, axis=0)
    x = preprocess_input(x)
    return x

def prepare_image(img_path, target_size=(224, 224)):
    """Prepare image from file path"""
    img = PILImage.open(img_path)
    # Convert to RGB mode to ensure 3 channels
    img = img.convert('RGB')
    img = img.resize(target_size)
    img_array = np.array(img)
    x = np.expand_dims(img_array, axis=0)
    x = preprocess_input(x)
    return x

def car_categories_gate(img_path, model):
    print("Validating that this is a picture of your car...")
    try:
        if img_path.startswith(('http://', 'https://')):
            img_data = get_image_from_url(img_path)
            # Display the image (but don't show in web context)
            print("Image received:")
            # Skip displaying in web context
            # display_image(img_data)

            # Prepare for prediction
            x = prepare_image_from_data(img_data)
        else:
            # Handle local file
            print("Image received:")
            # Skip displaying in web context
            # display_image(img_path)
            x = prepare_image(img_path)

        out = model.predict(x, verbose=0)
        top = get_predictions(out, top=5)

        for j in top[0]:
            if j[0:2] in cat_list:
                print(f"Detected car category: {j[0]}")
                return True

        print("⚠ Are you sure this is a picture of your car? Please take another picture (try a different angle or lighting) and try again.")
        return False

    except Exception as e:
        print(f"Error in car validation: {str(e)}")
        return False

def car_damage_gate(img_path, model, target_size=(224, 224)):
    print("Validating that damage exists...")
    try:
        if img_path.startswith(('http://', 'https://')):
            img_data = get_image_from_url(img_path)
            img = PILImage.open(img_data)
        else:
            img = PILImage.open(img_path)
        
        # Convert to RGB mode to ensure 3 channels
        img = img.convert('RGB')
        img = img.resize(target_size)
        x = np.array(img)
        x = np.expand_dims(x, axis=0)
        x = x / 255.0  # Normalize pixel values

        # Make prediction
        pred = model.predict(x, verbose=0)
        damage_probability = pred[0][0]

        print(f"Damage probability: {damage_probability:.2%}")

        # Check if this is the correct interpretation
        # If damage_probability represents "probability of NO damage",
        # then we want to return True when it's <= 0.5
        if damage_probability <= 0.5:
            print("✓ Validation complete - damage detected, proceeding to severity determination")
            return True
        else:
            print("⚠ No damage detected in this image. Please submit a picture that clearly shows the car damage.")
            print("Hint: Try zooming in to the damaged area, using a different angle or better lighting")
            return False

    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return False

def severity_estimator(img_path, model, target_size=(256, 256)):
    """Estimate the severity of car damage without saving temporary files"""
    print("Determining severity of damage...")

    try:
        if img_path.startswith(('http://', 'https://')):
            img_data = get_image_from_url(img_path)
            img = PILImage.open(img_data)
        else:
            img = PILImage.open(img_path)
        
        # Convert to RGB mode to ensure 3 channels
        img = img.convert('RGB')
        img = img.resize(target_size)
        x = np.array(img)
        x = np.expand_dims(x, axis=0)
        x = x / 255.0  # Normalize pixel values

        # Make prediction
        pred = model.predict(x, verbose=0)
        pred_label = np.argmax(pred, axis=1)

        # Map prediction to damage severity
        damage_levels = {
            0: 'Minor',
            1: 'Moderate',
            2: 'Severe'
        }

        result = damage_levels.get(pred_label[0], 'Unknown')
        print(f"Assessment: {result} damage to vehicle")
        print("Severity assessment complete.")
        return result

    except Exception as e:
        print(f"Error during severity assessment: {str(e)}")
        return None

def engine():
    while True:
        print("\n" + "="*50)
        print("CAR DAMAGE ASSESSMENT SYSTEM")
        print("="*50)
        print("Submit image link (or type 'exit' to quit)")
        img_path = input("Upload Image File Here: ")

        if img_path.lower() == 'exit':
            print("Exiting assessment engine.")
            return None

        # Don't clear output immediately to maintain better user experience
        print("\nProcessing image...\n")

        # Step 1: Verify this is a car
        g1 = car_categories_gate(img_path, first_gate)
        if not g1:
            print("\nCar validation failed. Please try again with a different image.")
            continue

        # Step 2: Verify damage exists
        g2 = car_damage_gate(img_path, second_gate)
        if not g2:
            print("\nDamage validation failed. Please try again with a clearer image of the damage.")
            continue

        # Step 3: Estimate damage severity
        severity = severity_estimator(img_path, severity_model)
        if severity:
            print(f"\n✅ FINAL ASSESSMENT: {severity.upper()} damage detected on vehicle")
            print("\n" + "-"*50)
            print("Would you like to assess another image? (Type 'exit' to quit or press Enter to continue)")
            choice = input()
            if choice.lower() == 'exit':
                print("Exiting assessment engine.")
                return None
            # Don't clear output here, it will be cleared at the next iteration
        else:
            print("\nError in severity assessment. Please try again.")

# To run the engine:
# engine()