"""
AskMe AI - Python Backend
Knowledge base chatbot with keyword-matching engine.
No external API. Run this file and open http://localhost:5000 in your browser.
"""

import re
import sys
import json
import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer


# ===============================================================
#  KNOWLEDGE BASE
#  Each entry:
#    keywords : list of trigger words/phrases
#    response : string reply  OR  callable () -> str
#    weight   : priority score (higher wins on tie)
# ===============================================================

JOKES = [
    "Why don't scientists trust atoms?\n\n**Because they make up everything!**",
    "Why did the scarecrow win an award?\n\n**Because he was outstanding in his field!**",
    "What do you call fake spaghetti?\n\n**An impasta!**",
    "Why can't a bicycle stand on its own?\n\n**Because it's two-tired!**",
    "What did the ocean say to the beach?\n\n**Nothing, it just waved!**",
]

FUN_FACTS = [
    "Honey never spoils. Archaeologists found **3,000-year-old honey** in Egyptian tombs that was still perfectly edible!",
    "Octopuses have **three hearts** - two pump blood to the gills and one pumps it to the rest of the body. They also have **blue blood!**",
    "A day on **Venus** is longer than a year on Venus. It rotates so slowly that it completes a full orbit around the Sun before finishing one rotation!",
    "Bananas are **slightly radioactive** because they contain potassium-40. You'd need to eat about 10 million bananas to get a harmful dose!",
    "The average person walks about **100,000 miles** in their lifetime - roughly **4 times around the Earth!**",
]

QUOTES = [
    '"The only way to do great work is to love what you do." - **Steve Jobs**',
    '"In the middle of every difficulty lies opportunity." - **Albert Einstein**',
    '"It does not matter how slowly you go as long as you do not stop." - **Confucius**',
    '"Believe you can and you\'re halfway there." - **Theodore Roosevelt**',
    '"The future belongs to those who believe in the beauty of their dreams." - **Eleanor Roosevelt**',
]

_joke_index = [0]
_fact_index = [0]
_quote_index = [0]


def next_joke():
    j = JOKES[_joke_index[0] % len(JOKES)]
    _joke_index[0] += 1
    return f"😄 Here's one for you:\n\n*{j}* 🤣\n\nWant another? Just ask!"


def next_fact():
    f = FUN_FACTS[_fact_index[0] % len(FUN_FACTS)]
    _fact_index[0] += 1
    return f"🤓 **Fun Fact:**\n\n{f}\n\nWant another fun fact? Just ask!"


def next_quote():
    q = QUOTES[_quote_index[0] % len(QUOTES)]
    _quote_index[0] += 1
    return f"✨ **Quote of the moment:**\n\n> {q}\n\nYou've got this! 💪"


def current_time():
    now = datetime.datetime.now()
    return f"⏰ The current time is **{now.strftime('%I:%M %p')}**."


def current_date():
    now = datetime.datetime.now()
    return f"📅 Today is **{now.strftime('%A, %B %d, %Y')}**."


KNOWLEDGE_BASE = [
    # -- Greetings ----------------------------------------------
    {
        "keywords": ["hello", "hi", "hey", "howdy", "greetings", "good morning",
                     "good afternoon", "good evening", "sup", "what's up"],
        "response": "👋 Hello! I'm AskMe AI, your knowledge base assistant. "
                    "I'm here to help answer your questions. What would you like to know?",
        "weight": 10,
    },
    {
        "keywords": ["how are you", "how do you do", "how's it going", "you ok", "doing well"],
        "response": "I'm doing great, thanks for asking! 😊 I'm always ready to help. "
                    "What can I assist you with today?",
        "weight": 10,
    },

    # -- About the bot ------------------------------------------
    {
        "keywords": ["who are you", "what are you", "your name", "introduce yourself",
                     "tell me about yourself", "what is askme"],
        "response": "I'm **AskMe AI** 🤖 — a smart offline chatbot powered by a "
                    "built-in Python knowledge base. I can answer general questions, "
                    "help with FAQs, and guide you through common topics. No internet required!",
        "weight": 9,
    },
    {
        "keywords": ["what can you do", "your capabilities", "help me", "what do you know",
                     "topics you cover", "abilities", "what topics"],
        "response": (
            "Here's what I can help with:\n\n"
            "• 👋 Greetings & general chat\n"
            "• ❓ Frequently asked questions\n"
            "• 💡 Tips & advice\n"
            "• 🌍 General knowledge\n"
            "• 🔐 Privacy & security basics\n"
            "• ⏰ Time & date info\n"
            "• 📚 Learning & education guidance\n"
            "• 💪 Health & wellness\n"
            "• ⚡ Productivity tips\n"
            "• 💻 Tech troubleshooting\n"
            "• 💰 Finance & budgeting\n"
            "• 😄 Jokes & fun facts\n"
            "• ✨ Motivational quotes\n\n"
            "Just ask and I'll do my best!"
        ),
        "weight": 9,
    },

    # -- Time & Date --------------------------------------------
    {
        "keywords": ["what time", "current time", "tell me the time", "time now", "time is it"],
        "response": current_time,
        "weight": 9,
    },
    {
        "keywords": ["what day", "today's date", "what date", "current date",
                     "what year", "what month", "date today"],
        "response": current_date,
        "weight": 9,
    },

    # -- Weather ------------------------------------------------
    {
        "keywords": ["weather", "temperature", "rain", "sunny", "forecast", "climate"],
        "response": (
            "🌤️ I don't have live weather data, but you can check:\n\n"
            "• **weather.com** for detailed forecasts\n"
            "• **Google** — search 'weather near me'\n"
            "• Your phone's built-in weather app\n\n"
            "For accurate info, check a live source!"
        ),
        "weight": 8,
    },

    # -- Security -----------------------------------------------
    {
        "keywords": ["password", "secure", "security", "hack", "privacy",
                     "protect", "safe", "strong password", "cybersecurity"],
        "response": (
            "🔐 **Password & Security Tips:**\n\n"
            "1. Use **12+ character passwords** mixing letters, numbers & symbols\n"
            "2. Never reuse passwords across sites\n"
            "3. Enable **two-factor authentication (2FA)**\n"
            "4. Use a reputable **password manager** (e.g., Bitwarden)\n"
            "5. Avoid public Wi-Fi for sensitive tasks\n\n"
            "Stay safe online! 🛡️"
        ),
        "weight": 8,
    },
    {
        "keywords": ["phishing", "scam", "spam", "fraud", "suspicious email", "fake", "malware"],
        "response": (
            "⚠️ **How to Spot Phishing / Scams:**\n\n"
            "• Urgent or threatening language ('Act NOW!')\n"
            "• Mismatched sender email addresses\n"
            "• Suspicious links — hover before clicking\n"
            "• Requests for personal info or passwords\n"
            "• Too-good-to-be-true offers\n\n"
            "When in doubt, **don't click** — contact the company directly."
        ),
        "weight": 8,
    },

    # -- Health -------------------------------------------------
    {
        "keywords": ["health", "exercise", "fitness", "workout", "stay healthy",
                     "diet", "nutrition", "water", "sleep"],
        "response": (
            "💪 **General Health Tips:**\n\n"
            "• Drink **8 glasses of water** daily\n"
            "• Aim for **7-9 hours** of sleep\n"
            "• Exercise **30 minutes** most days\n"
            "• Eat balanced meals with fruits & veggies\n"
            "• Manage stress with meditation or hobbies\n\n"
            "*Always consult a doctor for medical advice.*"
        ),
        "weight": 7,
    },
    {
        "keywords": ["mental health", "anxiety", "stress", "depression",
                     "sad", "overwhelmed", "burnout", "worry"],
        "response": (
            "💙 It's okay to feel stressed sometimes. Here are some tips:\n\n"
            "• Take short breaks throughout the day\n"
            "• Practice deep breathing or meditation\n"
            "• Talk to someone you trust\n"
            "• Limit social media if it affects your mood\n"
            "• Seek professional help if needed — it's a sign of strength!\n\n"
            "**You're not alone. 💛**"
        ),
        "weight": 7,
    },

    # -- Learning -----------------------------------------------
    {
        "keywords": ["learn", "study", "how to learn", "education", "course",
                     "skill", "improve", "tips for studying", "learning"],
        "response": (
            "📚 **Effective Learning Tips:**\n\n"
            "1. **Pomodoro Technique** — 25 min focus, 5 min break\n"
            "2. **Active recall** — test yourself instead of re-reading\n"
            "3. **Spaced repetition** — review over growing intervals\n"
            "4. Teach others to solidify your understanding\n"
            "5. Use platforms like **Coursera, Khan Academy, or YouTube**\n\n"
            "Consistency beats intensity every time! 🚀"
        ),
        "weight": 7,
    },

    # -- Productivity -------------------------------------------
    {
        "keywords": ["productivity", "focus", "procrastination", "time management",
                     "organize", "task", "to do", "get things done"],
        "response": (
            "⚡ **Productivity Boosters:**\n\n"
            "• **Prioritize** with the Eisenhower Matrix (urgent vs important)\n"
            "• Break big tasks into **small actionable steps**\n"
            "• Use apps like **Notion, Todoist, or Google Keep**\n"
            "• Eliminate distractions — silence notifications\n"
            "• Start with your **hardest task first** (eat the frog!)\n\n"
            "Small daily progress adds up! 🎯"
        ),
        "weight": 7,
    },

    # -- Tech Help ----------------------------------------------
    {
        "keywords": ["computer", "slow computer", "speed up", "pc",
                     "laptop", "restart", "freeze", "crash", "slow"],
        "response": (
            "💻 **Quick Computer Fixes:**\n\n"
            "• **Restart first** — solves 80% of issues\n"
            "• Clear browser cache & temp files\n"
            "• Check for malware with Windows Defender\n"
            "• Update drivers & operating system\n"
            "• Close unused background apps\n"
            "• Consider adding more RAM if consistently slow"
        ),
        "weight": 7,
    },
    {
        "keywords": ["internet", "wifi", "connection", "no internet",
                     "slow internet", "network", "router"],
        "response": (
            "🌐 **Internet Troubleshooting:**\n\n"
            "1. Restart your router (unplug 30 sec, replug)\n"
            "2. Check if other devices have the same issue\n"
            "3. Move closer to the router\n"
            "4. Forget and reconnect to the WiFi network\n"
            "5. Run Windows Network Troubleshooter\n"
            "6. Contact your ISP if all else fails\n\n"
            "Most issues are fixed with a simple restart! 🔄"
        ),
        "weight": 7,
    },

    # -- Finance ------------------------------------------------
    {
        "keywords": ["save money", "budget", "finance", "spending",
                     "investment", "saving", "money tips", "financial"],
        "response": (
            "💰 **Smart Money Tips:**\n\n"
            "• Follow the **50/30/20 rule**: 50% needs, 30% wants, 20% savings\n"
            "• Track every expense with apps like **Mint or YNAB**\n"
            "• Build an **emergency fund** (3-6 months of expenses)\n"
            "• Pay off high-interest debt first\n"
            "• Invest early — even small amounts compound!\n\n"
            "*This is general advice, not professional financial counsel.*"
        ),
        "weight": 7,
    },

    # -- Jokes & Fun --------------------------------------------
    {
        "keywords": ["joke", "funny", "make me laugh", "tell me a joke", "humor", "laugh"],
        "response": next_joke,
        "weight": 8,
    },
    {
        "keywords": ["another joke", "more jokes", "one more joke", "tell another", "next joke"],
        "response": next_joke,
        "weight": 9,
    },
    {
        "keywords": ["fun fact", "interesting fact", "did you know", "trivia", "fact"],
        "response": next_fact,
        "weight": 8,
    },
    {
        "keywords": ["another fact", "more facts", "one more fact", "next fact"],
        "response": next_fact,
        "weight": 9,
    },
    {
        "keywords": ["quote", "motivational", "inspiration", "motivate me",
                     "encourage", "inspire", "inspirational"],
        "response": next_quote,
        "weight": 7,
    },

    # -- AI & Tech ----------------------------------------------
    {
        "keywords": ["ai", "artificial intelligence", "machine learning",
                     "chatbot", "bot", "robot", "how do you work"],
        "response": (
            "🤖 **About AI & This Bot:**\n\n"
            "I'm a rule-based chatbot using **keyword matching** — "
            "no AI model or API, just a smart Python knowledge base!\n\n"
            "True AI (like ChatGPT) uses large language models trained on billions of texts. "
            "Key AI fields:\n\n"
            "• **Machine Learning** — systems that learn from data\n"
            "• **NLP** — understanding human language\n"
            "• **Computer Vision** — understanding images\n\n"
            "This bot runs entirely on your machine using Python! 🐍"
        ),
        "weight": 7,
    },

    # -- Philosophy ---------------------------------------------
    {
        "keywords": ["meaning of life", "life purpose", "why are we here",
                     "philosophy", "existence"],
        "response": (
            "🌌 Ah, the big question!\n\n"
            "Philosophers have debated this for centuries:\n\n"
            "• **Aristotle**: Pursue *eudaimonia* (happiness/flourishing)\n"
            "• **Existentialism**: You create your own meaning\n"
            "• **Science**: We're stardust experiencing itself\n"
            "• **42** — as Douglas Adams famously suggested 😄\n\n"
            "What do *you* think?"
        ),
        "weight": 6,
    },

    # -- Farewell -----------------------------------------------
    {
        "keywords": ["bye", "goodbye", "see you", "later", "take care",
                     "farewell", "quit", "exit"],
        "response": "👋 Goodbye! It was great chatting with you. "
                    "Come back anytime you have questions. Take care! 😊",
        "weight": 10,
    },

    # -- Gratitude ----------------------------------------------
    {
        "keywords": ["thank you", "thanks", "thank", "appreciate",
                     "helpful", "great job", "awesome", "amazing"],
        "response": "😊 You're very welcome! I'm always happy to help. "
                    "Feel free to ask anything else anytime!",
        "weight": 9,
    },

    # -- Affirmations -------------------------------------------
    {
        "keywords": ["yes", "yeah", "yep", "sure", "okay", "ok",
                     "alright", "absolutely", "definitely"],
        "response": "Great! 👍 What else can I help you with?",
        "weight": 3,
    },
    {
        "keywords": ["no", "nope", "not really", "never mind", "nothing", "nah"],
        "response": "No problem at all! 😊 If you think of anything later, I'm always here.",
        "weight": 3,
    },
]


# ===============================================================
#  MATCHING ENGINE
# ===============================================================

def normalize(text: str) -> str:
    """Lowercase and strip punctuation."""
    return re.sub(r"[^\w\s]", "", text.lower()).strip()


def find_best_match(user_input: str) -> dict:
    """
    Score every KB entry and return the best match.
    Returns dict: { 'text': str, 'confidence': float }
    """
    inp = normalize(user_input)
    tokens = inp.split()

    best_entry = None
    best_score = 0.0

    for entry in KNOWLEDGE_BASE:
        score = 0.0
        for keyword in entry["keywords"]:
            kw = normalize(keyword)

            if kw in inp:
                # Multi-word phrase match gets higher bonus
                phrase_bonus = len(kw.split())
                score += phrase_bonus * entry["weight"]
            else:
                # Partial token-level match
                kw_tokens = kw.split()
                for tok in tokens:
                    if any(k == tok and len(k) > 2 for k in kw_tokens):
                        score += 0.5 * entry["weight"]

        if score > best_score:
            best_score = score
            best_entry = entry

    if best_entry and best_score > 0:
        confidence = min(best_score / 10.0, 1.0)
        response = best_entry["response"]
        text = response() if callable(response) else response
        return {"text": text, "confidence": round(confidence, 2)}

    # Fallback response
    return {
        "text": (
            "🤔 Hmm, I'm not sure about that one. Try rephrasing or ask about:\n\n"
            "• Health tips 💪\n"
            "• Productivity ⚡\n"
            "• Tech help 💻\n"
            "• Jokes 😄\n"
            "• Security tips 🔐\n"
            "• Fun facts 🤓\n"
            "• Learning advice 📚"
        ),
        "confidence": 0.0,
    }


# ===============================================================
#  HTTP SERVER  (pure stdlib — no pip installs needed)
# ===============================================================

class ChatHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        """Override to print concise request logs."""
        print(f"  [{self.log_date_time_string()}] {format % args}")

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: str, content_type: str):
        try:
            with open(path, "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_error(404, "File not found")

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send_file("index.html", "text/html; charset=utf-8")
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/chat":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                user_msg = data.get("message", "").strip()
                if not user_msg:
                    self._send_json({"error": "Empty message"}, 400)
                    return
                result = find_best_match(user_msg)
                self._send_json(result)
            except (json.JSONDecodeError, Exception) as e:
                self._send_json({"error": str(e)}, 500)
        else:
            self.send_error(404)


# ===============================================================
#  ENTRY POINT
# ===============================================================

HOST = "localhost"
PORT = 5000

if __name__ == "__main__":
    # Ensure UTF-8 output on Windows terminals
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    server = HTTPServer((HOST, PORT), ChatHandler)
    print("=" * 52)
    print("  AskMe AI -- Python Knowledge Base Chatbot")
    print("=" * 52)
    print(f"  [OK]  Server running at  http://{HOST}:{PORT}")
    print(f"  [KB]  Knowledge base:    {len(KNOWLEDGE_BASE)} entries loaded")
    print(f"  [--]  Press Ctrl+C to stop")
    print("=" * 52)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped. Goodbye!")
        server.server_close()
