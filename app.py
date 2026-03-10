from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory, session
import cv2
import numpy as np
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session

# Create uploads folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Disease information
DISEASE_INFO = {
    "leaf_spot": {
        "name": "Leaf Spot Disease",
        "description": "A common fungal disease that appears as spots on leaves.",
        "symptoms": "🌿 Yellow or brown spots on leaves\n🌿 Spots may have dark borders\n🌿 Leaves may yellow and drop",
        "treatment": "💊 Remove affected leaves\n💊 Apply neem oil spray\n💊 Use copper fungicide",
        "prevention": "🛡️ Water at base\n🛡️ Good air circulation\n🛡️ Clean fallen leaves"
    },
    "early_blight": {
        "name": "Early Blight",
        "description": "Fungal disease common in tomatoes and potatoes.",
        "symptoms": "🌿 Brown spots with concentric rings\n🌿 Yellowing around spots\n🌿 Lower leaves affected",
        "treatment": "💊 Apply copper fungicide\n💊 Remove infected leaves\n💊 Mulch around plants",
        "prevention": "🛡️ Rotate crops\n🛡️ Water at base\n🛡️ Stake plants"
    },
    "powdery_mildew": {
        "name": "Powdery Mildew",
        "description": "Fungal disease with white powdery coating.",
        "symptoms": "🌿 White or gray powdery spots\n🌿 Leaves may curl\n🌿 Stunted growth",
        "treatment": "💊 Spray baking soda\n💊 Apply neem oil\n💊 Remove infected leaves",
        "prevention": "🛡️ Good air flow\n🛡️ Avoid overcrowding\n🛡️ Water in morning"
    },
    "healthy": {
        "name": "Healthy Plant",
        "description": "Your plant appears healthy with no signs of disease.",
        "symptoms": "🌿 Normal green color\n🌿 No spots or lesions\n🌿 Healthy growth",
        "treatment": "💊 No treatment needed\n💊 Continue regular care",
        "prevention": "🛡️ Regular watering\n🛡️ Proper sunlight\n🛡️ Monitor regularly"
    }
}

@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('home'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('home'))
    
    # Save file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"leaf_{timestamp}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    # Analyze image
    img = cv2.imread(filepath)
    if img is None:
        return redirect(url_for('home'))
        
    img = cv2.resize(img, (500, 500))
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Color detection
    lower_yellow = np.array([20, 80, 80])
    upper_yellow = np.array([35, 255, 255])
    lower_brown = np.array([10, 80, 20])
    upper_brown = np.array([25, 255, 200])
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])
    
    total = 500 * 500
    
    yellow = cv2.countNonZero(cv2.inRange(hsv, lower_yellow, upper_yellow)) / total * 100
    brown = cv2.countNonZero(cv2.inRange(hsv, lower_brown, upper_brown)) / total * 100
    white = cv2.countNonZero(cv2.inRange(hsv, lower_white, upper_white)) / total * 100
    green = cv2.countNonZero(cv2.inRange(hsv, lower_green, upper_green)) / total * 100
    
    # Decision logic
    if white > 8:
        disease = 'powdery_mildew'
        conf = min(white * 4, 98)
    elif yellow > 15:
        disease = 'leaf_spot'
        conf = min(yellow * 3, 98)
    elif brown > 12:
        disease = 'early_blight'
        conf = min(brown * 3, 98)
    elif green > 70:
        disease = 'healthy'
        conf = green
    else:
        disease = 'healthy'
        conf = 70
    
    info = DISEASE_INFO.get(disease, DISEASE_INFO['healthy'])
    
    # Store in session
    session['result'] = {
        'disease_name': info['name'],
        'confidence': round(conf, 1),
        'is_healthy': disease == 'healthy',
        'description': info['description'],
        'symptoms': info['symptoms'],
        'treatment': info['treatment'],
        'prevention': info['prevention'],
        'analysis': {
            'green': round(green, 1),
            'yellow': round(yellow, 1),
            'brown': round(brown, 1),
            'white': round(white, 1)
        },
        'filename': filename
    }
    
    return redirect(url_for('process'))

@app.route('/process')
def process():
    return render_template('process.html')

@app.route('/get_results')
def get_results():
    if 'result' in session:
        return jsonify(session['result'])
    return jsonify({'error': 'No results found'})

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🌱 PLANT DISEASE DETECTOR")
    print("="*50)
    print("✅ Server running!")
    print("🌐 Open: http://127.0.0.1:5000")
    print("="*50)
    app.run(debug=True, port=5000)