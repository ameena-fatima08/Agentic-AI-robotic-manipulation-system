# Agentic AI Voice-Controlled Robotic Arm

## 📌 Project Overview

This project presents an **Agentic AI-based voice-controlled robotic arm** implemented using a **hierarchical multi-agent architecture** on **Raspberry Pi**.  
Inspired by research such as **HiBerNac (Hierarchical Brain-Emulated Robotic Neural Agent Collective)**, the system adopts a **Master–Sub Agent model** to achieve intelligent perception, decision-making, and physical actuation.

The robotic arm responds to **natural voice commands**, perceives its environment through a **camera**, and executes safe, structured movements using servo motors.

---

## 🎯 Objectives

- Design a **hierarchical agentic AI architecture** for robotics
- Enable **voice-based human–robot interaction**
- Integrate **vision feedback** for environment awareness
- Implement **safe real-time motor control** on Raspberry Pi
- Demonstrate **research-to-implementation mapping**

---

## 🧠 System Architecture

The system follows a **hierarchical control structure**:

### Agents

- **Speech Agent** – converts voice to text and intent
- **Vision Agent** – detects objects and spatial context
- **Context Agent** – tracks system state and feasibility
- **Safety Agent** – enforces joint limits and safety rules
- **Master Agent** – coordinates sub-agents and makes decisions

### Execution Flow

User → Perception Agents → Master Agent → Planner → Raspberry Pi → Robotic Arm → Feedback Loop

---

## 🧩 Hardware Components

- Raspberry Pi 4 Model B
- 4–6 DOF Robotic Arm
- PCA9685 Servo Driver (I2C)
- External 5–6V Power Supply
- USB Camera
- USB Microphone

⚠ Servos are powered **externally**, not from Raspberry Pi GPIO.

---

## ⚙ Software Stack

- **OS**: Raspberry Pi OS, Linux (Ubuntu VM)
- **Language**: Python 3
- **Libraries**:
  - OpenCV
  - SpeechRecognition / Vosk / Whisper
  - Adafruit PCA9685
  - RPi.GPIO / gpiozero

Agent logic is implemented using **custom lightweight Python modules**, inspired by agentic AI research rather than cloud-based frameworks.

---

## 🧪 Development Strategy

- **Linux VM**: AI development, testing, simulation
- **Raspberry Pi**: Hardware control and deployment
- Shared codebase with hardware abstraction

---

## 📂 Project Structure

Refer to the documented modular folder structure separating:

- Agents
- Perception
- Planning
- Hardware abstraction
- Simulation
- Documentation

---

## 📚 Research Foundation

This project is inspired by:

- HiBerNac: Hierarchical Brain-Emulated Robotic Neural Agent Collective
- Multi-agent robotic control systems
- Human–Robot Interaction (HRI) literature
- Edge AI systems for embedded robotics

---

## 🎤 Academic Relevance

The project demonstrates:

- Agentic AI principles
- Hierarchical decision-making
- Real-time embedded system constraints
- Research-aligned system design

---

## 👥 Team Collaboration

The modular architecture enables parallel development across:

- AI & perception
- Hardware & control
- Integration & documentation

---

## 🏁 Conclusion

This project bridges **agentic AI research and practical robotics**, showcasing how hierarchical intelligence can be effectively deployed on low-cost embedded platforms like Raspberry Pi.
