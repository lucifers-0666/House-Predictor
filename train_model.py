# train_model.py - Train and save the model

import numpy as np
import pandas as pd
import pickle
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

print("=" * 70)
print("PHASE 3A: TRAINING MACHINE LEARNING MODEL")
print("=" * 70)

# ============= STEP 1: Load Dataset =============
print("\n1. Loading California Housing Dataset...")
housing = fetch_california_housing(as_frame=True)
df = housing.frame

print(f"   ✓ Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")

# ============= STEP 2: Prepare Features and Target =============
print("\n2. Preparing data for training...")
X = df.iloc[:, :-1]  # All columns except last (features)
y = df.iloc[:, -1]   # Last column (target - MedHouseVal)

print(f"   Features shape: {X.shape}")
print(f"   Target shape: {y.shape}")

# ============= STEP 3: Train-Test Split =============
print("\n3. Splitting data (80% train, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"   Training set: {X_train.shape[0]} samples")
print(f"   Test set: {X_test.shape[0]} samples")

# ============= STEP 4: Feature Scaling =============
print("\n4. Scaling features (StandardScaler)...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("   ✓ Features scaled successfully")

# ============= STEP 5: Train Model =============
print("\n5. Training Random Forest Regressor...")
model = RandomForestRegressor(
    n_estimators=100,
    max_depth=20,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train_scaled, y_train)
print("   ✓ Model training completed")

# ============= STEP 6: Model Evaluation =============
print("\n6. Evaluating model performance...")

y_pred_train = model.predict(X_train_scaled)
y_pred_test = model.predict(X_test_scaled)

# Training metrics
train_r2 = r2_score(y_train, y_pred_train)
train_mae = mean_absolute_error(y_train, y_pred_train)
train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))

# Test metrics
test_r2 = r2_score(y_test, y_pred_test)
test_mae = mean_absolute_error(y_test, y_pred_test)
test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))

print(f"\n   TRAINING SET METRICS:")
print(f"   - R² Score:        {train_r2:.4f}")
print(f"   - MAE:             ${train_mae*100000:.2f}")
print(f"   - RMSE:            ${train_rmse*100000:.2f}")

print(f"\n   TEST SET METRICS:")
print(f"   - R² Score:        {test_r2:.4f}")
print(f"   - MAE:             ${test_mae*100000:.2f}")
print(f"   - RMSE:            ${test_rmse*100000:.2f}")

# ============= STEP 7: Feature Importance =============
print("\n7. Feature Importance Ranking:")
feature_importance = pd.DataFrame({
    'Feature': X.columns,
    'Importance': model.feature_importances_
}).sort_values('Importance', ascending=False)

for idx, row in feature_importance.iterrows():
    print(f"   {row['Feature']:15} : {row['Importance']:.4f}")

# ============= STEP 8: Save Model & Scaler =============
print("\n8. Saving model and scaler...")

# Save model
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)
print("   ✓ Model saved as 'model.pkl'")

# Save scaler
with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
print("   ✓ Scaler saved as 'scaler.pkl'")

# Save feature names
with open('feature_names.pkl', 'wb') as f:
    pickle.dump(X.columns.tolist(), f)
print("   ✓ Feature names saved as 'feature_names.pkl'")

print("\n" + "=" * 70)
print("✓ PHASE 3A COMPLETED - Model Ready for Flask App!")
print("=" * 70)
