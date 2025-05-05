import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid
import json
from authlib.integrations.flask_client import OAuth
import pickle
import numpy as np
import pandas as pd
from PIL import Image
import io
import joblib
from fpdf import FPDF
from dotenv import load_dotenv
import re
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image as ReportLabImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import requests
import secrets

# Import the ML models
from damage_estimator_engine import car_categories_gate, car_damage_gate, severity_estimator, first_gate, second_gate, severity_model
from price_estimation_ML import predict_car_price, scaler, model as ml_model, encoding_dicts, cars_data

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///car_estimations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Load .env file
load_dotenv()  # Load environment variables from .env file

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize SQLAlchemy
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize Login Manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Initialize OAuth - only if environment variables are set
oauth = OAuth(app)

# Setup Google OAuth provider if credentials are available
google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')

# Define the Google userinfo endpoint as a global variable to avoid attribute errors
GOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'

if google_client_id and google_client_secret:
    # Basic OAuth 2.0 configuration with minimal features
    google = oauth.register(
        name='google',
        client_id=google_client_id,
        client_secret=google_client_secret,
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        access_token_url='https://oauth2.googleapis.com/token',
        client_kwargs={
            'scope': 'email profile',
            'prompt': 'select_account',
        },
    )
    print(f"Google OAuth configured with client ID: {google_client_id[:10]}...")
else:
    google = None
    print("Google OAuth not configured. Check your .env file for GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.")

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    profile_pic = db.Column(db.String(200))
    provider = db.Column(db.String(50))
    provider_id = db.Column(db.String(100))
    auth_type = db.Column(db.String(50))
    auth_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    estimations = db.relationship('CarEstimation', backref='user', lazy=True)

class CarEstimation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_path = db.Column(db.String(200))
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    year = db.Column(db.Integer)
    condition = db.Column(db.String(50))
    mileage = db.Column(db.Float)
    gearbox = db.Column(db.String(50))
    fiscal_power = db.Column(db.Integer)
    fuel = db.Column(db.String(50))
    doors = db.Column(db.Integer)
    origin = db.Column(db.String(50))
    first_owner = db.Column(db.String(10))
    rear_camera = db.Column(db.Boolean, default=False)
    air_conditioning = db.Column(db.Boolean, default=False)
    sunroof = db.Column(db.Boolean, default=False)
    cd_mp3_bluetooth = db.Column(db.Boolean, default=False)
    speed_limiter = db.Column(db.Boolean, default=False)
    esp = db.Column(db.Boolean, default=False)
    leather_seats = db.Column(db.Boolean, default=False)
    alloy_wheels = db.Column(db.Boolean, default=False)
    cruise_control = db.Column(db.Boolean, default=False)
    central_locking = db.Column(db.Boolean, default=False)
    electric_windows = db.Column(db.Boolean, default=False)
    abs = db.Column(db.Boolean, default=False)
    navigation = db.Column(db.Boolean, default=False)
    onboard_computer = db.Column(db.Boolean, default=False)
    airbags = db.Column(db.Boolean, default=False)
    damage_severity = db.Column(db.String(50))
    base_price = db.Column(db.Float)
    adjusted_price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    pdf_report_path = db.Column(db.String(200))
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper Functions
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_pdf_report(estimation):
    pdf = FPDF()
    pdf.add_page()
    
    # Add header with logo
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Smart Car Price Estimation Report', 0, 1, 'C')
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)
    
    # Add car image
    if estimation.image_path and os.path.exists(estimation.image_path):
        try:
            pdf.image(estimation.image_path, x=10, y=40, w=80)
        except Exception as e:
            print(f"Error adding image to PDF: {str(e)}")
            # Add a placeholder
            pdf.set_xy(10, 40)
            pdf.set_fill_color(200, 200, 200)
            pdf.rect(10, 40, 80, 60, style='F')
            pdf.set_xy(25, 65)
            pdf.set_font('Arial', 'I', 12)
            pdf.cell(50, 10, 'Image not available', 0, 1, 'C')
    else:
        # Add a placeholder
        pdf.set_xy(10, 40)
        pdf.set_fill_color(200, 200, 200)
        pdf.rect(10, 40, 80, 60, style='F')
        pdf.set_xy(25, 65)
        pdf.set_font('Arial', 'I', 12)
        pdf.cell(50, 10, 'Image not available', 0, 1, 'C')
    
    # Car details section
    pdf.set_xy(100, 40)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Car Details', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.set_xy(100, 50)
    pdf.cell(40, 10, 'Brand:', 0, 0)
    pdf.cell(0, 10, estimation.brand, 0, 1)
    
    pdf.set_xy(100, 60)
    pdf.cell(40, 10, 'Model:', 0, 0)
    pdf.cell(0, 10, estimation.model, 0, 1)
    
    pdf.set_xy(100, 70)
    pdf.cell(40, 10, 'Year:', 0, 0)
    pdf.cell(0, 10, str(estimation.year), 0, 1)
    
    pdf.set_xy(100, 80)
    pdf.cell(40, 10, 'Condition:', 0, 0)
    pdf.cell(0, 10, estimation.condition, 0, 1)
    
    pdf.set_xy(100, 90)
    pdf.cell(40, 10, 'Mileage:', 0, 0)
    pdf.cell(0, 10, f"{estimation.mileage} km", 0, 1)
    
    # Price section
    pdf.ln(20)
    pdf.set_xy(10, 130)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Price Estimation', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.set_xy(10, 140)
    pdf.cell(80, 10, 'Damage Severity:', 0, 0)
    
    # Set color based on damage level
    if estimation.damage_severity == 'Minor':
        pdf.set_text_color(0, 150, 0)  # Green
    elif estimation.damage_severity == 'Moderate':
        pdf.set_text_color(255, 165, 0)  # Orange
    elif estimation.damage_severity == 'Severe':
        pdf.set_text_color(255, 0, 0)  # Red
    else:
        pdf.set_text_color(0, 100, 255)  # Blue for no damage
        
    pdf.cell(0, 10, estimation.damage_severity if estimation.damage_severity else 'No Damage Detected', 0, 1)
    pdf.set_text_color(0, 0, 0)  # Reset text color
    
    if estimation.base_price > 0:
        pdf.set_xy(10, 150)
        pdf.cell(80, 10, 'Base Price Estimation:', 0, 0)
        pdf.cell(0, 10, f"{estimation.base_price:,.2f} DH", 0, 1)
        
        pdf.set_xy(10, 160)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(80, 10, 'Final Adjusted Price:', 0, 0)
        pdf.cell(0, 10, f"{estimation.adjusted_price:,.2f} DH", 0, 1)
    else:
        pdf.set_xy(10, 150)
        pdf.set_text_color(255, 0, 0)  # Red for error
        pdf.cell(0, 10, 'ML Model Error: Unable to calculate price', 0, 1)
        pdf.set_text_color(0, 0, 0)  # Reset text color
        
        pdf.set_xy(10, 160)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 10, 'Please try again with different parameters or contact support.', 0, 1)
    
    # Footer
    pdf.set_y(-30)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0, 10, f'Generated on {estimation.created_at.strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
    pdf.cell(0, 10, 'Thank you for using our Smart Car Price Estimation service!', 0, 1, 'C')
    
    # Save the PDF
    pdf_filename = f"report_{estimation.id}_{uuid.uuid4().hex[:8]}.pdf"
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
    pdf.output(pdf_path)
    
    return pdf_path

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login/google')
def login_google():
    if google is None:
        flash('Google login is not configured', 'danger')
        return redirect(url_for('login'))
    # Use hardcoded HTTPS URL for production or specific domains
    if request.host == '127.0.0.1:5000':
        # For local development 
        redirect_uri = url_for('authorize_google', _external=True)
    else:
        # For production - hardcode the exact URL that's registered in Google Console
        redirect_uri = 'https://your-registered-domain.com/login/google/authorize'
        
    print(f"Redirecting to Google with URI: {redirect_uri}")
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/authorize')
def authorize_google():
    if google is None:
        flash('Google login is not configured', 'danger')
        return redirect(url_for('login'))
        
    try:
        # Get the token using Authlib
        token = google.authorize_access_token()
        if not token:
            flash('Failed to get token from Google', 'danger')
            return redirect(url_for('login'))
            
        # Get access token
        access_token = token.get('access_token')
        if not access_token:
            flash('Access token not found in the response', 'danger')
            return redirect(url_for('login'))
        
        # Use direct request with requests library to get user info
        headers = {'Authorization': f'Bearer {access_token}'}
        
        print(f"Making request to: {GOOGLE_USERINFO_URL} with token: {access_token[:10]}...")
        
        response = requests.get(GOOGLE_USERINFO_URL, headers=headers)
        if response.status_code != 200:
            flash(f'Failed to get user info: HTTP {response.status_code}', 'danger')
            print(f"Error response: {response.text}")
            return redirect(url_for('login'))
            
        userinfo = response.json()
        print(f"Google userinfo: {userinfo}")
        
        if 'email' not in userinfo:
            flash('Email not found in Google response', 'danger')
            print(f"No email in response: {userinfo}")
            return redirect(url_for('login'))
            
        # Look up existing user or create a new one
        user = User.query.filter_by(email=userinfo['email']).first()
        if not user:
            # Google's v3 API uses 'sub' for the user ID
            user_id = userinfo.get('sub', 'unknown')
            
            user = User(
                name=userinfo.get('name', 'Google User'),
                email=userinfo['email'],
                auth_type='google',
                auth_id=user_id,
                profile_pic=userinfo.get('picture')
            )
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully!', 'success')
        
        # Log the user in
        login_user(user)
        next_page = session.pop('next', None)
        return redirect(next_page or url_for('index'))
        
    except Exception as e:
        flash(f"Error during Google authentication: {str(e)}", 'danger')
        print(f"Google OAuth Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    estimations = CarEstimation.query.filter_by(user_id=current_user.id).order_by(CarEstimation.created_at.desc()).all()
    return render_template('dashboard.html', estimations=estimations)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/history')
@login_required
def history():
    # This is just an alias for dashboard for now
    return redirect(url_for('dashboard'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/estimate', methods=['GET', 'POST'])
@login_required
def estimate():
    if request.method == 'POST':
        try:
            print("Form submitted, processing estimation...")
            
            # Validation - ensure required fields are present
            required_fields = ['brand', 'model', 'year', 'condition', 'mileage']
            for field in required_fields:
                if not request.form.get(field):
                    flash(f"Missing required field: {field}", "danger")
                    return redirect(url_for('estimate'))
            
            # Get form data
            brand = request.form.get('brand')
            model = request.form.get('model')
            year = request.form.get('year')
            condition = request.form.get('condition')
            mileage = request.form.get('mileage')
            gearbox = request.form.get('gearbox')  # Default if not provided
            fiscal_power = request.form.get('fiscal_power')  # Default value
            fuel = request.form.get('fuel')  # Default value
            doors = request.form.get('doors')  # Default value
            origin = request.form.get('origin')  # Default value
            first_owner = request.form.get('first_owner')  # Default value
            
            print(f"Processing car: {brand} {model} {year}, condition: {condition}")
            
            # Extract features
            features = {
                'rear_camera': 'rear_camera' in request.form,
                'air_conditioning': 'air_conditioning' in request.form,
                'sunroof': 'sunroof' in request.form,
                'cd_mp3_bluetooth': 'cd_mp3_bluetooth' in request.form,
                'speed_limiter': 'speed_limiter' in request.form,
                'esp': 'esp' in request.form,
                'leather_seats': 'leather_seats' in request.form,
                'alloy_wheels': 'alloy_wheels' in request.form,
                'cruise_control': 'cruise_control' in request.form,
                'central_locking': 'central_locking' in request.form,
                'electric_windows': 'electric_windows' in request.form,
                'abs': 'abs' in request.form,
                'navigation': 'navigation' in request.form,
                'onboard_computer': 'onboard_computer' in request.form,
                'airbags': 'airbags' in request.form
            }
            
            # Save the image if provided
            image_path = None
            damage_severity = 'Not Assessed'
            
            if 'car_image' in request.files and request.files['car_image'].filename:
                image = request.files['car_image']
                if allowed_file(image.filename):
                    filename = secure_filename(f"{uuid.uuid4().hex}_{image.filename}")
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    image.save(image_path)
                    print(f"Image saved to {image_path}")
                    
                    # Process image for damage detection
                    try:
                        # No need for image_obj, all functions expect a file path
                        is_car = car_categories_gate(image_path, first_gate)
                        print(f"Image classification: {is_car}")
                        
                        if is_car:  # The function returns True if it's a car
                            is_damaged = car_damage_gate(image_path, second_gate)
                            print(f"Damage detection: {is_damaged}")
                            
                            if is_damaged:  # The function returns True if damage is detected
                                damage_severity = severity_estimator(image_path, severity_model)
                                print(f"Damage severity: {damage_severity}")
                                
                                # Make sure damage_severity is one of the expected values
                                if damage_severity not in ['Minor', 'Moderate', 'Severe']:
                                    # If it's None or some unexpected value, default to Minor
                                    print(f"Warning: Unexpected damage_severity '{damage_severity}'. Defaulting to 'Minor'")
                                    damage_severity = 'Minor'
                            else:
                                damage_severity = 'None'
                        else:
                            damage_severity = 'Unknown (Not a car)'
                    except Exception as e:
                        print(f"Error in damage detection: {str(e)}")
                        damage_severity = 'Error in processing'
            
            # Set fallback default base price
            base_price = 0  # Default to 0 to indicate error
            
            # Predict base price using ML model
            try:
                print("Predicting car price...")
                # Directly use the ML model with proper parameters
                base_price = predict_car_price(
                    brand, model, int(year), 
                    condition, int(mileage), gearbox, 
                    int(fiscal_power), fuel,
                    int(float(doors)), origin, first_owner,
                    int(features['rear_camera']),
                    int(features['air_conditioning']),
                    int(features['sunroof']),
                    int(features['cd_mp3_bluetooth']),
                    int(features['speed_limiter']),
                    int(features['esp']),
                    int(features['leather_seats']),
                    int(features['alloy_wheels']),
                    int(features['cruise_control']),
                    int(features['central_locking']),
                    int(features['electric_windows']),
                    int(features['abs']),
                    int(features['navigation']),
                    int(features['onboard_computer']),
                    int(features['airbags']),
                    scaler, ml_model, encoding_dicts
                )
                print(f"Base price prediction: {base_price:,.2f} MAD")
                
                # If price is 0 or negative, set to 0 to indicate an error
                if base_price <= 0:
                    print("Warning: ML model returned zero or negative price. Setting to 0 to indicate error.")
                    base_price = 0
                    
            except Exception as e:
                print(f"Error in price prediction: {str(e)}")
                flash(f"Error in price prediction: {str(e)}", "danger")
                import traceback
                traceback.print_exc()
                # Set a placeholder price if the model fails
                base_price = 0
            
            # Adjust price based on damage severity
            adjusted_price = base_price
            if base_price > 0:  # Only adjust if base price is valid
                if damage_severity == 'Minor':
                    adjusted_price = base_price * 0.90  # 10% discount
                elif damage_severity == 'Moderate':
                    adjusted_price = base_price * 0.75  # 25% discount
                elif damage_severity == 'Severe':
                    adjusted_price = base_price * 0.60  # 40% discount
            
            print(f"Final adjusted price: {adjusted_price} MAD (damage severity: {damage_severity})")
            
            # Create new estimation record
            estimation = CarEstimation(
                user_id=current_user.id,
                image_path=image_path,
                brand=brand,
                model=model,
                year=int(year) if year else None,
                condition=condition,
                mileage=float(mileage) if mileage else None,
                gearbox=gearbox,
                fiscal_power=int(fiscal_power) if fiscal_power else None,
                fuel=fuel,
                doors=int(float(doors)) if doors else None,
                origin=origin,
                first_owner=first_owner,
                rear_camera=features['rear_camera'],
                air_conditioning=features['air_conditioning'],
                sunroof=features['sunroof'],
                cd_mp3_bluetooth=features['cd_mp3_bluetooth'],
                speed_limiter=features['speed_limiter'],
                esp=features['esp'],
                leather_seats=features['leather_seats'],
                alloy_wheels=features['alloy_wheels'],
                cruise_control=features['cruise_control'],
                central_locking=features['central_locking'],
                electric_windows=features['electric_windows'],
                abs=features['abs'],
                navigation=features['navigation'],
                onboard_computer=features['onboard_computer'],
                airbags=features['airbags'],
                damage_severity=damage_severity,
                base_price=base_price,
                adjusted_price=adjusted_price
            )
            
            print("Saving estimation to database...")
            db.session.add(estimation)
            db.session.commit()
            print(f"Estimation saved with ID: {estimation.id}")
            
            # Generate PDF report
            try:
                print("Generating PDF report...")
                pdf_path = generate_pdf_report(estimation)
                estimation.pdf_report_path = pdf_path
                db.session.commit()
                print(f"PDF report saved to {pdf_path}")
            except Exception as e:
                print(f"Error generating PDF: {str(e)}")
            
            flash("Your car valuation has been successfully processed!", "success")
            return redirect(url_for('estimation_result', estimation_id=estimation.id))
            
        except Exception as e:
            import traceback
            print(f"Error processing estimation: {str(e)}")
            traceback.print_exc()
            flash(f"Error processing your request: {str(e)}", "danger")
            return redirect(url_for('estimate'))
    
    # For GET request, use data from the cars_data dataset
    try:
        # Get unique values from the DataFrame
        df = cars_data
        
        # Map column names to form field names
        column_mapping = {
            'brand': 'Brand',
            'model': 'Model',
            'gearbox': 'Gearbox',
            'fuel': 'Fuel',
            'doors': 'Number of Doors',
            'origin': 'Origin',
            'first_owner': 'First Owner',
            'fiscal_power': 'Fiscal Power'
        }
        
        # Get unique values for each dropdown field
        brands = sorted(df['Brand'].unique().tolist())
        models = sorted(df['Model'].unique().tolist())
        years = sorted(list(range(2023, 1990, -1)))  # Keep years as generated range
        conditions = ['Excellent', 'Good', 'Fair', 'Poor']  # Keep predefined conditions
        gearboxes = sorted(df['Gearbox'].unique().tolist())
        fuels = sorted(df['Fuel'].unique().tolist())
        origins = sorted(df['Origin'].unique().tolist())
        
        # Handle numeric door values (convert from float to int)
        doors_values = df['Number of Doors'].unique().tolist()
        doors = [int(d) for d in doors_values if not pd.isna(d)]
        if not doors:  # If no valid door values found
            doors = [5]  # Default to 5 doors
            
        # Get first owner values
        first_owners = sorted(df['First Owner'].unique().tolist())
        
        # Create brand-models dictionary for the frontend
        brand_models = {}
        
        # Populate brand->model relationships
        for brand in brands:
            brand_models[brand] = sorted(df[df['Brand'] == brand]['Model'].unique().tolist())
        
        # Define dropdown relationships structure expected by the frontend
        dropdown_relationships = {
            'brand': ['model']
        }
        
        print(f"Loaded dropdown data: {len(brands)} brands, {len(models)} models")
        print(f"Door options: {doors}")
        print(f"First owner options: {first_owners}")
    except Exception as e:
        print(f"Error loading car data: {str(e)}")
        import traceback
        traceback.print_exc()
        # Fallback values in case of error
        brands = []
        models = []
        years = list(range(2023, 1990, -1))
        conditions = ['Excellent', 'Good', 'Fair', 'Poor']
        gearboxes = []
        fuels = []
        origins = []
        doors = [5]
        first_owners = ['Yes', 'No', 'Unknown']
        brand_models = {}
        dropdown_relationships = {'brand': ['model']}
    
    return render_template('estimate.html', 
                          brands=brands,
                          models=models,
                          years=years,
                          conditions=conditions,
                          gearboxes=gearboxes,
                          fuels=fuels,
                          origins=origins,
                          doors=doors,
                          first_owners=first_owners,
                          dropdown_relationships=dropdown_relationships,
                          brand_models=brand_models)

@app.route('/api/models/<brand>')
def get_models(brand):
    """Get models for a specific brand"""
    try:
        # Use the actual dataset to get models for the selected brand
        df = cars_data
        if brand in df['Brand'].values:
            models = sorted(df[df['Brand'] == brand]['Model'].unique().tolist())
            return jsonify(models)
        return jsonify([])
    except Exception as e:
        print(f"Error getting models for brand {brand}: {str(e)}")
        return jsonify([])

@app.route('/estimation/<int:estimation_id>')
@login_required
def estimation_result(estimation_id):
    estimation = CarEstimation.query.get_or_404(estimation_id)
    
    # Verify that this estimation belongs to the current user
    if estimation.user_id != current_user.id:
        flash("You don't have permission to view this estimation")
        return redirect(url_for('dashboard'))
        
    return render_template('result.html', estimation=estimation)

@app.route('/download_report/<int:estimation_id>')
@login_required
def download_report(estimation_id):
    estimation = CarEstimation.query.get_or_404(estimation_id)
    
    # Verify that this estimation belongs to the current user
    if estimation.user_id != current_user.id:
        flash("You don't have permission to download this report")
        return redirect(url_for('dashboard'))
    
    # If the base price is 0, notify the user about the ML error
    if estimation.base_price == 0:
        flash("Cannot generate PDF report because the ML model encountered an error during price prediction.", "warning")
        return redirect(url_for('estimation_result', estimation_id=estimation.id))
    
    # If the PDF doesn't exist, generate it
    if not estimation.pdf_report_path or not os.path.exists(estimation.pdf_report_path):
        try:
            pdf_path = generate_pdf_report(estimation)
            estimation.pdf_report_path = pdf_path
            db.session.commit()
            print(f"Generated new PDF report at {pdf_path}")
        except Exception as e:
            print(f"Error generating PDF report: {str(e)}")
            import traceback
            traceback.print_exc()
            flash(f"Error generating PDF report: {str(e)}", "danger")
            return redirect(url_for('estimation_result', estimation_id=estimation.id))
    
    # Get the filename for the download
    filename = os.path.basename(estimation.pdf_report_path)
    download_name = f"{estimation.brand}_{estimation.model}_{estimation.year}_Valuation.pdf"
    
    try:
        # Return the PDF file for download
        return send_file(
            estimation.pdf_report_path, 
            mimetype='application/pdf',
            as_attachment=True,
            download_name=download_name
        )
    except Exception as e:
        print(f"Error sending PDF file: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f"Error downloading the report: {str(e)}", "danger")
        return redirect(url_for('estimation_result', estimation_id=estimation.id))


@app.route('/api/filtered-options')
def get_filtered_options():
    """Get filtered options for dropdowns based on other selected values"""
    try:
        # Get request parameters
        target_field = request.args.get('target_field')
        
        # Map frontend field names to dataset column names
        column_mapping = {
            'brand': 'Brand',
            'model': 'Model',
            'gearbox': 'Gearbox',
            'fuel': 'Fuel',
            'doors': 'Number of Doors',
            'origin': 'Origin',
            'first_owner': 'First Owner',
            'fiscal_power': 'Fiscal Power'
        }
        
        # Map target field to its column name
        column_name = column_mapping.get(target_field, target_field)
        
        # Get filter parameters
        filters = {}
        for key, value in request.args.items():
            if key != 'target_field' and value:
                # Map the filter key to its column name
                column_key = column_mapping.get(key, key)
                filters[column_key] = value
        
        # Default empty response
        options = []
        
        # Use the actual dataset to filter options
        df = cars_data
        
        # Apply all filters
        for field, value in filters.items():
            if field in df.columns:
                # Handle numeric fields that might need type conversion
                if field == 'Number of Doors' and value.replace('.', '', 1).isdigit():
                    df = df[df[field] == float(value)]
                else:
                    df = df[df[field] == value]
        
        # Get unique values for the target field
        if column_name in df.columns:
            # Handle special case for numeric fields (like doors)
            if column_name == 'Number of Doors':
                door_values = df[column_name].unique().tolist()
                options = [int(d) for d in door_values if not pd.isna(d)]
            else:
                options = sorted(df[column_name].unique().tolist())
                
            # If we're looking for first_owner and got empty results,
            # provide default options
            if target_field == 'first_owner' and not options:
                options = ['Yes', 'No', 'Unknown']
            
            print(f"Found {len(options)} options for {target_field} (column: {column_name})")
        else:
            print(f"Column {column_name} not found in dataframe. Available columns: {df.columns.tolist()}")
            
            # Handle special case for first_owner if column not found
            if target_field == 'first_owner':
                options = ['Yes', 'No', 'Unknown']
        
        return jsonify(options)
    except Exception as e:
        print(f"Error getting filtered options: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Provide fallback values for key fields if there's an error
        if target_field == 'first_owner':
            return jsonify(['Yes', 'No', 'Unknown'])
        
        return jsonify([])

@app.route('/debug_form', methods=['POST'])
def debug_form():
    """Debug endpoint to check form submission data"""
    if not request.form:
        return jsonify({
            'error': 'No form data received',
            'message': 'Make sure the form is submitted with proper data'
        }), 400
    
    # Collect all form data
    form_data = {}
    for key in request.form:
        form_data[key] = request.form.get(key)
    
    # Check for file uploads
    file_info = {}
    for key in request.files:
        file = request.files[key]
        file_info[key] = {
            'filename': file.filename,
            'content_type': file.content_type if hasattr(file, 'content_type') else 'unknown',
            'size': 'unknown'  # Getting size would require reading the file
        }
    
    # Also include some technical info to help diagnose issues
    debug_info = {
        'form_data': form_data,
        'file_uploads': file_info,
        'headers': dict(request.headers),
        'content_type': request.content_type,
        'content_length': request.content_length,
        'mimetype': request.mimetype,
        'has_required_fields': {
            'brand': 'brand' in request.form,
            'model': 'model' in request.form,
            'year': 'year' in request.form,
            'condition': 'condition' in request.form,
            'mileage': 'mileage' in request.form
        }
    }
    
    return jsonify(debug_info)


@app.errorhandler(Exception)
def handle_error(e):
    """Global error handler for all exceptions"""
    print(f"Unhandled exception: {str(e)}")
    import traceback
    traceback.print_exc()
    
    # Check if this is a known HTTP error
    code = 500
    if hasattr(e, 'code'):
        code = e.code
    
    # For API requests, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), code
    
    # For web requests, show error page with flash message
    flash(f"An error occurred: {str(e)}", "danger")
    
    # Redirect to appropriate page based on error
    if code == 404:
        return render_template('404.html'), 404
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 