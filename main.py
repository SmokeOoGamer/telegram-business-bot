import requests
from flask import Flask, request, jsonify

# Replace the placeholders below with your actual Telegram Bot token and Google Gemini API key.
BOT_TOKEN = "7562945278:AAEZB5CzgMrOpGstwiYTqykvY_ihFi_Fi7Y"
GEMINI_API_KEY = "AIzaSyBneC_AkW7BamcSeNstFggFZkGt9xYp0o4"

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
