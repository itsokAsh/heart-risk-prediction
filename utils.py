import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
import plotly.graph_objects as go
from datetime import datetime
import os
from fpdf import FPDF
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from gtts import gTTS

# Constants for feature ranges and mappings
FEATURE_RANGES = {
    'age': (29, 77),
    'trestbps': (94, 200),
    'chol': (126, 564),
    'thalach': (71, 202),
    'oldpeak': (0.0, 6.2)
}

CATEGORICAL_MAPPINGS = {
    'cp': {
        'Typical Angina': 0,
        'Atypical Angina': 1,
        'Non-Anginal Pain': 2,
        'Asymptomatic': 3
    },
    'restecg': {
        'Normal': 0,
        'ST-T Wave Abnormality': 1,
        'Left Ventricular Hypertrophy': 2
    },
    'slope': {
        'Upsloping': 0,
        'Flat': 1,
        'Downsloping': 2
    },
    'thal': {
        'Normal': 0,
        'Fixed Defect': 1,
        'Reversible Defect': 2
    },
    'sex': [0, 1],
    'fbs': [0, 1],
    'exang': [0, 1]
}

# Valid ranges for numerical inputs
VALID_RANGES = {
    'age': (20, 100),
    'trestbps': (80, 200),
    'chol': (100, 600),
    'thalach': (60, 220),
    'oldpeak': (0.0, 10.0),
    'ca': (0, 3)
}

def validate_input(data):
    """
    Validate user input against predefined ranges and categories.
    """
    # Check numerical values
    for field, (min_val, max_val) in VALID_RANGES.items():
        if field in data:
            value = data[field]
            if not (min_val <= value <= max_val):
                return {
                    'valid': False,
                    'message': f"{field.replace('_', ' ').title()} must be between {min_val} and {max_val}"
                }

    # Check categorical values
    for field, valid_values in CATEGORICAL_MAPPINGS.items():
        if field in data:
            if isinstance(valid_values, dict):
                # For dictionary mappings (like cp, restecg, slope, thal)
                if data[field] not in valid_values.values():
                    return {
                        'valid': False,
                        'message': f"Invalid value for {field.replace('_', ' ').title()}"
                    }
            elif isinstance(valid_values, list):
                # For list mappings (like sex, smoking, etc.)
                if data[field] not in valid_values:
                    return {
                        'valid': False,
                        'message': f"Invalid value for {field.replace('_', ' ').title()}"
                    }

    return {'valid': True, 'message': 'All inputs are valid'}

def create_gauge_chart(risk_score):
    """
    Create a gauge chart visualization for the risk score.
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Risk Score", 'font': {'size': 24}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 20], 'color': "lightgreen"},
                {'range': [20, 40], 'color': "yellow"},
                {'range': [40, 100], 'color': "salmon"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': risk_score * 100
            }
        }
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=50, b=10),
        font={'size': 16}
    )

    return fig

def generate_audio_report(risk_score, recommendations, language_code):
    """
    Generate an audio report in the specified language with human-like, simple explanations.
    """
    try:
        # Create conversational report text based on language
        report_texts = {
            "en": {
                "intro": "Hello there! I have your heart health assessment ready. Let me explain what we found in simple terms.",
                "high_risk": "I need to be very clear with you - your risk score is {score:.1f} percent, which is quite high. This means you have a significant chance of developing heart problems. I'm not trying to scare you, but this is serious and you need to take action right away.",
                "low_risk": "Good news! Your risk score is {score:.1f} percent, which is relatively low. This means your heart is in pretty good shape, but there's always room for improvement to keep it that way.",
                "explanation": "Let me break down what this means for you in everyday terms:",
                "high_risk_explanation": "Think of your heart like a car engine. Right now, it's showing some warning signs that it might have trouble in the future. This doesn't mean you're having a heart attack right now, but it does mean you need to see a doctor soon to prevent problems.",
                "low_risk_explanation": "Your heart is working well right now, like a car that's running smoothly. But just like a car needs regular maintenance, your heart needs ongoing care to stay healthy.",
                "recommendations": "Here's what I recommend you do:",
                "immediate_action": "Most importantly, if your risk is high, please make an appointment with your doctor or cardiologist as soon as possible. Don't wait - early action can save your life.",
                "lifestyle_tips": "For your daily life, here are some simple things you can start doing:",
                "closing": "Remember, this is just a computer assessment to help guide you. Your doctor knows you best and can give you personalized advice. Take care of your heart - it's the only one you've got!",
                "emergency": "If you experience chest pain, shortness of breath, or feel like something is seriously wrong, call emergency services immediately. Don't wait to see if it gets better."
            },
            "es": {
                "intro": "¡Hola! Tengo tu evaluación de salud cardíaca lista. Déjame explicarte lo que encontramos en términos simples.",
                "high_risk": "Necesito ser muy claro contigo - tu puntaje de riesgo es {score:.1f} por ciento, que es bastante alto. Esto significa que tienes una probabilidad significativa de desarrollar problemas cardíacos. No quiero asustarte, pero esto es serio y necesitas tomar acción inmediatamente.",
                "low_risk": "¡Buenas noticias! Tu puntaje de riesgo es {score:.1f} por ciento, que es relativamente bajo. Esto significa que tu corazón está en bastante buen estado, pero siempre hay espacio para mejorar.",
                "explanation": "Déjame explicarte lo que esto significa para ti en términos cotidianos:",
                "high_risk_explanation": "Piensa en tu corazón como el motor de un carro. En este momento, está mostrando algunas señales de advertencia de que podría tener problemas en el futuro. Esto no significa que estés teniendo un ataque cardíaco ahora, pero sí significa que necesitas ver a un doctor pronto para prevenir problemas.",
                "low_risk_explanation": "Tu corazón está funcionando bien ahora, como un carro que funciona suavemente. Pero así como un carro necesita mantenimiento regular, tu corazón necesita cuidado continuo para mantenerse saludable.",
                "recommendations": "Aquí está lo que te recomiendo hacer:",
                "immediate_action": "Lo más importante, si tu riesgo es alto, por favor haz una cita con tu doctor o cardiólogo lo antes posible. No esperes - la acción temprana puede salvar tu vida.",
                "lifestyle_tips": "Para tu vida diaria, aquí hay algunas cosas simples que puedes empezar a hacer:",
                "closing": "Recuerda, esto es solo una evaluación computarizada para guiarte. Tu doctor te conoce mejor y puede darte consejos personalizados. Cuida tu corazón - ¡es el único que tienes!",
                "emergency": "Si experimentas dolor en el pecho, dificultad para respirar, o sientes que algo está seriamente mal, llama a servicios de emergencia inmediatamente. No esperes a ver si mejora."
            },
            "fr": {
                "intro": "Bonjour ! J'ai votre évaluation de santé cardiaque prête. Laissez-moi vous expliquer ce que nous avons trouvé en termes simples.",
                "high_risk": "Je dois être très clair avec vous - votre score de risque est de {score:.1f} pour cent, ce qui est assez élevé. Cela signifie que vous avez une probabilité significative de développer des problèmes cardiaques. Je ne veux pas vous faire peur, mais c'est sérieux et vous devez agir immédiatement.",
                "low_risk": "Bonne nouvelle ! Votre score de risque est de {score:.1f} pour cent, ce qui est relativement faible. Cela signifie que votre cœur est en assez bon état, mais il y a toujours place à l'amélioration.",
                "explanation": "Laissez-moi vous expliquer ce que cela signifie pour vous en termes quotidiens :",
                "high_risk_explanation": "Pensez à votre cœur comme au moteur d'une voiture. En ce moment, il montre des signes d'avertissement qu'il pourrait avoir des problèmes à l'avenir. Cela ne signifie pas que vous faites une crise cardiaque maintenant, mais cela signifie que vous devez voir un médecin bientôt pour prévenir les problèmes.",
                "low_risk_explanation": "Votre cœur fonctionne bien maintenant, comme une voiture qui roule en douceur. Mais comme une voiture a besoin d'entretien régulier, votre cœur a besoin de soins continus pour rester en bonne santé.",
                "recommendations": "Voici ce que je vous recommande de faire :",
                "immediate_action": "Le plus important, si votre risque est élevé, veuillez prendre rendez-vous avec votre médecin ou cardiologue dès que possible. N'attendez pas - une action précoce peut sauver votre vie.",
                "lifestyle_tips": "Pour votre vie quotidienne, voici quelques choses simples que vous pouvez commencer à faire :",
                "closing": "N'oubliez pas, ceci n'est qu'une évaluation informatique pour vous guider. Votre médecin vous connaît mieux et peut vous donner des conseils personnalisés. Prenez soin de votre cœur - c'est le seul que vous ayez !",
                "emergency": "Si vous ressentez une douleur thoracique, un essoufflement, ou sentez que quelque chose ne va vraiment pas, appelez immédiatement les services d'urgence. N'attendez pas de voir si cela s'améliore."
            },
            "de": {
                "intro": "Hallo! Ich habe Ihre Herzgesundheitsbewertung bereit. Lassen Sie mich erklären, was wir in einfachen Begriffen gefunden haben.",
                "high_risk": "Ich muss sehr klar mit Ihnen sein - Ihr Risikoscore beträgt {score:.1f} Prozent, was ziemlich hoch ist. Das bedeutet, dass Sie eine erhebliche Wahrscheinlichkeit haben, Herzprobleme zu entwickeln. Ich will Sie nicht erschrecken, aber das ist ernst und Sie müssen sofort handeln.",
                "low_risk": "Gute Nachrichten! Ihr Risikoscore beträgt {score:.1f} Prozent, was relativ niedrig ist. Das bedeutet, dass Ihr Herz in ziemlich gutem Zustand ist, aber es gibt immer Raum für Verbesserungen.",
                "explanation": "Lassen Sie mich erklären, was das für Sie in alltäglichen Begriffen bedeutet:",
                "high_risk_explanation": "Denken Sie an Ihr Herz wie an einen Automotor. Im Moment zeigt es einige Warnzeichen, dass es in Zukunft Probleme haben könnte. Das bedeutet nicht, dass Sie jetzt einen Herzinfarkt haben, aber es bedeutet, dass Sie bald einen Arzt aufsuchen müssen, um Probleme zu verhindern.",
                "low_risk_explanation": "Ihr Herz funktioniert jetzt gut, wie ein Auto, das sanft läuft. Aber wie ein Auto regelmäßige Wartung braucht, braucht Ihr Herz kontinuierliche Pflege, um gesund zu bleiben.",
                "recommendations": "Hier ist, was ich Ihnen empfehle zu tun:",
                "immediate_action": "Am wichtigsten ist, wenn Ihr Risiko hoch ist, vereinbaren Sie bitte so schnell wie möglich einen Termin bei Ihrem Arzt oder Kardiologen. Warten Sie nicht - frühes Handeln kann Ihr Leben retten.",
                "lifestyle_tips": "Für Ihr tägliches Leben, hier sind einige einfache Dinge, die Sie anfangen können zu tun:",
                "closing": "Denken Sie daran, dies ist nur eine Computerbewertung, um Sie zu führen. Ihr Arzt kennt Sie am besten und kann Ihnen personalisierte Ratschläge geben. Kümmern Sie sich um Ihr Herz - es ist das einzige, das Sie haben!",
                "emergency": "Wenn Sie Brustschmerzen, Atemnot verspüren oder das Gefühl haben, dass etwas ernsthaft nicht stimmt, rufen Sie sofort den Notdienst an. Warten Sie nicht, um zu sehen, ob es besser wird."
            },
            "it": {
                "intro": "Ciao! Ho la tua valutazione della salute del cuore pronta. Lasciami spiegare cosa abbiamo trovato in termini semplici.",
                "high_risk": "Devo essere molto chiaro con te - il tuo punteggio di rischio è del {score:.1f} percento, che è abbastanza alto. Questo significa che hai una probabilità significativa di sviluppare problemi cardiaci. Non voglio spaventarti, ma questo è serio e devi agire immediatamente.",
                "low_risk": "Buone notizie! Il tuo punteggio di rischio è del {score:.1f} percento, che è relativamente basso. Questo significa che il tuo cuore è in condizioni abbastanza buone, ma c'è sempre spazio per miglioramenti.",
                "explanation": "Lasciami spiegare cosa significa questo per te in termini quotidiani:",
                "high_risk_explanation": "Pensa al tuo cuore come al motore di un'auto. In questo momento, sta mostrando alcuni segnali di avvertimento che potrebbe avere problemi in futuro. Questo non significa che stai avendo un attacco di cuore ora, ma significa che devi vedere un medico presto per prevenire problemi.",
                "low_risk_explanation": "Il tuo cuore sta funzionando bene ora, come un'auto che gira dolcemente. Ma come un'auto ha bisogno di manutenzione regolare, il tuo cuore ha bisogno di cure continue per rimanere sano.",
                "recommendations": "Ecco cosa ti consiglio di fare:",
                "immediate_action": "Più importante, se il tuo rischio è alto, per favore fai un appuntamento con il tuo medico o cardiologo il prima possibile. Non aspettare - l'azione precoce può salvare la tua vita.",
                "lifestyle_tips": "Per la tua vita quotidiana, ecco alcune cose semplici che puoi iniziare a fare:",
                "closing": "Ricorda, questa è solo una valutazione computerizzata per guidarti. Il tuo medico ti conosce meglio e può darti consigli personalizzati. Prenditi cura del tuo cuore - è l'unico che hai!",
                "emergency": "Se provi dolore al petto, mancanza di respiro, o senti che qualcosa non va seriamente, chiama immediatamente i servizi di emergenza. Non aspettare di vedere se migliora."
            },
            "pt": {
                "intro": "Olá! Tenho sua avaliação de saúde cardíaca pronta. Deixe-me explicar o que encontramos em termos simples.",
                "high_risk": "Preciso ser muito claro com você - sua pontuação de risco é de {score:.1f} por cento, que é bastante alta. Isso significa que você tem uma probabilidade significativa de desenvolver problemas cardíacos. Não quero assustá-lo, mas isso é sério e você precisa agir imediatamente.",
                "low_risk": "Boas notícias! Sua pontuação de risco é de {score:.1f} por cento, que é relativamente baixa. Isso significa que seu coração está em bastante bom estado, mas sempre há espaço para melhorias.",
                "explanation": "Deixe-me explicar o que isso significa para você em termos cotidianos:",
                "high_risk_explanation": "Pense em seu coração como o motor de um carro. Agora, está mostrando alguns sinais de aviso de que pode ter problemas no futuro. Isso não significa que você está tendo um ataque cardíaco agora, mas significa que você precisa ver um médico logo para prevenir problemas.",
                "low_risk_explanation": "Seu coração está funcionando bem agora, como um carro que funciona suavemente. Mas como um carro precisa de manutenção regular, seu coração precisa de cuidados contínuos para se manter saudável.",
                "recommendations": "Aqui está o que eu recomendo que você faça:",
                "immediate_action": "Mais importante, se seu risco é alto, por favor marque uma consulta com seu médico ou cardiologista o mais rápido possível. Não espere - ação precoce pode salvar sua vida.",
                "lifestyle_tips": "Para sua vida diária, aqui estão algumas coisas simples que você pode começar a fazer:",
                "closing": "Lembre-se, esta é apenas uma avaliação computadorizada para guiá-lo. Seu médico o conhece melhor e pode dar-lhe conselhos personalizados. Cuide do seu coração - é o único que você tem!",
                "emergency": "Se você sentir dor no peito, falta de ar, ou sentir que algo está seriamente errado, chame os serviços de emergência imediatamente. Não espere para ver se melhora."
            },
            "hi": {
                "intro": "नमस्ते! मेरे पास आपकी हृदय स्वास्थ्य मूल्यांकन तैयार है। मुझे सरल शब्दों में बताएं कि हमने क्या पाया।",
                "high_risk": "मुझे आपके साथ बहुत स्पष्ट होना चाहिए - आपका जोखिम स्कोर {score:.1f} प्रतिशत है, जो काफी अधिक है। इसका मतलब है कि आपको हृदय की समस्याएं विकसित होने की महत्वपूर्ण संभावना है। मैं आपको डराना नहीं चाहता, लेकिन यह गंभीर है और आपको तुरंत कार्रवाई करने की आवश्यकता है।",
                "low_risk": "अच्छी खबर! आपका जोखिम स्कोर {score:.1f} प्रतिशत है, जो अपेक्षाकृत कम है। इसका मतलब है कि आपका दिल काफी अच्छी स्थिति में है, लेकिन हमेशा सुधार के लिए जगह है।",
                "explanation": "मुझे आपको रोजमर्रा के शब्दों में समझाएं कि इसका क्या मतलब है:",
                "high_risk_explanation": "अपने दिल के बारे में सोचें जैसे कार का इंजन। अभी, यह कुछ चेतावनी संकेत दिखा रहा है कि भविष्य में इसे समस्याएं हो सकती हैं। इसका मतलब यह नहीं है कि आपको अभी दिल का दौरा पड़ रहा है, लेकिन इसका मतलब है कि आपको समस्याओं को रोकने के लिए जल्द ही डॉक्टर से मिलने की जरूरत है।",
                "low_risk_explanation": "आपका दिल अभी अच्छी तरह से काम कर रहा है, जैसे कार जो नरमी से चलती है। लेकिन जैसे कार को नियमित रखरखाव की जरूरत होती है, वैसे ही आपके दिल को स्वस्थ रहने के लिए निरंतर देखभाल की जरूरत होती है।",
                "recommendations": "यहां मैं आपको क्या करने की सलाह देता हूं:",
                "immediate_action": "सबसे महत्वपूर्ण, यदि आपका जोखिम अधिक है, तो कृपया जितनी जल्दी हो सके अपने डॉक्टर या कार्डियोलॉजिस्ट से मिलें। इंतजार न करें - जल्दी की कार्रवाई आपकी जान बचा सकती है।",
                "lifestyle_tips": "आपके दैनिक जीवन के लिए, यहां कुछ सरल चीजें हैं जो आप करना शुरू कर सकते हैं:",
                "closing": "याद रखें, यह सिर्फ आपको मार्गदर्शन करने के लिए एक कंप्यूटर मूल्यांकन है। आपका डॉक्टर आपको सबसे अच्छी तरह जानता है और आपको व्यक्तिगत सलाह दे सकता है। अपने दिल की देखभाल करें - यही एकमात्र है जो आपके पास है!",
                "emergency": "यदि आपको छाती में दर्द, सांस लेने में कठिनाई, या लगता है कि कुछ गंभीर रूप से गलत है, तो तुरंत आपातकालीन सेवाओं को बुलाएं। यह देखने के लिए इंतजार न करें कि क्या यह बेहतर होता है।"
            },
            "zh-CN": {
                "intro": "您好！您的心脏健康评估已经准备好了。让我用简单的语言解释我们发现了什么。",
                "high_risk": "我需要非常清楚地告诉您 - 您的风险评分为{score:.1f}%，这相当高。这意味着您有显著的可能性发展心脏病问题。我不想吓唬您，但这很严重，您需要立即采取行动。",
                "low_risk": "好消息！您的风险评分为{score:.1f}%，相对较低。这意味着您的心脏状况相当好，但总有改进的空间。",
                "explanation": "让我用日常用语解释这对您意味着什么：",
                "high_risk_explanation": "把您的心脏想象成汽车发动机。现在，它显示了一些警告信号，表明将来可能会有问题。这并不意味着您现在正在心脏病发作，但这确实意味着您需要很快看医生来预防问题。",
                "low_risk_explanation": "您的心脏现在工作得很好，就像一辆平稳行驶的汽车。但就像汽车需要定期维护一样，您的心脏需要持续护理来保持健康。",
                "recommendations": "以下是我建议您做的：",
                "immediate_action": "最重要的是，如果您的风险很高，请尽快与您的医生或心脏病专家预约。不要等待 - 早期行动可以挽救您的生命。",
                "lifestyle_tips": "对于您的日常生活，以下是一些您可以开始做的简单事情：",
                "closing": "请记住，这只是为了指导您的计算机评估。您的医生最了解您，可以给您个性化的建议。照顾好您的心脏 - 这是您唯一拥有的！",
                "emergency": "如果您感到胸痛、呼吸急促，或感觉有什么严重问题，请立即呼叫紧急服务。不要等待看是否好转。"
            }
        }

        # Use English as fallback if language not available
        texts = report_texts.get(language_code, report_texts['en'])
        
        # Build the conversational report text
        report_text = texts['intro'] + " "
        
        if risk_score > 50:
            report_text += texts['high_risk'].format(score=risk_score) + " "
            report_text += texts['explanation'] + " "
            report_text += texts['high_risk_explanation'] + " "
        else:
            report_text += texts['low_risk'].format(score=risk_score) + " "
            report_text += texts['explanation'] + " "
            report_text += texts['low_risk_explanation'] + " "
        
        # Add immediate action advice
        report_text += texts['recommendations'] + " "
        if risk_score > 50:
            report_text += texts['immediate_action'] + " "
            report_text += texts['emergency'] + " "
        
        # Add lifestyle recommendations in simple terms
        report_text += texts['lifestyle_tips'] + " "
        for rec in recommendations:
            if rec['category'] in ['Lifestyle Modifications', 'Dietary Guidelines', 'Physical Activity Plan']:
                for step in rec['steps'][:2]:  # Limit to top 2 steps per category for brevity
                    report_text += step + ". "
        
        # Add closing message
        report_text += " " + texts['closing']

        # Generate audio using gTTS with error handling
        try:
            tts = gTTS(text=report_text, lang=language_code, slow=False)
            audio_file = BytesIO()
            tts.write_to_fp(audio_file)
            audio_file.seek(0)
            return audio_file.getvalue()
        except Exception as e:
            # Try with a fallback language if the requested language fails
            if language_code != "en":
                try:
                    tts = gTTS(text=report_text, lang="en", slow=False)
                    audio_file = BytesIO()
                    tts.write_to_fp(audio_file)
                    audio_file.seek(0)
                    return audio_file.getvalue()
                except Exception as fallback_error:
                    raise Exception(f"Failed to generate audio in both {language_code} and English: {str(e)} -> {str(fallback_error)}")
            else:
                raise Exception(f"Error generating audio in {language_code}: {str(e)}")

    except Exception as e:
        raise Exception(f"Error preparing audio report: {str(e)}")

def generate_health_recommendations(user_input, risk_score):
    """
    Generate personalized health recommendations based on user input and risk score.
    """
    recommendations = []
    
    # Risk-based recommendations
    if risk_score > 0.5:  # High risk
        risk_rec = {
            'category': '🚨 Immediate Actions Required',
            'advice': 'Please take these steps as soon as possible to protect your heart health:',
            'steps': [
                "Schedule an appointment with a cardiologist within the next week",
                "Begin monitoring your blood pressure daily and keep a log",
                "Start keeping a detailed health diary of any symptoms",
                "Review your current medications with your doctor",
                "Consider scheduling a stress test evaluation",
                "Have an emergency contact plan ready"
            ]
        }
    else:  # Lower risk
        risk_rec = {
            'category': '✅ Preventive Measures',
            'advice': 'Great job! Here are some steps to keep your heart healthy:',
            'steps': [
                "Schedule regular check-ups with your primary care physician",
                "Maintain a consistent exercise routine",
                "Keep tracking your blood pressure periodically",
                "Focus on heart-healthy dietary choices",
                "Stay up to date with your health screenings"
            ]
        }
    recommendations.append(risk_rec)
    
    # Lifestyle recommendations based on metrics
    lifestyle_rec = {
        'category': '💪 Lifestyle Modifications',
        'advice': 'Here are some lifestyle changes that can make a big difference:',
        'steps': []
    }
    
    if user_input['trestbps'] > 130:
        lifestyle_rec['steps'].extend([
            "Reduce sodium intake to less than 2,300mg daily (about 1 teaspoon of salt)",
            "Practice stress-reduction techniques like deep breathing or meditation",
            "Consider following the DASH diet approach for blood pressure control",
            "Limit alcohol consumption to moderate levels"
        ])
    
    if user_input['chol'] > 200:
        lifestyle_rec['steps'].extend([
            "Increase consumption of omega-3 rich foods like fatty fish",
            "Reduce saturated fat intake from red meat and dairy",
            "Add more fiber to your diet through whole grains and vegetables",
            "Consider adding plant sterols to your diet"
        ])
    
    if user_input['thalach'] < 150:
        lifestyle_rec['steps'].extend([
            "Start a graduated exercise program approved by your doctor",
            "Consider cardiac rehabilitation if recommended",
            "Focus on aerobic exercises like walking, swimming, or cycling",
            "Build up your exercise tolerance gradually"
        ])
    
    if user_input['exang'] == 1:
        lifestyle_rec['steps'].extend([
            "Work with a physical therapist for safe exercise planning",
            "Learn to recognize exercise-related warning signs",
            "Keep nitroglycerin handy if prescribed by your doctor",
            "Avoid exercising in extreme temperatures"
        ])
    
    # Add general lifestyle tips if no specific conditions
    if not lifestyle_rec['steps']:
        lifestyle_rec['steps'].extend([
            "Aim for 7-8 hours of quality sleep each night",
            "Practice stress management techniques regularly",
            "Maintain a healthy weight through balanced diet and exercise",
            "Avoid smoking and limit exposure to secondhand smoke"
        ])
    
    recommendations.append(lifestyle_rec)
    
    # Diet recommendations
    diet_rec = {
        'category': '🥗 Dietary Guidelines',
        'advice': 'Your diet plays a crucial role in heart health. Here are some simple guidelines:',
        'steps': [
            "Eat a variety of colorful fruits and vegetables daily (aim for 5-7 servings)",
            "Choose whole grains over refined grains (brown rice, whole wheat bread)",
            "Select lean proteins like fish, chicken, and plant-based options",
            "Limit processed foods and added sugars",
            "Stay hydrated with water throughout the day (aim for 8 glasses)",
            "Use healthy cooking methods like grilling, baking, or steaming"
        ]
    }
    recommendations.append(diet_rec)
    
    # Exercise recommendations
    exercise_rec = {
        'category': '🏃‍♂️ Physical Activity Plan',
        'advice': 'Regular physical activity is essential for heart health. Here\'s a plan for you:',
        'steps': []
    }
    
    if risk_score > 0.5:
        exercise_rec['steps'].extend([
            "Begin with supervised exercise sessions under medical guidance",
            "Start with short, low-intensity walks (5-10 minutes)",
            "Gradually increase activity as approved by your doctor",
            "Monitor your heart rate during exercise",
            "Stop activity immediately if you experience chest pain or shortness of breath",
            "Consider joining a cardiac rehabilitation program"
        ])
    else:
        exercise_rec['steps'].extend([
            "Aim for 150 minutes of moderate activity weekly (30 minutes, 5 days/week)",
            "Include both cardio and strength training in your routine",
            "Try activities like brisk walking, swimming, or cycling",
            "Exercise with a partner when possible for motivation and safety",
            "Track your progress with a fitness app or journal",
            "Make exercise a fun part of your daily routine"
        ])
    
    recommendations.append(exercise_rec)
    
    return recommendations

class ReportGenerator:
    """
    Generate PDF reports with assessment results and recommendations.
    """
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12
        )
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12
        )

    def generate_report(self, personal_info, risk_score, recommendations):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        
        # Build the document content
        content = []
        
        # Title
        content.append(Paragraph("Heart Health Assessment Report", self.title_style))
        content.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", self.body_style))
        content.append(Spacer(1, 20))

        # Executive Summary
        content.append(Paragraph("Executive Summary", self.heading_style))
        if risk_score > 50:
            content.append(Paragraph(
                f"Your heart disease risk assessment shows a <b>HIGH RISK</b> level of {risk_score:.1f}%. "
                "This requires immediate attention and medical consultation.", 
                self.body_style
            ))
        else:
            content.append(Paragraph(
                f"Your heart disease risk assessment shows a <b>LOWER RISK</b> level of {risk_score:.1f}%. "
                "While this is positive, maintaining heart health through lifestyle choices is important.", 
                self.body_style
            ))
        content.append(Spacer(1, 20))

        # Personal Information
        content.append(Paragraph("Your Health Information", self.heading_style))
        
        # Create a more readable format for personal info
        info_mapping = {
            'age': 'Age',
            'sex': 'Sex',
            'cp': 'Chest Pain Type',
            'trestbps': 'Resting Blood Pressure (mm Hg)',
            'chol': 'Cholesterol (mg/dL)',
            'fbs': 'High Blood Sugar (>120 mg/dL)',
            'restecg': 'ECG Results',
            'thalach': 'Maximum Heart Rate',
            'exang': 'Exercise-Induced Angina',
            'oldpeak': 'ST Depression',
            'slope': 'ST Slope',
            'ca': 'Major Vessels',
            'thal': 'Thalassemia'
        }
        
        # Value mappings for better readability
        value_mappings = {
            'sex': {0: 'Female', 1: 'Male'},
            'cp': {0: 'Typical Angina', 1: 'Atypical Angina', 2: 'Non-anginal Pain', 3: 'Asymptomatic'},
            'fbs': {0: 'No', 1: 'Yes'},
            'restecg': {0: 'Normal', 1: 'ST-T Wave Abnormality', 2: 'Left Ventricular Hypertrophy'},
            'exang': {0: 'No', 1: 'Yes'},
            'slope': {0: 'Upsloping', 1: 'Flat', 2: 'Downsloping'},
            'thal': {0: 'Normal', 1: 'Fixed Defect', 2: 'Reversible Defect'}
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
        
        if risk_score > 50:
            content.append(Paragraph(
                f"<b>Risk Level: HIGH ({risk_score:.1f}%)</b>", 
                ParagraphStyle('HighRisk', parent=self.body_style, textColor='red', fontSize=14)
            ))
            content.append(Paragraph(
                "What this means: Your assessment indicates a significant risk of heart disease. "
                "Think of your heart like a car engine showing warning signs - it doesn't mean you're having "
                "a heart attack right now, but it does mean you need to see a doctor soon to prevent problems.", 
                self.body_style
            ))
        else:
            content.append(Paragraph(
                f"<b>Risk Level: LOW TO MODERATE ({risk_score:.1f}%)</b>", 
                ParagraphStyle('LowRisk', parent=self.body_style, textColor='green', fontSize=14)
            ))
            content.append(Paragraph(
                "What this means: Your heart is working well right now, like a car that's running smoothly. "
                "But just like a car needs regular maintenance, your heart needs ongoing care to stay healthy.", 
                self.body_style
            ))
        content.append(Spacer(1, 20))

        # Immediate Action Required
        if risk_score > 50:
            content.append(Paragraph("🚨 IMMEDIATE ACTION REQUIRED", self.heading_style))
            content.append(Paragraph(
                "<b>Most importantly:</b> Please make an appointment with your doctor or cardiologist "
                "as soon as possible. Don't wait - early action can save your life.", 
                self.body_style
            ))
            content.append(Paragraph(
                "<b>Emergency Warning:</b> If you experience chest pain, shortness of breath, or feel like "
                "something is seriously wrong, call emergency services immediately. Don't wait to see if it gets better.", 
                self.body_style
            ))
            content.append(Spacer(1, 20))

        # Recommendations
        content.append(Paragraph("Your Personalized Health Recommendations", self.heading_style))
        content.append(Paragraph(
            "Here's what I recommend you do to improve your heart health:", 
            self.body_style
        ))
        
        for rec in recommendations:
            content.append(Paragraph(f"<b>{rec['category']}</b>", self.heading_style))
            content.append(Paragraph(rec['advice'], self.body_style))
            for step in rec['steps']:
                content.append(Paragraph(f"• {step}", self.body_style))
            content.append(Spacer(1, 10))

        # Lifestyle Tips Section
        content.append(Spacer(1, 20))
        content.append(Paragraph("Simple Daily Tips for Heart Health", self.heading_style))
        content.append(Paragraph(
            "Here are some simple things you can start doing today:", 
            self.body_style
        ))
        
        daily_tips = [
            "Take a 30-minute walk every day",
            "Eat more fruits and vegetables",
            "Reduce salt in your diet",
            "Get 7-8 hours of sleep",
            "Manage stress through relaxation techniques",
            "Stay hydrated by drinking water",
            "Limit processed foods and added sugars"
        ]
        
        for tip in daily_tips:
            content.append(Paragraph(f"• {tip}", self.body_style))

        # Important Disclaimer
        content.append(Spacer(1, 30))
        content.append(Paragraph("Important Medical Disclaimer", self.heading_style))
        content.append(Paragraph(
            "This assessment is for informational purposes only and should not replace professional medical advice. "
            "Your doctor knows you best and can give you personalized advice. Always consult with healthcare "
            "professionals for medical decisions. Take care of your heart - it's the only one you've got!", 
            self.body_style
        ))

        # Build and return the PDF
        doc.build(content)
        buffer.seek(0)
        return buffer.getvalue() 