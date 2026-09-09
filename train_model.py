import os
import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import joblib

def main():
    print("Starting Model Training Pipeline...")
    
    # 1. Load data
    csv_path = "WA_Fn-UseC_-Telco-Customer-Churn.csv"
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}. Please download it first.")
        
    df = pd.read_csv(csv_path)
    print(f"Dataset loaded. Initial shape: {df.shape}")
    
    # 2. Clean TotalCharges (convert to numeric and remove NaNs)
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    initial_nulls = df["TotalCharges"].isnull().sum()
    df.dropna(subset=["TotalCharges"], inplace=True)
    print(f"Dropped {initial_nulls} missing TotalCharges rows. Shape: {df.shape}")
    
    # 3. Drop customerID
    if "customerID" in df.columns:
        df.drop("customerID", axis=1, inplace=True)
        print("Dropped customerID.")
        
    # 4. Map binary columns
    binary_columns = ["Partner", "Dependents", "PhoneService", "PaperlessBilling", "Churn"]
    for column in binary_columns:
        if column in df.columns:
            df[column] = df[column].map({"Yes": 1, "No": 0})
            
    if "gender" in df.columns:
        df["gender"] = df["gender"].map({"Female": 0, "Male": 1})
        
    # 5. One-hot encoding for multi-class categorical columns
    categorical_columns = df.select_dtypes(include="object").columns.tolist()
    print(f"Applying one-hot encoding to: {categorical_columns}")
    df = pd.get_dummies(df, columns=categorical_columns, drop_first=True, dtype=int)
    
    # 6. Train-test split
    X = df.drop("Churn", axis=1)
    y = df["Churn"]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"Train set shape: {X_train.shape}, Test set shape: {X_test.shape}")
    
    # 7. Scale numerical features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 8. Train the tuned Random Forest Classifier on X_train (unscaled, matching notebook)
    best_rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        max_features="log2",
        min_samples_leaf=1,
        min_samples_split=5,
        class_weight="balanced_subsample",
        random_state=42
    )
    
    best_rf.fit(X_train, y_train)
    print("Trained the optimal Random Forest model.")
    
    # Evaluate
    train_acc = best_rf.score(X_train, y_train)
    test_acc = best_rf.score(X_test, y_test)
    print(f"Training Accuracy: {train_acc:.4f}")
    print(f"Testing Accuracy: {test_acc:.4f}")
    
    # 9. Save artifacts
    joblib.dump(best_rf, "model.joblib")
    joblib.dump(scaler, "scaler.joblib")
    
    feature_cols = X_train.columns.tolist()
    with open("features.json", "w") as f:
        json.dump(feature_cols, f)
        
    print("Exported model.joblib, scaler.joblib, and features.json successfully!")

if __name__ == "__main__":
    main()
