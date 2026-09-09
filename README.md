# 📊 Telecom Customer Churn Prediction System

An end-to-end Data Science and Machine Learning project that predicts whether a telecom customer is likely to churn (leave the service) and identifies key contributing risk factors. The project features a complete ML workflow, an exported tuned Random Forest pipeline, and a modern, responsive web dashboard built with Flask and Vanilla CSS.

---

## 🚀 Key Features

- **End-to-End ML Pipeline**: From raw data loading and preprocessing to exploratory data analysis (EDA), model training, evaluation, hyperparameter tuning, and serialization.
- **Multiple Classification Models Compared**:
  - Logistic Regression
  - Decision Tree
  - Random Forest (Selected & Tuned)
  - XGBoost
- **Trained Model Serialization**: Pre-trained Random Forest model (`model.joblib`), `StandardScaler` (`scaler.joblib`), and feature schemas (`features.json`).
- **Interactive Web Application**:
  - Sleek dark-mode dashboard with glassmorphism aesthetics.
  - Real-time churn probability gauge with color-coded risk levels (Low, Medium, High).
  - Dynamic risk attribution explaining specific factors driving customer churn risk (e.g., month-to-month contracts, lack of tech support, fiber optic plan issues, high monthly charges).

---

## 📁 Repository Structure

```text
├── Customer_Churn_Prediction.ipynb   # Complete Jupyter Notebook with EDA, training, and evaluations
├── WA_Fn-UseC_-Telco-Customer-Churn.csv # IBM Telco Customer Churn dataset
├── cleaned_churn.csv                 # Cleaned dataset after preprocessing
├── train_model.py                    # Standalone training script to reproduce model artifacts
├── app.py                            # Flask server providing the API and serving the UI
├── model.joblib                      # Exported tuned Random Forest model
├── scaler.joblib                     # Fitted StandardScaler
├── features.json                     # Feature names schema for inference
├── templates/
│   └── index.html                    # Frontend dashboard HTML template
├── static/
│   ├── style.css                     # Premium dark-mode UI styling
│   └── script.js                     # Dynamic UI interactions, sliders, and API requests
├── requirements.txt                  # Python dependencies
└── .gitignore                        # Git ignore patterns
```

---

## 🧠 Machine Learning Workflow

1. **Data Cleaning**:
   - Converted `TotalCharges` to numeric and removed missing rows.
   - Dropped non-predictive identifier (`customerID`).
2. **Feature Engineering & Encoding**:
   - Binary encoding for two-class variables (`Partner`, `Dependents`, `PhoneService`, `PaperlessBilling`, `Churn`).
   - Categorical mapping for `gender`.
   - One-hot encoding for multi-class features (`Contract`, `InternetService`, `PaymentMethod`, etc.).
3. **Model Training & Tuning**:
   - Handled class imbalance using balanced subsample weights.
   - Selected Random Forest for superior generalization on tabular telecom data.
   - Evaluated using Accuracy, Precision, Recall, F1-score, and ROC-AUC.

---

## 🛠️ Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Pranays21/Customer_Churn_Prediction.git
cd Customer_Churn_Prediction
```

### 2. Set Up Environment & Install Dependencies
```bash
# Optional: Create virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Retrain the Model (Optional)
```bash
python train_model.py
```

### 4. Run the Web Dashboard
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 💻 Tech Stack

- **Data Science & ML**: Python, Pandas, NumPy, Scikit-Learn, XGBoost, Matplotlib, Seaborn, Joblib
- **Web Backend**: Flask
- **Frontend**: HTML5, Vanilla CSS, JavaScript, FontAwesome, Google Fonts
