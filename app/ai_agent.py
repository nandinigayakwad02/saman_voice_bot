from openai import AsyncOpenAI
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# Conversation history storage (in-memory for simplicity)
# In production, use Redis or database
conversation_history = {}


async def get_ai_response(user_phone: str, user_message: str) -> str:
    """
    Get AI response using OpenAI Chat API
    
    Args:
        user_phone: User's phone number (used as conversation ID)
        user_message: User's message text
        
    Returns:
        AI response text
    """
    try:
        # Get or create conversation history for this user
        if user_phone not in conversation_history:
            conversation_history[user_phone] = [
                {
                    "role": "system",
                    "content": """Je bent een AI-assistent voor een AI-automatiseringsbedrijf. Je helpt leads kwalificeren en vragen beantwoorden. Reageer ALTIJD in het Nederlands.

**FAQ KENNIS - Beantwoord deze vragen wanneer gevraagd:**

Q: Hoe ziet jullie proces eruit?
A: We werken met ontwikkelingskosten plus een maandelijkse onderhoudskosten.

Q: Wat doen jullie precies?
A: We bouwen AI-systemen voor bedrijven die hun bedrijf willen automatiseren en meer ruimte voor groei willen creëren.

Q: Wat maakt jullie anders dan andere bedrijven?
A: We bouwen onze eigen AI-systemen, implementeren twee keer zo snel in vergelijking met andere aanbieders, en bieden een 30-dagen resultatengarantie.

Q: Kunnen jullie integreren met onze bestaande systemen?
A: We kunnen naadloos integreren met uw huidige systemen.

**KWALIFICATIEPROCES:**
Wanneer een prospect interesse toont, zeg ALTIJD: "Ik heb een paar vragen die ik moet stellen om te zien of we u verder kunnen helpen."

Stel deze vragen dan ÉÉN VOOR ÉÉN (wacht op elk antwoord voordat je de volgende vraag stelt):
1. Met welk probleem wordt u momenteel geconfronteerd?
2. Wat verliest u aan geld en tijd?
3. Wat heeft u tot nu toe gedaan om dit probleem op te lossen?
4. Hoe ziet uw ideale oplossing eruit?
5. Hoeveel budget heeft u beschikbaar om dit probleem op te lossen?

**TOON & STIJL:**
- Wees vriendelijk, professioneel en beknopt (dit is WhatsApp)
- Houd antwoorden kort en duidelijk
- Stel kwalificatievragen natuurlijk in het gesprek
- Luister actief en erken hun antwoorden
- Stel niet alle vragen tegelijk - maak het conversationeel
- Reageer ALTIJD in het Nederlands, ongeacht de taal van de gebruiker"""
                }
            ]
        
        # Add user message to history
        conversation_history[user_phone].append({
            "role": "user",
            "content": user_message
        })
        
        # Keep only last 10 messages to avoid token limits
        if len(conversation_history[user_phone]) > 11:  # 1 system + 10 messages
            conversation_history[user_phone] = [
                conversation_history[user_phone][0]  # Keep system message
            ] + conversation_history[user_phone][-10:]  # Keep last 10 messages
        
        # Get AI response
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=conversation_history[user_phone],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_message = response.choices[0].message.content
        
        # Add AI response to history
        conversation_history[user_phone].append({
            "role": "assistant",
            "content": ai_message
        })
        
        logger.info(f" AI response generated for {user_phone}")
        return ai_message
    
    except Exception as e:
        logger.error(f" Error getting AI response: {e}")
        return "Sorry, I encountered an error. Please try again."


def clear_conversation(user_phone: str):
    """Clear conversation history for a user"""
    if user_phone in conversation_history:
        del conversation_history[user_phone]
        logger.info(f" Cleared conversation for {user_phone}")
