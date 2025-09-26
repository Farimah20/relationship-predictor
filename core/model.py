# این فایل مدل NN رو می‌سازه. چرا؟ برای پیش‌بینی ریسک طلاق بر اساس ۵۴ ویژگی DPS.
import pandas as pd  # برای خواندن CSV.
import numpy as np  # برای array.
from sklearn.model_selection import train_test_split  # برای split داده.
from sklearn.preprocessing import StandardScaler  # برای normalize.
import tensorflow as tf  # برای NN.
import joblib  # برای ذخیره scaler.

# بارگذاری داده (delimiter=';' برای UCI CSV).
df = pd.read_csv('../divorce.csv', delimiter=';')  # path نسبت به core/ – ۱۷۰ ردیف.
X = df.drop('Class', axis=1).values  # ۵۴ ویژگی (Atr1 تا Atr54) – 0-4 scale.
y = df['Class'].values  # کلاس (0=موفق, 1=طلاق).
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)  # split 80/20.
scaler = StandardScaler()  # scaler برای normalize.
X_train = scaler.fit_transform(X_train)  # fit و transform train.
X_test = scaler.transform(X_test)  # transform test.

# مدل NN (Sequential – ۳ لایه).
model = tf.keras.Sequential([  # Sequential مدل ساده.
    tf.keras.layers.Dense(64, activation='relu', input_shape=(54,)),  # لایه مخفی ۱ – relu activation.
    tf.keras.layers.Dense(32, activation='relu'),  # لایه مخفی ۲.
    tf.keras.layers.Dense(1, activation='sigmoid')  # خروجی باینری – sigmoid برای احتمال ۰-۱.
])
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])  # compile – adam optimizer, binary_crossentropy loss.
model.fit(X_train, y_train, epochs=50, batch_size=16, validation_split=0.1, verbose=1)  # آموزش – epochs ۵۰, verbose=1 برای خروجی.

# ارزیابی – دقت رو چک کن.
loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
print(f'دقت مدل: {accuracy:.2f}')  # باید >0.9 باشه (با این دیتاست).

# ذخیره در core/ – برای لود در views.py.
model.save('divorce_model.h5')  # مدل NN.
joblib.dump(scaler, 'scaler.pkl')  # scaler.
print('مدل و scaler ذخیره شد!')  # تأیید.