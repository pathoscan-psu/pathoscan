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

# --- Modern dark CSS ---
st.markdown("""
    <style>
    /* Overall background */
    .stApp {
        background: radial-gradient(circle at top left, #111827, #0f172a, #1e293b);
        color: #f9fafb !important;
        font-family: 'Poppins', 'Segoe UI', sans-serif;
    }

    /* Headings */
    h1, h2, h3 {
        color: #f8fafc !important;
        text-align: center;
        font-weight: 700;
        letter-spacing: 0.3px;
    }

    /* Paragraphs and labels */
    p, label, span, .stMarkdown, .stCaption {
        color: #e2e8f0 !important;
        font-size: 15px !important;
    }

    /* Logo banner */
    .banner {
        background: linear-gradient(90deg, #0ea5e9, #6366f1);
        padding: 12px 0;
        text-align: center;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    }
    .banner img {
        height: 55px;
        border-radius: 10px;
    }

    /* Upload area */
    .uploadedImage {
        border: 2px solid #334155;
        border-radius: 12px;
        background-color: #1e293b;
        padding: 10px;
        box-shadow: 0 2px 10px rgba(255,255,255,0.05);
    }

    /* Spinner text */
    div[data-testid="stSpinner"] p {
        font-size: 17px;
        font-weight: 600;
        color: #e2e8f0;
    }

    /* Divider */
    hr {border: 0; border-top: 1px solid #334155; margin: 1.5em 0;}

    /* Success */
    .stSuccess {
        background-color: #1e3a8a !important;
        color: #e0f2fe !important;
        border-left: 5px solid #38bdf8 !important;
    }

    /* Input boxes */
    input, textarea {
        background-color: #111827 !important;
        color: #f9fafb !important;
        border: 1px solid #334155 !important;
        border-radius: 6px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Top banner for logo ---
st.markdown("""
    <div class="banner">
        <img src="https://upload.wikimedia.org/wikipedia/commons/a/a7/React-icon.svg" alt="Your Logo Here">
    </div>
""", unsafe_allow_html=True)
# 👆 Replace the image link above with your logo URL

# --- Header ---
st.title("🩹 PathoScan by HealLens")
st.caption("AI-powered wound infection detector for educational and demo use only.")
st.warning("⚠️ This tool provides AI-generated insights — **not** a medical diagnosis.")

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
                {"inline_data": {"mime_type": "image/jpeg", "data": image_bytes}}
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

    st.info("This analysis is AI-generated for educational purposes only.")
else:
    st.info("📷 Please upload an image above to begin the analysis.")
