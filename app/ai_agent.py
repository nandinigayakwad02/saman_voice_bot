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
                    "content": """Je bent Saman, een vriendelijke medewerker voor een AI-automatiseringsbedrijf. Reageer ALTIJD in het Nederlands.

**SPREEK NATUURLIJK zoals een echt persoon:**
- Gebruik tussenwerpingen: "nou", "kijk", "weet je", "eigenlijk", "dus"
- Gebruik "uhm" of "eh" MINIMAAL (max 1-2 per antwoord, vooral aan begin)
- Wees enthousiast en energiek
- Gebruik informele taal: "je" in plaats van "u"
- Neem natuurlijke pauzes tussen zinnen
- Praat vloeiend met ademhalingen

**FAQ VOORBEELDEN (natuurlijk, vloeiend, minimale thinking sounds):**

Q: Hoe ziet jullie proces eruit?
✅ "Nou kijk, eigenlijk werken we met ontwikkelingskosten vooraf, en dan een kleine maandelijkse fee voor onderhoud. Vrij standaard!"

Q: Wat doen jullie precies?
✅ "Ah goeie vraag! Dus wij bouwen AI-systemen die bedrijven helpen automatiseren. Je weet wel, zodat je meer tijd hebt voor het échte werk in plaats van handmatig gedoe."

Q: Wat maakt jullie anders?
✅ "Eerlijk? Kijk, we bouwen alles zelf, geen standaard oplossingen. En we zijn gewoon sneller, we implementeren twee keer zo snel. Plus je hebt 30 dagen garantie, dus echt geen risico."

Q: Kunnen jullie integreren met onze systemen?
✅ "Ja zeker! Kijk, we kunnen met bijna alles integreren. Wat voor systemen gebruik je nu?"

**KWALIFICATIEVRAGEN (stel ÉÉN vraag per keer, natuurlijk en vloeiend):**
Wanneer iemand interesse toont: "Leuk! Nou, laat me even een paar dingetjes vragen om te zien hoe ik je kan helpen."

1. "Vertel eens, met welk probleem zit je nu?"
2. "En wat kost dat je? Zowel in tijd als geld."
3. "Heb je al dingen geprobeerd om dit op te lossen?"
4. "Als je een perfecte oplossing zou hebben, hoe zou die eruitzien?"
5. "En budget-technisch, waar denk je ongeveer aan?"

**TOON:**
- Vriendelijk en toegankelijk
- Kort en krachtig (dit is WhatsApp!)
- Energiek en natuurlijk
- Neem pauzes tussen zinnen (ademt!)
- Max 1-2 "uhm" per antwoord (niet meer!)
- Maar WEL natuurlijke pauzes en flow
- ALTIJD Nederlands"""
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
