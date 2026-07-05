import streamlit as st
import os
from urllib.parse import quote
from dotenv import load_dotenv
from audio_recorder_streamlit import audio_recorder
from storage import load_workers, save_worker, add_rating
from voice import transcribe_audio_bytes, transcribe_audio
from profile_builder import build_profile

load_dotenv()
st.set_page_config(page_title="KaamYab", page_icon="K", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Noto+Nastaliq+Urdu:wght@400;600;700&family=Outfit:wght@400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Outfit',sans-serif;color:#fff;}
body,.stApp,[data-testid="stAppViewContainer"]{background-color:#1a5276!important;}
[data-testid="stHeader"],[data-testid="stToolbar"]{display:none!important;}
#MainMenu,footer,header{visibility:hidden!important;}
.block-container{padding:0.5rem 1.1rem 5rem!important;max-width:480px;margin:auto;}
.kname{font-family:'Playfair Display',serif;font-size:2.7rem;font-weight:800;color:#fff;text-align:center;letter-spacing:0.5px;line-height:1.1;}
.k-line{width:44px;height:3px;background:#E8722A;border-radius:2px;margin:8px auto 10px;}
.stButton>button{font-family:'Outfit',sans-serif!important;font-weight:600!important;border-radius:12px!important;width:100%!important;padding:0.65rem 1rem!important;background:#E8722A!important;color:#fff!important;border:none!important;}
.stButton>button:hover{background:#cf611c!important;}
.back-btn .stButton>button{background:#6D1A36!important;width:auto!important;padding:0.4rem 1rem!important;}
.back-btn .stButton>button:hover{background:#5a1530!important;}
.burg-btn .stButton>button{background:#6D1A36!important;}
.burg-btn .stButton>button:hover{background:#5a1530!important;}
.stTextInput input,.stTextArea textarea{background:#fff!important;border:1px solid #ddd!important;border-radius:10px!important;color:#111!important;font-family:'Outfit',sans-serif!important;}
.stTextInput input::placeholder,.stTextArea textarea::placeholder{color:#999!important;}
div[data-baseweb="select"]>div{background:#E8722A!important;border:none!important;border-radius:10px!important;color:#fff!important;}
div[data-baseweb="select"] span{color:#fff!important;}
.stFileUploader>div{background:rgba(255,255,255,0.08)!important;border:1px dashed rgba(255,255,255,0.2)!important;border-radius:12px!important;}
.stCheckbox label{color:#fff!important;}
.stTextInput label,.stSelectbox label,.stFileUploader label,.stTextArea label{color:#fff!important;font-weight:600!important;}
div[data-testid='stVerticalBlock'] label{color:#fff!important;}
hr.d{border:none;border-top:1px solid rgba(255,255,255,0.1);margin:0.8rem 0;}
.dots{display:flex;gap:5px;margin-bottom:1.1rem;}
.dot{width:7px;height:7px;border-radius:50%;background:rgba(255,255,255,0.2);}
.dot.on{background:#E8722A;width:20px;border-radius:3px;}
.dot.done{background:rgba(232,114,42,0.35);}
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────
SKILLS_EN = ["Plumber","Electrician","AC Technician","Carpenter","Painter",
    "Mason","Welder","Tile Fixer","Mobile Repair","Computer Repair",
    "CCTV Technician","Internet Technician","Mechanic","Driver",
    "Mazdoor","Helper","Gardener","Cook","Cleaner","Laundry/Iron","Other"]
SKILLS_UR = {
    "Plumber":"پلمبر","Electrician":"الیکٹریشن","AC Technician":"اے سی ٹیکنیشن",
    "Carpenter":"بڑھئی","Painter":"پینٹر","Mason":"راج مستری","Welder":"ویلڈر",
    "Tile Fixer":"ٹائل مستری","Mobile Repair":"موبائل مکینک","Computer Repair":"کمپیوٹر مکینک",
    "CCTV Technician":"سی سی ٹی وی","Internet Technician":"انٹرنیٹ ٹیکنیشن",
    "Mechanic":"مکینک","Driver":"ڈرائیور","Mazdoor":"مزدور","Helper":"ہیلپر",
    "Gardener":"مالی","Cook":"باورچی","Cleaner":"صفائی والا","Laundry/Iron":"استری والا","Other":"دیگر"
}
CITIES_EN = ["Karachi","Lahore","Islamabad","Rawalpindi","Faisalabad","Multan",
    "Peshawar","Quetta","Hyderabad","Sialkot","Gujranwala","Sargodha",
    "Bahawalpur","Sukkur","Larkana","Abbottabad","Mardan","Mingora",
    "Dera Ghazi Khan","Sahiwal","Gujrat","Sheikhupura","Jhang","Chiniot",
    "Kasur","Rahim Yar Khan","Mirpur Khas","Nawabshah","Jacobabad",
    "Muzaffarabad","Gilgit","Skardu","Turbat","Khuzdar","Chaman",
    "Dera Ismail Khan","Bannu","Kohat","Chakwal","Jhelum"]
CITIES_UR = {
    "Karachi":"کراچی","Lahore":"لاہور","Islamabad":"اسلام آباد","Rawalpindi":"راولپنڈی",
    "Faisalabad":"فیصل آباد","Multan":"ملتان","Peshawar":"پشاور","Quetta":"کوئٹہ",
    "Hyderabad":"حیدرآباد","Sialkot":"سیالکوٹ","Gujranwala":"گوجرانوالہ","Sargodha":"سرگودھا",
    "Bahawalpur":"بہاولپور","Sukkur":"سکھر","Larkana":"لاڑکانہ","Abbottabad":"ایبٹ آباد",
    "Mardan":"مردان","Mingora":"منگورہ","Dera Ghazi Khan":"ڈیرہ غازی خان","Sahiwal":"ساہیوال",
    "Gujrat":"گجرات","Sheikhupura":"شیخوپورہ","Jhang":"جھنگ","Chiniot":"چنیوٹ",
    "Kasur":"قصور","Rahim Yar Khan":"رحیم یار خان","Mirpur Khas":"میرپور خاص",
    "Nawabshah":"نواب شاہ","Jacobabad":"جیکب آباد","Muzaffarabad":"مظفرآباد",
    "Gilgit":"گلگت","Skardu":"سکردو","Turbat":"تربت","Khuzdar":"خضدار",
    "Chaman":"چمن","Dera Ismail Khan":"ڈیرہ اسماعیل خان","Bannu":"بنوں",
    "Kohat":"کوہاٹ","Chakwal":"چکوال","Jhelum":"جہلم"
}
SKILL_CLR = {
    "Plumber":("#60A5FA","rgba(96,165,250,0.15)"),"Electrician":("#FBBF24","rgba(251,191,36,0.15)"),
    "AC Technician":("#38BDF8","rgba(56,189,248,0.15)"),"Carpenter":("#F97316","rgba(249,115,22,0.15)"),
    "Painter":("#F472B6","rgba(244,114,182,0.15)"),"Mason":("#E8722A","rgba(232,114,42,0.15)"),
    "Welder":("#FB923C","rgba(251,146,60,0.15)"),"Tile Fixer":("#A78BFA","rgba(167,139,250,0.15)"),
    "Mobile Repair":("#34D399","rgba(52,211,153,0.15)"),"Computer Repair":("#60A5FA","rgba(96,165,250,0.15)"),
    "CCTV Technician":("#94A3B8","rgba(148,163,184,0.15)"),"Internet Technician":("#38BDF8","rgba(56,189,248,0.15)"),
    "Mechanic":("#FBBF24","rgba(251,191,36,0.15)"),"Driver":("#A78BFA","rgba(167,139,250,0.15)"),
    "Mazdoor":("#94A3B8","rgba(148,163,184,0.15)"),"Helper":("#94A3B8","rgba(148,163,184,0.15)"),
    "Gardener":("#34D399","rgba(52,211,153,0.15)"),"Cook":("#F472B6","rgba(244,114,182,0.15)"),
    "Cleaner":("#60A5FA","rgba(96,165,250,0.15)"),"Laundry/Iron":("#A78BFA","rgba(167,139,250,0.15)"),
    "Other":("#94A3B8","rgba(148,163,184,0.15)"),
}
AV=[("linear-gradient(135deg,#E8722A,#1a5276)","#fff"),("linear-gradient(135deg,#1a5276,#60A5FA)","#fff"),
    ("linear-gradient(135deg,#FBBF24,#E8722A)","#fff"),("linear-gradient(135deg,#A78BFA,#1a5276)","#fff"),
    ("linear-gradient(135deg,#38BDF8,#1a5276)","#fff")]

def av_s(n): return AV[(ord(n[0]) if n else 0)%len(AV)]
def bdg(skill,lang="en"):
    c,b=SKILL_CLR.get(skill,SKILL_CLR["Other"])
    lbl=SKILLS_UR.get(skill,skill) if lang=="ur" else skill
    return f'<span style="display:inline-block;padding:2px 10px;border-radius:20px;font-size:0.7rem;font-weight:600;background:{b};color:{c};border:1px solid {c}40;">{lbl}</span>'
def strs(r):
    r=round(float(r)) if r else 0
    return "★"*r+"☆"*(5-r)

# Session
for k,v in {"lang":None,"page":"welcome","step":1,"tx":"","prof":None,"show_rating":{}}.items():
    if k not in st.session_state: st.session_state[k]=v
L=st.session_state.lang or "en"
def go(page,**kw):
    st.session_state.page=page
    for k,v in kw.items(): st.session_state[k]=v
    st.rerun()

# ── WELCOME ────────────────────────────────────────────────────────────────
if st.session_state.page=="welcome":
    st.markdown("<div style='height:2rem'></div>",unsafe_allow_html=True)
    st.markdown('<div class="kname">KaamYab</div>',unsafe_allow_html=True)
    st.markdown('<div class="k-line"></div>',unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.68rem;color:#E8722A;text-align:center;letter-spacing:2.5px;text-transform:uppercase;margin-bottom:4px;font-weight:600;'>Connecting Pakistan's Workforce</div>",unsafe_allow_html=True)
    st.markdown("<div style='font-family:Noto Nastaliq Urdu,serif;font-size:1rem;color:#fff;text-align:center;direction:rtl;line-height:2.2;margin-bottom:2rem;'>روزگار کی تلاش اب آسان</div>",unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.65rem;text-transform:uppercase;letter-spacing:2.5px;color:rgba(255,255,255,0.4);text-align:center;margin-bottom:0.8rem;'>زبان منتخب کریں &nbsp;/&nbsp; Choose Language</div>",unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        if st.button("Continue in English",key="len"): st.session_state.lang="en"; go("home")
    with c2:
        if st.button("اردو میں جاری رکھیں",key="lur"): st.session_state.lang="ur"; go("home")

# ── HOME ───────────────────────────────────────────────────────────────────
elif st.session_state.page=="home":
    workers=load_workers()
    avail=sum(1 for w in workers if w.get("available",True))
    cities=len(set(w.get("city","").split(",")[0].strip() for w in workers if w.get("city")))
    skills_ct=len(set(w.get("skill","") for w in workers))
    st.markdown(f"""
    <div style="text-align:center;padding:1.2rem 0 0.8rem;">
        <div class="kname" style="font-size:2rem;">KaamYab</div>
        <div style="font-size:0.68rem;color:#fff;text-align:center;letter-spacing:2px;text-transform:uppercase;margin-top:3px;">Connecting Pakistan's Workforce</div>
    </div>
    <div style="display:flex;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.12);border-radius:12px;margin-bottom:1rem;overflow:hidden;">
        <div style="flex:1;text-align:center;padding:8px 3px;border-right:1px solid rgba(255,255,255,0.1);"><div style="font-size:1.3rem;font-weight:700;color:#E8722A;">{len(workers)}</div><div style="font-size:0.68rem;color:#fff;margin-top:2px;">{"کارکن" if L=="ur" else "Workers"}</div></div>
        <div style="flex:1;text-align:center;padding:8px 3px;border-right:1px solid rgba(255,255,255,0.1);"><div style="font-size:1.3rem;font-weight:700;color:#E8722A;">{avail}</div><div style="font-size:0.68rem;color:#fff;margin-top:2px;">{"حاضر" if L=="ur" else "Available"}</div></div>
        <div style="flex:1;text-align:center;padding:8px 3px;border-right:1px solid rgba(255,255,255,0.1);"><div style="font-size:1.3rem;font-weight:700;color:#E8722A;">{cities}</div><div style="font-size:0.68rem;color:#fff;margin-top:2px;">{"شہر" if L=="ur" else "Cities"}</div></div>
        <div style="flex:1;text-align:center;padding:8px 3px;"><div style="font-size:1.3rem;font-weight:700;color:#E8722A;">{skills_ct}</div><div style="font-size:0.68rem;color:#fff;margin-top:2px;">{"ہنر" if L=="ur" else "Skills"}</div></div>
    </div>
    """,unsafe_allow_html=True)

    if L=="ur":
        st.markdown("<div style='font-family:Noto Nastaliq Urdu,serif;font-size:1rem;font-weight:700;color:#E8722A;direction:rtl;text-align:right;margin-bottom:6px;'>آپ کیا کرنا چاہتے ہیں؟</div>",unsafe_allow_html=True)
        st.markdown("<div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px;'><div style='background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.14);border-radius:14px;padding:14px 10px;text-align:center;'><div style='font-family:Noto Nastaliq Urdu,serif;font-size:0.88rem;font-weight:700;color:#fff;direction:rtl;line-height:1.7;'>میں کام کی تلاش میں ہوں</div><div style='font-family:Noto Nastaliq Urdu,serif;font-size:0.72rem;color:rgba(255,255,255,0.6);direction:rtl;'>پروفائل بنائیں، کام پائیں</div></div><div style='background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.14);border-radius:14px;padding:14px 10px;text-align:center;'><div style='font-family:Noto Nastaliq Urdu,serif;font-size:0.88rem;font-weight:700;color:#fff;direction:rtl;line-height:1.7;'>میں کاریگر کی تلاش میں ہوں</div><div style='font-family:Noto Nastaliq Urdu,serif;font-size:0.72rem;color:rgba(255,255,255,0.6);direction:rtl;'>قریبی ہنرمند تلاش کریں</div></div></div>",unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-size:1rem;font-weight:700;color:#E8722A;margin-bottom:6px;'>What would you like to do?</div>",unsafe_allow_html=True)
        st.markdown("<div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px;'><div style='background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.14);border-radius:14px;padding:14px 10px;text-align:center;'><div style='font-size:0.88rem;font-weight:700;color:#fff;'>I'm looking for work</div><div style='font-size:0.72rem;color:rgba(255,255,255,0.6);margin-top:2px;'>Create profile, get hired</div></div><div style='background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.14);border-radius:14px;padding:14px 10px;text-align:center;'><div style='font-size:0.88rem;font-weight:700;color:#fff;'>I need a worker</div><div style='font-size:0.72rem;color:rgba(255,255,255,0.6);margin-top:2px;'>Find skilled workers nearby</div></div></div>",unsafe_allow_html=True)

    c1,c2=st.columns(2)
    with c1:
        if st.button("اپنا پروفائل بنائیں" if L=="ur" else "Register as Worker",key="gw"): go("worker",step=1)
    with c2:
        if st.button("کاریگر تلاش کریں" if L=="ur" else "Find a Worker",key="ge"): go("employer")
    st.markdown("<hr class='d'>",unsafe_allow_html=True)
    st.markdown('<style>#lt_wrap .stButton>button{background:#6D1A36!important;color:#fff!important;display:block;margin:0 auto;}</style><div id="lt_wrap">',unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        if st.button("Switch to English" if L=="ur" else "اردو میں دیکھیں",key="lt",use_container_width=True):
            st.session_state.lang="en" if L=="ur" else "ur"; st.rerun()
    st.markdown('</div>',unsafe_allow_html=True)

# ── WORKER ─────────────────────────────────────────────────────────────────
elif st.session_state.page=="worker":
    with st.container():
        st.markdown('<div class="back-btn">',unsafe_allow_html=True)
        if st.button("← "+(("واپس") if L=="ur" else "Back"),key="bkw"): go("home")
        st.markdown('</div>',unsafe_allow_html=True)

    step=st.session_state.step
    dots="".join(['<div class="dot on"></div>' if i==step else '<div class="dot done"></div>' if i<step else '<div class="dot"></div>' for i in range(1,4)])
    st.markdown(f'<div class="dots">{dots}</div>',unsafe_allow_html=True)

    if step==1:
        st.markdown("<div style='font-family:Noto Nastaliq Urdu,serif;font-size:1.2rem;font-weight:700;color:#fff;direction:rtl;text-align:right;margin-bottom:12px;'>اپنی معلومات دیں</div>",unsafe_allow_html=True)
        speak="اپنا پورا نام بتائیں۔ اپنا ہنر بتائیں۔ شہر اور علاقہ بتائیں۔ تجربہ اور روزانہ فیس بتائیں۔ فون نمبر بتائیں۔"
        btn_lbl="ہدایات سنیں" if L=="ur" else "Listen to Instructions"
        st.markdown(f"<button onclick=\"(function(){{window.speechSynthesis.cancel();var u=new SpeechSynthesisUtterance('{speak}');u.lang='ur-PK';u.rate=0.82;window.speechSynthesis.speak(u);}})()\" style=\"width:100%;padding:10px 14px;background:#000;border-radius:11px;color:#E8722A;font-family:Noto Nastaliq Urdu,serif;font-size:1rem;cursor:pointer;margin-bottom:0.9rem;border:none;font-weight:700;\">{btn_lbl}</button>",unsafe_allow_html=True)

        instrs=[("اپنا پورا نام بتائیں","مثال: میرا نام محمد زفر ہے"),("اپنا ہنر بتائیں","مثال: میں پلمبر ہوں"),
                ("کتنے سال کا تجربہ ہے","مثال: دس سال"),("شہر اور محلہ بتائیں","مثال: کراچی، ناظم آباد"),
                ("روزانہ کتنا معاوضہ","مثال: ڈھائی ہزار روپے"),("فون نمبر بتائیں","مثال: صفر تین صفر صفر"),
                ("کیا ابھی فارغ ہیں","مثال: جی ہاں ابھی حاضر ہوں")]
        rows="".join(f"<div style='display:flex;align-items:flex-start;gap:9px;direction:rtl;padding:9px 0;border-bottom:1px solid rgba(255,255,255,0.08);'><div style='flex:1;'><div style='font-family:Noto Nastaliq Urdu,serif;font-size:0.9rem;line-height:2;color:#fff;text-align:right;'>{t}</div><div style='font-family:Noto Nastaliq Urdu,serif;font-size:0.75rem;color:rgba(255,255,255,0.65);text-align:right;'>{e}</div></div><div style='min-width:24px;height:24px;background:#000;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.72rem;font-weight:700;color:#E8722A;flex-shrink:0;'>{i+1}</div></div>" for i,(t,e) in enumerate(instrs))
        st.markdown(f"<div style='background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.12);border-radius:14px;padding:10px 12px;margin-bottom:0.8rem;'>{rows}</div>",unsafe_allow_html=True)
        st.markdown("<div style='padding:8px 0 0.8rem;'><div style='font-size:0.65rem;color:#E8722A;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:5px;'>مثال</div><div style='font-family:Noto Nastaliq Urdu,serif;font-size:0.85rem;direction:rtl;text-align:right;line-height:2.2;color:rgba(255,255,255,0.85);'>&quot;میرا نام زفر ہے۔ پلمبر ہوں۔ کراچی ناظم آباد۔ پندرہ سال۔ ڈھائی ہزار۔ صفر تین صفر صفر۔ ابھی حاضر ہوں۔&quot;</div></div>",unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="burg-btn">',unsafe_allow_html=True)
            if st.button("آگے بڑھیں" if L=="ur" else "Continue",use_container_width=True,key="s1n"): go("worker",step=2)
            st.markdown('</div>',unsafe_allow_html=True)

    elif step==2:
        st.markdown(f"<div style='font-size:1.2rem;font-weight:700;color:#fff;margin-bottom:10px;'>{'ابھی ریکارڈ کریں' if L=='ur' else 'Record Yourself'}</div>",unsafe_allow_html=True)
        st.markdown(f"<div style='background:rgba(255,255,255,0.06);border:1.5px dashed rgba(255,255,255,0.15);border-radius:16px;padding:1.2rem 1rem;text-align:center;margin-bottom:0.8rem;'><div style='width:50px;height:50px;border-radius:50%;background:rgba(232,114,42,0.15);border:2px solid rgba(232,114,42,0.4);display:flex;align-items:center;justify-content:center;margin:0 auto 8px;'><div style='width:14px;height:14px;background:#E8722A;border-radius:50%;'></div></div><div style='font-family:Noto Nastaliq Urdu,serif;font-size:0.95rem;color:#fff;direction:rtl;line-height:1.9;'>{'اپنے کام/ہنر کے متعلق معلومات دیں' if L=='ur' else 'Share information about your work and skills'}</div></div>",unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.82rem;color:rgba(255,255,255,0.8);margin-bottom:6px;'>{'ریکارڈ کرنے کے لیے نیچے دبائیں:' if L=='ur' else 'Press mic to start recording:'}</div>",unsafe_allow_html=True)

        audio_bytes=audio_recorder(text="",recording_color="#E8722A",neutral_color="#ffffff",icon_name="microphone",icon_size="2x",pause_threshold=3.0)
        if audio_bytes:
            st.audio(audio_bytes,format="audio/wav")
            if st.button("آواز سمجھیں اور پروفائل بنائیں" if L=="ur" else "Transcribe & Build Profile",use_container_width=True,key="tr_rec"):
                with st.spinner("آواز سمجھی جا رہی ہے..." if L=="ur" else "Transcribing..."):
                    tx=transcribe_audio_bytes(audio_bytes)
                if tx:
                    st.session_state.tx=tx; st.session_state.step=3; st.session_state.prof=None; st.rerun()
                else:
                    st.error("آواز نہیں سمجھی — دوبارہ کوشش کریں" if L=="ur" else "Could not transcribe. Try again.")

        st.markdown("<hr class='d'>",unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.88rem;color:#fff;font-weight:600;margin-bottom:5px;'>{'آڈیو فائل اپلوڈ کریں' if L=='ur' else 'Upload Audio File'}</div>",unsafe_allow_html=True)
        af=st.file_uploader("audio",type=["mp3","wav","m4a","ogg","webm"],label_visibility="collapsed")
        if af:
            st.audio(af)
            if st.button("آواز سمجھیں" if L=="ur" else "Transcribe Upload",use_container_width=True,key="tr_up"):
                with st.spinner("..."):
                    tx=transcribe_audio(af)
                if tx:
                    st.session_state.tx=tx; st.session_state.step=3; st.session_state.prof=None; st.rerun()
                else:
                    st.error("Could not transcribe.")

        st.markdown("<hr class='d'>",unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.88rem;color:#fff;font-weight:600;margin-bottom:5px;'>{'ڈیمو کے لیے — متن لکھیں' if L=='ur' else 'For demo — type text directly'}</div>",unsafe_allow_html=True)
        demo=st.text_area("dt",label_visibility="collapsed",height=80,placeholder="میرا نام زفر ہے۔ میں پلمبر ہوں..." if L=="ur" else "My name is Zafar. I am a plumber...")
        if st.button("اس سے پروفائل بنائیں" if L=="ur" else "Build Profile from Text",use_container_width=True,key="db"):
            if demo.strip():
                st.session_state.tx=demo.strip(); st.session_state.step=3; st.session_state.prof=None; st.rerun()

        with st.container():
            st.markdown('<div class="back-btn">',unsafe_allow_html=True)
            if st.button("← "+("واپس" if L=="ur" else "Back"),key="bk2"): go("worker",step=1)
            st.markdown('</div>',unsafe_allow_html=True)

    elif step==3:
        st.markdown(f"<div style='font-size:1.2rem;font-weight:700;color:#fff;margin-bottom:10px;'>{'آپ کا پروفائل' if L=='ur' else 'Your Profile'}</div>",unsafe_allow_html=True)
        if st.session_state.prof is None:
            with st.spinner("AI پروفائل بنا رہا ہے..." if L=="ur" else "Building profile with AI..."):
                p=build_profile(st.session_state.tx)
            if p: st.session_state.prof=p
            else:
                st.error("پروفائل نہیں بنا۔" if L=="ur" else "Could not build profile.")
                with st.container():
                    st.markdown('<div class="back-btn">',unsafe_allow_html=True)
                    if st.button("← Back",key="bk3e"): go("worker",step=2)
                    st.markdown('</div>',unsafe_allow_html=True)
                st.stop()

        p=st.session_state.prof
        skill=p.get("skill","Other"); sc,sb=SKILL_CLR.get(skill,SKILL_CLR["Other"])
        nm=p.get("name","?"); init=nm[0].upper() if nm else "?"
        abg,ac=av_s(nm); avail=p.get("available",True); bio=p.get("bio","")
        bio_html=f"<div style='font-size:0.75rem;color:rgba(255,255,255,0.85);margin-top:7px;padding-top:7px;border-top:1px solid rgba(255,255,255,0.25);line-height:1.55;'>{bio}</div>" if bio else ""

        st.markdown(f"<div style='background:#E8722A;border-radius:16px;padding:1.1rem;margin-bottom:0.8rem;'><div style='display:flex;align-items:center;gap:10px;margin-bottom:8px;'><div style='width:40px;height:40px;border-radius:50%;background:rgba(255,255,255,0.25);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:1.1rem;color:#fff;flex-shrink:0;'>{init}</div><div style='flex:1;'><div style='font-size:1.05rem;font-weight:700;color:#fff;'>{nm}</div><div style='margin-top:3px;'>{bdg(skill,L)}</div></div><div style='padding:3px 10px;background:#000;border-radius:20px;font-size:0.7rem;color:#fff;font-weight:600;'>{'حاضر' if avail else 'مصروف'}</div></div><div style='font-size:0.82rem;color:rgba(255,255,255,0.9);margin:3px 0;'>{p.get('city','---')}</div><div style='font-size:0.82rem;color:rgba(255,255,255,0.9);margin:3px 0;'>{p.get('experience','---')}</div><div style='font-size:0.82rem;color:rgba(255,255,255,0.9);margin:3px 0;'>{p.get('phone','---')}</div><div style='display:flex;justify-content:space-between;align-items:baseline;margin-top:8px;padding-top:8px;border-top:1px solid rgba(255,255,255,0.25);'><span style='font-size:0.72rem;color:rgba(255,255,255,0.8);'>{'روزانہ معاوضہ' if L=='ur' else 'Daily Rate'}</span><span style='font-size:1.05rem;font-weight:700;color:#fff;'>PKR {p.get('daily_rate','---')}</span></div>{bio_html}</div>",unsafe_allow_html=True)

        st.markdown(f"<div style='font-size:0.9rem;color:#fff;font-weight:600;margin-bottom:5px;'>{'اپنی تصویر اپلوڈ کریں' if L=='ur' else 'Upload Your Photo'}</div>",unsafe_allow_html=True)
        photo=st.file_uploader("photo",type=["jpg","jpeg","png"],label_visibility="collapsed")
        if photo: st.image(photo,width=80)

        st.markdown(f"<div style='font-size:0.88rem;color:#fff;font-weight:600;margin:8px 0 5px;'>{'کچھ غلط ہے؟ نیچے ٹھیک کریں:' if L=='ur' else 'Something wrong? Edit below:'}</div>",unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            p["name"]=st.text_input("نام / Name",value=p.get("name",""),key="en")
            p["city"]=st.text_input("شہر / City",value=p.get("city",""),key="ec")
            p["phone"]=st.text_input("فون / Phone",value=p.get("phone",""),key="ep")
        with c2:
            slbls=[SKILLS_UR[s] if L=="ur" else s for s in SKILLS_EN]
            cur=SKILLS_EN.index(p.get("skill","Other")) if p.get("skill") in SKILLS_EN else 0
            sel=st.selectbox("ہنر / Skill",slbls,index=cur,key="esk")
            p["skill"]=SKILLS_EN[slbls.index(sel)]
            p["daily_rate"]=st.text_input("روزانہ (Rs.)",value=str(p.get("daily_rate","")),key="er")
            p["available"]=st.checkbox("حاضر ہوں / Available",value=p.get("available",True),key="ea")

        if st.button("پروفائل محفوظ کر کے آگے بڑھیں" if L=="ur" else "Save Profile & Continue",use_container_width=True,key="save"):
            save_worker(p); go("success")
        with st.container():
            st.markdown('<div class="back-btn">',unsafe_allow_html=True)
            if st.button("← "+("واپس" if L=="ur" else "Back"),key="bk3"):
                st.session_state.prof=None; go("worker",step=2)
            st.markdown('</div>',unsafe_allow_html=True)

# ── SUCCESS ────────────────────────────────────────────────────────────────
elif st.session_state.page=="success":
    st.markdown("<div style='text-align:center;padding:3rem 0 2rem;'><div style='width:52px;height:52px;background:rgba(232,114,42,0.15);border:2px solid rgba(232,114,42,0.4);border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 14px;'><svg width='24' height='24' viewBox='0 0 24 24' fill='none'><path d='M5 13l4 4L19 7' stroke='#E8722A' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'/></svg></div><div style='font-family:Noto Nastaliq Urdu,serif;font-size:1.3rem;font-weight:700;color:#E8722A;direction:rtl;'>پروفائل تیار ہو گیا!</div><div style='font-size:0.82rem;color:#fff;margin-top:5px;'>Profile saved successfully</div><div style='font-family:Noto Nastaliq Urdu,serif;font-size:0.88rem;color:#fff;direction:rtl;margin-top:5px;line-height:2;'>اب لوگ آپ سے رابطہ کر سکتے ہیں</div></div>",unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="burg-btn">',unsafe_allow_html=True)
        if st.button("واپس جائیں" if L=="ur" else "Back to Home",use_container_width=True,key="hb"): go("home")
        st.markdown('</div>',unsafe_allow_html=True)

# ── EMPLOYER ───────────────────────────────────────────────────────────────
elif st.session_state.page=="employer":
    with st.container():
        st.markdown('<div class="back-btn">',unsafe_allow_html=True)
        if st.button("← "+("واپس" if L=="ur" else "Back"),key="bkemp"): go("home")
        st.markdown('</div>',unsafe_allow_html=True)

    st.markdown(f"<div style='font-family:Noto Nastaliq Urdu,serif;font-size:1.2rem;font-weight:700;color:#fff;direction:rtl;text-align:right;margin-bottom:2px;'>{'کاریگر تلاش کریں' if L=='ur' else 'Find a Worker'}</div>",unsafe_allow_html=True)
    st.markdown(f"<div style='font-family:Noto Nastaliq Urdu,serif;font-size:0.78rem;color:rgba(255,255,255,0.7);direction:rtl;text-align:right;margin-bottom:0.8rem;'>{'ہنر اور شہر منتخب کریں' if L=='ur' else 'Select skill and city'}</div>",unsafe_allow_html=True)

    chips="".join(f"<span style='display:inline-block;padding:5px 11px;border-radius:20px;font-size:0.72rem;font-weight:500;background:rgba(255,255,255,0.09);border:1px solid rgba(255,255,255,0.15);color:#fff;margin:2px;font-family:Noto Nastaliq Urdu,serif;'>{('سب' if s=='All' else SKILLS_UR.get(s,s)) if L=='ur' else s}</span>" for s in ["All"]+SKILLS_EN)
    st.markdown(f"<div style='display:flex;flex-wrap:wrap;margin-bottom:0.8rem;'>{chips}</div>",unsafe_allow_html=True)

    skill_labels=["All / سب"]+([SKILLS_UR[s] for s in SKILLS_EN] if L=="ur" else SKILLS_EN)
    c1,c2=st.columns(2)
    with c1:
        city_labels=["All / سب"]+([CITIES_UR.get(c,c) for c in CITIES_EN] if L=="ur" else CITIES_EN)
        sel_city=st.selectbox("شہر",city_labels,key="ec2",label_visibility="collapsed")
    with c2:
        sel_sk=st.selectbox("ہنر",skill_labels,key="esk2",label_visibility="collapsed")
    area_q=st.text_input("علاقہ",placeholder="ناظم آباد..." if L=="ur" else "e.g. Gulberg",key="ea2",label_visibility="collapsed")

    workers=load_workers(); filtered=workers
    if sel_sk not in ["All / سب","All"]:
        ur_s=[SKILLS_UR[s] for s in SKILLS_EN]
        en_s=SKILLS_EN[ur_s.index(sel_sk)] if L=="ur" and sel_sk in ur_s else sel_sk
        filtered=[w for w in filtered if w.get("skill","")==en_s]
    if sel_city not in ["All / سب","All"]:
        en_c=next((c for c in CITIES_EN if CITIES_UR.get(c,c)==sel_city or c==sel_city),sel_city)
        filtered=[w for w in filtered if en_c.lower() in w.get("city","").lower()]
    if area_q.strip():
        filtered=[w for w in filtered if area_q.lower() in w.get("city","").lower()]

    st.markdown(f"<div style='display:flex;align-items:center;gap:10px;margin:0.5rem 0 0.8rem;'><span style='font-size:1.2rem;font-weight:700;color:#6D1A36;'>{len(filtered)}</span><span style='font-size:0.95rem;color:#000;font-weight:600;font-family:Noto Nastaliq Urdu,serif;'>{'کارکن ملے' if L=='ur' else 'workers found'}</span></div>",unsafe_allow_html=True)

    if not filtered:
        st.markdown(f"<div style='text-align:center;padding:2rem;color:rgba(255,255,255,0.5);'>{'کوئی کارکن نہیں ملا' if L=='ur' else 'No workers found'}</div>",unsafe_allow_html=True)
    else:
        for w in filtered:
            skill=w.get("skill","Other"); sc,sb=SKILL_CLR.get(skill,SKILL_CLR["Other"])
            nm=w.get("name","?"); init=nm[0].upper() if nm else "?"
            abg,ac=av_s(nm); avail=w.get("available",True)
            reviews=w.get("reviews",[]); avg_r=round(sum(r.get("stars",0) for r in reviews)/len(reviews),1) if reviews else w.get("rating",0)
            phone=w.get("phone","").replace(" ","").replace("-","")
            wa_num=f"92{phone[1:]}" if phone.startswith("0") else f"92{phone}"
            wa_msg=quote("السلام علیکم، میں نے KaamYab پر آپ کا پروفائل دیکھا۔ کیا آپ کام کے لیے حاضر ہیں؟")
            wa_url=f"https://wa.me/{wa_num}?text={wa_msg}"
            call_url=f"tel:{w.get('phone','')}"
            wid=w.get("id",""); bio=w.get("bio","")
            show_r=st.session_state.show_rating.get(wid,False)
            bio_html=f"<div style='font-size:0.72rem;color:rgba(255,255,255,0.55);margin-top:5px;padding-top:5px;border-top:1px solid rgba(255,255,255,0.08);line-height:1.5;'>{bio}</div>" if bio else ""

            st.markdown(f"<div style='background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.13);border-radius:14px;padding:1rem;margin-bottom:0.7rem;'><div style='display:flex;align-items:center;gap:9px;margin-bottom:7px;'><div style='width:38px;height:38px;border-radius:50%;background:{abg};color:{ac};display:flex;align-items:center;justify-content:center;font-weight:700;font-size:1rem;flex-shrink:0;'>{init}</div><div style='flex:1;'><div style='font-size:1rem;font-weight:700;color:#fff;'>{nm}</div><div style='font-size:0.75rem;color:rgba(255,255,255,0.65);margin-top:1px;'>{bdg(skill,L)} &nbsp; {w.get('city','---')}</div></div><div style='text-align:right;'><div style='font-size:1rem;font-weight:700;color:#E8722A;'>PKR {w.get('daily_rate','---')}</div><div style='font-size:0.62rem;color:rgba(255,255,255,0.45);'>{'روز' if L=='ur' else 'per day'}</div></div></div><div style='display:flex;align-items:center;gap:6px;margin-bottom:5px;'><span style='padding:2px 9px;background:rgba(0,0,0,0.25);color:#fff;border-radius:20px;font-size:0.7rem;border:1px solid rgba(255,255,255,0.15);'>{'حاضر' if avail else 'مصروف'}</span><span style='color:#FBBF24;font-size:0.82rem;margin-left:auto;'>{strs(avg_r)}</span><span style='font-size:0.68rem;color:rgba(255,255,255,0.45);'>({len(reviews)})</span></div><div style='font-size:0.72rem;color:rgba(255,255,255,0.65);margin:2px 0;'>{w.get('experience','---')} experience</div>{bio_html}<div style='display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:8px;'><a href='{wa_url}' target='_blank' style='display:block;background:#25D366;border-radius:9px;padding:8px;font-size:0.8rem;font-weight:600;color:#fff;text-align:center;text-decoration:none;'>{'واٹس ایپ' if L=='ur' else 'WhatsApp'}</a><a href='{call_url}' style='display:block;background:#6D1A36;border-radius:9px;padding:8px;font-size:0.8rem;font-weight:600;color:#fff;text-align:center;text-decoration:none;'>{'کال کریں' if L=='ur' else 'Call'}</a></div></div>",unsafe_allow_html=True)

            rlbl=("ریٹنگ بند کریں" if show_r else "ریٹنگ دیں") if L=="ur" else ("Close Rating" if show_r else "Leave a Rating")
            if st.button(rlbl,key=f"tog_{wid}"):
                st.session_state.show_rating[wid]=not show_r; st.rerun()
            if show_r:
                sv=st.select_slider("Rating",options=[1,2,3,4,5],value=3,key=f"st_{wid}")
                cm=st.text_input("تبصرہ" if L=="ur" else "Comment",key=f"cm_{wid}")
                if st.button("جمع کریں" if L=="ur" else "Submit",key=f"rt_{wid}"):
                    add_rating(wid,sv,cm); st.session_state.show_rating[wid]=False; st.rerun()