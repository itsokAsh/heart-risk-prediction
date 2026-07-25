"""Health recommendations generator — ported exactly from utils.py lines 296-423."""

from typing import Any

from ml.constants import (
    CATEGORY_IMMEDIATE,
    CATEGORY_PREVENTIVE,
    CATEGORY_LIFESTYLE,
    CATEGORY_DIET,
    CATEGORY_EXERCISE,
    HIGH_RISK_THRESHOLD,
)


def generate_health_recommendations(user_input: dict[str, Any], risk_score: float) -> list[dict[str, Any]]:
    """
    Generate personalized health recommendations based on user input and risk score.
    risk_score is expected as a 0-1 probability (not percentage).
    """
    recommendations: list[dict[str, Any]] = []

    # Risk-based recommendations
    if risk_score > (HIGH_RISK_THRESHOLD / 100.0):
        risk_rec = {
            "category": CATEGORY_IMMEDIATE,
            "advice": "Please take these steps as soon as possible to protect your heart health:",
            "steps": [
                "Schedule an appointment with a cardiologist within the next week",
                "Begin monitoring your blood pressure daily and keep a log",
                "Start keeping a detailed health diary of any symptoms",
                "Review your current medications with your doctor",
                "Consider scheduling a stress test evaluation",
                "Have an emergency contact plan ready",
            ],
        }
    else:
        risk_rec = {
            "category": CATEGORY_PREVENTIVE,
            "advice": "Great job! Here are some steps to keep your heart healthy:",
            "steps": [
                "Schedule regular check-ups with your primary care physician",
                "Maintain a consistent exercise routine",
                "Keep tracking your blood pressure periodically",
                "Focus on heart-healthy dietary choices",
                "Stay up to date with your health screenings",
            ],
        }
    recommendations.append(risk_rec)

    # Lifestyle recommendations based on metrics
    lifestyle_rec: dict[str, Any] = {
        "category": CATEGORY_LIFESTYLE,
        "advice": "Here are some lifestyle changes that can make a big difference:",
        "steps": [],
    }

    if user_input["trestbps"] > 130:
        lifestyle_rec["steps"].extend([
            "Reduce sodium intake to less than 2,300mg daily (about 1 teaspoon of salt)",
            "Practice stress-reduction techniques like deep breathing or meditation",
            "Consider following the DASH diet approach for blood pressure control",
            "Limit alcohol consumption to moderate levels",
        ])

    if user_input["chol"] > 200:
        lifestyle_rec["steps"].extend([
            "Increase consumption of omega-3 rich foods like fatty fish",
            "Reduce saturated fat intake from red meat and dairy",
            "Add more fiber to your diet through whole grains and vegetables",
            "Consider adding plant sterols to your diet",
        ])

    if user_input["thalach"] < 150:
        lifestyle_rec["steps"].extend([
            "Start a graduated exercise program approved by your doctor",
            "Consider cardiac rehabilitation if recommended",
            "Focus on aerobic exercises like walking, swimming, or cycling",
            "Build up your exercise tolerance gradually",
        ])

    if user_input["exang"] == 1:
        lifestyle_rec["steps"].extend([
            "Work with a physical therapist for safe exercise planning",
            "Learn to recognize exercise-related warning signs",
            "Keep nitroglycerin handy if prescribed by your doctor",
            "Avoid exercising in extreme temperatures",
        ])

    if not lifestyle_rec["steps"]:
        lifestyle_rec["steps"].extend([
            "Aim for 7-8 hours of quality sleep each night",
            "Practice stress management techniques regularly",
            "Maintain a healthy weight through balanced diet and exercise",
            "Avoid smoking and limit exposure to secondhand smoke",
        ])

    recommendations.append(lifestyle_rec)

    # Diet recommendations
    diet_rec = {
        "category": CATEGORY_DIET,
        "advice": "Your diet plays a crucial role in heart health. Here are some simple guidelines:",
        "steps": [
            "Eat a variety of colorful fruits and vegetables daily (aim for 5-7 servings)",
            "Choose whole grains over refined grains (brown rice, whole wheat bread)",
            "Select lean proteins like fish, chicken, and plant-based options",
            "Limit processed foods and added sugars",
            "Stay hydrated with water throughout the day (aim for 8 glasses)",
            "Use healthy cooking methods like grilling, baking, or steaming",
        ],
    }
    recommendations.append(diet_rec)

    # Exercise recommendations
    exercise_rec: dict[str, Any] = {
        "category": CATEGORY_EXERCISE,
        "advice": "Regular physical activity is essential for heart health. Here's a plan for you:",
        "steps": [],
    }

    if risk_score > (HIGH_RISK_THRESHOLD / 100.0):
        exercise_rec["steps"].extend([
            "Begin with supervised exercise sessions under medical guidance",
            "Start with short, low-intensity walks (5-10 minutes)",
            "Gradually increase activity as approved by your doctor",
            "Monitor your heart rate during exercise",
            "Stop activity immediately if you experience chest pain or shortness of breath",
            "Consider joining a cardiac rehabilitation program",
        ])
    else:
        exercise_rec["steps"].extend([
            "Aim for 150 minutes of moderate activity weekly (30 minutes, 5 days/week)",
            "Include both cardio and strength training in your routine",
            "Try activities like brisk walking, swimming, or cycling",
            "Exercise with a partner when possible for motivation and safety",
            "Track your progress with a fitness app or journal",
            "Make exercise a fun part of your daily routine",
        ])

    recommendations.append(exercise_rec)

    return recommendations
