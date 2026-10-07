# AI-Powered Chatbot

A college-level customer-support and FAQ chatbot built with:

- Python
- Flask
- NLTK
- Hugging Face Transformers
- SQLite
- HTML/CSS/JavaScript

The project uses a retrieval-first design. FAQ questions are matched using
NLP-cleaned text. When an FAQ is not sufficiently relevant, a Transformers
instruction model receives the recent conversation context and attempts a
controlled response. If the model cannot answer reliably, the chatbot uses a
safe fallback instead of inventing an answer.

## 1. Project structure

```text
chatbot_project/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── database/
│   ├── __init__.py
│   └── db.py
├── models/
│   ├── __init__.py
│   └── chatbot_model.py
├── nlp/
│   ├── __init__.py
│   └── processor.py
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
└── data/
    └── faqs.json
```

`database/chatbot.db` is generated automatically when the application starts,
so it does not need to be committed to source control.

## 2. Requirements

Recommended:

- Python 3.10 or newer
- pip
- Internet connection for the first Transformers model download

## 3. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

The first model initialization downloads `google/flan-t5-small` from Hugging
Face. The model is then cached locally by Transformers.

## 5. Configure environment variables

Copy `.env.example` to `.env`.

Windows:

```bash
copy .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

The default values are suitable for local development.

## 6. Initialize the SQLite database

No separate migration command is required.

Run:

```bash
python app.py
```

The application automatically creates:

```text
database/chatbot.db
```

with these tables:

- `users`
- `conversations`
- `messages`
- `interaction_logs`

## 7. Run the application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## 8. Test the chatbot

Try questions such as:

```text
Hello
What are your delivery charges?
How long does delivery take?
And how long does it take?
How can I track my order?
I forgot my password.
What payment methods do you accept?
What is your return policy?
How do I contact support?
```

The second delivery question demonstrates conversation context. The frontend
sends the same conversation ID, and the backend includes recent messages when
using the Transformers model.

## 9. REST API

### Start a conversation

```http
POST /api/conversations
Content-Type: application/json

{
  "name": "Guest"
}
```

### Send a message

```http
POST /api/chat
Content-Type: application/json

{
  "conversation_id": 1,
  "message": "What are your delivery charges?"
}
```

### Retrieve conversation history

```http
GET /api/conversations/1/messages
```

### View interaction logs

```http
GET /api/logs?limit=50
```

The log endpoint is intentionally simple for a college demonstration. In a
production system it should be protected with administrator authentication.

## 10. Database design

### users

Stores basic user information.

### conversations

Connects a user with a conversation/session.

### messages

Stores every user and chatbot message with timestamps.

### interaction_logs

Stores the user query, chatbot response, intent, confidence, source and
timestamp for every chatbot interaction.

## 11. NLP processing

`nlp/processor.py` performs:

1. Lowercasing
2. Tokenization using NLTK
3. Stop-word removal
4. Lemmatization

The resulting text is used by the FAQ retrieval layer.

## 12. Transformers model

The default model is:

```text
google/flan-t5-small
```

It is loaded through the Hugging Face `transformers` pipeline.

To use another compatible text-to-text model, change:

```text
TRANSFORMERS_MODEL=google/flan-t5-small
```

in `.env`.

For a college demonstration, `flan-t5-small` is a reasonable balance between
model capability and local resource usage. Larger models require substantially
more RAM/CPU/GPU resources.

## 13. FAQ knowledge base

Edit:

```text
data/faqs.json
```

Each FAQ has:

- `intent`
- `question`
- `keywords`
- `answer`

Add your own customer-support questions without changing the frontend.

## 14. Error handling

The project handles:

- Empty messages
- Messages over 1000 characters
- Invalid conversation IDs
- Invalid JSON requests
- Database exceptions
- Transformer model loading failures
- Transformer generation failures

User-facing errors are intentionally kept simple.

## 15. Security and privacy

The project:

- Does not use hard-coded passwords or API keys.
- Uses `.env` for configurable settings.
- Does not collect unnecessary personal information.
- Validates incoming message length.
- Stores only the information required for the demonstration.

Before production deployment, add authentication and authorization for
administrator endpoints, HTTPS, rate limiting, CSRF protection where
appropriate, and stronger input/content controls.

## 16. Deployment

The project is Flask-based and can be deployed to a Python-compatible cloud
platform.

A typical production setup is:

```text
Internet
   |
Cloud platform
   |
Gunicorn
   |
Flask application
   |
SQLite
```

Install Gunicorn:

```bash
pip install gunicorn
```

Start the application on Linux/cloud environments:

```bash
gunicorn app:app
```

Set the environment variables on the cloud platform rather than committing
`.env`.

### SQLite deployment note

SQLite is appropriate for a college project and small demonstrations. For a
high-traffic production service, replace SQLite with a managed relational
database such as PostgreSQL and update the database layer accordingly.

### Model deployment note

The Transformers model may take time to download on the first startup and may
require more memory than a small cloud instance provides. Use a machine with
sufficient memory or select a smaller compatible model.

## 17. Demonstration flow

1. Open the chatbot website.
2. A conversation is automatically created.
3. Ask an FAQ question.
4. The NLTK processor cleans the query.
5. The FAQ matcher calculates a relevance score.
6. A sufficiently matched FAQ returns its predefined support answer.
7. For questions without a strong FAQ match, recent conversation context is
   passed to the Transformers model.
8. If the model cannot answer reliably, the fixed fallback response is used.
9. User messages, bot responses and interaction information are stored in
   SQLite.
10. `/api/logs` displays the stored interaction logs.

## 18. Important limitation

This project intentionally does not pretend to know private order/account
data. It only has the information contained in the FAQ knowledge base and
conversation. Real order lookup would require a secure integration with an
actual order-management system.
