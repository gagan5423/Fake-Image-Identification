
# 🔐 Crypto Image Authenticity Tool

A **Streamlit-based application** that allows users to embed secret messages into images, verify their authenticity, and track a history of verifications.
It uses **LSB (Least Significant Bit) steganography**, **MongoDB** for secure storage, and provides an easy-to-use interface to detect **real vs fake images**.

---

## 🚀 Features

* 📝 **Embed Secret Messages**

  * Hide secret keys/messages inside PNG or JPEG images using **LSB steganography**.
  * Securely store the secret and image in **MongoDB**.
  * Auto-generate strong random secret keys.
  * Download embedded images for later use.

* 🔍 **Detect Real vs Fake**

  * Verify if an uploaded image contains a valid secret.
  * Compare **two images** to check which one is authentic.
  * View results with a clear verdict.

* 📜 **View History**

  * List of all embedded images (secret is masked).
  * Logs of detection/verification attempts with results.

---

## 🏗️ Tech Stack

* **Frontend/UI** → [Streamlit](https://streamlit.io/)
* **Image Processing** → [Pillow (PIL)](https://pillow.readthedocs.io/) + [stegano](https://pypi.org/project/stegano/) (LSB)
* **Database** → [MongoDB](https://www.mongodb.com/) (pymongo)
* **Backend Logic** → Python

---

## 📂 Project Structure

```
crypto-image-tool/
│── images/              # Directory for storing uploaded/encoded images
│── app.py               # Main Streamlit application
│── requirements.txt     # Python dependencies
│── README.md            # Project documentation
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/crypto-image-tool.git
cd crypto-image-tool
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Setup MongoDB

* Install and start **MongoDB Community Server**
* Default connection string is used:

  ```
  mongodb://localhost:27017
  ```
* A database **crypto\_image\_db** with collections will be auto-created:

  * `image_records` → stores images + secrets
  * `logs` → stores detection logs

### 5️⃣ Run Application

```bash
streamlit run app.py
```

The app will start on → [http://localhost:8501](http://localhost:8501)

---

## 📊 Usage

1. **Embed Secret in Image**

   * Upload an image
   * Enter secret or auto-generate one
   * Save & download the new "authentic" image

2. **Detect Real vs Fake**

   * Upload one image → Verify authenticity
   * Upload two images → Compare and identify which is real

3. **View History**

   * See all embedding activity
   * Review detection/verification logs

