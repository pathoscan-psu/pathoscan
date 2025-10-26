import os
# 💡 Must come before importing Streamlit
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"
os.environ["STREAMLIT_WATCHDOG_WARNING"] = "false"
import streamlit as st
import io
from PIL import Image
import google.generativeai as genai

# --- Configure Gemini API ---
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- Streamlit setup ---
st.set_page_config(page_title="PathoScan", page_icon="🩹", layout="centered")
st.title("🩹 PathoScan: AI Wound Infection Detector")
st.caption("AI-based wound analysis for educational and demo purposes.")
st.warning("⚠️ This app provides AI-generated insights and is **not** a substitute for professional medical advice.")

# --- File uploader ---
uploaded = st.file_uploader("Upload a wound image", type=["jpg", "jpeg", "png"])

def analyze_image_with_gemini(image_bytes: bytes):
    """
    Sends the wound image and prompt to Gemini 2.5 Flash with enforced timeout
    and robust fallback error handling for Streamlit Cloud.
    """
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

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

        # 🔒 Critical: Add request options to prevent hanging
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
            request_options={"timeout": 30},  # seconds
        )

        text = response.text or "(No response text received.)"
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
    st.image(img, caption="Uploaded Image", use_container_width=True)

    # Convert to bytes
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    image_bytes = buffer.getvalue()

    with st.spinner("🔍 Analyzing wound image using Gemini 2.5 Flash..."):
        result = analyze_image_with_gemini(image_bytes)

    # Display result with preserved newlines
    st.subheader("🧠 AI Diagnosis Result")
    st.text(result)

    # Footer note
    st.info("This analysis is AI-generated for demonstration only. Always consult a medical professional for real diagnosis.")
