import requests
from flask import Flask, request, jsonify

"""
Configuration for the Telegram business bot.

The bot token and Gemini API key are defined below. These values can be
overridden by setting environment variables named `BOT_TOKEN` and
`GEMINI_API_KEY` respectively. If the environment variables are not set,
the constants defined here will be used as defaults.

Important: Keep these keys secret. Do not commit your real tokens to a
public repository unless you have rotated them and understand the
security implications.
"""

import os

# Telegram Bot token. This value can be overridden by the BOT_TOKEN
# environment variable at runtime.
BOT_TOKEN = os.getenv("BOT_TOKEN", "7562945278:AAF-VvPkc-r2SlLL_3Z3ylgA_e9ePcwAMjM")

# Google Gemini API key. This value can be overridden by the
# GEMINI_API_KEY environment variable at runtime.
GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY", "AIzaSyBneC_AkW7BamcSeNstFggFZkGt9xYp0o4"
)

# Initialize the Flask app
app = Flask(__name__)


def ask_gemini(question: str) -> str:
    """Send a question to the Gemini API and return the generated response.

    Args:
        question (str): The user's message from Telegram.

    Returns:
        str: The generated response text from Gemini. If an error occurs, a default
        message is returned.
    """
    try:
        url = (
            "https://generativelanguage.googleapis.com/v1/models/"
            "gemini-pro:generateContent?key=" + GEMINI_API_KEY
        )
        data = {"contents": [{"parts": [{"text": question}]}]}
        response = requests.post(url, json=data)
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        # Print the error for debugging purposes and return a friendly fallback message
        print("Gemini API error:", e)
        return "متاسفم، مشکلی پیش آمده است. لطفاً دوباره تلاش کنید."


@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook() -> str:
    """Handle incoming webhook updates from Telegram.

    This function processes both new business connections and incoming business messages.
    It replies to incoming messages using the Gemini API.

    Returns:
        str: JSON response confirming receipt of the update.
    """
    update = request.get_json(force=True)

    # Handle a new or updated business connection
    if "business_connection" in update:
        # Log or handle business connection updates as needed
        print("Received business connection update:", update["business_connection"])
        return jsonify({"status": "ok"})

    # Handle an incoming business message
    if "business_message" in update:
        message = update["business_message"]
        chat_id = message["chat"]["id"]
        business_conn_id = message["business_connection_id"]
        user_text = message.get("text", "")

        # Generate a response using Gemini
        reply_text = ask_gemini(user_text)

        # Send the response on behalf of the business account
        send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "business_connection_id": business_conn_id,
            "chat_id": chat_id,
            "text": reply_text,
        }
        try:
            requests.post(send_url, json=payload)
        except Exception as send_exception:
            print("Error sending Telegram message:", send_exception)
        return jsonify({"status": "ok"})

    # Return 'ok' if the update type isn't specifically handled
    return jsonify({"status": "ignored"})


@app.route("/", methods=["GET"])
def health_check() -> str:
    """A basic route to confirm that the bot is running."""
    return "🤖 Telegram Business Bot is running!"


if __name__ == "__main__":
    # Run the Flask app. When deploying to Render or similar platforms, the host
    # and port will be set automatically by the environment.
    app.run(host="0.0.0.0", port=8080)
