# ==============================
# HealthPulse - Model Training
# ==============================

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import joblib

# 1️⃣ Load Dataset
data = pd.read_csv("heart.csv")

# 2️⃣ Separate Features and Target
X = data.drop("target", axis=1)
y = data["target"]

# 3️⃣ Feature Scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 4️⃣ Train Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

# 5️⃣ Train Model
model = LogisticRegression()
model.fit(X_train, y_train)

# 6️⃣ Save Model & Scaler
joblib.dump(model, "model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("Model Trained & Saved Successfully!")