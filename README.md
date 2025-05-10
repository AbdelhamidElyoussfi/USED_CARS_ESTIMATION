# Smart Car Price Estimation Web Application

A full-stack web application that provides car price estimation based on damage analysis and car features using machine learning models.

## Templates

# Home page before login
![image](https://github.com/user-attachments/assets/77c683cd-11b2-4783-94ce-ae4861555af5)

# Login 
![image](https://github.com/user-attachments/assets/236f6c4d-5770-4012-9fb1-71a4f9bf377a)

# Home page after login
![image](https://github.com/user-attachments/assets/56bbbc9f-7ed0-45cb-8f6a-e9a08376229d)

# Estimate from
![image](https://github.com/user-attachments/assets/afc15a0c-3062-4590-98a4-7369e93a01bc)

# Result damage
![image](https://github.com/user-attachments/assets/08c56074-557b-4cc1-ad98-2ad7b1ebc83f)

# Dashboard 
![image](https://github.com/user-attachments/assets/6e8c599e-4be5-4d19-87ed-3de4a5dceda5)

# About
![image](https://github.com/user-attachments/assets/cc56194a-2234-4189-ba16-72cf142652c6)

# Profile
![image](https://github.com/user-attachments/assets/27f4a8b8-fb15-4cdb-b45c-1f75ea8823bc)


## Features

- 🔐 User authentication with Google OAuth 2.0
- 🖼️ Image upload with drag-and-drop support and animated preview
- 🧠 Integration of multiple machine learning models for:
  - Car type validation
  - Damage detection
  - Damage severity analysis
  - Price prediction
- 💥 Automatic damage severity classification (Minor, Moderate, Severe)
- 📋 User dashboard with past estimation history
- 📥 PDF report generation for each estimation
- 🎨 Modern, responsive UI with animations and dark mode support

## Tech Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login, Authlib
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Machine Learning**: TensorFlow, Keras, Scikit-learn
- **Database**: SQLite (can be easily changed to other databases)
- **Authentication**: OAuth 2.0 (Google, Facebook)

## Installation

1. Clone the repository:
```
git clone <repository-url>
cd smart-car-price-estimator
```

2. Create and activate a virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Set environment variables (create a `.env` file in the project root):
```
SECRET_KEY=your-secure-secret-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

5. Initialize the database:
```
flask db init
flask db migrate
flask db upgrade
```

6. Run the application:
```
flask run
```

The application will be available at `http://localhost:5000`

## Project Structure

```
.
├── app.py                  # Main Flask application
├── damage_analyzer_engine.py  # Damage analysis ML model
├── price_estimation_ML.py  # Price estimation ML model
├── requirements.txt        # Python dependencies
├── models/                 # ML & deep learning models
├── static/                 # Static assets
│   ├── css/                # CSS styles
│   ├── js/                 # JavaScript files
│   └── uploads/            # User uploaded files (images, PDFs)
└── templates/              # HTML templates
    ├── base.html           # Base template
    ├── index.html          # Landing page
    ├── login.html          # Login page
    ├── dashboard.html      # User dashboard
    ├── estimate.html       # Estimation form
    └── result.html         # Estimation result
```

## ML Models

The application uses several machine learning models:

1. **First Gate (VGG16)**: Validates that the uploaded image is a car
2. **Second Gate (Damage Detection)**: Verifies the car has damage
3. **Severity Estimator**: Classifies damage as Minor, Moderate, or Severe
4. **Price Estimator**: Predicts car price based on features and damage severity

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
