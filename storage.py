import json, os, uuid
from datetime import datetime

DATA_FILE = "workers.json"

def load_workers() -> list:
    if not os.path.exists(DATA_FILE):
        _init_demo()
    try:
        with open(DATA_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_worker(profile: dict) -> bool:
    workers = load_workers()
    if "id" not in profile or not profile["id"]:
        profile["id"] = str(uuid.uuid4())[:8]
    profile["created_at"] = datetime.now().isoformat()
    workers.append(profile)
    return _write(workers)

def add_rating(worker_id: str, stars: int, comment: str="") -> bool:
    workers = load_workers()
    for w in workers:
        if w.get("id")==worker_id:
            if "reviews" not in w: w["reviews"]=[]
            w["reviews"].append({"stars":stars,"comment":comment,"date":datetime.now().strftime("%Y-%m-%d")})
            w["rating"] = round(sum(r["stars"] for r in w["reviews"])/len(w["reviews"]),1)
            return _write(workers)
    return False

def _write(workers):
    try:
        with open(DATA_FILE,"w",encoding="utf-8") as f:
            json.dump(workers,f,ensure_ascii=False,indent=2)
        return True
    except Exception as e:
        print(f"Write error: {e}")
        return False

def _init_demo():
    demo = [
        {"id":"d001","name":"محمد زفر","skill":"Plumber","experience":"15 سال",
         "city":"Karachi, Nazimabad","daily_rate":"2500","phone":"0300-1234567","available":True,
         "rating":4.5,"bio":"Experienced plumber with 15 years in Karachi, specializing in pipe fitting and bathroom installations.",
         "reviews":[{"stars":5,"comment":"بہت اچھا کام","date":"2025-04-01"},{"stars":4,"comment":"وقت پر آئے","date":"2025-04-10"}],"created_at":"2025-04-01T10:00:00"},

        {"id":"d002","name":"علی احمد","skill":"Electrician","experience":"8 سال",
         "city":"Lahore, Gulberg","daily_rate":"3000","phone":"0321-9876543","available":True,
         "rating":5.0,"bio":"Expert electrician with 8 years experience in home wiring, industrial panels, and solar installation.",
         "reviews":[{"stars":5,"comment":"بہترین الیکٹریشن","date":"2025-04-05"},{"stars":5,"comment":"کام بہت صاف","date":"2025-04-12"}],"created_at":"2025-04-02T10:00:00"},

        {"id":"d003","name":"خالد محمود","skill":"Carpenter","experience":"12 سال",
         "city":"Islamabad, G-9","daily_rate":"2800","phone":"0333-5551234","available":False,
         "rating":4.0,"bio":"Skilled carpenter with 12 years experience in custom furniture and wooden structures.",
         "reviews":[{"stars":4,"comment":"اچھا کام کیا","date":"2025-04-08"}],"created_at":"2025-04-03T10:00:00"},

        {"id":"d004","name":"شاہد خان","skill":"Painter","experience":"6 سال",
         "city":"Karachi, Defence","daily_rate":"2000","phone":"0345-7778899","available":True,
         "rating":4.8,"bio":"Professional painter with 6 years experience in interior and exterior wall finishing.",
         "reviews":[{"stars":5,"comment":"رنگ بہت سندر","date":"2025-04-15"},{"stars":5,"comment":"محنتی ہے","date":"2025-04-20"},{"stars":4,"comment":"وقت پر آئے","date":"2025-04-22"}],"created_at":"2025-04-04T10:00:00"},

        {"id":"d005","name":"رحیم بخش","skill":"Mason","experience":"20 سال",
         "city":"Lahore, Model Town","daily_rate":"3500","phone":"0311-2223344","available":True,
         "rating":4.7,"bio":"Highly experienced mason with 20 years in construction, plastering, and structural work.",
         "reviews":[{"stars":5,"comment":"تجربہ کار استاد","date":"2025-04-18"},{"stars":4,"comment":"مضبوط کام","date":"2025-04-25"}],"created_at":"2025-04-05T10:00:00"},

        {"id":"d006","name":"طارق حسین","skill":"AC Technician","experience":"7 سال",
         "city":"Rawalpindi, Saddar","daily_rate":"2200","phone":"0315-4445566","available":True,
         "rating":4.3,"bio":"Certified AC technician with 7 years experience in installation, servicing, and repair of all AC brands.",
         "reviews":[{"stars":4,"comment":"جلدی ٹھیک کیا","date":"2025-04-11"},{"stars":5,"comment":"سستا اور اچھا","date":"2025-04-19"}],"created_at":"2025-04-06T10:00:00"},

        {"id":"d007","name":"ارشد علی","skill":"Driver","experience":"10 سال",
         "city":"Karachi, Gulshan-e-Iqbal","daily_rate":"1800","phone":"0312-6667788","available":True,
         "rating":4.6,"bio":"Professional driver with 10 years experience, valid license, familiar with all Karachi routes.",
         "reviews":[{"stars":5,"comment":"بہت اچھا ڈرائیور","date":"2025-04-14"},{"stars":4,"comment":"وقت کا پابند","date":"2025-04-21"}],"created_at":"2025-04-07T10:00:00"},

        {"id":"d008","name":"عمران قریشی","skill":"Mobile Repair","experience":"5 سال",
         "city":"Faisalabad, D-Ground","daily_rate":"1500","phone":"0303-9990011","available":True,
         "rating":4.4,"bio":"Mobile phone technician with 5 years experience repairing all smartphone brands including screen replacement.",
         "reviews":[{"stars":4,"comment":"جلدی ٹھیک کیا","date":"2025-04-09"},{"stars":5,"comment":"سستا کام","date":"2025-04-17"}],"created_at":"2025-04-08T10:00:00"},

        {"id":"d009","name":"نادر شاہ","skill":"Welder","experience":"14 سال",
         "city":"Peshawar, Hayatabad","daily_rate":"2600","phone":"0309-1112233","available":False,
         "rating":4.2,"bio":"Expert welder with 14 years experience in metal fabrication, gates, and structural welding.",
         "reviews":[{"stars":4,"comment":"مضبوط کام","date":"2025-04-13"}],"created_at":"2025-04-09T10:00:00"},

        {"id":"d010","name":"جاوید اقبال","skill":"Mechanic","experience":"11 سال",
         "city":"Lahore, Shahdara","daily_rate":"2400","phone":"0300-5556677","available":True,
         "rating":4.9,"bio":"Experienced auto mechanic with 11 years specializing in engine repair and general vehicle maintenance.",
         "reviews":[{"stars":5,"comment":"بہترین مکینک","date":"2025-04-16"},{"stars":5,"comment":"ماہر ہے","date":"2025-04-23"},{"stars":4,"comment":"اچھا کام","date":"2025-04-27"}],"created_at":"2025-04-10T10:00:00"},

        {"id":"d011","name":"فیصل رضا","skill":"Tile Fixer","experience":"9 سال",
         "city":"Karachi, North Nazimabad","daily_rate":"2300","phone":"0322-3334455","available":True,
         "rating":4.5,"bio":"Professional tile fixer with 9 years experience in floor and wall tiling for residential and commercial projects.",
         "reviews":[{"stars":5,"comment":"کام بہت صاف","date":"2025-04-12"},{"stars":4,"comment":"وقت پر آئے","date":"2025-04-24"}],"created_at":"2025-04-11T10:00:00"},

        {"id":"d012","name":"سلمان حیدر","skill":"Computer Repair","experience":"6 سال",
         "city":"Islamabad, F-10","daily_rate":"1700","phone":"0336-8889900","available":True,
         "rating":4.1,"bio":"Computer repair specialist with 6 years experience in hardware troubleshooting, software installation, and networking.",
         "reviews":[{"stars":4,"comment":"جلدی ٹھیک کیا","date":"2025-04-10"}],"created_at":"2025-04-12T10:00:00"},

        {"id":"d013","name":"غلام مصطفیٰ","skill":"Mazdoor","experience":"8 سال",
         "city":"Multan, Gulgasht","daily_rate":"1200","phone":"0301-7778899","available":True,
         "rating":4.0,"bio":"Hard working general laborer with 8 years experience in construction, loading, and shifting work.",
         "reviews":[{"stars":4,"comment":"محنتی ہے","date":"2025-04-15"},{"stars":4,"comment":"وقت پر آئے","date":"2025-04-26"}],"created_at":"2025-04-13T10:00:00"},

        {"id":"d014","name":"اصغر علی","skill":"Gardener","experience":"13 سال",
         "city":"Lahore, DHA","daily_rate":"1600","phone":"0344-2223344","available":True,
         "rating":4.7,"bio":"Experienced gardener with 13 years in lawn maintenance, plant care, and landscape designing.",
         "reviews":[{"stars":5,"comment":"باغ بہت سندر بنایا","date":"2025-04-11"},{"stars":4,"comment":"اچھا کام","date":"2025-04-22"}],"created_at":"2025-04-14T10:00:00"},

        {"id":"d015","name":"بشیر احمد","skill":"Cook","experience":"16 سال",
         "city":"Karachi, Clifton","daily_rate":"2800","phone":"0318-5556677","available":False,
         "rating":4.8,"bio":"Professional cook with 16 years experience in Pakistani cuisine, event catering, and home cooking services.",
         "reviews":[{"stars":5,"comment":"کھانا بہت لذیذ","date":"2025-04-08"},{"stars":5,"comment":"صفائی کا خیال","date":"2025-04-20"}],"created_at":"2025-04-15T10:00:00"},

        {"id":"d016","name":"زاہد حسین","skill":"CCTV Technician","experience":"4 سال",
         "city":"Rawalpindi, Bahria Town","daily_rate":"2000","phone":"0307-4445566","available":True,
         "rating":4.3,"bio":"CCTV installation specialist with 4 years experience in security camera systems for homes and businesses.",
         "reviews":[{"stars":4,"comment":"اچھا کام کیا","date":"2025-04-18"}],"created_at":"2025-04-16T10:00:00"},

        {"id":"d017","name":"محسن رضا","skill":"Internet Technician","experience":"5 سال",
         "city":"Karachi, Korangi","daily_rate":"1800","phone":"0316-1112233","available":True,
         "rating":4.2,"bio":"Internet and networking technician with 5 years experience in fiber optic, router setup, and WiFi installation.",
         "reviews":[{"stars":4,"comment":"جلدی حل کیا","date":"2025-04-17"},{"stars":4,"comment":"سستا","date":"2025-04-25"}],"created_at":"2025-04-17T10:00:00"},

        {"id":"d018","name":"حمزہ شیخ","skill":"Cleaner","experience":"3 سال",
         "city":"Lahore, Johar Town","daily_rate":"1000","phone":"0302-6667788","available":True,
         "rating":4.5,"bio":"Professional cleaner with 3 years experience in deep cleaning, sofa cleaning, and post-construction cleanup.",
         "reviews":[{"stars":5,"comment":"بہت صاف کیا","date":"2025-04-19"},{"stars":4,"comment":"محنتی ہے","date":"2025-04-26"}],"created_at":"2025-04-18T10:00:00"},

        {"id":"d019","name":"عابد علی","skill":"Helper","experience":"2 سال",
         "city":"Islamabad, G-11","daily_rate":"900","phone":"0314-9990011","available":True,
         "rating":3.9,"bio":"Reliable helper with 2 years experience in general assistance, shifting, and daily household tasks.",
         "reviews":[{"stars":4,"comment":"اچھا لڑکا","date":"2025-04-21"}],"created_at":"2025-04-19T10:00:00"},

        {"id":"d020","name":"یاسر ملک","skill":"Laundry/Iron","experience":"7 سال",
         "city":"Karachi, Saddar","daily_rate":"1100","phone":"0308-3334455","available":True,
         "rating":4.4,"bio":"Laundry and ironing specialist with 7 years experience, offering pickup and delivery services.",
         "reviews":[{"stars":5,"comment":"کپڑے بالکل صاف","date":"2025-04-13"},{"stars":4,"comment":"جلدی کیا","date":"2025-04-23"}],"created_at":"2025-04-20T10:00:00"},
    ]
    _write(demo)
