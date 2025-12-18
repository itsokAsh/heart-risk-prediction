import streamlit as st
import pandas as pd
import numpy as np
import pickle
from xgboost import XGBClassifier
from fpdf import FPDF
import datetime
import os
import plotly.graph_objects as go
import plotly.express as px
from utils import (
    validate_input,
    create_gauge_chart,
    generate_health_recommendations,
    ReportGenerator,
    VALID_RANGES,
    CATEGORICAL_MAPPINGS,
    generate_audio_report
)
from train_model import custom_scaling
import traceback
from gtts import gTTS
from io import BytesIO

# Page config
st.set_page_config(
    page_title="Heart Disease Risk Predictor",
    page_icon="💓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'risk_score' not in st.session_state:
    st.session_state.risk_score = None
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None
if 'language' not in st.session_state:
    st.session_state.language = "English (US)"
if 'audio_content' not in st.session_state:
    st.session_state.audio_content = {}
if 'input_data' not in st.session_state:
    st.session_state.input_data = None
if 'audio_generated' not in st.session_state:
    st.session_state.audio_generated = False

# Language configuration
LANGUAGES = {
    "English (US)": {"code": "en", "name": "English"},
    "Español": {"code": "es", "name": "Spanish"},
    "Français": {"code": "fr", "name": "French"},
    "Deutsch": {"code": "de", "name": "German"},
    "Italiano": {"code": "it", "name": "Italian"},
    "Português": {"code": "pt", "name": "Portuguese"},
    "हिंदी": {"code": "hi", "name": "Hindi"},
    "中文": {"code": "zh-CN", "name": "Chinese"}
}

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stAlert {
        padding: 1rem;
        margin: 1rem 0;
    }
    .css-1v0mbdj.ebxwdo61 {
        width: 100%;
        max-width: 800px;
        margin: auto;
    }
</style>
""", unsafe_allow_html=True)

# Title and introduction
st.title("💓 Heart Disease Risk Predictor")
st.markdown("""
Please fill in your health information below for a personalized risk assessment.
""")

# Load model and scaler
@st.cache_resource
def load_model():
    try:
        with open("xgb_model.pkl", "rb") as f:
            model = pickle.load(f)
        with open("scaler.pkl", "rb") as f:
            scaler = pickle.load(f)
        return model, scaler
    except FileNotFoundError:
        st.error("Model files not found. Please ensure the model is trained first.")
        st.stop()

model, scaler = load_model()

# Load and cache reference data
@st.cache_data
def load_reference_data():
    try:
        return pd.read_csv("heart.csv")
    except FileNotFoundError:
        st.error("Reference data not found. Please ensure heart.csv exists.")
        st.stop()

df = load_reference_data()

# Feature mappings
feature_maps = {
    "cp": {
        "Typical Angina": 0,
        "Atypical Angina": 1,
        "Non-anginal Pain": 2,
        "Asymptomatic": 3
    },
    "restecg": {
        "Normal": 0,
        "ST-T Wave Abnormality": 1,
        "Left Ventricular Hypertrophy": 2
    },
    "thal": {
        "Normal": 0,
        "Fixed Defect": 1,
        "Reversible Defect": 2
    },
    "slope": {
        "Upsloping": 0,
        "Flat": 1,
        "Downsloping": 2
    }
}

# Create columns for better layout
col1, col2 = st.columns(2)

# User inputs
with col1:
    st.subheader("📋 Personal Information")
    user_input = {}
    
    age = st.number_input(
        "Age (years)",
        min_value=20,
        max_value=100,
        value=40,
        help="Enter your age in years"
    )
    user_input['age'] = age

    sex = st.selectbox(
        "Sex",
        ["Male", "Female"],
        help="Select your biological sex"
    )
    user_input['sex'] = 1 if sex == "Male" else 0

    cp = st.selectbox(
        "Chest Pain Type",
        list(feature_maps['cp'].keys()),
        help="Select the type of chest pain you experience"
    )
    user_input['cp'] = feature_maps['cp'][cp]

with col2:
    st.subheader("🔬 Medical Measurements")
    
    trestbps = st.number_input(
        "Resting Blood Pressure (mm Hg)",
        min_value=80,
        max_value=200,
        value=120,
        help="Enter your resting blood pressure"
    )
    user_input['trestbps'] = trestbps

    chol = st.number_input(
        "Serum Cholesterol (mg/dL)",
        min_value=100,
        max_value=600,
        value=200,
        help="Enter your serum cholesterol level"
    )
    user_input['chol'] = chol

    fbs = st.selectbox(
        "Fasting Blood Sugar > 120 mg/dL",
        ["No", "Yes"],
        help="Select if your fasting blood sugar is above 120 mg/dL"
    )
    user_input['fbs'] = 1 if fbs == "Yes" else 0

    restecg = st.selectbox(
        "Resting ECG Results",
        list(feature_maps['restecg'].keys()),
        help="Select your resting ECG results"
    )
    user_input['restecg'] = feature_maps['restecg'][restecg]

    ca = st.number_input(
        "Number of Major Vessels (0-3)",
        min_value=0,
        max_value=3,
        value=0,
        help="Number of major vessels colored by fluoroscopy"
    )
    user_input['ca'] = ca

    thal = st.selectbox(
        "Thalassemia",
        list(feature_maps['thal'].keys()),
        help="Select your thalassemia type"
    )
    user_input['thal'] = feature_maps['thal'][thal]

# Additional inputs in two columns
col3, col4 = st.columns(2)

with col3:
    thalach = st.number_input(
        "Maximum Heart Rate",
        min_value=60,
        max_value=220,
        value=150,
        help="Enter your maximum heart rate achieved"
    )
    user_input['thalach'] = thalach

    oldpeak = st.number_input(
        "ST Depression",
        min_value=0.0,
        max_value=10.0,
        value=0.0,
        help="Enter your ST depression induced by exercise relative to rest"
    )
    user_input['oldpeak'] = oldpeak

with col4:
    exang = st.selectbox(
        "Exercise Induced Angina",
        ["No", "Yes"],
        help="Select if you experience angina due to exercise"
    )
    user_input['exang'] = 1 if exang == "Yes" else 0

    slope = st.selectbox(
        "ST Slope",
        ["Upsloping", "Flat", "Downsloping"],
        help="Select the slope of your peak exercise ST segment"
    )
    user_input['slope'] = feature_maps['slope'][slope]

# Process button
with st.form("prediction_form"):
    prediction_submitted = st.form_submit_button("Generate Risk Assessment")
    
    if prediction_submitted:
        # Show loading spinner
        with st.spinner("Analyzing your health data and generating risk assessment..."):
            # Create report generator instance
            report_gen = ReportGenerator()
            
            # Prepare input data
            input_data = {
                'age': user_input['age'],
                'sex': user_input['sex'],
                'cp': user_input['cp'],
                'trestbps': user_input['trestbps'],
                'chol': user_input['chol'],
                'fbs': user_input['fbs'],
                'restecg': user_input['restecg'],
                'thalach': user_input['thalach'],
                'exang': user_input['exang'],
                'oldpeak': user_input['oldpeak'],
                'slope': user_input['slope'],
                'ca': user_input['ca'],
                'thal': user_input['thal']
            }
            
            try:
                # Create DataFrame and scale input
                input_df = pd.DataFrame([input_data])
                
                # Validate input data
                validation_result = validate_input(input_data)
                if not validation_result['valid']:
                    st.error(f"Input validation error: {validation_result['message']}")
                    st.info("Please check your input values and try again.")
                    st.stop()
                    
                try:
                    input_scaled = scaler.transform(input_df)
                except Exception as scaling_error:
                    st.error(f"Error processing input data: {str(scaling_error)}")
                    st.info("This might be due to unexpected input format. Please try again.")
                    st.stop()
                
                # Get prediction and probability
                try:
                    risk_prob = model.predict_proba(input_scaled)[0][1]
                    st.session_state.risk_score = risk_prob * 100
                    st.session_state.recommendations = generate_health_recommendations(input_data, risk_prob)
                    st.session_state.input_data = input_data  # Store input data for later use
                except Exception as prediction_error:
                    st.error(f"Error generating prediction: {str(prediction_error)}")
                    st.info("Please try again or contact support if the issue persists.")
                    st.stop()

                # Display gauge chart
                st.subheader("Risk Assessment Results")
                fig = create_gauge_chart(risk_prob)
                st.plotly_chart(fig, use_container_width=True)

                # Display risk assessment message
                if st.session_state.risk_score > 50:
                    st.error("⚠️ High Risk Alert")
                    st.markdown("""
                    ### Immediate Action Required
                    Based on your health metrics, you are at high risk for heart disease. 
                    It is strongly recommended that you consult a healthcare professional as soon as possible.
                    """)
                else:
                    st.success("✅ Lower Risk Assessment")
                    st.markdown("""
                    ### Preventive Recommendations
                    While your risk level is lower, it's important to maintain good heart health through lifestyle modifications.
                    """)

                # Display recommendations
                st.subheader("Detailed Recommendations")
                for rec in st.session_state.recommendations:
                    with st.expander(rec['category']):
                        st.write(rec['advice'])
                        for step in rec['steps']:
                            st.write(f"• {step}")

            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
                st.info("Please try again or contact support if the issue persists.")

# Audio Report Section - Completely outside the prediction form
if st.session_state.risk_score is not None:
    st.markdown("---")
    st.subheader("🔊 Audio Report")

    # Create a container for audio generation
    audio_container = st.container()
    
    with audio_container:
        # Language selection
        selected_language = st.selectbox(
            "Select Language for Audio Report:",
            options=list(LANGUAGES.keys()),
            index=list(LANGUAGES.keys()).index(st.session_state.language),
            key="language_select_audio"
        )
        
        # Update session state language
        st.session_state.language = selected_language
        
        # Generate audio button
        if st.button("🎵 Generate Audio Report", key="generate_audio_btn"):
            try:
                lang_code = LANGUAGES[selected_language]["code"]
                
                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Generate audio
                status_text.text("Generating audio report...")
                progress_bar.progress(25)
                
                audio_content = generate_audio_report(
                    risk_score=st.session_state.risk_score,
                    recommendations=st.session_state.recommendations,
                    language_code=lang_code
                )
                
                progress_bar.progress(75)
                status_text.text("Audio generated successfully!")
                
                # Store in session state
                st.session_state.audio_content[lang_code] = audio_content
                
                progress_bar.progress(100)
                status_text.text("✅ Audio report ready!")
                
                # Show success message
                st.success(f"Audio report generated successfully in {LANGUAGES[selected_language]['name']}")
                
            except Exception as e:
                st.error(f"Error generating audio: {str(e)}")
                st.info("This might be due to network connectivity issues. Please try again.")

    # Display all generated audio reports in a separate container
    if st.session_state.audio_content:
        st.markdown("### 📻 Available Audio Reports")
        
        for lang_code, audio_data in st.session_state.audio_content.items():
            lang_name = next((lang['name'] for lang in LANGUAGES.values() if lang['code'] == lang_code), lang_code)
            
            # Create a container for each audio report
            with st.container():
                st.markdown(f"**🎵 {lang_name} Audio Report**")
                
                # Audio player
                st.audio(audio_data, format='audio/mp3')
                
                # Download button in a separate container
                download_container = st.container()
                with download_container:
                    st.download_button(
                        label=f"📥 Download {lang_name} Report (MP3)",
                        data=audio_data,
                        file_name=f"heart_health_report_{lang_code}.mp3",
                        mime="audio/mp3",
                        key=f"download_audio_{lang_code}_{hash(audio_data) % 10000}"
                    )
                
                st.markdown("---")
    else:
        st.info("No audio reports generated yet. Select a language and click 'Generate Audio Report' above.")

    # Written Report Section
    st.markdown("---")
    st.subheader("📄 Written Report")
    
    # Create a container for PDF generation
    pdf_container = st.container()
    
    with pdf_container:
        try:
            report_gen = ReportGenerator()
            report_pdf = report_gen.generate_report(
                st.session_state.input_data, 
                st.session_state.risk_score,
                st.session_state.recommendations
            )
            
            st.download_button(
                label="📥 Download Written Report (PDF)",
                data=report_pdf,
                file_name="heart_health_report.pdf",
                mime="application/pdf",
                key=f"download_pdf_{hash(report_pdf) % 10000}"
            )
        except Exception as e:
            st.error(f"Error generating PDF report: {str(e)}")

# Footer
st.markdown("---")

# Add a clear button to reset the session state
if st.session_state.risk_score is not None:
    if st.button("🔄 Start New Assessment"):
        # Clear session state
        st.session_state.risk_score = None
        st.session_state.recommendations = None
        st.session_state.audio_content = {}
        st.session_state.input_data = None
        st.rerun()

st.markdown("""
<div style='text-align: center'>
    <p><small>This tool is for educational purposes only and should not replace professional medical advice.</small></p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    pass