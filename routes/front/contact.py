from app import app, render_template
from flask import request, redirect, url_for
import requests
import os
import logging

logger = logging.getLogger(__name__)


@app.get('/contact')
def contact():
    return render_template("front/contact.html")


@app.post('/contact/submit')
def contact_submit():
    try:
        form = request.form
        name = form.get('name')
        email = form.get('email')
        message = form.get('message')

        # Validate form data
        if not all([name, email, message]):
            logger.warning("Contact form submitted with missing fields")
            return "Missing required fields", 400

        logger.info(f"Processing contact form from {name} ({email})")

        token = os.environ.get('TELEGRAM_BOT_TOKEN', '8277635671:AAFk00SgNqkE34WNkst_GwlCprCZw3AQCcg')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID', '@teamsupport_channel')
        url = f"https://api.telegram.org/bot{token}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": (
                "<b>📩 New Contact Form Submission</b>\n\n"
                "Here's a new inquiry from your website contact page:\n\n"
                f"👤 <b>Name:</b> {name}\n"
                f"📧 <b>Email:</b> {email}\n"
                f"💬 <b>Message:</b>\n{message}\n\n"
                "---------------------------------------\n"
                "<i>Sent automatically from your website contact form.</i>"
            ),
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }

        headers = {
            "accept": "application/json",
            "User-Agent": "Telegram Bot",
            "content-type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()

        logger.info(f"Contact form successfully sent to Telegram for {name}")
        return redirect(url_for("contact"))
        
    except requests.exceptions.Timeout:
        logger.error("Timeout sending message to Telegram")
        return "Service timeout, please try again later", 503
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send message to Telegram: {e}")
        return "Failed to send message. Please try again later.", 500
    except Exception as e:
        logger.error(f"Unexpected error in contact form: {e}")
        return "An error occurred. Please try again later.", 500
