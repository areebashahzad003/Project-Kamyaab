import os
import json
import uuid
from groq import Groq

def build_profile(transcript: str) -> dict:
    if not transcript or not transcript.strip():
        return None
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        system = """You extract worker profile info from Urdu speech transcripts.
Return ONLY a valid JSON object — no markdown, no extra text, no backticks.

Fields to extract:
- name (string): full name
- skill (string): must be exactly one of: Plumber, Electrician, AC Technician, Carpenter, Painter, Mason, Welder, Tile Fixer, Mobile Repair, Computer Repair, CCTV Technician, Internet Technician, Mechanic, Driver, Mazdoor, Helper, Gardener, Cook, Cleaner, Laundry/Iron, Other
- experience (string): years of experience e.g. "10 years" or "10 سال"
- city (string): city and area e.g. "Karachi, Nazimabad"
- daily_rate (string): number only e.g. "2500"
- phone (string): phone number
- available (boolean): true if available now
- bio (string): one professional English sentence about this worker

Defaults if not mentioned: name=Worker, skill=Other, experience=Not mentioned, city=Not mentioned, daily_rate=0, phone=Not provided, available=true, bio=""

Return ONLY the JSON object."""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": f"Transcript:\n{transcript}"}
            ],
            temperature=0.1,
            max_tokens=500,
        )

        raw = response.choices[0].message.content.strip()

        # Clean markdown if present
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        # Find JSON object
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            raw = raw[start:end]

        p = json.loads(raw)
        p["id"] = str(uuid.uuid4())[:8]
        p["rating"] = 0
        p["reviews"] = []
        return p

    except Exception as e:
        print(f"Profile error: {e}")
        return {
            "id": str(uuid.uuid4())[:8],
            "name": "Worker",
            "skill": "Other",
            "experience": "Not mentioned",
            "city": "Not mentioned",
            "daily_rate": "0",
            "phone": "Not provided",
            "available": True,
            "bio": "",
            "rating": 0,
            "reviews": []
        }
