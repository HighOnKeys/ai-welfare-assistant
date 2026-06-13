# 🇮🇳 AI Welfare Scheme Assistant

> A low-bandwidth, multilingual conversational assistant that helps rural users discover the government welfare schemes they're eligible for, understand the required documents, and get a personalised shortlist — built for WhatsApp.

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Demo-FF4B4B.svg)](https://ai-welfare-assistant.streamlit.app/)
[![Twilio](https://img.shields.io/badge/Twilio-WhatsApp-25D366.svg)](https://www.twilio.com/whatsapp)
[![LangChain](https://img.shields.io/badge/LangChain-RAG-1C3C3C.svg)](https://www.langchain.com/)

---

## 📌 The Problem

India runs 950+ central and state welfare schemes, but a 2023 NITI Aayog study found **fewer than 40% of eligible rural beneficiaries know which schemes they qualify for**. The bottleneck isn't policy — it's information asymmetry, language barriers, and intimidating documentation.

This project closes that gap with a conversational assistant that meets users where they already are: **WhatsApp**.

---

## ✨ Features

- 🗣️ **Conversational eligibility check** — 8 simple questions, no forms, no jargon
- 🎯 **Personalised shortlist** across 8 high-impact central schemes
- 📚 **RAG-grounded answers** — every explanation is retrieved from official scheme data, not generated from memory, with an explicit "I don't have enough verified information" fallback to prevent hallucinated entitlements
- 🌐 **Multilingual** — English + Hindi (Streamlit demo)
- 📱 **WhatsApp-native** — works on a basic smartphone with WhatsApp, no app install, no high-bandwidth portal
- 🖥️ **Streamlit dashboard** — for live demos and internal testing, powered by the same backend

---

## 🏗️ Architecture

```
                ┌──────────────────────┐
                │   Shared Backend      │
                │  ─────────────────    │
                │  eligibility.py        │  ← rule-based matching engine
                │  rag.py                 │  ← FAISS + Groq (Llama 3.3 70B)
                └─────────┬─────────────┘
                          │
            ┌─────────────┴─────────────┐
            │                            │
   ┌────────▼────────┐         ┌────────▼────────┐
   │  app.py          │         │ whatsapp_bot.py  │
   │  (Streamlit)     │         │ (Flask + Twilio) │
   │  Demo dashboard  │         │ Production-style │
   │                  │         │ low-bandwidth UI │
   └──────────────────┘         └──────────────────┘
```

Both interfaces call the **same** eligibility and RAG logic — Streamlit is for demos and testing; WhatsApp is the deliverable that addresses the brief's "₹500 keypad phone" requirement.

---

## 📋 Schemes Covered

| Scheme | Key Benefit |
|---|---|
| PM-KISAN | ₹6,000/year direct cash transfer to farmers |
| Ayushman Bharat | Up to ₹5,00,000/year health insurance |
| PMAY | Housing construction assistance |
| Ujjwala Yojana | Free LPG connection for eligible women |
| MGNREGA | 100 days/year guaranteed rural wage employment |
| Sukanya Samriddhi Yojana | High-interest savings for girl children |
| PM Shram Yogi Maandhan | ₹3,000/month pension after age 60 |
| PMJJBY | ₹2,00,000 life insurance cover |

---

## 🚀 Getting Started

### 1. Clone & set up environment

```bash
git clone <your-repo-url>
cd welfare-chatbot
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API keys

Create a `.env` file in the root directory:

```
GROQ_API_KEY=your_groq_api_key_here
```

Get a free key from [console.groq.com](https://console.groq.com/keys).

### 3. Run the Streamlit demo

```bash
streamlit run app.py
```

### 4. Run the WhatsApp bot (local + Twilio Sandbox)

```bash
cd backend
python whatsapp_bot.py
```

In a separate terminal, expose it with ngrok:

```bash
ngrok http 5001
```

Set the generated `https://<your-ngrok-url>/whatsapp` as the webhook in your [Twilio WhatsApp Sandbox settings](https://www.twilio.com/console/sms/whatsapp/sandbox) (method: POST).

---

## 📁 Project Structure

```
welfare-chatbot/
├── app.py                    # Streamlit demo dashboard
├── backend/
│   ├── eligibility.py        # Rule-based eligibility engine
│   ├── rag.py                # RAG pipeline (FAISS + Groq)
│   └── whatsapp_bot.py        # Flask + Twilio WhatsApp webhook
├── data/
│   ├── shcemes.csv
│   └── schemes.txt           # Knowledge base for RAG
├── requirements.txt
└── .env                        # API keys (not committed)
```

---

## ⚠️ Known Limitations & Next Steps

- **Hindi on WhatsApp**: Currently English-only on WhatsApp (Hindi is supported in the Streamlit demo). Extending via the bot's existing language-toggle pattern is the immediate next step.
- **Session storage**: User progress is stored in memory; resets on server restart. A production deployment would use Redis or a lightweight database.
- **Eligibility proxies**: Some schemes (e.g. Ayushman Bharat) use simplified proxies (BPL card status, age 70+) in place of the real SECC-2011 deprivation database, which isn't publicly accessible. Documented inline in `eligibility.py`.
- **Response time**: Eligibility matching is near-instant (~1-2s). RAG-based scheme explanations take ~5s on broadband due to embedding model load and LLM inference. Caching pre-generated explanations for the fixed 8-scheme catalogue would bring this under the brief's 3-second target.
- **Hallucination guard**: The RAG prompt instructs the model to say "I do not have enough verified information" for out-of-scope queries — tested and working, but this relies on the LLM following instructions rather than retrieval returning empty results.
- **Language scaling**: Built for English + Hindi (meeting the brief's minimum of 2 languages). Scaling to Tamil, Bengali, Marathi etc. would use the AI4Bharat IndicTrans2 pipeline.

---

## 📊 Impact Potential

For a district or NGO with 10,000 beneficiary households, even a conservative 20-point lift in scheme enrollment translates to an estimated **₹1-2 crore/year in additional entitlements reaching households**, across just 3 of the 8 covered schemes (PM-KISAN, Ayushman Bharat, MGNREGA). See `impact_projection.md` for the full breakdown and assumptions.

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit (demo), WhatsApp via Twilio (production-style)
- **Backend**: Flask
- **LLM**: Groq (Llama 3.3 70B)
- **RAG**: LangChain + FAISS + HuggingFace sentence-transformers
- **Tunneling**: ngrok
