# app.py - Advanced Flask Backend with PDF Export

from flask import Flask, render_template, request, jsonify, send_file
import pickle
import numpy as np
import pandas as pd
import json
from datetime import datetime
import csv
import io
import logging
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

predictions_history = []

# Load model at startup
print("Loading ML model and scaler...")
try:
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    with open('feature_names.pkl', 'rb') as f:
        feature_names = pickle.load(f)
    print("✓ Model loaded successfully!")
except FileNotFoundError as e:
    print(f"✗ Error: {e}")
    model = None

# ============= ROUTES =============

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        logger.info(f"Prediction request: {data}")
        
        features = [
            float(data.get('MedInc', 0)),
            float(data.get('HouseAge', 0)),
            float(data.get('AveRooms', 0)),
            float(data.get('AveBedrms', 0)),
            float(data.get('Population', 0)),
            float(data.get('AveOccup', 0)),
            float(data.get('Latitude', 0)),
            float(data.get('Longitude', 0))
        ]
        
        if not all(isinstance(f, float) for f in features):
            return jsonify({'error': 'Invalid input.'}), 400
        
        features_df = pd.DataFrame([features], columns=feature_names)
        features_scaled = scaler.transform(features_df)
        
        prediction = model.predict(features_scaled)[0]
        predicted_price = prediction * 100000
        
        feature_importance = dict(zip(feature_names, model.feature_importances_))
        top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]
        
        prediction_record = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'input': data,
            'prediction': round(predicted_price, 2),
            'price_value': prediction
        }
        predictions_history.append(prediction_record)
        
        logger.info(f"Prediction: ${predicted_price:,.2f}")
        
        # Generate insights
        insights = generateInsights(feature_importance, data, predicted_price)
        
        return jsonify({
            'success': True,
            'prediction': round(predicted_price, 2),
            'median_house_value': round(prediction, 4),
            'top_features': [{'name': f[0], 'importance': round(f[1], 4)} for f in top_features],
            'timestamp': prediction_record['timestamp'],
            'insights': insights
        })
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

@app.route('/api/batch-predict', methods=['POST'])
def batch_predict():
    try:
        data = request.get_json()
        houses = data.get('houses', [])
        
        if not houses or len(houses) == 0:
            return jsonify({'error': 'No houses provided'}), 400
        
        if len(houses) > 100:
            return jsonify({'error': 'Maximum 100 houses per request'}), 400
        
        results = []
        
        for idx, house in enumerate(houses):
            try:
                features = [
                    float(house.get('MedInc', 0)),
                    float(house.get('HouseAge', 0)),
                    float(house.get('AveRooms', 0)),
                    float(house.get('AveBedrms', 0)),
                    float(house.get('Population', 0)),
                    float(house.get('AveOccup', 0)),
                    float(house.get('Latitude', 0)),
                    float(house.get('Longitude', 0))
                ]
                
                features_df = pd.DataFrame([features], columns=feature_names)
                features_scaled = scaler.transform(features_df)
                prediction = model.predict(features_scaled)[0]
                predicted_price = prediction * 100000
                
                results.append({
                    'house_id': idx + 1,
                    'prediction': round(predicted_price, 2),
                    'status': 'success'
                })
            except Exception as e:
                results.append({
                    'house_id': idx + 1,
                    'error': str(e),
                    'status': 'failed'
                })
        
        return jsonify({
            'success': True,
            'total': len(houses),
            'results': results
        })
    
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        return jsonify({'error': f'Batch prediction failed: {str(e)}'}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify({
        'success': True,
        'total_predictions': len(predictions_history),
        'predictions': predictions_history[-10:],
        'average_price': round(np.mean([p['prediction'] for p in predictions_history]), 2) if predictions_history else 0
    })

@app.route('/api/export', methods=['GET'])
def export_history():
    if not predictions_history:
        return jsonify({'error': 'No predictions to export'}), 400
    
    try:
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(['Timestamp', 'Median Income', 'House Age', 'Average Rooms', 
                        'Average Bedrooms', 'Population', 'Average Occupancy', 
                        'Latitude', 'Longitude', 'Predicted Price'])
        
        for pred in predictions_history:
            inp = pred['input']
            writer.writerow([
                pred['timestamp'],
                inp.get('MedInc'),
                inp.get('HouseAge'),
                inp.get('AveRooms'),
                inp.get('AveBedrms'),
                inp.get('Population'),
                inp.get('AveOccup'),
                inp.get('Latitude'),
                inp.get('Longitude'),
                pred['prediction']
            ])
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'house_predictions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-pdf', methods=['POST'])
def export_pdf():
    try:
        data = request.get_json()
        prediction = data.get('prediction', 0)
        input_data = data.get('input', {})
        top_features = data.get('top_features', [])
        
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#0B4F3C'),
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#B8860B'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6
        )
        
        # Title
        elements.append(Paragraph("🏰 Luxury House Price Predictor", title_style))
        elements.append(Paragraph("Advanced AI-Powered Real Estate Valuation Report", styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Prediction Result
        elements.append(Paragraph("Predicted Price", heading_style))
        price_str = f"${prediction:,.0f}"
        elements.append(Paragraph(f"<b>{price_str}</b>", styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Input Data
        elements.append(Paragraph("Property Details", heading_style))
        input_table_data = [
            ['Feature', 'Value'],
            ['Median Income', f"${float(input_data.get('MedInc', 0)) * 10000:,.0f}"],
            ['House Age', f"{input_data.get('HouseAge', 0)} years"],
            ['Average Rooms', f"{input_data.get('AveRooms', 0)}"],
            ['Average Bedrooms', f"{input_data.get('AveBedrms', 0)}"],
            ['Population', f"{input_data.get('Population', 0)}"],
            ['Average Occupancy', f"{input_data.get('AveOccup', 0)}"],
            ['Latitude', f"{input_data.get('Latitude', 0)}"],
            ['Longitude', f"{input_data.get('Longitude', 0)}"],
        ]
        
        input_table = Table(input_table_data, colWidths=[3*inch, 3*inch])
        input_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0B4F3C')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f0f0')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
        ]))
        elements.append(input_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Top Features
        elements.append(Paragraph("Top Influencing Features", heading_style))
        features_data = [['Feature', 'Importance Score']]
        for feature in top_features:
            importance_pct = f"{feature['importance'] * 100:.1f}%"
            features_data.append([feature['name'], importance_pct])
        
        features_table = Table(features_data, colWidths=[3*inch, 3*inch])
        features_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#B8860B')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fffacd')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        elements.append(features_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Footer
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        elements.append(Paragraph("Luxury House Price Predictor © 2025", styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'house_prediction_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    except Exception as e:
        logger.error(f"PDF export error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/model-info', methods=['GET'])
def model_info():
    feature_importance = dict(zip(feature_names, model.feature_importances_))
    
    return jsonify({
        'model': 'Random Forest Regressor',
        'features': feature_names,
        'feature_importance': feature_importance,
        'dataset': 'California Housing',
        'total_predictions_made': len(predictions_history)
    })

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    global predictions_history
    predictions_history = []
    return jsonify({'success': True, 'message': 'History cleared'})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

def generateInsights(feature_importance, input_data, predicted_price):
    """Generate AI insights based on prediction"""
    insights = []
    
    # Most important feature
    top_feature = max(feature_importance.items(), key=lambda x: x[1])
    insights.append(f"📊 <strong>{top_feature[0]}</strong> is the most important factor ({top_feature[1]*100:.1f}%) affecting this price.")
    
    # Income insight
    income = float(input_data.get('MedInc', 0))
    if income > 10:
        insights.append("💰 High income area - Premium pricing expected.")
    elif income < 3:
        insights.append("💰 Lower income area - Budget-friendly pricing.")
    
    # Age insight
    age = int(input_data.get('HouseAge', 0))
    if age > 50:
        insights.append("🏘️ Older property - May benefit from renovations.")
    elif age < 10:
        insights.append("🏘️ Newer property - Premium condition advantage.")
    
    # Location insight
    lat = float(input_data.get('Latitude', 0))
    if lat > 37.8:
        insights.append("📍 Northern California location - Strong market area.")
    
    # Room insight
    rooms = float(input_data.get('AveRooms', 0))
    if rooms > 7:
        insights.append("🛏️ Spacious property - Large rooms command premium prices.")
    
    return insights

if __name__ == '__main__':
    if model is None:
        print("\n⚠️ Model not loaded!")
    else:
        print("\n✓ Advanced Flask App with PDF Export & Insights")
        app.run(debug=True, port=5000)
