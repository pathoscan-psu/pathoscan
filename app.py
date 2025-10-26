import os
# 💡 Must come before importing Streamlit
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"
os.environ["STREAMLIT_WATCHDOG_WARNING"] = "false"

import io
from PIL import Image
import streamlit as st
import google.generativeai as genai

# --- Configure Gemini API ---
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- Streamlit setup ---
st.set_page_config(page_title="PathoScan - HealLens", page_icon="🩹", layout="centered")

# --- Custom CSS for styling ---
st.markdown("""
    <style>
    body {background-color: #f5f7fa;}
    .stApp {
        background: linear-gradient(180deg, #fefefe 0%, #f1f5f9 100%);
        border-radius: 20px;
        padding: 20px;
    }
    h1, h2, h3 {
        text-align: center;
        color: #2b2d42;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .uploadedImage {
        border: 2px solid #d0d7de;
        border-radius: 15px;
        padding: 10px;
        background-color: #ffffff;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.title("🩹 PathoScan by HealLens")
st.caption("Smart AI-powered wound infection detector for educational and demo use only.")
st.warning("⚠️ This tool provides AI-generated insights — **not** a medical diagnosis. Always consult a professional.")

# --- User Info Form ---
with st.expander("👤 Enter your basic details (optional, for better context only)"):
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", min_value=1, max_value=120, value=25, step=1)
        height = st.number_input("Height (cm)", min_value=50, max_value=250, value=170)
    with col2:
        weight = st.number_input("Weight (kg)", min_value=10, max_value=300, value=65)

st.markdown("---")

# --- File uploader ---
st.header("📤 Upload a wound image for analysis")
uploaded = st.file_uploader("Choose an image (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

def analyze_image_with_gemini(image_bytes: bytes):
    """Sends the wound image to Gemini and returns structured output."""
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = (
            "You are a medical imaging analysis assistant. "
            "Analyze the attached wound image and respond in EXACTLY 5 lines as follows — "
            "no explanations, no markdown, just plain text:\n\n"
            "Disease Diagnosis: <the single most probable bacterial or fungal disease>\n"
            "Probability: <only a number with % sign>\n"
            "Urgency Advice: <choose exactly one — SEEK IMMEDIATE ATTENTION / Seek attention if causes discomfort / Attention may not be required>\n"
            "Home Remedy: <one short at-home remedy if not severe>\n"
            "Confidence Statement: <a single sentence showing how confident you are>\n\n"
            "Ensure each line is separated by a newline character."
        )

        response = model.generate_content(
            [
                prompt,
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": image_bytes
                    }
                }
            ],
            request_options={"timeout": 30},
        )

        text = response.text or "(No response received.)"
        text = text.strip()
        text = text.replace("Probability:", "\nProbability:") \
                   .replace("Urgency Advice:", "\nUrgency Advice:") \
                   .replace("Home Remedy:", "\nHome Remedy:") \
                   .replace("Confidence Statement:", "\nConfidence Statement:")
        return text

    except Exception as e:
        return f"❌ Error calling Gemini: {e}"

# --- Main logic ---
if uploaded:
    img = Image.open(uploaded).convert("RGB")

    st.markdown("### 📸 Uploaded Image Preview")
    st.image(img, caption="Uploaded Wound Image", width="stretch", output_format="JPEG")

    # Convert to bytes
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    image_bytes = buffer.getvalue()

    # Loading spinner
    with st.spinner("🤖 Using AI to analyze image... please wait ⏳"):
        result = analyze_image_with_gemini(image_bytes)

    st.success("✅ Analysis complete!")
    st.subheader("🧠 AI Diagnosis Result")
    st.text(result)

    # Display user info summary
    st.markdown("---")
    st.markdown(f"**👤 Submitted Info (not used by AI)**\n\n- Age: {age}\n- Height: {height} cm\n- Weight: {weight} kg")

    # Footer note
    st.info("This analysis is AI-generated for educational purposes only. Consult a licensed clinician for medical advice.")
else:
    st.info("📷 Please upload an image above to begin the analysis.")
