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
        RESEND_API_KEY = "re_dmz9pidY_71yM9R6vrP6VkeNfJesh8cKZ"

        subject = "Find the right pro for the job!"

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
        
        
        <p>Welcome to <span class="platform-name">FidaMano</span>. Whether you have a leaking pipe, need a new roof, or want to redesign your living room, the right expert is just a phone call away.</p>
        
        <h3>How it works:</h3>
        
        <div class="step">
            <p><span class="step-number">1.</span> <strong>Search:</strong> Filter by your State and Category.</p>
        </div>
        
        <div class="step">
            <p><span class="step-number">2.</span> <strong>Connect:</strong> Call or WhatsApp the craftsman directly.</p>
        </div>
        
        <div class="step">
            <p><span class="step-number">3.</span> <strong>Negotiate:</strong> Discuss your project and agree on a price—no middleman fees!</p>
        </div>
        
        <div class="safety-box">
            <h3>Safety First</h3>
            <p>To keep your experience great, remember:</p>
            <ul>
                <li><strong>Meet & Quote:</strong> Invite your pro for a site visit to get an accurate price and plan the details together.</li>
                <li><strong>Check the Gallery:</strong> View their "Previous Work" photos to see their skill and style in action.</li>
                <li><strong>Agreement:</strong> Ensure you both agree on costs and timelines before the work begins.</li>
                <li><strong>Rate the Pro:</strong> Finished? Leave a review to support your pro and help others find the best talent!</li>
            </ul>
        </div>
        
        <p style="text-align: center;">
            <a href="https://fidamano.com/customer-dashboard/" class="button">Find a Craftsman Near Me</a>
        </p>
        
        <p>Happy building,<br>
        <strong>The <span class="platform-name">FidaMano</span> Team</strong></p>
    </div>
</body>
</html>"""

        plain_message = f"""Hey there!,

Welcome to FidaMano. Whether you have a leaking pipe, need a new roof, or want to redesign your living room, the right expert is just a phone call away.

How it works:

1. Search: Filter by your State and Category.
2. Connect: Call or WhatsApp the craftsman directly.
3. Negotiate: Discuss your project and agree on a price—no middleman fees!

Safety First: To keep your experience great, remember:

• Meet & Quote: Invite your pro for a site visit to get an accurate price and plan the details together.
• Check the Gallery: View their "Previous Work" photos to see their skill and style in action.
• Agreement: Ensure you both agree on costs and timelines before the work begins.
• Rate the Pro: Finished? Leave a review to support your pro and help others find the best talent!

Find a Craftsman Near Me: https://fidamano.com/customer-dashboard/

Happy building,
The FidaMano Team"""

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
            print(f"DEBUG: ✅ Craftsman email sent to {user_email}")
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

        RESEND_API_KEY = "re_dmz9pidY_71yM9R6vrP6VkeNfJesh8cKZ"

        subject = "You're open for business! Let's get your first lead."

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
        
        
        <p>Welcome to <span class="platform-name">FidaMano</span>! You've just joined a community of the best hands in the business—from Plumbers and Masons to Interior Designers.</p>
        
        <p>We've built this platform to help you grow your business without the middleman. Remember: <span class="highlight">You are the boss.</span> You talk to the clients, you set your prices, and you keep 100% of what you earn.</p>
        
        <h3>3 Steps to get your first call:</h3>
        
        <div class="step">
            <p><span class="step-number">1.</span> <strong>Complete your Profile:</strong> Upload a clear photo of yourself or your business logo.</p>
        </div>
        
        <div class="step">
            <p><span class="step-number">2.</span> <strong>Show off your work:</strong> Upload at least 5 photos of your best "Before & After" projects.</p>
        </div>
        
        <div class="step">
            <p><span class="step-number">3.</span> <strong>Set your Location:</strong> Make sure your State and Neighborhood are correct so local clients can find you.</p>
        </div>
        
        <div class="safety-box">
            <h3>💡 Safety Tip</h3>
            <p>Always meet new clients in a safe environment and clearly agree on material costs before starting work.</p>
        </div>
        
        <p style="text-align: center;">
            <a href="https://yourdomain.com/craftsman-dashboard/" class="button">Post Your Service Now</a>
        </p>
        
        <p>To your success,<br>
        <strong>The <span class="platform-name">FidaMano</span> Team</strong></p>
    </div>
</body>
</html>"""

        plain_message = f"""Hey there!,

Welcome to FidaMano! You've just joined a community of the best hands in the business—from Plumbers and Masons to Interior Designers.

We've built this platform to help you grow your business without the middleman. Remember: You are the boss. You talk to the clients, you set your prices, and you keep 100% of what you earn.

3 Steps to get your first call:

1. Complete your Profile: Upload a clear photo of yourself or your business logo.
2. Show off your work: Upload at least 5 photos of your best "Before & After" projects.
3. Set your Location: Make sure your State and Neighborhood are correct so local clients can find you.

Safety Tip: Always meet new clients in a safe environment and clearly agree on material costs before starting work.

Post Your Service Now: https://yourdomain.com/craftsman-dashboard/

To your success,
The FidaMano Team"""

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
            print(f"DEBUG: ✅ Craftsman email sent to {user_email}")
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
        RESEND_API_KEY = "re_dmz9pidY_71yM9R6vrP6VkeNfJesh8cKZ"

        subject = f"We're on the hunt for top {category} professionals in {city}!"

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
        <p>Hi <strong>{user_name}</strong>,</p>
        
        <p>We noticed you were looking for <strong>{category}</strong> services in <strong>{city}</strong> on <span class="platform-name">FidaMano</span> today.</p>
        
        <div class="highlight-box">
            <p><strong>Right now, we are in our "Quality Over Quantity" phase.</strong> We are hand-picking and verifying craftsmen one by one to ensure that when you hire someone through FidaMano, they are truly the best in the business.</p>
            
            <div class="founder-badge">
                FOUNDING MEMBER STATUS
            </div>
            
            <p>Because we don't have a verified pro in your specific area yet, we've <strong>upgraded your account to "Founding Member" status.</strong></p>
        </div>
        
        <h3>What we're doing for you:</h3>
        
        <div class="feature-list">
            <div class="feature">
                <div class="feature-icon"></div>
                <div>
                    <strong>The Hunt:</strong> Our team is now actively scouting and verifying {category} professionals in {city} specifically because of your request.
                </div>
            </div>
            
            <div class="feature">
                <div class="feature-icon"></div>
                <div>
                    <strong>Priority Notification:</strong> As soon as we verify a top-tier {category} professional in your neighborhood, you will be the <strong>first to know</strong> via email.
                </div>
            </div>
            
            <div class="feature">
                <div class="feature-icon"></div>
                <div>
                    <strong>Founder Perks:</strong> As a thank you for your patience, you will receive <strong>lifetime priority booking</strong> and <strong>exclusive discounts</strong> once we fully launch in your region.
                </div>
            </div>
        </div>
        
        <div class="urgent-box">
            <h3>Is your job urgent?</h3>
            <p>Simply reply to this email with a few details about what you need. We will do our best to manually find a trusted professional for you through our private network.</p>
            <p><strong>Reply to:</strong> support@retechloans.com</p>
        </div>
        
        <p>In the meantime, you can:</p>
        <ul>
            <li>Explore services available in nearby areas</li>
            <li>Save your search to get notified when professionals become available</li>
            <li>Browse our verified professionals' portfolios</li>
        </ul>
        
        <p>Thank you for helping us build a more trusted community, one city at a time.</p>
        
        <p>Best regards,<br>
        <strong>The <span class="platform-name">FidaMano</span> Team</strong></p>
    </div>
    
    <div class="footer">
        <p>This email was sent to {user_email} because you signed up for the FidaMano waitlist.</p>
        <p>© 2024 FidaMano. All rights reserved.</p>
    </div>
</body>
</html>"""

        plain_message = f"""Hi {user_name},

We noticed you were looking for {category} services in {city} on FidaMano today.

Right now, we are in our "Quality Over Quantity" phase. We are hand-picking and verifying craftsmen one by one to ensure that when you hire someone through FidaMano, they are truly the best in the business.

Because we don't have a verified pro in your specific area yet, we've upgraded your account to "Founding Member" status.

What we're doing for you:

 THE HUNT: Our team is now actively scouting and verifying {category} professionals in {city} specifically because of your request.

 PRIORITY NOTIFICATION: As soon as we verify a top-tier {category} professional in your neighborhood, you will be the FIRST to know via email.

 FOUNDER PERKS: As a thank you for your patience, you will receive lifetime priority booking and exclusive discounts once we fully launch in your region.

 IS YOUR JOB URGENT?
Simply reply to this email with a few details about what you need. We will do our best to manually find a trusted professional for you through our private network.

Reply to: support@retechloans.com

Thank you for helping us build a more trusted community, one city at a time.

Best regards,
The FidaMano Team

---
This email was sent to {user_email} because you signed up for the FidaMano waitlist.
© 2024 FidaMano. All rights reserved."""

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
            print(f"DEBUG: ✅ Waitlist confirmation email sent to {user_email}")
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
