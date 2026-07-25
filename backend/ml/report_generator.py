"""PDF report generator — ported exactly from utils.py ReportGenerator class."""

import logging
from datetime import datetime
from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from ml.constants import HIGH_RISK_THRESHOLD

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate PDF reports with assessment results and recommendations."""

    def __init__(self) -> None:
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            "CustomTitle",
            parent=self.styles["Heading1"],
            fontSize=24,
            spaceAfter=30,
        )
        self.heading_style = ParagraphStyle(
            "CustomHeading",
            parent=self.styles["Heading2"],
            fontSize=14,
            spaceAfter=12,
        )
        self.body_style = ParagraphStyle(
            "CustomBody",
            parent=self.styles["Normal"],
            fontSize=12,
            spaceAfter=12,
        )

    def generate_report(
        self,
        personal_info: dict[str, Any],
        risk_score: float,
        recommendations: list[dict[str, Any]],
    ) -> bytes:
        """Build the full PDF and return it as bytes."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )

        content: list = []

        # Title
        content.append(Paragraph("Heart Health Assessment Report", self.title_style))
        content.append(
            Paragraph(
                f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                self.body_style,
            )
        )
        content.append(Spacer(1, 20))

        # Executive Summary
        content.append(Paragraph("Executive Summary", self.heading_style))
        if risk_score > HIGH_RISK_THRESHOLD:
            content.append(
                Paragraph(
                    f"Your heart disease risk assessment shows a <b>HIGH RISK</b> level of {risk_score:.1f}%. "
                    "This requires immediate attention and medical consultation.",
                    self.body_style,
                )
            )
        else:
            content.append(
                Paragraph(
                    f"Your heart disease risk assessment shows a <b>LOWER RISK</b> level of {risk_score:.1f}%. "
                    "While this is positive, maintaining heart health through lifestyle choices is important.",
                    self.body_style,
                )
            )
        content.append(Spacer(1, 20))

        # Personal Information
        content.append(Paragraph("Your Health Information", self.heading_style))

        info_mapping = {
            "age": "Age",
            "sex": "Sex",
            "cp": "Chest Pain Type",
            "trestbps": "Resting Blood Pressure (mm Hg)",
            "chol": "Cholesterol (mg/dL)",
            "fbs": "High Blood Sugar (>120 mg/dL)",
            "restecg": "ECG Results",
            "thalach": "Maximum Heart Rate",
            "exang": "Exercise-Induced Angina",
            "oldpeak": "ST Depression",
            "slope": "ST Slope",
            "ca": "Major Vessels",
            "thal": "Thalassemia",
        }

        value_mappings: dict[str, dict[int, str]] = {
            "sex": {0: "Female", 1: "Male"},
            "cp": {0: "Typical Angina", 1: "Atypical Angina", 2: "Non-anginal Pain", 3: "Asymptomatic"},
            "fbs": {0: "No", 1: "Yes"},
            "restecg": {0: "Normal", 1: "ST-T Wave Abnormality", 2: "Left Ventricular Hypertrophy"},
            "exang": {0: "No", 1: "Yes"},
            "slope": {0: "Upsloping", 1: "Flat", 2: "Downsloping"},
            "thal": {1: "Normal", 2: "Fixed Defect", 3: "Reversible Defect"},
        }

        for key, value in personal_info.items():
            if key in info_mapping:
                display_key = info_mapping[key]
                if key in value_mappings:
                    display_value = value_mappings[key].get(value, str(value))
                else:
                    display_value = str(value)
                content.append(Paragraph(f"<b>{display_key}:</b> {display_value}", self.body_style))
        content.append(Spacer(1, 20))

        # Risk Assessment with Explanation
        content.append(Paragraph("Understanding Your Risk Assessment", self.heading_style))

        if risk_score > HIGH_RISK_THRESHOLD:
            content.append(
                Paragraph(
                    f"<b>Risk Level: HIGH ({risk_score:.1f}%)</b>",
                    ParagraphStyle("HighRisk", parent=self.body_style, textColor="red", fontSize=14),
                )
            )
            content.append(
                Paragraph(
                    "What this means: Your assessment indicates a significant risk of heart disease. "
                    "Think of your heart like a car engine showing warning signs - it doesn't mean you're having "
                    "a heart attack right now, but it does mean you need to see a doctor soon to prevent problems.",
                    self.body_style,
                )
            )
        else:
            content.append(
                Paragraph(
                    f"<b>Risk Level: LOW TO MODERATE ({risk_score:.1f}%)</b>",
                    ParagraphStyle("LowRisk", parent=self.body_style, textColor="green", fontSize=14),
                )
            )
            content.append(
                Paragraph(
                    "What this means: Your heart is working well right now, like a car that's running smoothly. "
                    "But just like a car needs regular maintenance, your heart needs ongoing care to stay healthy.",
                    self.body_style,
                )
            )
        content.append(Spacer(1, 20))

        # Immediate Action Required
        if risk_score > HIGH_RISK_THRESHOLD:
            content.append(Paragraph("\U0001f6a8 IMMEDIATE ACTION REQUIRED", self.heading_style))
            content.append(
                Paragraph(
                    "<b>Most importantly:</b> Please make an appointment with your doctor or cardiologist "
                    "as soon as possible. Don't wait - early action can save your life.",
                    self.body_style,
                )
            )
            content.append(
                Paragraph(
                    "<b>Emergency Warning:</b> If you experience chest pain, shortness of breath, or feel like "
                    "something is seriously wrong, call emergency services immediately. Don't wait to see if it gets better.",
                    self.body_style,
                )
            )
            content.append(Spacer(1, 20))

        # Recommendations
        content.append(Paragraph("Your Personalized Health Recommendations", self.heading_style))
        content.append(
            Paragraph(
                "Here's what I recommend you do to improve your heart health:",
                self.body_style,
            )
        )

        for rec in recommendations:
            content.append(Paragraph(f"<b>{rec['category']}</b>", self.heading_style))
            content.append(Paragraph(rec["advice"], self.body_style))
            for step in rec["steps"]:
                content.append(Paragraph(f"\u2022 {step}", self.body_style))
            content.append(Spacer(1, 10))

        # Lifestyle Tips Section
        content.append(Spacer(1, 20))
        content.append(Paragraph("Simple Daily Tips for Heart Health", self.heading_style))
        content.append(
            Paragraph(
                "Here are some simple things you can start doing today:",
                self.body_style,
            )
        )

        daily_tips = [
            "Take a 30-minute walk every day",
            "Eat more fruits and vegetables",
            "Reduce salt in your diet",
            "Get 7-8 hours of sleep",
            "Manage stress through relaxation techniques",
            "Stay hydrated by drinking water",
            "Limit processed foods and added sugars",
        ]

        for tip in daily_tips:
            content.append(Paragraph(f"\u2022 {tip}", self.body_style))

        # Important Disclaimer
        content.append(Spacer(1, 30))
        content.append(Paragraph("Important Medical Disclaimer", self.heading_style))
        content.append(
            Paragraph(
                "This assessment is for informational purposes only and should not replace professional medical advice. "
                "Your doctor knows you best and can give you personalized advice. Always consult with healthcare "
                "professionals for medical decisions. Take care of your heart - it's the only one you've got!",
                self.body_style,
            )
        )

        doc.build(content)
        buffer.seek(0)
        return buffer.getvalue()
