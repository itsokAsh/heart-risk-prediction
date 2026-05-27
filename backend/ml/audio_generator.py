"""Audio report generator — ported exactly from utils.py generate_audio_report()."""

import logging
from io import BytesIO
from typing import Any

from gtts import gTTS

logger = logging.getLogger(__name__)


def generate_audio_report(
    risk_score: float,
    recommendations: list[dict[str, Any]],
    language_code: str,
) -> bytes:
    """
    Generate an audio report in the specified language with human-like, simple explanations.
    risk_score is expected as a percentage (0-100).
    """
    try:
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
                "emergency": "If you experience chest pain, shortness of breath, or feel like something is seriously wrong, call emergency services immediately. Don't wait to see if it gets better.",
            },
            "es": {
                "intro": "\u00a1Hola! Tengo tu evaluaci\u00f3n de salud card\u00edaca lista. D\u00e9jame explicarte lo que encontramos en t\u00e9rminos simples.",
                "high_risk": "Necesito ser muy claro contigo - tu puntaje de riesgo es {score:.1f} por ciento, que es bastante alto. Esto significa que tienes una probabilidad significativa de desarrollar problemas card\u00edacos. No quiero asustarte, pero esto es serio y necesitas tomar acci\u00f3n inmediatamente.",
                "low_risk": "\u00a1Buenas noticias! Tu puntaje de riesgo es {score:.1f} por ciento, que es relativamente bajo. Esto significa que tu coraz\u00f3n est\u00e1 en bastante buen estado, pero siempre hay espacio para mejorar.",
                "explanation": "D\u00e9jame explicarte lo que esto significa para ti en t\u00e9rminos cotidianos:",
                "high_risk_explanation": "Piensa en tu coraz\u00f3n como el motor de un carro. En este momento, est\u00e1 mostrando algunas se\u00f1ales de advertencia de que podr\u00eda tener problemas en el futuro. Esto no significa que est\u00e9s teniendo un ataque card\u00edaco ahora, pero s\u00ed significa que necesitas ver a un doctor pronto para prevenir problemas.",
                "low_risk_explanation": "Tu coraz\u00f3n est\u00e1 funcionando bien ahora, como un carro que funciona suavemente. Pero as\u00ed como un carro necesita mantenimiento regular, tu coraz\u00f3n necesita cuidado continuo para mantenerse saludable.",
                "recommendations": "Aqu\u00ed est\u00e1 lo que te recomiendo hacer:",
                "immediate_action": "Lo m\u00e1s importante, si tu riesgo es alto, por favor haz una cita con tu doctor o cardi\u00f3logo lo antes posible. No esperes - la acci\u00f3n temprana puede salvar tu vida.",
                "lifestyle_tips": "Para tu vida diaria, aqu\u00ed hay algunas cosas simples que puedes empezar a hacer:",
                "closing": "Recuerda, esto es solo una evaluaci\u00f3n computarizada para guiarte. Tu doctor te conoce mejor y puede darte consejos personalizados. Cuida tu coraz\u00f3n - \u00a1es el \u00fanico que tienes!",
                "emergency": "Si experimentas dolor en el pecho, dificultad para respirar, o sientes que algo est\u00e1 seriamente mal, llama a servicios de emergencia inmediatamente. No esperes a ver si mejora.",
            },
            "fr": {
                "intro": "Bonjour ! J'ai votre \u00e9valuation de sant\u00e9 cardiaque pr\u00eate. Laissez-moi vous expliquer ce que nous avons trouv\u00e9 en termes simples.",
                "high_risk": "Je dois \u00eatre tr\u00e8s clair avec vous - votre score de risque est de {score:.1f} pour cent, ce qui est assez \u00e9lev\u00e9. Cela signifie que vous avez une probabilit\u00e9 significative de d\u00e9velopper des probl\u00e8mes cardiaques. Je ne veux pas vous faire peur, mais c'est s\u00e9rieux et vous devez agir imm\u00e9diatement.",
                "low_risk": "Bonne nouvelle ! Votre score de risque est de {score:.1f} pour cent, ce qui est relativement faible. Cela signifie que votre c\u0153ur est en assez bon \u00e9tat, mais il y a toujours place \u00e0 l'am\u00e9lioration.",
                "explanation": "Laissez-moi vous expliquer ce que cela signifie pour vous en termes quotidiens :",
                "high_risk_explanation": "Pensez \u00e0 votre c\u0153ur comme au moteur d'une voiture. En ce moment, il montre des signes d'avertissement qu'il pourrait avoir des probl\u00e8mes \u00e0 l'avenir. Cela ne signifie pas que vous faites une crise cardiaque maintenant, mais cela signifie que vous devez voir un m\u00e9decin bient\u00f4t pour pr\u00e9venir les probl\u00e8mes.",
                "low_risk_explanation": "Votre c\u0153ur fonctionne bien maintenant, comme une voiture qui roule en douceur. Mais comme une voiture a besoin d'entretien r\u00e9gulier, votre c\u0153ur a besoin de soins continus pour rester en bonne sant\u00e9.",
                "recommendations": "Voici ce que je vous recommande de faire :",
                "immediate_action": "Le plus important, si votre risque est \u00e9lev\u00e9, veuillez prendre rendez-vous avec votre m\u00e9decin ou cardiologue d\u00e8s que possible. N'attendez pas - une action pr\u00e9coce peut sauver votre vie.",
                "lifestyle_tips": "Pour votre vie quotidienne, voici quelques choses simples que vous pouvez commencer \u00e0 faire :",
                "closing": "N'oubliez pas, ceci n'est qu'une \u00e9valuation informatique pour vous guider. Votre m\u00e9decin vous conna\u00eet mieux et peut vous donner des conseils personnalis\u00e9s. Prenez soin de votre c\u0153ur - c'est le seul que vous ayez !",
                "emergency": "Si vous ressentez une douleur thoracique, un essoufflement, ou sentez que quelque chose ne va vraiment pas, appelez imm\u00e9diatement les services d'urgence. N'attendez pas de voir si cela s'am\u00e9liore.",
            },
            "de": {
                "intro": "Hallo! Ich habe Ihre Herzgesundheitsbewertung bereit. Lassen Sie mich erkl\u00e4ren, was wir in einfachen Begriffen gefunden haben.",
                "high_risk": "Ich muss sehr klar mit Ihnen sein - Ihr Risikoscore betr\u00e4gt {score:.1f} Prozent, was ziemlich hoch ist. Das bedeutet, dass Sie eine erhebliche Wahrscheinlichkeit haben, Herzprobleme zu entwickeln. Ich will Sie nicht erschrecken, aber das ist ernst und Sie m\u00fcssen sofort handeln.",
                "low_risk": "Gute Nachrichten! Ihr Risikoscore betr\u00e4gt {score:.1f} Prozent, was relativ niedrig ist. Das bedeutet, dass Ihr Herz in ziemlich gutem Zustand ist, aber es gibt immer Raum f\u00fcr Verbesserungen.",
                "explanation": "Lassen Sie mich erkl\u00e4ren, was das f\u00fcr Sie in allt\u00e4glichen Begriffen bedeutet:",
                "high_risk_explanation": "Denken Sie an Ihr Herz wie an einen Automotor. Im Moment zeigt es einige Warnzeichen, dass es in Zukunft Probleme haben k\u00f6nnte. Das bedeutet nicht, dass Sie jetzt einen Herzinfarkt haben, aber es bedeutet, dass Sie bald einen Arzt aufsuchen m\u00fcssen, um Probleme zu verhindern.",
                "low_risk_explanation": "Ihr Herz funktioniert jetzt gut, wie ein Auto, das sanft l\u00e4uft. Aber wie ein Auto regelm\u00e4\u00dfige Wartung braucht, braucht Ihr Herz kontinuierliche Pflege, um gesund zu bleiben.",
                "recommendations": "Hier ist, was ich Ihnen empfehle zu tun:",
                "immediate_action": "Am wichtigsten ist, wenn Ihr Risiko hoch ist, vereinbaren Sie bitte so schnell wie m\u00f6glich einen Termin bei Ihrem Arzt oder Kardiologen. Warten Sie nicht - fr\u00fches Handeln kann Ihr Leben retten.",
                "lifestyle_tips": "F\u00fcr Ihr t\u00e4gliches Leben, hier sind einige einfache Dinge, die Sie anfangen k\u00f6nnen zu tun:",
                "closing": "Denken Sie daran, dies ist nur eine Computerbewertung, um Sie zu f\u00fchren. Ihr Arzt kennt Sie am besten und kann Ihnen personalisierte Ratschl\u00e4ge geben. K\u00fcmmern Sie sich um Ihr Herz - es ist das einzige, das Sie haben!",
                "emergency": "Wenn Sie Brustschmerzen, Atemnot versp\u00fcren oder das Gef\u00fchl haben, dass etwas ernsthaft nicht stimmt, rufen Sie sofort den Notdienst an. Warten Sie nicht, um zu sehen, ob es besser wird.",
            },
            "it": {
                "intro": "Ciao! Ho la tua valutazione della salute del cuore pronta. Lasciami spiegare cosa abbiamo trovato in termini semplici.",
                "high_risk": "Devo essere molto chiaro con te - il tuo punteggio di rischio \u00e8 del {score:.1f} percento, che \u00e8 abbastanza alto. Questo significa che hai una probabilit\u00e0 significativa di sviluppare problemi cardiaci. Non voglio spaventarti, ma questo \u00e8 serio e devi agire immediatamente.",
                "low_risk": "Buone notizie! Il tuo punteggio di rischio \u00e8 del {score:.1f} percento, che \u00e8 relativamente basso. Questo significa che il tuo cuore \u00e8 in condizioni abbastanza buone, ma c'\u00e8 sempre spazio per miglioramenti.",
                "explanation": "Lasciami spiegare cosa significa questo per te in termini quotidiani:",
                "high_risk_explanation": "Pensa al tuo cuore come al motore di un'auto. In questo momento, sta mostrando alcuni segnali di avvertimento che potrebbe avere problemi in futuro. Questo non significa che stai avendo un attacco di cuore ora, ma significa che devi vedere un medico presto per prevenire problemi.",
                "low_risk_explanation": "Il tuo cuore sta funzionando bene ora, come un'auto che gira dolcemente. Ma come un'auto ha bisogno di manutenzione regolare, il tuo cuore ha bisogno di cure continue per rimanere sano.",
                "recommendations": "Ecco cosa ti consiglio di fare:",
                "immediate_action": "Pi\u00f9 importante, se il tuo rischio \u00e8 alto, per favore fai un appuntamento con il tuo medico o cardiologo il prima possibile. Non aspettare - l'azione precoce pu\u00f2 salvare la tua vita.",
                "lifestyle_tips": "Per la tua vita quotidiana, ecco alcune cose semplici che puoi iniziare a fare:",
                "closing": "Ricorda, questa \u00e8 solo una valutazione computerizzata per guidarti. Il tuo medico ti conosce meglio e pu\u00f2 darti consigli personalizzati. Prenditi cura del tuo cuore - \u00e8 l'unico che hai!",
                "emergency": "Se provi dolore al petto, mancanza di respiro, o senti che qualcosa non va seriamente, chiama immediatamente i servizi di emergenza. Non aspettare di vedere se migliora.",
            },
            "pt": {
                "intro": "Ol\u00e1! Tenho sua avalia\u00e7\u00e3o de sa\u00fade card\u00edaca pronta. Deixe-me explicar o que encontramos em termos simples.",
                "high_risk": "Preciso ser muito claro com voc\u00ea - sua pontua\u00e7\u00e3o de risco \u00e9 de {score:.1f} por cento, que \u00e9 bastante alta. Isso significa que voc\u00ea tem uma probabilidade significativa de desenvolver problemas card\u00edacos. N\u00e3o quero assust\u00e1-lo, mas isso \u00e9 s\u00e9rio e voc\u00ea precisa agir imediatamente.",
                "low_risk": "Boas not\u00edcias! Sua pontua\u00e7\u00e3o de risco \u00e9 de {score:.1f} por cento, que \u00e9 relativamente baixa. Isso significa que seu cora\u00e7\u00e3o est\u00e1 em bastante bom estado, mas sempre h\u00e1 espa\u00e7o para melhorias.",
                "explanation": "Deixe-me explicar o que isso significa para voc\u00ea em termos cotidianos:",
                "high_risk_explanation": "Pense em seu cora\u00e7\u00e3o como o motor de um carro. Agora, est\u00e1 mostrando alguns sinais de aviso de que pode ter problemas no futuro. Isso n\u00e3o significa que voc\u00ea est\u00e1 tendo um ataque card\u00edaco agora, mas significa que voc\u00ea precisa ver um m\u00e9dico logo para prevenir problemas.",
                "low_risk_explanation": "Seu cora\u00e7\u00e3o est\u00e1 funcionando bem agora, como um carro que funciona suavemente. Mas como um carro precisa de manuten\u00e7\u00e3o regular, seu cora\u00e7\u00e3o precisa de cuidados cont\u00ednuos para se manter saud\u00e1vel.",
                "recommendations": "Aqui est\u00e1 o que eu recomendo que voc\u00ea fa\u00e7a:",
                "immediate_action": "Mais importante, se seu risco \u00e9 alto, por favor marque uma consulta com seu m\u00e9dico ou cardiologista o mais r\u00e1pido poss\u00edvel. N\u00e3o espere - a\u00e7\u00e3o precoce pode salvar sua vida.",
                "lifestyle_tips": "Para sua vida di\u00e1ria, aqui est\u00e3o algumas coisas simples que voc\u00ea pode come\u00e7ar a fazer:",
                "closing": "Lembre-se, esta \u00e9 apenas uma avalia\u00e7\u00e3o computadorizada para gui\u00e1-lo. Seu m\u00e9dico o conhece melhor e pode dar-lhe conselhos personalizados. Cuide do seu cora\u00e7\u00e3o - \u00e9 o \u00fanico que voc\u00ea tem!",
                "emergency": "Se voc\u00ea sentir dor no peito, falta de ar, ou sentir que algo est\u00e1 seriamente errado, chame os servi\u00e7os de emerg\u00eancia imediatamente. N\u00e3o espere para ver se melhora.",
            },
            "hi": {
                "intro": "\u0928\u092e\u0938\u094d\u0924\u0947! \u092e\u0947\u0930\u0947 \u092a\u093e\u0938 \u0906\u092a\u0915\u0940 \u0939\u0943\u0926\u092f \u0938\u094d\u0935\u093e\u0938\u094d\u0925\u094d\u092f \u092e\u0942\u0932\u094d\u092f\u093e\u0902\u0915\u0928 \u0924\u0948\u092f\u093e\u0930 \u0939\u0948\u0964 \u092e\u0941\u091d\u0947 \u0938\u0930\u0932 \u0936\u092c\u094d\u0926\u094b\u0902 \u092e\u0947\u0902 \u092c\u0924\u093e\u090f\u0902 \u0915\u093f \u0939\u092e\u0928\u0947 \u0915\u094d\u092f\u093e \u092a\u093e\u092f\u093e\u0964",
                "high_risk": "\u092e\u0941\u091d\u0947 \u0906\u092a\u0915\u0947 \u0938\u093e\u0925 \u092c\u0939\u0941\u0924 \u0938\u094d\u092a\u0937\u094d\u091f \u0939\u094b\u0928\u093e \u091a\u093e\u0939\u093f\u090f - \u0906\u092a\u0915\u093e \u091c\u094b\u0916\u093f\u092e \u0938\u094d\u0915\u094b\u0930 {score:.1f} \u092a\u094d\u0930\u0924\u093f\u0936\u0924 \u0939\u0948, \u091c\u094b \u0915\u093e\u092b\u0940 \u0905\u0927\u093f\u0915 \u0939\u0948\u0964 \u0907\u0938\u0915\u093e \u092e\u0924\u0932\u092c \u0939\u0948 \u0915\u093f \u0906\u092a\u0915\u094b \u0939\u0943\u0926\u092f \u0915\u0940 \u0938\u092e\u0938\u094d\u092f\u093e\u090f\u0902 \u0935\u093f\u0915\u0938\u093f\u0924 \u0939\u094b\u0928\u0947 \u0915\u0940 \u092e\u0939\u0924\u094d\u0935\u092a\u0942\u0930\u094d\u0923 \u0938\u0902\u092d\u093e\u0935\u0928\u093e \u0939\u0948\u0964 \u092e\u0948\u0902 \u0906\u092a\u0915\u094b \u0921\u0930\u093e\u0928\u093e \u0928\u0939\u0940\u0902 \u091a\u093e\u0939\u0924\u093e, \u0932\u0947\u0915\u093f\u0928 \u092f\u0939 \u0917\u0902\u092d\u0940\u0930 \u0939\u0948 \u0914\u0930 \u0906\u092a\u0915\u094b \u0924\u0941\u0930\u0902\u0924 \u0915\u093e\u0930\u094d\u0930\u0935\u093e\u0908 \u0915\u0930\u0928\u0947 \u0915\u0940 \u0906\u0935\u0936\u094d\u092f\u0915\u0924\u093e \u0939\u0948\u0964",
                "low_risk": "\u0905\u091a\u094d\u091b\u0940 \u0916\u092c\u0930! \u0906\u092a\u0915\u093e \u091c\u094b\u0916\u093f\u092e \u0938\u094d\u0915\u094b\u0930 {score:.1f} \u092a\u094d\u0930\u0924\u093f\u0936\u0924 \u0939\u0948, \u091c\u094b \u0905\u092a\u0947\u0915\u094d\u0937\u093e\u0915\u0943\u0924 \u0915\u092e \u0939\u0948\u0964 \u0907\u0938\u0915\u093e \u092e\u0924\u0932\u092c \u0939\u0948 \u0915\u093f \u0906\u092a\u0915\u093e \u0926\u093f\u0932 \u0915\u093e\u092b\u0940 \u0905\u091a\u094d\u091b\u0940 \u0938\u094d\u0925\u093f\u0924\u093f \u092e\u0947\u0902 \u0939\u0948, \u0932\u0947\u0915\u093f\u0928 \u0939\u092e\u0947\u0936\u093e \u0938\u0941\u0927\u093e\u0930 \u0915\u0947 \u0932\u093f\u090f \u091c\u0917\u0939 \u0939\u0948\u0964",
                "explanation": "\u092e\u0941\u091d\u0947 \u0906\u092a\u0915\u094b \u0930\u094b\u091c\u092e\u0930\u094d\u0930\u093e \u0915\u0947 \u0936\u092c\u094d\u0926\u094b\u0902 \u092e\u0947\u0902 \u0938\u092e\u091d\u093e\u090f\u0902 \u0915\u093f \u0907\u0938\u0915\u093e \u0915\u094d\u092f\u093e \u092e\u0924\u0932\u092c \u0939\u0948:",
                "high_risk_explanation": "\u0905\u092a\u0928\u0947 \u0926\u093f\u0932 \u0915\u0947 \u092c\u093e\u0930\u0947 \u092e\u0947\u0902 \u0938\u094b\u091a\u0947\u0902 \u091c\u0948\u0938\u0947 \u0915\u093e\u0930 \u0915\u093e \u0907\u0902\u091c\u0928\u0964 \u0905\u092d\u0940, \u092f\u0939 \u0915\u0941\u091b \u091a\u0947\u0924\u093e\u0935\u0928\u0940 \u0938\u0902\u0915\u0947\u0924 \u0926\u093f\u0916\u093e \u0930\u0939\u093e \u0939\u0948 \u0915\u093f \u092d\u0935\u093f\u0937\u094d\u092f \u092e\u0947\u0902 \u0907\u0938\u0947 \u0938\u092e\u0938\u094d\u092f\u093e\u090f\u0902 \u0939\u094b \u0938\u0915\u0924\u0940 \u0939\u0948\u0902\u0964 \u0907\u0938\u0915\u093e \u092e\u0924\u0932\u092c \u092f\u0939 \u0928\u0939\u0940\u0902 \u0939\u0948 \u0915\u093f \u0906\u092a\u0915\u094b \u0905\u092d\u0940 \u0926\u093f\u0932 \u0915\u093e \u0926\u094c\u0930\u093e \u092a\u0921\u093c \u0930\u0939\u093e \u0939\u0948, \u0932\u0947\u0915\u093f\u0928 \u0907\u0938\u0915\u093e \u092e\u0924\u0932\u092c \u0939\u0948 \u0915\u093f \u0906\u092a\u0915\u094b \u0938\u092e\u0938\u094d\u092f\u093e\u0913\u0902 \u0915\u094b \u0930\u094b\u0915\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f \u091c\u0932\u094d\u0926 \u0939\u0940 \u0921\u0949\u0915\u094d\u091f\u0930 \u0938\u0947 \u092e\u093f\u0932\u0928\u0947 \u0915\u0940 \u091c\u0930\u0942\u0930\u0924 \u0939\u0948\u0964",
                "low_risk_explanation": "\u0906\u092a\u0915\u093e \u0926\u093f\u0932 \u0905\u092d\u0940 \u0905\u091a\u094d\u091b\u0940 \u0924\u0930\u0939 \u0938\u0947 \u0915\u093e\u092e \u0915\u0930 \u0930\u0939\u093e \u0939\u0948, \u091c\u0948\u0938\u0947 \u0915\u093e\u0930 \u091c\u094b \u0928\u0930\u092e\u0940 \u0938\u0947 \u091a\u0932\u0924\u0940 \u0939\u0948\u0964 \u0932\u0947\u0915\u093f\u0928 \u091c\u0948\u0938\u0947 \u0915\u093e\u0930 \u0915\u094b \u0928\u093f\u092f\u092e\u093f\u0924 \u0930\u0916\u0930\u0916\u093e\u0935 \u0915\u0940 \u091c\u0930\u0942\u0930\u0924 \u0939\u094b\u0924\u0940 \u0939\u0948, \u0935\u0948\u0938\u0947 \u0939\u0940 \u0906\u092a\u0915\u0947 \u0926\u093f\u0932 \u0915\u094b \u0938\u094d\u0935\u0938\u094d\u0925 \u0930\u0939\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f \u0928\u093f\u0930\u0902\u0924\u0930 \u0926\u0947\u0916\u092d\u093e\u0932 \u0915\u0940 \u091c\u0930\u0942\u0930\u0924 \u0939\u094b\u0924\u0940 \u0939\u0948\u0964",
                "recommendations": "\u092f\u0939\u093e\u0902 \u092e\u0948\u0902 \u0906\u092a\u0915\u094b \u0915\u094d\u092f\u093e \u0915\u0930\u0928\u0947 \u0915\u0940 \u0938\u0932\u093e\u0939 \u0926\u0947\u0924\u093e \u0939\u0942\u0902:",
                "immediate_action": "\u0938\u092c\u0938\u0947 \u092e\u0939\u0924\u094d\u0935\u092a\u0942\u0930\u094d\u0923, \u092f\u0926\u093f \u0906\u092a\u0915\u093e \u091c\u094b\u0916\u093f\u092e \u0905\u0927\u093f\u0915 \u0939\u0948, \u0924\u094b \u0915\u0943\u092a\u092f\u093e \u091c\u093f\u0924\u0928\u0940 \u091c\u0932\u094d\u0926\u0940 \u0939\u094b \u0938\u0915\u0947 \u0905\u092a\u0928\u0947 \u0921\u0949\u0915\u094d\u091f\u0930 \u092f\u093e \u0915\u093e\u0930\u094d\u0921\u093f\u092f\u094b\u0932\u0949\u091c\u093f\u0938\u094d\u091f \u0938\u0947 \u092e\u093f\u0932\u0947\u0902\u0964 \u0907\u0902\u0924\u091c\u093e\u0930 \u0928 \u0915\u0930\u0947\u0902 - \u091c\u0932\u094d\u0926\u0940 \u0915\u0940 \u0915\u093e\u0930\u094d\u0930\u0935\u093e\u0908 \u0906\u092a\u0915\u0940 \u091c\u093e\u0928 \u092c\u091a\u093e \u0938\u0915\u0924\u0940 \u0939\u0948\u0964",
                "lifestyle_tips": "\u0906\u092a\u0915\u0947 \u0926\u0948\u0928\u093f\u0915 \u091c\u0940\u0935\u0928 \u0915\u0947 \u0932\u093f\u090f, \u092f\u0939\u093e\u0902 \u0915\u0941\u091b \u0938\u0930\u0932 \u091a\u0940\u091c\u0947\u0902 \u0939\u0948\u0902 \u091c\u094b \u0906\u092a \u0915\u0930\u0928\u093e \u0936\u0941\u0930\u0942 \u0915\u0930 \u0938\u0915\u0924\u0947 \u0939\u0948\u0902:",
                "closing": "\u092f\u093e\u0926 \u0930\u0916\u0947\u0902, \u092f\u0939 \u0938\u093f\u0930\u094d\u092b \u0906\u092a\u0915\u094b \u092e\u093e\u0930\u094d\u0917\u0926\u0930\u094d\u0936\u0928 \u0915\u0930\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f \u090f\u0915 \u0915\u0902\u092a\u094d\u092f\u0942\u091f\u0930 \u092e\u0942\u0932\u094d\u092f\u093e\u0902\u0915\u0928 \u0939\u0948\u0964 \u0906\u092a\u0915\u093e \u0921\u0949\u0915\u094d\u091f\u0930 \u0906\u092a\u0915\u094b \u0938\u092c\u0938\u0947 \u0905\u091a\u094d\u091b\u0940 \u0924\u0930\u0939 \u091c\u093e\u0928\u0924\u093e \u0939\u0948 \u0914\u0930 \u0906\u092a\u0915\u094b \u0935\u094d\u092f\u0915\u094d\u0924\u093f\u0917\u0924 \u0938\u0932\u093e\u0939 \u0926\u0947 \u0938\u0915\u0924\u093e \u0939\u0948\u0964 \u0905\u092a\u0928\u0947 \u0926\u093f\u0932 \u0915\u0940 \u0926\u0947\u0916\u092d\u093e\u0932 \u0915\u0930\u0947\u0902 - \u092f\u0939\u0940 \u090f\u0915\u092e\u093e\u0924\u094d\u0930 \u0939\u0948 \u091c\u094b \u0906\u092a\u0915\u0947 \u092a\u093e\u0938 \u0939\u0948!",
                "emergency": "\u092f\u0926\u093f \u0906\u092a\u0915\u094b \u091b\u093e\u0924\u0940 \u092e\u0947\u0902 \u0926\u0930\u094d\u0926, \u0938\u093e\u0902\u0938 \u0932\u0947\u0928\u0947 \u092e\u0947\u0902 \u0915\u0920\u093f\u0928\u093e\u0908, \u092f\u093e \u0932\u0917\u0924\u093e \u0939\u0948 \u0915\u093f \u0915\u0941\u091b \u0917\u0902\u092d\u0940\u0930 \u0930\u0942\u092a \u0938\u0947 \u0917\u0932\u0924 \u0939\u0948, \u0924\u094b \u0924\u0941\u0930\u0902\u0924 \u0906\u092a\u093e\u0924\u0915\u093e\u0932\u0940\u0928 \u0938\u0947\u0935\u093e\u0913\u0902 \u0915\u094b \u092c\u0941\u0932\u093e\u090f\u0902\u0964 \u092f\u0939 \u0926\u0947\u0916\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f \u0907\u0902\u0924\u091c\u093e\u0930 \u0928 \u0915\u0930\u0947\u0902 \u0915\u093f \u0915\u094d\u092f\u093e \u092f\u0939 \u092c\u0947\u0939\u0924\u0930 \u0939\u094b\u0924\u093e \u0939\u0948\u0964",
            },
            "zh-CN": {
                "intro": "\u60a8\u597d\uff01\u60a8\u7684\u5fc3\u810f\u5065\u5eb7\u8bc4\u4f30\u5df2\u7ecf\u51c6\u5907\u597d\u4e86\u3002\u8ba9\u6211\u7528\u7b80\u5355\u7684\u8bed\u8a00\u89e3\u91ca\u6211\u4eec\u53d1\u73b0\u4e86\u4ec0\u4e48\u3002",
                "high_risk": "\u6211\u9700\u8981\u975e\u5e38\u6e05\u695a\u5730\u544a\u8bc9\u60a8 - \u60a8\u7684\u98ce\u9669\u8bc4\u5206\u4e3a{score:.1f}%\uff0c\u8fd9\u76f8\u5f53\u9ad8\u3002\u8fd9\u610f\u5473\u7740\u60a8\u6709\u663e\u8457\u7684\u53ef\u80fd\u6027\u53d1\u5c55\u5fc3\u810f\u75c5\u95ee\u9898\u3002\u6211\u4e0d\u60f3\u5413\u5510\u60a8\uff0c\u4f46\u8fd9\u5f88\u4e25\u91cd\uff0c\u60a8\u9700\u8981\u7acb\u5373\u91c7\u53d6\u884c\u52a8\u3002",
                "low_risk": "\u597d\u6d88\u606f\uff01\u60a8\u7684\u98ce\u9669\u8bc4\u5206\u4e3a{score:.1f}%\uff0c\u76f8\u5bf9\u8f83\u4f4e\u3002\u8fd9\u610f\u5473\u7740\u60a8\u7684\u5fc3\u810f\u72b6\u51b5\u76f8\u5f53\u597d\uff0c\u4f46\u603b\u6709\u6539\u8fdb\u7684\u7a7a\u95f4\u3002",
                "explanation": "\u8ba9\u6211\u7528\u65e5\u5e38\u7528\u8bed\u89e3\u91ca\u8fd9\u5bf9\u60a8\u610f\u5473\u7740\u4ec0\u4e48\uff1a",
                "high_risk_explanation": "\u628a\u60a8\u7684\u5fc3\u810f\u60f3\u8c61\u6210\u6c7d\u8f66\u53d1\u52a8\u673a\u3002\u73b0\u5728\uff0c\u5b83\u663e\u793a\u4e86\u4e00\u4e9b\u8b66\u544a\u4fe1\u53f7\uff0c\u8868\u660e\u5c06\u6765\u53ef\u80fd\u4f1a\u6709\u95ee\u9898\u3002\u8fd9\u5e76\u4e0d\u610f\u5473\u7740\u60a8\u73b0\u5728\u6b63\u5728\u5fc3\u810f\u75c5\u53d1\u4f5c\uff0c\u4f46\u8fd9\u786e\u5b9e\u610f\u5473\u7740\u60a8\u9700\u8981\u5f88\u5feb\u770b\u533b\u751f\u6765\u9884\u9632\u95ee\u9898\u3002",
                "low_risk_explanation": "\u60a8\u7684\u5fc3\u810f\u73b0\u5728\u5de5\u4f5c\u5f97\u5f88\u597d\uff0c\u5c31\u50cf\u4e00\u8f86\u5e73\u7a33\u884c\u9a76\u7684\u6c7d\u8f66\u3002\u4f46\u5c31\u50cf\u6c7d\u8f66\u9700\u8981\u5b9a\u671f\u7ef4\u62a4\u4e00\u6837\uff0c\u60a8\u7684\u5fc3\u810f\u9700\u8981\u6301\u7eed\u62a4\u7406\u6765\u4fdd\u6301\u5065\u5eb7\u3002",
                "recommendations": "\u4ee5\u4e0b\u662f\u6211\u5efa\u8bae\u60a8\u505a\u7684\uff1a",
                "immediate_action": "\u6700\u91cd\u8981\u7684\u662f\uff0c\u5982\u679c\u60a8\u7684\u98ce\u9669\u5f88\u9ad8\uff0c\u8bf7\u5c3d\u5feb\u4e0e\u60a8\u7684\u533b\u751f\u6216\u5fc3\u810f\u75c5\u4e13\u5bb6\u9884\u7ea6\u3002\u4e0d\u8981\u7b49\u5f85 - \u65e9\u671f\u884c\u52a8\u53ef\u4ee5\u631d\u6551\u60a8\u7684\u751f\u547d\u3002",
                "lifestyle_tips": "\u5bf9\u4e8e\u60a8\u7684\u65e5\u5e38\u751f\u6d3b\uff0c\u4ee5\u4e0b\u662f\u4e00\u4e9b\u60a8\u53ef\u4ee5\u5f00\u59cb\u505a\u7684\u7b80\u5355\u4e8b\u60c5\uff1a",
                "closing": "\u8bf7\u8bb0\u4f4f\uff0c\u8fd9\u53ea\u662f\u4e3a\u4e86\u6307\u5bfc\u60a8\u7684\u8ba1\u7b97\u673a\u8bc4\u4f30\u3002\u60a8\u7684\u533b\u751f\u6700\u4e86\u89e3\u60a8\uff0c\u53ef\u4ee5\u7ed9\u60a8\u4e2a\u6027\u5316\u7684\u5efa\u8bae\u3002\u7167\u987e\u597d\u60a8\u7684\u5fc3\u810f - \u8fd9\u662f\u60a8\u552f\u4e00\u62e5\u6709\u7684\uff01",
                "emergency": "\u5982\u679c\u60a8\u611f\u5230\u80f8\u75db\u3001\u547c\u5438\u6025\u4fc3\uff0c\u6216\u611f\u89c9\u6709\u4ec0\u4e48\u4e25\u91cd\u95ee\u9898\uff0c\u8bf7\u7acb\u5373\u547c\u53eb\u7d27\u6025\u670d\u52a1\u3002\u4e0d\u8981\u7b49\u5f85\u770b\u662f\u5426\u597d\u8f6c\u3002",
            },
        }

        texts = report_texts.get(language_code, report_texts["en"])

        report_text = texts["intro"] + " "

        if risk_score > 50:
            report_text += texts["high_risk"].format(score=risk_score) + " "
            report_text += texts["explanation"] + " "
            report_text += texts["high_risk_explanation"] + " "
        else:
            report_text += texts["low_risk"].format(score=risk_score) + " "
            report_text += texts["explanation"] + " "
            report_text += texts["low_risk_explanation"] + " "

        report_text += texts["recommendations"] + " "
        if risk_score > 50:
            report_text += texts["immediate_action"] + " "
            report_text += texts["emergency"] + " "

        report_text += texts["lifestyle_tips"] + " "
        for rec in recommendations:
            if rec["category"] in ["Lifestyle Modifications", "Dietary Guidelines", "Physical Activity Plan"]:
                for step in rec["steps"][:2]:
                    report_text += step + ". "

        report_text += " " + texts["closing"]

        try:
            tts = gTTS(text=report_text, lang=language_code, slow=False)
            audio_file = BytesIO()
            tts.write_to_fp(audio_file)
            audio_file.seek(0)
            return audio_file.getvalue()
        except Exception as e:
            if language_code != "en":
                try:
                    tts = gTTS(text=report_text, lang="en", slow=False)
                    audio_file = BytesIO()
                    tts.write_to_fp(audio_file)
                    audio_file.seek(0)
                    return audio_file.getvalue()
                except Exception as fallback_error:
                    raise Exception(
                        f"Failed to generate audio in both {language_code} and English: {str(e)} -> {str(fallback_error)}"
                    )
            else:
                raise Exception(f"Error generating audio in {language_code}: {str(e)}")

    except Exception as e:
        raise Exception(f"Error preparing audio report: {str(e)}")
