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

# --- Clean readable CSS ---
st.markdown("""
    <style>
    /* Overall app container */
    .stApp {
        background: linear-gradient(180deg, #fdfdfd 0%, #f4f7fb 100%);
        color: #1c1e21;
        font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
    }

    /* Headings */
    h1, h2, h3 {
        color: #1e293b !important;
        font-weight: 700;
        text-align: center;
    }

    /* Subheaders and captions */
    .stCaption, .stMarkdown, p, label, span {
        color: #1c1e21 !important;
        font-size: 15px !important;
    }

    /* Image box */
    .uploadedImage {
        border: 2px solid #d6dee6;
        border-radius: 10px;
        background-color: #ffffff;
        padding: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }

    /* Spinner text */
    div[data-testid="stSpinner"] p {
        font-size: 17px;
        font-weight: 600;
        color: #334155;
    }

    /* Divider line */
    hr {border: 0; border-top: 1px solid #cbd5e1; margin: 1.5em 0;}

    /* Success banner */
    .stSuccess {
        background-color: #ecfdf5 !important;
        color: #065f46 !important;
        border-left: 4px solid #10b981 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.title("🩹 PathoScan by HealLens")
st.caption("Smart AI-powered wound infection detector for educational and demo purposes.")
st.warning("⚠️ This tool provides AI-generated insights — **not** a medical diagnosis. Always consult a professional.")

# --- User Info Form ---
with st.expander("👤 Enter your basic details (optional)"):
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", min_value=1, max_value=120, value=25, step=1)
        height = st.number_input("Height (cm)", min_value=50, max_value=250, value=170)
    with col2:
        weight = st.number_input("Weight (kg)", min_value=10, max_value=300, value=65)

st.markdown("<hr>", unsafe_allow_html=True)

# --- File uploader ---
st.header("📤 Upload a wound image for analysis")
uploaded = st.file_uploader("Choose an image (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

def analyze_image_with_gemini(image_bytes: bytes):
    """Send the wound image to Gemini and return the analysis."""
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
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"**👤 Submitted Info (not used by AI)**  \n- Age: {age}  \n- Height: {height} cm  \n- Weight: {weight} kg")

    # Footer
    st.info("This analysis is AI-generated for educational purposes only. Consult a licensed clinician for medical advice.")
else:
    st.info("📷 Please upload an image above to begin the analysis.")
