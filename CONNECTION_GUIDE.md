# WhatsApp AI Chatbot - Connection & Setup Guide

This guide documents the exact steps to connect your local AI chatbot to WhatsApp. Use this if you need to set it up again in the future.

---

## 1. Start the Local Server

**Use Case:** Runs the Python code that powers your bot (receives messages, talks to OpenAI, sends replies).

1.  Open a terminal in your project folder.
2.  Activate the virtual environment:
    ```bash
    source venv/bin/activate
    ```
3.  Run the application:
    ```bash
    python run.py
    ```
    *You should see: `Server running on http://0.0.0.0:8000`*

---

## 2. Create a Public Tunnel (Localtunnel)

**Use Case:** Makes your local computer accessible to the internet so Facebook/Meta can send messages to it.

1.  Open a **new** terminal window.
2.  Run localtunnel:
    ```bash
    lt --port 8000
    ```
3.  **Copy the URL** it gives you (e.g., `https://funny-cat-42.loca.lt`).
4.  **IMPORTANT:** Open this URL in your browser once. Click "Click to Continue" if you see a security page. This "wakes up" the tunnel.

---

## 3. Configure Meta Developer Dashboard

**Use Case:** Tells WhatsApp where to send incoming messages (to your tunnel URL).

1.  Go to [developers.facebook.com/apps](https://developers.facebook.com/apps/).
2.  Click on your app: **payment-reminder-app**.
3.  On the **Left Sidebar**, look for the **WhatsApp** section.
4.  Click **Configuration** under WhatsApp.

### A. Setup Webhook
1.  Find the **Webhook** section (usually at the top).
2.  Click the **Edit** button.
3.  **Callback URL:** Paste your tunnel URL + `/webhook`
    *   *Example:* `https://funny-cat-42.loca.lt/webhook`
4.  **Verify Token:** Enter `whatsapp_ai_chatbot_2026`
    *   *Note:* This must match the `WEBHOOK_VERIFY_TOKEN` in your `.env` file.
5.  Click **Verify and Save**.
    *   *Success:* The dialog closes.
    *   *Error:* Check if your python server is running and if you visited the tunnel URL in your browser.

### B. Subscribe to Messages
1.  Scroll down to the **Webhook fields** section.
2.  Click the **Manage** button (or it might just list fields).
3.  Find the row labeled **`messages`**.
4.  Click **Subscribe** in the right column.
    *   *Why:* This tells Meta to actually send you the user's text messages. Without this, your bot stays silent.

---

## 4. Testing

**Use Case:** Verifying everything works.

1.  Open WhatsApp on your phone.
2.  Send a message to the **Test Number** (+1 555 157 1989).
    *   *Message:* "Hello, who are you?"
3.  **Check your Python Terminal:** You should see `📨 Received webhook` and `✅ Sent AI response`.
4.  **Check WhatsApp:** You should get a reply from the AI.

---

## Troubleshooting

-   **"Verify and Save" Failed:**
    -   Is `python run.py` running?
    -   Did you open the `loca.lt` URL in a browser first?
    -   Did you add `/webhook` to the end of the URL?

-   **No Reply on WhatsApp:**
    -   Did you click **Subscribe** for `messages`?
    -   Is the OpenAI API key correct in `.env`?
    -   Check the terminal logs for errors.
