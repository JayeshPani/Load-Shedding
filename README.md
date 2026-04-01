# Load Shedding Smart Scheduler

A WhatsApp-native AI energy advisor for South African households. Every morning at 6 AM, the app automatically pulls the real load shedding schedule, checks the solar forecast, reads the household's simulated battery state, and sends a plain-English daily appliance plan over WhatsApp.

**College Project | 100% Free Stack | Zero Hardware Required**

---

## What the family receives on WhatsApp at 6 AM

```
Good morning! Today's load shedding: 10 AM–12 PM & 6 PM–8 PM (Stage 3).
Battery: 78% | Solar peak: 11 AM–2 PM (est. 2.1 kWh)

My plan for today:
• Run geyser NOW (grid available, battery healthy)
• Washing machine → 1 PM solar window
• Water pump → avoid during cuts

Reply CHANGE, STATUS, or ask me anything.
```

---

## What is Real vs Simulated

| Component              | Real or Simulated | Why                       |
|------------------------|-------------------|---------------------------|
| Load shedding schedule | Real              | EskomSePush API           |
| Solar / weather forecast | Real            | Open-Meteo API            |
| WhatsApp messages      | Real              | Twilio Sandbox            |
| AI scheduling brain    | Real              | Gemini API                |
| Inverter + battery data | Simulated        | No hardware needed        |
| Household appliances   | Simulated         | Hardcoded realistic data  |

---

## Tech Stack

### Real Data Sources
| Tool | What it does | Cost |
|------|-------------|------|
| EskomSePush API | Real load shedding schedules for SA | Free — 50 calls/day |
| Open-Meteo API | Real solar irradiance + weather forecast | Free — no key needed |

### Simulated (Your Code)
| Tool | What it does |
|------|-------------|
| `SimulatedInverter` | Fake battery %, solar watts, grid status |
| `SimulatedHousehold` | Fake appliance list with deadlines + wattages |

### AI Brain
| Tool | What it does | Cost |
|------|-------------|------|
| Gemini API | Reasons over all data, produces the daily plan | Free — 1500 req/day |

### Backend
| Tool | What it does |
|------|-------------|
| FastAPI | Python web framework — the app's server |
| APScheduler | Runs the 6 AM job automatically |
| SQLite | Stores plans + household data (built into Python) |

### Messaging
| Tool | What it does | Cost |
|------|-------------|------|
| Twilio WhatsApp Sandbox | Sends + receives WhatsApp messages | Free for dev |

### Deployment
| Tool | What it does | Cost |
|------|-------------|------|
| Railway | Hosts the FastAPI app in the cloud | Free credits ($5/mo) |

---

## How Everything Connects

```
6:00 AM — APScheduler wakes up
    │
    ├── 1. Fetch load shedding schedule  →  EskomSePush API
    ├── 2. Fetch solar forecast          →  Open-Meteo API
    ├── 3. Read inverter state           →  SimulatedInverter class
    ├── 4. Read household profile        →  SimulatedHousehold class
    │
    ├── 5. All 4 inputs → Gemini API → generates plain-English plan
    ├── 6. Save plan to SQLite
    └── 7. Send plan via Twilio → WhatsApp

User replies on WhatsApp
    └── Twilio webhook → FastAPI /webhook → Gemini parses reply
        → updates plan → sends confirmation back on WhatsApp
```

---

## Folder Structure

```
smart-scheduler/
├── simulators/
│   ├── __init__.py
│   ├── inverter.py          # SimulatedInverter class
│   └── household.py         # SimulatedHousehold class
│
├── integrations/
│   ├── __init__.py
│   ├── eskomsepush.py       # Calls EskomSePush API
│   ├── openmeteo.py         # Calls Open-Meteo API
│   └── whatsapp.py          # Twilio send / receive
│
├── agent/
│   ├── __init__.py
│   └── scheduler.py         # Gemini agent logic
│
├── api/
│   ├── __init__.py
│   └── main.py              # FastAPI app + APScheduler
│
├── db/
│   ├── __init__.py
│   └── models.py            # SQLite schema
│
├── .env                     # All API keys — NEVER commit this
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Prerequisites

- Python 3.10+
- A free [EskomSePush](https://eskomsepush.com) account (API key)
- A free [Google AI Studio](https://aistudio.google.com) account (Gemini API key)
- A free [Twilio](https://twilio.com) account (WhatsApp Sandbox)
- A free [Railway](https://railway.app) account (deployment)

---

## Local Setup

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd smart-scheduler

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env file
cp .env.example .env
# Fill in your API keys (see API Setup below)

# 5. Run the app locally
uvicorn api.main:app --reload
```

---

## Environment Variables

Create a `.env` file in the project root with the following keys:

```env
ESKOMSEPUSH_KEY=your_eskomsepush_token_here
GEMINI_KEY=your_gemini_api_key_here
TWILIO_SID=your_twilio_account_sid_here
TWILIO_TOKEN=your_twilio_auth_token_here
TWILIO_FROM=whatsapp:+14155238886
```

> **Never commit `.env` to GitHub.** It is already listed in `.gitignore`. Set these as environment variables in the Railway dashboard for production.

---

## API Setup Guide

### EskomSePush
1. Go to [eskomsepush.com](https://eskomsepush.com) → click **Business API** → sign up
2. Verify your email and copy the API token from your dashboard
3. Add to `.env`: `ESKOMSEPUSH_KEY=your_token`

### Open-Meteo
- No signup required — call the URL directly
- Cape Town coordinates: `latitude=-33.9249`, `longitude=18.4241`
- No key needed in `.env`

### Google Gemini
1. Go to [aistudio.google.com](https://aistudio.google.com) → sign in with Google
2. Click **Get API Key** → **Create API Key**
3. Add to `.env`: `GEMINI_KEY=your_key`
4. Free tier: 1500 requests/day

### Twilio WhatsApp Sandbox
1. Go to [twilio.com](https://twilio.com) → sign up free
2. Go to **Console → Messaging → Try it out → Send a WhatsApp message**
3. Follow the Sandbox join instructions
4. Add `TWILIO_SID`, `TWILIO_TOKEN`, and `TWILIO_FROM` to `.env`
5. Set the Sandbox **"When a message comes in"** webhook URL to:
   `https://your-railway-app.up.railway.app/webhook`

---

## Deployment on Railway

1. Push your code to GitHub
2. Go to [railway.app](https://railway.app) → sign up with GitHub
3. Click **New Project → Deploy from GitHub repo** → select your repo
4. Railway auto-detects Python and installs `requirements.txt`
5. Go to **Variables** tab → add all keys from your `.env` file
6. Go to **Settings** → set Start Command:
   ```
   uvicorn api.main:app --host 0.0.0.0 --port $PORT
   ```
7. Railway gives you a public URL (e.g. `https://smart-scheduler.up.railway.app`)
8. Paste that URL + `/webhook` into your Twilio Sandbox settings

> Railway gives $5 free credits/month. A small FastAPI + SQLite app uses roughly $0.50–$1.00/month — well within the free tier for a college project.

---

## Week-by-Week Build Plan

| Week | Focus | What You Build |
|------|-------|---------------|
| 1 | Simulator Classes | `SimulatedInverter`, `SimulatedHousehold` |
| 2 | Real Data Integrations | `eskomsepush.py`, `openmeteo.py` |
| 3 | Gemini AI Agent | `agent/scheduler.py`, prompt engineering |
| 4 | WhatsApp Integration | `whatsapp.py`, Twilio webhook |
| 5 | FastAPI + Scheduler | `api/main.py`, APScheduler 6 AM cron |
| 6 | Deploy + Polish | Railway deployment, live demo |

---

## Demo Script

1. **Open WhatsApp** — show a real phone with the test number open
2. **Trigger manually** — hit `/run-now` in your browser; message arrives within seconds
3. **Read the plan** — point out the real EskomSePush + Open-Meteo data
4. **Reply on WhatsApp** — type "Change washing machine to 4 PM"; Gemini responds in seconds
5. **Show the code** — `simulators/inverter.py` and `agent/scheduler.py`
6. **Show Railway** — live dashboard with the scheduled 6 AM job

> "We built an AI energy advisor that pulls real South African load shedding schedules, reasons over them with Gemini, and sends households an optimised daily appliance plan over WhatsApp — completely free to run, no hardware required."

---

## Security Notes

- Never hardcode API keys in Python files
- Always use environment variables via `.env` locally and Railway Variables in production
- Add `.env` to `.gitignore` before your first commit
