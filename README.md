# AI-Powered Mock Interview Platform

An intelligent, state-based mock interview simulator that acts as a real-world technical interviewer and a professional English communication coach.

### 🎥 Live Demo Video
https://drive.google.com/file/d/1-GPsLE8KzrficSqqcXqL9nWpWU8tv0dP/view?usp=drive_link

### ✨ The "X-Factor" Features
* **🎙️ Real-Time Audio Transcription & Fluency Coach:** Uses Whisper API to listen to answers and gently corrects English phrasing/grammar.
* **⏱️ The "Pressure Cooker" Timer:** Strict 60-second timer per question. Late submissions face severe time-efficiency penalties.
* **🧠 Adaptive State-Machine Logic:** Dynamically adjusts difficulty (Easy → Medium → Hard) based on real-time evaluation of Accuracy, Clarity, Depth, and Relevance.
* **🎯 Comprehensive Readiness Score:** Generates a 0-100 hiring readiness score with a detailed skill breakdown dashboard.

### 💻 Tech Stack
* **Frontend:** Streamlit (Python)
* **AI Engine:** Llama 3.3 70b (via Groq API) for lightning-fast adaptive reasoning
* **Speech-to-Text:** Whisper Large v3
* **Resume Parsing:** PyPDF2

### 🛠️ How to run locally
1. Clone the repo: `git clone [https://github.com/ShutterCreation/hackathon]`
2. Install dependencies: `pip install streamlit openai PyPDF2 python-dotenv`
3. Create a `.env` file and add: `GROQ_API_KEY=your_api_key_here`
4. Run the app: `python -m streamlit run app.py`
