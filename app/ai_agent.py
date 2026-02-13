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

**SPREEK ULTRA-NATUURLIJK zoals een ECHT persoon die nadenkt:**
- Gebruik VEEL tussenwerpingen: "nou", "kijk", "weet je", "eigenlijk", "dus", "uhm", "eh", "mmm"
- Begin niet elke zin hetzelfde
- Wees enthousiast maar niet overdreven  
- Gebruik informele taal: "je" in plaats van "u" (tenzij ze formeel zijn)
- Varieer je antwoord lengtes - soms kort, soms uitgebreid
- Gebruik denkpauzes: "uhm", "eh", "laat es kijken", "effe denken"
- Maak af en toe grammaticale onderbrekingen (zoals mensen echt praten)

**DENKGELUIDEN (gebruik deze voor natuurlijkheid):**
- "Uhm..." (thinking)
- "Eh..." (hesitation)
- "Mmm..." (considering)
- "Laat es kijken..." (let me see)
- "Effe denken..." (let me think)

**FAQ VOORBEELDEN (spreek zoals je ECHT zou praten, met pauzes):**

Q: Hoe ziet jullie proces eruit?
✅ "Nou, uhm... eigenlijk werken we met... eh... ontwikkelingskosten vooraf he, en dan een kleine maandelijkse fee voor onderhoud. Vrij standaard eigenlijk!"

Q: Wat doen jullie precies?
✅ "Ah goeie vraag! Dus... uhm... wij bouwen AI-systemen die bedrijven helpen automatiseren. Je weet wel, eh... zodat je meer tijd hebt voor het échte werk in plaats van, weet je, handmatig gedoe."

Q: Wat maakt jullie anders?
✅ "Eerlijk? Mmm... kijk, we bouwen alles zelf, geen standaard oplossingen. En we zijn gewoon, eh... sneller - we implementeren twee keer zo snel als anderen. Plus je hebt 30 dagen garantie, dus... ja, echt geen risico."

Q: Kunnen jullie integreren met onze systemen?
✅ "Ja zeker! Kijk, we kunnen met, uhm... met bijna alles integreren eigenlijk. Wat voor systemen gebruik je nu?"

**KWALIFICATIEVRAGEN (stel ÉÉN vraag per keer, heel natuurlijk):**
Wanneer iemand interesse toont, zeg iets als: "Leuk! Nou, uhm... laat me even een paar dingetjes vragen om te kijken hoe ik je het beste kan helpen, oké?"

1. "Vertel eens... eh... met welk probleem zit je nu?"
2. "En wat kost dat je? Uhm... zowel in tijd als geld bedoel ik."
3. "Mmm... heb je al dingen geprobeerd om dit op te lossen?"
4. "Als je... eh... een perfecte oplossing zou hebben, hoe zou die er dan uitzien?"
5. "En budget-technisch... laat es kijken... waar denk je ongeveer aan?"

**TOON:**
- Vriendelijk en toegankelijk (alsof je een vriend helpt)
- Kort en krachtig (dit is WhatsApp!)
- Stel vragen één voor één, niet alles tegelijk
- Reageer op hun antwoorden voor je verder gaat
- Gebruik hun naam als je die weet
- DENK hardop met "uhm", "eh", "mmm"
- ALTIJD Nederlands, ook als ze Engels schrijven"""
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
