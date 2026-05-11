import requests
import logging
from threading import Thread
from django.conf import settings

logger = logging.getLogger(__name__)


def send_customer_welcome_email(user_email):
    """
    Send welcome email to customer after registration
    """
    try:
        RESEND_API_KEY = settings.RESEND_API_KEY

        subject = "Trova il professionista giusto per il lavoro!"

        html_message = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .content {{ background: #f8f9fa; padding: 25px; border-radius: 10px; }}
        .button {{ display: inline-block; background: #007bff; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; margin: 15px 0; font-weight: bold; }}
        .footer {{ margin-top: 25px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
        .safety-box {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        .step {{ margin-bottom: 15px; padding-left: 20px; }}
        .step-number {{ font-weight: bold; color: #007bff; }}
        .platform-name {{ color: #007bff; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h2 style="color: #007bff;">FidaMano</h2>
    </div>
    
    <div class="content">
        
        
        <p>Bentornato su <span class="platform-name">FidaMano</span>. Che tu abbia un tubo che perde, bisogno di un nuovo tetto o voglia ristrutturare il tuo soggiorno, l'esperto giusto è a solo una telefonata di distanza.</p>
        
        <h3>Come funziona:</h3>
        
        <div class="step">
            <p><span class="step-number">1.</span> <strong>Cerca:</strong> Filtra per Regione e Categoria.</p>
        </div>
        
        <div class="step">
            <p><span class="step-number">2.</span> <strong>Connettiti:</strong> Chiama o contatta il professionista direttamente su WhatsApp.</p>
        </div>
        
        <div class="step">
            <p><span class="step-number">3.</span> <strong>Negozia:</strong> Discuti il tuo progetto e accordati sul prezzo—nessuna commissione intermediaria!</p>
        </div>
        
        <div class="safety-box">
            <h3>Sicurezza prima di tutto</h3>
            <p>Per mantenere la tua esperienza ottima, ricorda:</p>
            <ul>
                <li><strong>Incontro e Preventivo:</strong> Invita il professionista per un sopralluogo per ottenere un prezzo accurato e pianificare i dettagli insieme.</li>
                <li><strong>Controlla la Galleria:</strong> Visualizza le foto dei "Lavori Precedenti" per vedere le loro abilità e stile in azione.</li>
                <li><strong>Accordo:</strong> Assicurati che entrambi siate d'accordo su costi e tempistiche prima che il lavoro inizi.</li>
                <li><strong>Valuta il Professionista:</strong> Lavoro finito? Lascia una recensione per supportare il professionista e aiutare gli altri a trovare i migliori talenti!</li>
            </ul>
        </div>
        
        <p style="text-align: center;">
            <a href="https://fidamano.com/customer-dashboard/" class="button">Trova un Professionista Vicino a Me</a>
        </p>
        
        <p>Buon lavoro,<br>
        <strong>Il Team <span class="platform-name">FidaMano</span></strong></p>
    </div>
</body>
</html>"""

        plain_message = f"""Ciao!,

Bentornato su FidaMano. Che tu abbia un tubo che perde, bisogno di un nuovo tetto o voglia ristrutturare il tuo soggiorno, l'esperto giusto è a solo una telefonata di distanza.

Come funziona:

1. Cerca: Filtra per Regione e Categoria.
2. Connettiti: Chiama o contatta il professionista direttamente su WhatsApp.
3. Negozia: Discuti il tuo progetto e accordati sul prezzo—nessuna commissione intermediaria!

Sicurezza prima di tutto: Per mantenere la tua esperienza ottima, ricorda:

• Incontro e Preventivo: Invita il professionista per un sopralluogo per ottenere un prezzo accurato e pianificare i dettagli insieme.
• Controlla la Galleria: Visualizza le foto dei "Lavori Precedenti" per vedere le loro abilità e stile in azione.
• Accordo: Assicurati che entrambi siate d'accordo su costi e tempistiche prima che il lavoro inizi.
• Valuta il Professionista: Lavoro finito? Lascia una recensione per supportare il professionista e aiutare gli altri a trovare i migliori talenti!

Trova un Professionista Vicino a Me: https://fidamano.com/customer-dashboard/

Buon lavoro,
Il Team FidaMano"""

        email_data = {
            "from": "FidaMano <support@retechloans.com>",
            "to": [user_email],
            "subject": subject,
            "html": html_message,
            "text": plain_message,
            "reply_to": "support@retechloans.com",
        }

        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json=email_data,
            timeout=5,
        )

        if response.status_code == 200:
            print(f"DEBUG: Craftsman email sent to {user_email}")
            logger.info(f"Customer welcome email sent to {user_email}")
            return True
        else:
            logger.error(f"Email API error for {user_email}: {response.text}")
            return False

    except Exception as e:
        print(f"DEBUG ERROR: Exception in send_craftsman_welcome_email: {str(e)}")
        logger.error(f"Error sending customer welcome email to {user_email}: {str(e)}")
        return False


def send_craftsman_welcome_email(
    user_email,
):
    """
    Send welcome email to craftsman after registration
    """
    try:
        print(f"DEBUG: Starting craftsman email to {user_email}")

        RESEND_API_KEY = settings.RESEND_API_KEY

        subject = "Sei pronto per lavorare! Troviamo il tuo primo cliente."

        html_message = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .content {{ background: #f8f9fa; padding: 25px; border-radius: 10px; }}
        .button {{ display: inline-block; background: #28a745; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; margin: 15px 0; font-weight: bold; }}
        .footer {{ margin-top: 25px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
        .safety-box {{ background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        .step {{ margin-bottom: 15px; padding-left: 20px; }}
        .step-number {{ font-weight: bold; color: #28a745; }}
        .highlight {{ color: #28a745; font-weight: bold; }}
        .platform-name {{ color: #28a745; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h2 style="color: #28a745;">FidaMano </h2>
    </div>
    
    <div class="content">
        
        
        <p>Bentornato su <span class="platform-name">FidaMano</span>! Sei appena entrato a far parte di una community dei migliori professionisti del settore—da Idraulici e Muratori a Designer d'interni.</p>
        
        <p>Abbiamo costruito questa piattaforma per aiutarti a far crescere la tua attività senza intermediari. Ricorda: <span class="highlight">Tu sei il capo.</span> Parli direttamente con i clienti, fissi i tuoi prezzi e mantieni il 100% di quanto guadagni.</p>
        
        <h3>3 passaggi per ricevere la tua prima chiamata:</h3>
        
        <div class="step">
            <p><span class="step-number">1.</span> <strong>Completa il tuo Profilo:</strong> Carica una foto chiara di te o del logo della tua attività.</p>
        </div>
        
        <div class="step">
            <p><span class="step-number">2.</span> <strong>Mostra i tuoi lavori:</strong> Carica almeno 5 foto dei tuoi migliori progetti "Prima e Dopo".</p>
        </div>
        
        <div class="step">
            <p><span class="step-number">3.</span> <strong>Imposta la tua Posizione:</strong> Assicurati che Regione e Quartiere siano corretti così i clienti locali possono trovarti.</p>
        </div>
        
        <div class="safety-box">
            <h3>💡 Consiglio sulla Sicurezza</h3>
            <p>Incontra sempre i nuovi clienti in un ambiente sicuro e accordati chiaramente sui costi dei materiali prima di iniziare il lavoro.</p>
        </div>
        
        <p style="text-align: center;">
            <a href="https://yourdomain.com/craftsman-dashboard/" class="button">Pubblica il tuo Servizio Ora</a>
        </p>
        
        <p>Al tuo successo,<br>
        <strong>Il Team <span class="platform-name">FidaMano</span></strong></p>
    </div>
</body>
</html>"""

        plain_message = f"""Ciao!,

Bentornato su FidaMano! Sei appena entrato a far parte di una community dei migliori professionisti del settore—da Idraulici e Muratori a Designer d'interni.

Abbiamo costruito questa piattaforma per aiutarti a far crescere la tua attività senza intermediari. Ricorda: Tu sei il capo. Parli direttamente con i clienti, fissi i tuoi prezzi e mantieni il 100% di quanto guadagni.

3 passaggi per ricevere la tua prima chiamata:

1. Completa il tuo Profilo: Carica una foto chiara di te o del logo della tua attività.
2. Mostra i tuoi lavori: Carica almeno 5 foto dei tuoi migliori progetti "Prima e Dopo".
3. Imposta la tua Posizione: Assicurati che Regione e Quartiere siano corretti così i clienti locali possono trovarti.

Consiglio sulla Sicurezza: Incontra sempre i nuovi clienti in un ambiente sicuro e accordati chiaramente sui costi dei materiali prima di iniziare il lavoro.

Pubblica il tuo Servizio Ora: https://yourdomain.com/craftsman-dashboard/

Al tuo successo,
Il Team FidaMano"""

        email_data = {
            "from": "FidaMano <support@retechloans.com>",
            "to": [user_email],
            "subject": subject,
            "html": html_message,
            "text": plain_message,
            "reply_to": "support@retechloans.com",
        }

        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json=email_data,
            timeout=5,
        )

        if response.status_code == 200:
            print(f"DEBUG: Craftsman email sent to {user_email}")
            logger.info(f"Craftsman welcome email sent to {user_email}")
            return True
        else:
            logger.error(f"Email API error for {user_email}: {response.text}")
            return False

    except Exception as e:
        print(f"DEBUG ERROR: Exception in send_craftsman_welcome_email: {str(e)}")
        logger.error(f"Error sending craftsman welcome email to {user_email}: {str(e)}")
        return False


def send_welcome_email_async(user_email, is_craftsman=False):

    def send_email():
        if is_craftsman:
            send_craftsman_welcome_email(user_email)
        else:
            send_customer_welcome_email(user_email)

    email_thread = Thread(target=send_email)
    email_thread.daemon = True
    email_thread.start()


def send_waitlist_confirmation_email(user_email, user_name, city, category):
    """
    Send waitlist confirmation email to users who signed up
    """
    try:
        RESEND_API_KEY = settings.RESEND_API_KEY

        subject = f"Stiamo cercando i migliori professionisti {category} a {city}!"

        html_message = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .content {{ background: #f8f9fa; padding: 25px; border-radius: 10px; }}
        .highlight-box {{ background: #e7f3ff; border: 1px solid #b3d7ff; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .feature-list {{ margin: 20px 0; }}
        .feature {{ display: flex; align-items: flex-start; margin-bottom: 15px; }}
        .feature-icon {{ color: #007bff; font-size: 18px; margin-right: 10px; min-width: 25px; }}
        .footer {{ margin-top: 25px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
        .founder-badge {{ background: #15803D; color: white; padding: 8px 20px; border-radius: 20px; display: inline-block; font-weight: bold; margin: 10px 0; }}
        .platform-name {{ color: #007bff; font-weight: bold; }}
        .urgent-box {{ background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h2 style="color: #007bff;">FidaMano </h2>
        <p style="color: #666; font-size: 14px;">Connecting you with trusted professionals</p>
    </div>
    
    <div class="content">
        <p>Ciao <strong>{user_name}</strong>,</p>
        
        <p>Abbiamo notato che stavi cercando servizi <strong>{category}</strong> a <strong>{city}</strong> su <span class="platform-name">FidaMano</span> oggi.</p>
        
        <div class="highlight-box">
            <p><strong>Al momento siamo nella nostra fase "Qualità sulla Quantità".</strong> Stiamo selezionando e verificando i professionisti uno per uno per assicurarci che quando assumi qualcuno attraverso FidaMano, siano davvero i migliori del settore.</p>
            
            <div class="founder-badge">
                STATO DI MEMBRO FONDATORE
            </div>
            
            <p>Perché non abbiamo ancora un professionista verificato nella tua area specifica, abbiamo <strong>aggiornato il tuo account a stato "Membro Fondatore".</strong></p>
        </div>
        
        <h3>Cosa stiamo facendo per te:</h3>
        
        <div class="feature-list">
            <div class="feature">
                <div class="feature-icon"></div>
                <div>
                    <strong>La Ricerca:</strong> Il nostro team sta attivamente cercando e verificando professionisti {category} a {city} specificamente a causa della tua richiesta.
                </div>
            </div>
            
            <div class="feature">
                <div class="feature-icon"></div>
                <div>
                    <strong>Notifica Prioritaria:</strong> Non appena verifichiamo un professionista di prima classe {category} nel tuo quartiere, sarai il <strong>primo a saperlo</strong> via email.
                </div>
            </div>
            
            <div class="feature">
                <div class="feature-icon"></div>
                <div>
                    <strong>Vantaggi Fondatore:</strong> Come ringraziamento per la tua pazienza, riceverai <strong>prenotazione prioritaria a vita</strong> e <strong>sconti esclusivi</strong> una volta che lanceremo completamente nella tua regione.
                </div>
            </div>
        </div>
        
        <div class="urgent-box">
            <h3>Il tuo lavoro è urgente?</h3>
            <p>Rispondi semplicemente a questa email con alcuni dettagli su cosa ti serve. Faremo del nostro meglio per trovare manualmente un professionista fidato per te attraverso la nostra rete privata.</p>
            <p><strong>Rispondi a:</strong> support@retechloans.com</p>
        </div>
        
        <p>Nel frattempo, puoi:</p>
        <ul>
            <li>Esplorare servizi disponibili nelle aree vicine</li>
            <li>Salvare la tua ricerca per ricevere notifiche quando i professionisti diventano disponibili</li>
            <li>Consultare i portfolio dei nostri professionisti verificati</li>
        </ul>
        
        <p>Grazie per aiutarci a costruire una community più fidata, una città alla volta.</p>
        
        <p>Cordiali saluti,<br>
        <strong>Il Team <span class="platform-name">FidaMano</span></strong></p>
    </div>
    
    <div class="footer">
        <p>Questa email è stata inviata a {user_email} perché ti sei iscritto alla lista d'attesa di FidaMano.</p>
        <p>© 2024 FidaMano. All rights reserved.</p>
    </div>
</body>
</html>"""

        plain_message = f"""Ciao {user_name},

Abbiamo notato che stavi cercando servizi {category} a {city} su FidaMano oggi.

Al momento siamo nella nostra fase "Qualità sulla Quantità". Stiamo selezionando e verificando i professionisti uno per uno per assicurarci che quando assumi qualcuno attraverso FidaMano, siano davvero i migliori del settore.

Perché non abbiamo ancora un professionista verificato nella tua area specifica, abbiamo aggiornato il tuo account a stato "Membro Fondatore".

Cosa stiamo facendo per te:

LA RICERCA: Il nostro team sta attivamente cercando e verificando professionisti {category} a {city} specificamente a causa della tua richiesta.

NOTIFICA PRIORITARIA: Non appena verifichiamo un professionista di prima classe {category} nel tuo quartiere, sarai il PRIMO a saperlo via email.

VANTAGGI FONDATORE: Come ringraziamento per la tua pazienza, riceverai prenotazione prioritaria a vita e sconti esclusivi una volta che lanceremo completamente nella tua regione.

IL TUO LAVORO È URGENTE?
Rispondi semplicemente a questa email con alcuni dettagli su cosa ti serve. Faremo del nostro meglio per trovare manualmente un professionista fidato per te attraverso la nostra rete privata.

Rispondi a: support@retechloans.com

Grazie per aiutarci a costruire una community più fidata, una città alla volta.

Cordiali saluti,
Il Team FidaMano

---
Questa email è stata inviata a {user_email} perché ti sei iscritto alla lista d'attesa di FidaMano.
© 2024 FidaMano. Tutti i diritti riservati."""

        email_data = {
            "from": "FidaMano Waitlist <support@retechloans.com>",
            "to": [user_email],
            "subject": subject,
            "html": html_message,
            "text": plain_message,
            "reply_to": "support@retechloans.com",
        }

        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json=email_data,
            timeout=5,
        )

        if response.status_code == 200:
            print(f"DEBUG: Waitlist confirmation email sent to {user_email}")
            logger.info(f"Waitlist confirmation email sent to {user_email}")
            return True
        else:
            logger.error(f"Waitlist email API error for {user_email}: {response.text}")
            return False

    except Exception as e:
        print(f"DEBUG ERROR: Exception in send_waitlist_confirmation_email: {str(e)}")
        logger.error(f"Error sending waitlist email to {user_email}: {str(e)}")
        return False


def send_waitlist_email_async(user_email, user_name, city, category):
    """
    Send waitlist email asynchronously
    """

    def send_email():
        send_waitlist_confirmation_email(user_email, user_name, city, category)

    email_thread = Thread(target=send_email)
    email_thread.daemon = True
    email_thread.start()
