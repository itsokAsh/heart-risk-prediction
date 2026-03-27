# Heart Disease Risk Prediction Application

This application provides a comprehensive heart disease risk assessment tool with interactive visualizations and detailed reporting capabilities.

## Features

- Heart disease risk prediction using machine learning
- Interactive gauge visualization of risk scores
- Input validation for health metrics
- Personalized health recommendations
- Detailed PDF report generation
- User-friendly web interface

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository:**
```bash
git clone https://github.com/itsokAsh/heart-risk-prediction.git
cd heart-risk-prediction
```

2. **Create a virtual environment (optional but recommended):**
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit application:
```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## Quick Start Guide

1. **Enter Your Health Metrics**: Fill in your health information on the left sidebar
2. **Get Risk Assessment**: View your heart disease risk prediction with a visual gauge
3. **Review Recommendations**: Read personalized health recommendations based on your profile
4. **Generate Report** (Optional): Export a PDF report of your assessment

## Project Structure

- `app.py`: Main Streamlit application
- `utils.py`: Utility functions for validation, visualization, and report generation
- `model/`: Directory containing trained model files
- `requirements.txt`: Project dependencies

## Dependencies

- Python 3.8+
- See `requirements.txt` for complete list of dependencies

## Notes

- All health recommendations are general guidelines. Always consult with healthcare professionals for medical advice.
- The risk prediction model is based on statistical analysis and should not be used as the sole basis for medical decisions.

## Input Features

- **Age**: Age in years
- **Sex**: Male/Female
- **Chest Pain Type**: Type of chest pain experienced
- **Blood Pressure**: Resting blood pressure (mm Hg)
- **Cholesterol**: Serum cholesterol level (mg/dL)
- **Blood Sugar**: Fasting blood sugar > 120 mg/dL
- **ECG Results**: Resting electrocardiographic results
- **Max Heart Rate**: Maximum heart rate achieved
- **Exercise Angina**: Exercise-induced angina
- **ST Depression**: ST depression induced by exercise
- **ST Slope**: Slope of peak exercise ST segment
- **Number of Vessels**: Number of major vessels colored by fluoroscopy
- **Thalassemia**: Type of thalassemia

## Model Details

The application uses an XGBoost classifier trained on the UCI Heart Disease dataset. The model is optimized for both accuracy and interpretability, with the following characteristics:

- Cross-validation during training
- Feature standardization
- Hyperparameter optimization
- Regular retraining capability

## Security and Privacy

- No personal health data is stored
- All processing is done locally
- PDF reports are generated on-demand and immediately removed
- No external API calls or data sharing

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This application is for educational purposes only and should not be used as a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition. 