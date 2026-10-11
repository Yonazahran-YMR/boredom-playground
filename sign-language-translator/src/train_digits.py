from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "landmarks.csv"

df = pd.read_csv(CSV_PATH, dtype={"label": str})
df = df[df["hand"] == "Right"]  # drops the one stray Left row

# oldest session trains, newest session tests (hardcoded for now)
sessions = sorted(df["session"].unique())
train = df[df["session"] == sessions[0]]
test = df[df["session"] == sessions[-1]]

feature_cols = [c for c in df.columns if c[0] in "xy" and c[1:].isdigit()]  # x0..y20 = 42 columns

# labels as integers for the model, names kept for printing
encoder = LabelEncoder().fit(df["label"].astype(str))
names = list(encoder.classes_)

X_train = train[feature_cols].to_numpy()
X_test = test[feature_cols].to_numpy()
y_train = encoder.transform(train["label"].astype(str))
y_test = encoder.transform(test["label"].astype(str))
print(f"train session {sessions[0]}: {X_train.shape}")
print(f"test session  {sessions[-1]}: {X_test.shape}")

model = RandomForestClassifier(n_estimators=200, class_weight="balanced", random_state=42)
model.fit(X_train, y_train)

print()
print(f"train accuracy: {accuracy_score(y_train, model.predict(X_train)):.3f}")
pred = model.predict(X_test)
print(f"test accuracy:  {accuracy_score(y_test, pred):.3f}")

cm = confusion_matrix(y_test, pred, labels=list(range(len(names))))
print("\nconfusion matrix (rows = true label, columns = predicted):")
print("     " + " ".join(f"{n:>4}" for n in names))
for n, row in zip(names, cm):
    print(f"{n:>4} " + " ".join(f"{v:4d}" for v in row))

print()
for n, recall in zip(names, cm.diagonal() / cm.sum(axis=1)):
    print(f"label {n}: {recall:.1%} correct")

# Extra experiment: the dishonest way. Random split inside session 1 only.
Xa, Xb, ya, yb = train_test_split(X_train, y_train, test_size=0.25, random_state=42)
leaky = RandomForestClassifier(n_estimators=200, class_weight="balanced", random_state=42).fit(Xa, ya)
print(f"\nrandom split inside session 1 (leaky): {accuracy_score(yb, leaky.predict(Xb)):.3f}")

import joblib

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "digits_rf.joblib"
MODEL_PATH.parent.mkdir(exist_ok=True)

# final model: trained on both sessions
X_all = df[feature_cols].to_numpy()
y_all = encoder.transform(df["label"].astype(str))
final = RandomForestClassifier(n_estimators=200, class_weight="balanced", random_state=42)
final.fit(X_all, y_all)
joblib.dump({"model": final, "names": names}, MODEL_PATH)
print(f"\nsaved final model ({len(X_all)} samples) to {MODEL_PATH}")