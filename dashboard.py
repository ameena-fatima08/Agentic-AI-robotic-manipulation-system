"""
AI Robotic Grasping — Robotics-Themed Dashboard
Save as: app.py
Run: streamlit run app.py
"""

import streamlit as st
from streamlit_lottie import st_lottie
from PIL import Image
import numpy as np
import cv2
import time
import random
import pandas as pd
import requests
import io
from datetime import datetime
import plotly.graph_objects as go

import json

# Agent Endpoints (make sure they match your Flask APIs)
SPEECH_API = "http://localhost:8002/speech/latest"
VISION_API = "http://localhost:8001/vision/latest"

# Helper functions
def fetch_speech_data():
    try:
        res = requests.get(SPEECH_API, timeout=5)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

def fetch_vision_data():
    try:
        res = requests.get(VISION_API, timeout=5)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        return None

def add_log(agent: str, action: str, status: str = "info"):
    entry = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "agent": agent,
        "action": action,
        "status": status
    }
    st.session_state.logs.insert(0, entry)
    st.session_state.logs = st.session_state.logs[:200]

def draw_detections(image: Image.Image, detections: list):
    img = np.array(image.convert("RGB"))[:, :, ::-1].copy()
    colors = {"bottle": (0, 255, 127), "cup": (0, 191, 255), "box": (138, 43, 226), "can": (255, 215, 0)}
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        conf = det["confidence"]
        label = det["label"]
        color = colors.get(label, (0, 255, 255))
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
        cv2.putText(img, f"{label} {conf:.0%}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    return Image.fromarray(img[:, :, ::-1])

def simulate_detections(w, h):
    labels = ["bottle", "cup", "box", "can"]
    n = random.randint(1, 3)
    dets = []
    for _ in range(n):
        lw = random.randint(int(w*0.15), int(w*0.35))
        lh = random.randint(int(h*0.15), int(h*0.35))
        x1 = random.randint(20, max(20, w - lw - 20))
        y1 = random.randint(20, max(20, h - lh - 20))
        dets.append({"bbox": [x1, y1, x1 + lw, y1 + lh], "confidence": random.uniform(0.65, 0.98), "label": random.choice(labels)})
    return dets

# Session state
if "logs" not in st.session_state:
    st.session_state.logs = []
if "last_command" not in st.session_state:
    st.session_state.last_command = {}
if "metrics" not in st.session_state:
    st.session_state.metrics = {"total_grasps": 0, "successes": 0, "last_response_time": 0.0, "history": []}
if "detections" not in st.session_state:
    st.session_state.detections = []

# Page config
st.set_page_config(page_title="AI Robotic Grasping", layout="wide", page_icon="🤖")

# Styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto+Mono&display=swap');
.stApp {
    background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%);
}
.cyber-header {
    background: linear-gradient(135deg, rgba(0,255,255,0.1), rgba(255,0,255,0.1));
    border: 2px solid #00ffff;
    border-radius: 15px;
    padding: 25px;
    box-shadow: 0 0 20px rgba(0,255,255,0.3);
    animation: glow 3s ease-in-out infinite;
}
@keyframes glow {
    0%, 100% { box-shadow: 0 0 20px rgba(0,255,255,0.3); }
    50% { box-shadow: 0 0 30px rgba(0,255,255,0.6); }
}
.tech-card {
    background: linear-gradient(135deg, rgba(26,31,58,0.9), rgba(15,20,25,0.9));
    border: 1px solid #00ffff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 20px rgba(0,255,255,0.2);
    transition: all 0.3s;
}
.tech-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 30px rgba(0,255,255,0.4);
}
h1, h2, h3 {
    font-family: 'Orbitron', sans-serif;
    color: #00ffff;
    text-shadow: 0 0 10px rgba(0,255,255,0.5);
}
.stButton>button {
    background: linear-gradient(135deg, rgba(0,255,255,0.2), rgba(255,0,255,0.2));
    border: 2px solid #00ffff;
    color: #00ffff;
    font-family: 'Orbitron', sans-serif;
    font-weight: 700;
    border-radius: 8px;
    transition: all 0.3s;
}
.stButton>button:hover {
    box-shadow: 0 0 25px rgba(0,255,255,0.6);
    transform: translateY(-2px);
}
[data-testid="stMetricValue"] {
    font-family: 'Orbitron', sans-serif;
    color: #00ffff;
    text-shadow: 0 0 15px rgba(0,255,255,0.8);
}
.led {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
.led-on { background: #00ff00; box-shadow: 0 0 10px #00ff00; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="cyber-header">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    st.markdown('<h1 style="font-size: 2.5em;">🤖 ROBOTIC GRASPING AI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #00ff88; font-family: Roboto Mono;">[ VISION • SPEECH • MOTOR • LEARNING ]</p>', unsafe_allow_html=True)
with col2:
    # Animated robot visualization
    st.markdown('''
    <div style="text-align: center; padding: 20px;">
        <div style="position: relative; display: inline-block;">
            <div style="font-size: 90px; animation: float 3s ease-in-out infinite;">
                🤖
            </div>
            <div style="position: absolute; top: -10px; right: -10px; width: 20px; height: 20px; background: #00ff00; border-radius: 50%; animation: blink 1s infinite;"></div>
        </div>
    </div>
    <style>
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    @keyframes blink {
        0%, 50%, 100% { opacity: 1; }
        25%, 75% { opacity: 0; }
    }
    </style>
    ''', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div style="text-align: right; padding-top: 15px;"><div style="color: #00ff00; font-size: 1.4em; font-family: Orbitron;">ACTIVE</div><div style="color: #00ffff; font-size: 0.85em;">{len(st.session_state.logs)} EVENTS</div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ SYSTEM CONTROL")
    st.markdown('<span class="led led-on"></span> 🎤 SPEECH', unsafe_allow_html=True)
    speech_enabled = st.toggle("Enable", value=True, key="speech")
    st.markdown('<span class="led led-on"></span> 👁️ VISION', unsafe_allow_html=True)
    vision_enabled = st.toggle("Enable", value=True, key="vision")
    st.markdown('<span class="led led-on"></span> 🤖 MOTOR', unsafe_allow_html=True)
    motor_enabled = st.toggle("Enable", value=True, key="motor")
    st.markdown("---")
    st.markdown("### 🚀 QUICK ACTIONS")
    if st.button("▶️ FULL PIPELINE", use_container_width=True):
        with st.spinner("EXECUTING..."):
            intent = {"action": "pick", "object": random.choice(["bottle", "cup"]), "confidence": 0.92}
            add_log("speech", f"CMD: {intent['action']} {intent['object']}", "success")
            time.sleep(0.3)
            add_log("vision", "DETECTED", "success")
            time.sleep(0.3)
            success = random.random() < 0.85
            add_log("motor", "SUCCESS" if success else "FAILED", "success" if success else "error")
            st.session_state.metrics["total_grasps"] += 1
            if success:
                st.session_state.metrics["successes"] += 1
            rate = st.session_state.metrics["successes"] / st.session_state.metrics["total_grasps"]
            st.session_state.metrics["history"].append(rate)
        st.success("✅ COMPLETE")
    
    st.markdown("---")
    st.markdown("### 📊 STATS")
    total = st.session_state.metrics["total_grasps"]
    rate = (st.session_state.metrics["successes"] / total * 100) if total > 0 else 0
    st.metric("ATTEMPTS", total)
    st.metric("SUCCESS", f"{rate:.1f}%")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🎤 SPEECH", "👁️ VISION", "🤖 MOTOR", "📊 ANALYTICS"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        st.markdown("### 🎙️ VOICE INTERFACE")
        # Animated voice waveform visualization
        st.markdown('''
        <div style="text-align: center; padding: 30px; background: rgba(0,255,255,0.05); border-radius: 10px;">
            <div style="display: flex; justify-content: center; align-items: center; gap: 8px; height: 100px;">
                <div style="width: 6px; background: #00ffff; animation: wave 0.8s ease-in-out infinite; animation-delay: 0s;"></div>
                <div style="width: 6px; background: #00ffff; animation: wave 0.8s ease-in-out infinite; animation-delay: 0.1s;"></div>
                <div style="width: 6px; background: #00ffff; animation: wave 0.8s ease-in-out infinite; animation-delay: 0.2s;"></div>
                <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #00ffff, #ff00ff); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; box-shadow: 0 0 20px rgba(0,255,255,0.5);">
                    🎤
                </div>
                <div style="width: 6px; background: #00ffff; animation: wave 0.8s ease-in-out infinite; animation-delay: 0.3s;"></div>
                <div style="width: 6px; background: #00ffff; animation: wave 0.8s ease-in-out infinite; animation-delay: 0.4s;"></div>
                <div style="width: 6px; background: #00ffff; animation: wave 0.8s ease-in-out infinite; animation-delay: 0.5s;"></div>
            </div>
            <div style="color: #00ffff; font-family: Orbitron; margin-top: 15px; font-size: 14px;">
                SPEECH RECOGNITION ACTIVE
            </div>
        </div>
        <style>
        @keyframes wave {
            0%, 100% { height: 20px; opacity: 0.3; }
            50% { height: 80px; opacity: 1; }
        }
        </style>
        ''', unsafe_allow_html=True)
        typed = st.text_input("COMMAND:", placeholder="pick the bottle")
        if st.button("📤 SEND"):
            if typed:
                words = typed.lower().split()
                action = "pick" if "pick" in words or "grab" in words else "place"
                obj = next((w for w in ["bottle", "cup", "box"] if w in words), "object")
                st.session_state.last_command = {"action": action, "object": obj, "confidence": 0.9}
                add_log("speech", f"TEXT: {typed}", "success")
                st.success(f"✅ {action.upper()} {obj.upper()}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 INTENT")
        if st.session_state.last_command:
            cmd = st.session_state.last_command
            col_a, col_b = st.columns(2)
            col_a.metric("ACTION", cmd.get("action", "—").upper())
            col_b.metric("OBJECT", cmd.get("object", "—").upper())
            if st.button("✅ EXECUTE", use_container_width=True):
                st.success("⚡ DISPATCHED")
        else:
            st.info("⏳ AWAITING COMMAND")
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        st.markdown("### 📹 CAMERA")
        uploaded = st.file_uploader("UPLOAD", type=["jpg", "png"])
        if uploaded:
            img = Image.open(uploaded)
        else:
            try:
                img = Image.open(io.BytesIO(requests.get("https://ultralytics.com/images/zidane.jpg", timeout=3).content))
            except:
                img = Image.new("RGB", (640, 480), (20, 25, 45))
        st.image(img, use_column_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        st.markdown("### 🔍 DETECT")
        if st.button("🎯 RUN YOLO", use_container_width=True):
            with st.spinner("ANALYZING..."):
                time.sleep(0.8)
                dets = simulate_detections(img.width, img.height)
                annotated = draw_detections(img, dets)
                st.image(annotated, use_column_width=True)
                for d in dets:
                    add_log("vision", f"{d['label']} {d['confidence']:.0%}", "success")
                st.success(f"✅ {len(dets)} OBJECTS")
        st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="tech-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 🦾 ROBOT ARM")
        # Animated robotic arm gripper
        st.markdown('''
        <div style="text-align: center; padding: 40px; background: rgba(0,255,255,0.03); border-radius: 10px;">
            <div style="position: relative; display: inline-block;">
                <!-- Arm base -->
                <div style="width: 80px; height: 20px; background: linear-gradient(135deg, #00ffff, #0099cc); border-radius: 10px; margin: 0 auto;"></div>
                <!-- Arm segment 1 -->
                <div style="width: 15px; height: 80px; background: linear-gradient(180deg, #00ffff, #0099cc); margin: 0 auto; animation: armMove1 2s ease-in-out infinite;"></div>
                <!-- Arm segment 2 -->
                <div style="width: 12px; height: 60px; background: linear-gradient(180deg, #0099cc, #00ffff); margin: 0 auto; animation: armMove2 2s ease-in-out infinite; animation-delay: 0.2s;"></div>
                <!-- Gripper -->
                <div style="margin-top: 10px; display: flex; justify-content: center; gap: 5px; animation: grip 2s ease-in-out infinite;">
                    <div style="width: 30px; height: 8px; background: #ff00ff; border-radius: 4px; transform-origin: right; animation: gripLeft 2s ease-in-out infinite;"></div>
                    <div style="width: 30px; height: 8px; background: #ff00ff; border-radius: 4px; transform-origin: left; animation: gripRight 2s ease-in-out infinite;"></div>
                </div>
                <!-- Target object -->
                <div style="margin-top: 20px; font-size: 30px; animation: targetBounce 2s ease-in-out infinite;">
                    📦
                </div>
            </div>
            <div style="color: #00ffff; font-family: Orbitron; margin-top: 20px; font-size: 16px; font-weight: 700;">
                ROBOTIC GRIPPER SYSTEM
            </div>
            <div style="color: #00ff88; font-family: Roboto Mono; font-size: 12px; margin-top: 8px;">
                [ 6-DOF ARTICULATED ARM ]
            </div>
        </div>
        <style>
        @keyframes armMove1 {
            0%, 100% { transform: rotate(0deg); }
            50% { transform: rotate(-5deg); }
        }
        @keyframes armMove2 {
            0%, 100% { transform: rotate(0deg); }
            50% { transform: rotate(5deg); }
        }
        @keyframes gripLeft {
            0%, 100% { transform: rotate(0deg); }
            50% { transform: rotate(-15deg); }
        }
        @keyframes gripRight {
            0%, 100% { transform: rotate(0deg); }
            50% { transform: rotate(15deg); }
        }
        @keyframes targetBounce {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
        }
        </style>
        ''', unsafe_allow_html=True)
        if st.button("🎮 EXECUTE GRASP", use_container_width=True):
            progress = st.progress(0)
            for i in range(100):
                progress.progress(i + 1)
                time.sleep(0.02)
            success = random.random() < 0.87
            if success:
                st.success("✅ GRASP SUCCESS")
                st.session_state.metrics["successes"] += 1
            else:
                st.error("❌ GRASP FAILED")
            st.session_state.metrics["total_grasps"] += 1
    with col2:
        st.markdown("### 🎛️ CONTROL")
        st.slider("GRIP (cm)", 1, 10, 5)
        st.slider("REACH (cm)", 10, 100, 50)
        st.metric("ANGLE", f"{random.randint(15, 85)}°")
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="tech-card">', unsafe_allow_html=True)
    total = st.session_state.metrics["total_grasps"]
    success = st.session_state.metrics["successes"]
    rate = (success / total * 100) if total > 0 else 0
    col1, col2, col3 = st.columns(3)
    col1.metric("TOTAL", total)
    col2.metric("SUCCESS", success)
    col3.metric("RATE", f"{rate:.1f}%")
    if len(st.session_state.metrics["history"]) > 1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=[h*100 for h in st.session_state.metrics["history"]], mode='lines+markers', line=dict(color='#00ffff', width=3)))
        fig.update_layout(title="SUCCESS RATE", xaxis_title="Attempt", yaxis_title="Rate (%)", height=300, plot_bgcolor='rgba(0,0,0,0.1)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#00ffff'))
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Logs
st.markdown("---")
st.markdown('<div class="tech-card">', unsafe_allow_html=True)
st.markdown("### 📡 SYSTEM LOGS")
col1, col2 = st.columns([3, 1])
with col1:
    if st.session_state.logs:
        st.dataframe(pd.DataFrame(st.session_state.logs[:20]), use_container_width=True, height=200)
    else:
        st.info("NO LOGS")
with col2:
    if st.button("🗑️ CLEAR", use_container_width=True):
        st.session_state.logs = []
        st.success("CLEARED")
    if st.button("💾 EXPORT", use_container_width=True):
        if st.session_state.logs:
            csv = pd.DataFrame(st.session_state.logs).to_csv(index=False).encode('utf-8')
            st.download_button("📥 DOWNLOAD", csv, "logs.csv", "text/csv", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div style="text-align: center; color: rgba(0,255,255,0.5); padding: 20px;">🤖 AI ROBOTICS CONTROL SYSTEM v1.0</div>', unsafe_allow_html=True)