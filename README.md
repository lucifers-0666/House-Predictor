# 🏠 House Price Predictor

A machine learning-powered web application that predicts housing prices based on various features using Flask and scikit-learn.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.2-green.svg)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.7.2-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Table of Contents
- [Features](#features)
- [Demo](#demo)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Model Training](#model-training)
- [Technologies Used](#technologies-used)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- 🎯 **Accurate Predictions**: Machine learning model trained on housing data
- 🎨 **Modern UI**: Clean and responsive interface with dark/light mode
- 📊 **Interactive Forms**: Easy-to-use input forms for housing features
- 📈 **Real-time Predictions**: Instant price predictions based on input
- 💾 **Prediction History**: Track and review past predictions
- 🌙 **Dark Mode**: Eye-friendly dark theme option
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile devices

## 🎬 Demo

### Input Features:
- Median Income
- House Age
- Average Rooms
- Average Bedrooms
- Population
- Average Occupancy
- Latitude & Longitude

### Output:
- Predicted house price in USD

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/lucifers-0666/House-Predictor.git
cd House-Predictor
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv housing-env
housing-env\Scripts\activate

# macOS/Linux
python3 -m venv housing-env
source housing-env/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Train the Model (Optional)
If you want to retrain the model:
```bash
python train_model.py
```

### Step 5: Run the Application
```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000`

## 📖 Usage

1. **Open your browser** and navigate to `http://127.0.0.1:5000`
2. **Fill in the housing features** in the form:
   - Median Income (in tens of thousands)
   - House Age (in years)
   - Average Rooms per household
   - Average Bedrooms per household
   - Population in the area
   - Average Occupancy
   - Latitude and Longitude coordinates
3. **Click "Predict Price"** to get the estimated house price
4. **View your prediction history** in the sidebar

## 📁 Project Structure

```
House-Predictor/
├── app.py                      # Flask application
├── train_model.py              # Model training script
├── requirements.txt            # Python dependencies
├── model.pkl                   # Trained ML model
├── scaler.pkl                  # Feature scaler
├── feature_names.pkl           # Feature names list
├── README.md                   # Project documentation
├── .gitignore                  # Git ignore file
│
├── templates/                  # HTML templates
│   └── index.html             # Main page template
│
├── static/                     # Static files
│   ├── css/
│   │   └── style.css          # Stylesheet
│   └── js/
│       └── script.js          # JavaScript logic
│
└── housing-env/               # Virtual environment (not in Git)
```

## 🧠 Model Training

The model is trained using the California Housing Dataset with the following steps:

1. **Data Loading**: Load the California Housing dataset
2. **Feature Scaling**: Standardize features using StandardScaler
3. **Model Training**: Train a Random Forest Regressor
4. **Model Evaluation**: Calculate R² score and performance metrics
5. **Model Saving**: Save model, scaler, and feature names as pickle files

### Training the Model:
```bash
python train_model.py
```

This will generate:
- `model.pkl` - Trained Random Forest model
- `scaler.pkl` - StandardScaler for feature normalization
- `feature_names.pkl` - List of feature names

## 🛠️ Technologies Used

### Backend
- **Flask** - Web framework
- **scikit-learn** - Machine learning library
- **pandas** - Data manipulation
- **numpy** - Numerical computing
- **joblib** - Model serialization

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling
- **JavaScript** - Interactivity
- **Responsive Design** - Mobile-friendly layout

### Machine Learning
- **Random Forest Regressor** - Prediction model
- **StandardScaler** - Feature normalization
- **California Housing Dataset** - Training data

## 🔌 API Endpoints

### `GET /`
- Returns the main HTML page

### `POST /predict`
- **Description**: Predicts house price based on input features
- **Content-Type**: `application/json`
- **Request Body**:
```json
{
  "median_income": 3.5,
  "house_age": 15,
  "avg_rooms": 6,
  "avg_bedrooms": 1.2,
  "population": 1500,
  "avg_occupancy": 3.5,
  "latitude": 34.05,
  "longitude": -118.25
}
```
- **Response**:
```json
{
  "prediction": 250000.50,
  "features": { ... }
}
```

### `GET /model-info`
- **Description**: Returns information about the trained model
- **Response**:
```json
{
  "model_type": "RandomForestRegressor",
  "features": ["median_income", "house_age", ...],
  "n_features": 8
}
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**lucifers-0666**
- GitHub: [@lucifers-0666](https://github.com/lucifers-0666)
- Project Link: [https://github.com/lucifers-0666/House-Predictor](https://github.com/lucifers-0666/House-Predictor)

## 🙏 Acknowledgments

- California Housing Dataset from scikit-learn
- Flask documentation and community
- All contributors and supporters

## 📞 Support

If you have any questions or issues, please open an issue on GitHub.

---

⭐ **Star this repository if you find it helpful!** ⭐