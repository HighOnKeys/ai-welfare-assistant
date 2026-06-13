from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from eligibility import get_eligible_schemes
from rag import get_scheme_info

app = Flask(__name__)

# Stores each user's progress. Key = phone number, Value = their state.
# WARNING: this resets if the server restarts. Fine for a hackathon demo,
# not fine for production (would need a real database like Redis/SQLite).
sessions = {}

# The 8 questions, in order. Each has:
# - field: matches keys expected by get_eligible_schemes()
# - text: what to ask
# - parser: function to convert user's raw text into the right type/value


def parse_yes_no(text):
    text = text.strip().lower()
    if text in ["yes", "y", "haan", "हाँ", "han"]:
        return "Yes"
    if text in ["no", "n", "nahi", "नहीं"]:
        return "No"
    return None  # invalid input


QUESTIONS = [
    {
        "field": "occupation",
        "text": "What is your occupation?\n1. Farmer\n2. Unorganised Worker\n3. Other\n(Reply with 1, 2, or 3)",
        "parser": lambda t: {"1": "Farmer", "2": "Unorganised Worker", "3": "Other"}.get(t.strip())
    },
    {
        "field": "income",
        "text": "What is your annual family income in Rupees? (Just type the number, e.g. 150000)",
        "parser": lambda t: int(t.strip()) if t.strip().isdigit() else None
    },
    {
        "field": "house",
        "text": "Do you own a pucca (concrete) house? (yes/no)",
        "parser": parse_yes_no
    },
    {
        "field": "gender",
        "text": "What is your gender?\n1. Male\n2. Female\n(Reply with 1 or 2)",
        "parser": lambda t: {"1": "Male", "2": "Female"}.get(t.strip())
    },
    {
        "field": "rural",
        "text": "Do you live in a rural area? (yes/no)",
        "parser": parse_yes_no
    },
    {
        "field": "girl_child",
        "text": "Do you have a girl child below 10 years of age? (yes/no)",
        "parser": parse_yes_no
    },
    {
        "field": "age",
        "text": "What is your age? (Just type the number)",
        "parser": lambda t: int(t.strip()) if t.strip().isdigit() else None
    },
    {
        "field": "bpl_card",
        "text": "Do you have a BPL / priority household ration card? (yes/no)",
        "parser": parse_yes_no
    },
]


@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")

    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg.strip().lower() == "restart":
        sessions[sender] = {"step": 0, "answers": {}}
        msg.body("Restarting...\n\n" + QUESTIONS[0]["text"])
        return str(resp)

    # New user - start the flow
    if sender not in sessions:
        sessions[sender] = {"step": 0, "answers": {}}
        msg.body(
            "Welcome! I'll ask you a few questions to check which welfare schemes you may be eligible for.\n\n" + QUESTIONS[0]["text"])
        return str(resp)

    session = sessions[sender]
    step = session["step"]

    # If user already finished the eligibility flow, treat their message
    # as a request for details about one of the matched schemes.
    if step == "done":
        matched = session.get("matched_schemes", [])
        user_choice = incoming_msg.strip()

        # Find a matched scheme name that the user's message roughly matches
        found = None
        for scheme in matched:
            if scheme.lower() in user_choice.lower() or user_choice.lower() in scheme.lower():
                found = scheme
                break

        if found is None:
            msg.body("Sorry, I didn't recognize that scheme name. Please type one of the scheme names exactly as shown earlier, or send 'restart' to start over.")
            return str(resp)

        query = f"""Explain the scheme: {found}
Mention:
1. Benefits
2. Eligibility
3. Required Documents
4. Application Process
Keep it short and simple."""

        answer = get_scheme_info(query)
        msg.body(answer)
        return str(resp)

    # Otherwise, continue the normal question flow
    current_q = QUESTIONS[step]
    parsed = current_q["parser"](incoming_msg)

    if parsed is None:
        msg.body("Sorry, I didn't understand that.\n\n" + current_q["text"])
        return str(resp)

    session["answers"][current_q["field"]] = parsed
    session["step"] += 1

    # More questions left?
    if session["step"] < len(QUESTIONS):
        msg.body(QUESTIONS[session["step"]]["text"])
        return str(resp)

    # All questions answered - run eligibility check
    schemes, notes = get_eligible_schemes(session["answers"])

    if not schemes:
        reply_text = "Based on your answers, we couldn't match you to any schemes in our database right now. This may not cover all schemes you qualify for - please visit your nearest Common Service Centre for a full check."
    else:
        reply_text = f"You may be eligible for {len(schemes)} scheme(s):\n\n"
        for s in schemes:
            reply_text += f"- {s}\n"
        reply_text += "\nReply with the name of any scheme above to get full details (benefits, documents, how to apply)."

    # Reset session so user can restart, but keep the matched schemes for follow-up
    session["matched_schemes"] = schemes
    session["step"] = "done"

    msg.body(reply_text)
    return str(resp)


if __name__ == "__main__":
    app.run(port=5001, debug=True)
