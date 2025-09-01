import streamlit as st
from PIL import Image
from stegano import lsb
import os
from datetime import datetime
from pymongo import MongoClient
from bson.binary import Binary
import secrets
import string

# MongoDB setup
MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)
db = client["crypto_image_db"]
image_collection = db["image_records"]
log_collection = db["logs"]

# Create image storage directory
IMAGE_DIR = "images"
os.makedirs(IMAGE_DIR, exist_ok=True)

# Streamlit UI setup
st.set_page_config(page_title="Crypto Image Authenticity Tool", layout="centered")
st.title("🔐 Crypto Image Authenticity Tool")
st.sidebar.title("🔧 PixelProof")

mode = st.sidebar.radio("Choose an action:", ["📝 Embed Secret in Image", "🔍 Detect Real vs Fake", "📜 View History"])

# ==========================
# 📝 EMBED SECRET
# ==========================
if mode == "📝 Embed Secret in Image":
    st.header("📝 Embed a Secret Message")

    embed_image = st.file_uploader("Upload an image (PNG or JPEG)", type=["png", "jpg", "jpeg"], key="embed_img")
    custom_filename = st.text_input("Enter a name for the output image file ")

    # Button to generate a secret key
    if st.button("🔑 Generate Random Secret"):
        def generate_secret(length=16):
            charset = string.ascii_letters + string.digits
            return ''.join(secrets.choice(charset) for _ in range(length))
        secret_text = generate_secret()
        st.session_state['generated_secret'] = secret_text

    # If generated, mask the key and show asterisks
    if 'generated_secret' in st.session_state:
        st.success("Generated Secret: ******** (Saved securely)")
        secret_text = st.session_state['generated_secret']
    else:
        secret_text = st.text_input("Enter the secret message to embed")

    if embed_image and secret_text and custom_filename:
        if st.button("🧬 Embed Message"):
            safe_filename = f"{custom_filename.strip().replace(' ', '_')}.png"

            # Convert uploaded image to RGB and save temporarily
            original = Image.open(embed_image).convert("RGB")
            original_path = os.path.join(IMAGE_DIR, "uploaded_to_embed.png")
            original.save(original_path, format="PNG")

            # Embed message using LSB
            encoded_img = lsb.hide(original_path, secret_text)
            saved_path = os.path.join(IMAGE_DIR, safe_filename)
            encoded_img.save(saved_path)

            st.success("✅ Secret embedded successfully!")
            st.image(saved_path, caption="Real Image (with message)", use_container_width=True)

            # Read image as binary and allow download
            with open(saved_path, "rb") as f:
                image_binary = Binary(f.read())
                st.download_button("⬇️ Download Embedded Image", data=image_binary, file_name=safe_filename, mime="image/png")

            # Save secret (not shown) in database
            image_collection.insert_one({
                "filename": safe_filename,
                "secret": secret_text,
                "image_data": image_binary,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

# ==========================
# 🔍 DETECT REAL VS FAKE
# ==========================
elif mode == "🔍 Detect Real vs Fake":
    st.header("🔍 Detect Real vs Fake Image")
    col1, col2 = st.columns(2)

    with col1:
        img1 = st.file_uploader("Upload Image 1", type=["png", "jpg", "jpeg"], key="img1")
    with col2:
        img2 = st.file_uploader("Upload Image 2", type=["png", "jpg", "jpeg"], key="img2")

    def detect_and_verify(uploaded_file):
        if uploaded_file:
            image = Image.open(uploaded_file).convert("RGB")
            temp_path = "temp_" + uploaded_file.name
            image.save(temp_path, format="PNG")
            try:
                message = lsb.reveal(temp_path)
                matched = image_collection.find_one({"secret": message}) if message else None
                return message, matched is not None
            except:
                return None, False
            finally:
                os.remove(temp_path)
        return None, False

    # Single image verification
    st.markdown("---")
    st.subheader("🔍 Verify a Single Image")
    single_img = st.file_uploader("Upload an image to verify", type=["png", "jpg", "jpeg"], key="single_img")

    if single_img:
        if st.button("✅ Verify Image"):
            msg, is_real = detect_and_verify(single_img)
            st.image(single_img, caption="Uploaded Image", use_container_width=True)
            if is_real:
                st.success("✅ The image is authentic!")
            else:
                st.error("❌ The image is fake or contains no valid key.")

    # Two-image comparison
    st.markdown("---")
    if img1 and img2:
        if st.button("🔎 Check Which is Real"):
            msg1, is_real1 = detect_and_verify(img1)
            msg2, is_real2 = detect_and_verify(img2)

            col1, col2 = st.columns(2)
            with col1:
                st.image(img1, caption="Image 1", use_container_width=True)
                st.info("✅ Real (key matched)" if is_real1 else "❌ Fake (no match)")
            with col2:
                st.image(img2, caption="Image 2", use_container_width=True)
                st.info("✅ Real (key matched)" if is_real2 else "❌ Fake (no match)")

            st.markdown("---")
            st.subheader("🔐 Final Verdict:")
            if is_real1 and not is_real2:
                result = "Image 1 is Real. Image 2 is Fake."
            elif is_real2 and not is_real1:
                result = "Image 2 is Real. Image 1 is Fake."
            elif not is_real1 and not is_real2:
                result = "Neither image is authentic."
            else:
                result = "Both images may be real (valid secrets found)."
            st.success(result)

            log_collection.insert_one({
                "image1_name": img1.name,
                "image2_name": img2.name,
                "result": result,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

# ==========================
# 📜 VIEW HISTORY
# ==========================
elif mode == "📜 View History":
    st.header("📜 Detection and Embedding History")

    st.subheader("🧬 Embedded Keys")
    for record in image_collection.find().sort("timestamp", -1):
        st.markdown(f"- 🖼️ **File**: {record['filename']} | 🔑 **Secret**: `********` | 🕒 {record['timestamp']}")

    st.markdown("---")
    st.subheader("🔍 Detection Logs")
    for log in log_collection.find().sort("timestamp", -1):
        st.markdown(
            f"- **Image 1**: {log['image1_name']} | **Image 2**: {log['image2_name']} | 🕒 {log['timestamp']}<br>"
            f"📌 **Result**: _{log['result']}_",
            unsafe_allow_html=True
        )
