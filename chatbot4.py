import streamlit as st
from dotenv import load_dotenv
import os
from openai import OpenAI
import csv
from datetime import datetime
import pandas as pd
import random

# -------------------------
# Load .env
# -------------------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

CSV_FILE = "chat_history.csv"

# -------------------------
# Page Config
# -------------------------
st.set_page_config(page_title="KU KPS Medical Companionship", page_icon="🏥")

st.title("🏥 KU KPS Medical Companionship")
st.subheader("โดย สถานพยาบาล มหาวิทยาลัยเกษตรศาสตร์ วิทยาเขตกำแพงแสน นครปฐม")

# -------------------------
# SAFE Session Initialization
# -------------------------
if "messages" not in st.session_state or not isinstance(st.session_state.messages, list):
    st.session_state.messages = []

if "contact_shown" not in st.session_state:
    st.session_state.contact_shown = False

if "history_loaded" not in st.session_state:
    st.session_state.history_loaded = False

# -------------------------
# Sidebar: User Info
# -------------------------
st.sidebar.header("👤 ผู้ใช้งาน")

nickname_input = st.sidebar.text_input("กรอกชื่อเล่น (เว้นว่างหากไม่ต้องการระบุ)")

if nickname_input.strip() == "":
    nickname = "99"
    st.sidebar.info("โหมด Anonymous")
else:
    nickname = nickname_input.strip()

# -------------------------
# Gender Selection
# -------------------------
st.sidebar.header("👩‍⚕️ เพศแพทย์")
doctor_gender = st.sidebar.radio("เลือกแพทย์", ["👨‍⚕️ แพทย์ชาย", "👩‍⚕️ แพทย์หญิง"])

if doctor_gender == "👨‍⚕️ แพทย์ชาย":
    pronoun = "ผม"
    ending = "ครับ"
    doctor_name = "นพ.นนทกร"
    avatar = "👨‍⚕️"
else:
    pronoun = "ดิฉัน"
    ending = "ค่ะ"
    doctor_name = "พญ.กานต์พิชชา"
    avatar = "👩‍⚕️"

# -------------------------
# Faculty Selection
# -------------------------
st.sidebar.header("🎓 คณะ")
faculty = st.sidebar.selectbox(
    "เลือกคณะ",
    ["Engineering", "Humanities", "Sports Science", "Other"]
)

AUTO_PERSONA = {
    "Engineering": "🔬 หมอสายวิทย์",
    "Humanities": "🧠 โค้ชใจ",
    "Sports Science": "🌿 เพื่อนสุขภาพดี"
}

suggested_persona = AUTO_PERSONA.get(faculty, "🔬 หมอสายวิทย์")

# -------------------------
# Persona Selection
# -------------------------
st.sidebar.header("🧠 เลือกสไตล์แพทย์")

persona_options = ["🔬 หมอสายวิทย์", "🧠 โค้ชใจ", "🌿 เพื่อนสุขภาพดี"]

selected_persona = st.sidebar.radio(
    "เลือกแนวแพทย์ (สามารถเปลี่ยนเองได้)",
    persona_options,
    index=persona_options.index(suggested_persona)
)

# -------------------------
# Persona Prompts
# -------------------------
PERSONAS = {
    "🔬 หมอสายวิทย์": f"""
You are a medical doctor who explains using evidence-based reasoning.
Use logical medical explanations and mechanisms.
Use pronoun "{pronoun}" and end sentences politely with "{ending}" when speaking Thai.
""",

    "🧠 โค้ชใจ": f"""
You are a supportive medical doctor focusing on emotional reflection.
Use empathetic language and open-ended questions.
Use pronoun "{pronoun}" and end sentences politely with "{ending}" when speaking Thai.
""",

    "🌿 เพื่อนสุขภาพดี": f"""
You are a lifestyle-focused medical doctor.
Give advice about sleep, nutrition, exercise, and stress balance.
Use pronoun "{pronoun}" and end sentences politely with "{ending}" when speaking Thai.
"""
}

# -------------------------
# Daily Tip
# -------------------------
today = datetime.now().strftime("%Y-%m-%d")

if "daily_tip_date" not in st.session_state or st.session_state.daily_tip_date != today:
    tips = [
        "💧 ดื่มน้ำอย่างน้อย 6-8 แก้วต่อวัน",
        "😴 นอนให้ได้อย่างน้อย 7 ชั่วโมง",
        "🚶‍♂️ เดินเร็ววันละ 30 นาที",
        "📵 ลดการใช้หน้าจอก่อนนอน 1 ชั่วโมง",
        "🥦 เพิ่มผักในมื้ออาหารวันนี้"
    ]
    st.session_state.daily_tip = random.choice(tips)
    st.session_state.daily_tip_date = today

st.info(f"📌 Daily Health Tip: {st.session_state.daily_tip}")

# -------------------------
# Load History (Privacy Safe)
# -------------------------
if not st.session_state.history_loaded and os.path.exists(CSV_FILE):

    if nickname != "99":  # Do NOT load history for anonymous
        df = pd.read_csv(CSV_FILE)

        if "nickname" in df.columns:
            user_history = df[df["nickname"] == nickname]
            recent_history = user_history.tail(30)

            for _, row in recent_history.iterrows():
                st.session_state.messages.append({
                    "role": row["role"],
                    "content": row["message"]
                })

    st.session_state.history_loaded = True

# -------------------------
# Language Detection
# -------------------------
def is_thai(text):
    for char in text:
        if "\u0E00" <= char <= "\u0E7F":
            return True
    return False

# -------------------------
# Display Doctor Header
# -------------------------
st.markdown(f"### {avatar} {doctor_name} ({selected_persona})")

# -------------------------
# Display Chat
# -------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------
# Chat Input
# -------------------------
user_input = st.chat_input("พิมพ์อาการหรือสิ่งที่ต้องการปรึกษา...")

if user_input:

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # Language Logic
    if is_thai(user_input):
        language_instruction = f"""
ตอบเป็นภาษาไทยสุภาพ
ใช้สรรพนาม "{pronoun}" ลงท้ายด้วย "{ending}"
หากพบอาการรุนแรง ให้แนะนำมาพบสถานพยาบาลมหาวิทยาลัยหรือโทร 1669 ทันที
"""
    else:
        language_instruction = """
Respond in clear professional English.
Maintain the same caring medical tone.
If severe symptoms appear, advise visiting the university clinic or emergency services immediately.
"""

    system_prompt = f"""
{PERSONAS[selected_persona]}

{language_instruction}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                *st.session_state.messages[-20:]
            ],
            temperature=0.4
        )

        assistant_reply = response.choices[0].message.content

    except Exception as e:
        assistant_reply = f"Error occurred: {e}"

    # Contact shown only once
    if not st.session_state.contact_shown:
        assistant_reply += """

---

👩‍⚕️ หากต้องการปรึกษาปัญหาสุขภาพที่ซับซ้อน  
โปรดติดต่อ ผศ.นพ.กำธร ตันติวิทยาทันต์  
📧 dr.kamthorn.tan@gmail.com
"""
        st.session_state.contact_shown = True

    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

    with st.chat_message("assistant"):
        st.markdown(assistant_reply)

    # -------------------------
    # Save to CSV
    # -------------------------
    file_exists = os.path.exists(CSV_FILE)

    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["nickname", "timestamp", "role", "message", "persona", "faculty", "gender"])

        writer.writerow([nickname, timestamp, "user", user_input, selected_persona, faculty, doctor_gender])
        writer.writerow([nickname, timestamp, "assistant", assistant_reply, selected_persona, faculty, doctor_gender])