import os
import json
import joblib
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder='templates', static_folder='static')

# Load the model, scaler and feature columns order
model_path = 'model.joblib'
features_path = 'features.json'

if os.path.exists(model_path) and os.path.exists(features_path):
    model = joblib.load(model_path)
    with open(features_path, 'r') as f:
        feature_cols = json.load(f)
    print("Model and features loaded successfully.")
else:
    model = None
    feature_cols = None
    print("Warning: Model files not found. Please train the model first.")

def preprocess_input(data, cols):
    # Initialize all values to 0
    encoded = {col: 0 for col in cols}
    
    # Simple binary mappings
    encoded['gender'] = 1 if data.get('gender') == 'Male' else 0
    encoded['SeniorCitizen'] = 1 if data.get('SeniorCitizen') in [1, 'Yes', '1'] else 0
    encoded['Partner'] = 1 if data.get('Partner') == 'Yes' else 0
    encoded['Dependents'] = 1 if data.get('Dependents') == 'Yes' else 0
    encoded['PhoneService'] = 1 if data.get('PhoneService') == 'Yes' else 0
    encoded['PaperlessBilling'] = 1 if data.get('PaperlessBilling') == 'Yes' else 0
    
    # Numeric values
    tenure = int(data.get('tenure', 0))
    monthly_charges = float(data.get('MonthlyCharges', 0.0))
    
    # Total charges defaults to tenure * MonthlyCharges if not provided
    total_charges_raw = data.get('TotalCharges')
    if total_charges_raw is None or total_charges_raw == '':
        total_charges = tenure * monthly_charges
    else:
        total_charges = float(total_charges_raw)
        
    encoded['tenure'] = tenure
    encoded['MonthlyCharges'] = monthly_charges
    encoded['TotalCharges'] = total_charges
    
    # MultipleLines
    ml = data.get('MultipleLines', 'No')
    if ml == 'No phone service':
        encoded['MultipleLines_No phone service'] = 1
    elif ml == 'Yes':
        encoded['MultipleLines_Yes'] = 1
        
    # InternetService
    is_val = data.get('InternetService', 'DSL')
    if is_val == 'Fiber optic':
        encoded['InternetService_Fiber optic'] = 1
    elif is_val == 'No':
        encoded['InternetService_No'] = 1
        
    # OnlineSecurity
    os_val = data.get('OnlineSecurity', 'No')
    if os_val == 'No internet service':
        encoded['OnlineSecurity_No internet service'] = 1
    elif os_val == 'Yes':
        encoded['OnlineSecurity_Yes'] = 1
        
    # OnlineBackup
    ob_val = data.get('OnlineBackup', 'No')
    if ob_val == 'No internet service':
        encoded['OnlineBackup_No internet service'] = 1
    elif ob_val == 'Yes':
        encoded['OnlineBackup_Yes'] = 1
        
    # DeviceProtection
    dp_val = data.get('DeviceProtection', 'No')
    if dp_val == 'No internet service':
        encoded['DeviceProtection_No internet service'] = 1
    elif dp_val == 'Yes':
        encoded['DeviceProtection_Yes'] = 1
        
    # TechSupport
    ts_val = data.get('TechSupport', 'No')
    if ts_val == 'No internet service':
        encoded['TechSupport_No internet service'] = 1
    elif ts_val == 'Yes':
        encoded['TechSupport_Yes'] = 1
        
    # StreamingTV
    st_val = data.get('StreamingTV', 'No')
    if st_val == 'No internet service':
        encoded['StreamingTV_No internet service'] = 1
    elif st_val == 'Yes':
        encoded['StreamingTV_Yes'] = 1
        
    # StreamingMovies
    sm_val = data.get('StreamingMovies', 'No')
    if sm_val == 'No internet service':
        encoded['StreamingMovies_No internet service'] = 1
    elif sm_val == 'Yes':
        encoded['StreamingMovies_Yes'] = 1
        
    # Contract
    cnt = data.get('Contract', 'Month-to-month')
    if cnt == 'One year':
        encoded['Contract_One year'] = 1
    elif cnt == 'Two year':
        encoded['Contract_Two year'] = 1
        
    # PaymentMethod
    pm = data.get('PaymentMethod', 'Mailed check')
    if pm == 'Credit card (automatic)':
        encoded['PaymentMethod_Credit card (automatic)'] = 1
    elif pm == 'Electronic check':
        encoded['PaymentMethod_Electronic check'] = 1
    elif pm == 'Mailed check':
        encoded['PaymentMethod_Mailed check'] = 1
        
    return [encoded[col] for col in cols]

def analyze_risk_factors(data):
    factors = []
    
    # Contract Month-to-month is a high risk factor
    if data.get('Contract') == 'Month-to-month':
        factors.append({
            "feature": "Contract Type",
            "value": "Month-to-month",
            "impact": "High Risk",
            "description": "Month-to-month contracts have a 43% historical churn rate. Switching to a 1-year or 2-year contract increases customer stability."
        })
        
    # InternetService Fiber Optic is associated with higher churn rate
    if data.get('InternetService') == 'Fiber optic':
        factors.append({
            "feature": "Internet Service",
            "value": "Fiber optic",
            "impact": "Medium-High Risk",
            "description": "Fiber optic customers exhibit high churn, likely due to high price sensitivity or technical concerns."
        })
        
    # Electronic Check payment method
    if data.get('PaymentMethod') == 'Electronic check':
        factors.append({
            "feature": "Payment Method",
            "value": "Electronic check",
            "impact": "Medium-High Risk",
            "description": "Electronic check users churn at 45%. Automating payments (credit card or bank transfer) improves retention."
        })
        
    # Short tenure
    tenure = int(data.get('tenure', 0))
    if tenure < 12:
        factors.append({
            "feature": "Tenure",
            "value": f"{tenure} months",
            "impact": "High Risk",
            "description": "Newer customers (tenure < 12 months) are in the critical retention window and are 3x more likely to churn."
        })
    elif tenure < 24:
        factors.append({
            "feature": "Tenure",
            "value": f"{tenure} months",
            "impact": "Medium Risk",
            "description": "Customers in their second year show moderate churn probability. Nurturing loyalty at this phase is crucial."
        })
        
    # No Tech Support or Online Security
    if data.get('TechSupport') == 'No':
        factors.append({
            "feature": "Tech Support",
            "value": "No support subscription",
            "impact": "Medium Risk",
            "description": "Customers without tech support subscriptions have higher churn rates. Upselling tech support can lower risk."
        })
    if data.get('OnlineSecurity') == 'No':
        factors.append({
            "feature": "Online Security",
            "value": "No security subscription",
            "impact": "Medium Risk",
            "description": "Lack of online security services correlates with reduced customer attachment and higher churn."
        })
        
    # High Monthly Charges
    monthly = float(data.get('MonthlyCharges', 0))
    if monthly > 80:
        factors.append({
            "feature": "Monthly Charges",
            "value": f"${monthly:.2f}",
            "impact": "Medium Risk",
            "description": "High monthly charges (> $80) increase price sensitivity, making the customer vulnerable to competitive offers."
        })
        
    return factors

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if model is None or feature_cols is None:
        return jsonify({"error": "Model not loaded. Please train the model."}), 500
        
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No input data provided."}), 400
            
        # Preprocess the inputs
        features_vector = preprocess_input(data, feature_cols)
        
        # Model predictions (expects unscaled features)
        import pandas as pd
        features_df = pd.DataFrame([features_vector], columns=feature_cols)
        prob = model.predict_proba(features_df)[0][1]
        
        # Determine risk level
        prob_pct = round(prob * 100, 1)
        if prob_pct >= 60.0:
            risk_level = "High"
            badge_class = "danger"
        elif prob_pct >= 30.0:
            risk_level = "Medium"
            badge_class = "warning"
        else:
            risk_level = "Low"
            badge_class = "success"
            
        # Get risk factors
        risk_factors = analyze_risk_factors(data)
        
        return jsonify({
            "probability": prob_pct,
            "risk_level": risk_level,
            "badge_class": badge_class,
            "risk_factors": risk_factors
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
