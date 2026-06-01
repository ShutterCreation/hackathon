import streamlit as st
import PyPDF2
import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

# Setup Groq API
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

st.set_page_config(page_title="AI Mock Interviewer", layout="wide")

st.title("🚀 AI-Powered Mock Interview Platform")
st.markdown("Upload your Resume and paste the Job Description to start.")

# Initialize session state for interview tracking
if 'interview_started' not in st.session_state:
    st.session_state.interview_started = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = ""
if 'difficulty' not in st.session_state:
    st.session_state.difficulty = "Easy"
if 'last_feedback' not in st.session_state:
    st.session_state.last_feedback = None
if 'question_count' not in st.session_state:
    st.session_state.question_count = 0
if 'start_time' not in st.session_state:
    st.session_state.start_time = 0
if 'total_scores' not in st.session_state:
    st.session_state.total_scores = {"accuracy": 0, "clarity": 0, "depth": 0, "relevance": 0, "time_efficiency": 0}
if 'interview_over' not in st.session_state:
    st.session_state.interview_over = False
if 'asked_questions' not in st.session_state:
    st.session_state.asked_questions = []

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Job Description (JD)")
    jd_text = st.text_area("Paste the JD here:", height=250, key="jd_input")

with col2:
    st.subheader("2. Candidate Resume")
    uploaded_file = st.file_uploader("Upload Resume (PDF format)", type=["pdf"], key="resume_upload")

def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()
    return text

def generate_question(resume, jd, difficulty, asked_questions):
    asked_str = "\n".join(asked_questions) if asked_questions else "None"
    
    prompt = f"""
    You are an expert technical AI interviewer. 
    Job Description: {jd}
    Candidate Resume: {resume}
    
    PREVIOUSLY ASKED QUESTIONS (DO NOT REPEAT THESE):
    {asked_str}
    
    Task: Ask exactly ONE {difficulty} level interview question relevant to the candidate's skills and the JD. 
    Ensure it is completely different from the 'Previously Asked Questions'.
    Do not include any greetings or extra text, just the question.
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8 
    )
    return response.choices[0].message.content

def evaluate_answer(question, answer, current_difficulty, time_taken):
    prompt = f"""
    You are an expert technical interviewer and a professional English communication coach.
    
    Question: {question}
    Candidate Answer: {answer}
    Difficulty: {current_difficulty}
    Time Taken: {time_taken} seconds.
    
    Task 1: Evaluate out of 10 for Accuracy, Clarity, Depth, Relevance, and Time_Efficiency.
    CRITICAL RULE FOR TIME: If 'Time Taken' is greater than 60 seconds, heavily penalize 'time_efficiency' (make it below 5). If under 60 seconds, score it high.
    Task 2: Act as a professional English fluency coach. The candidate answered using a microphone. If their phrasing, grammar, or spoken structure is incorrect, provide a gentle, professional correction to fix their spoken English.
    Task 3: Provide brief Technical feedback.
    Task 4: Decide next difficulty (Easy, Medium, or Hard) based on overall performance.
    
    Return STRICTLY in JSON:
    {{
        "scores": {{"accuracy": 8, "clarity": 7, "depth": 6, "relevance": 8, "time_efficiency": 9}},
        "english_coach_feedback": "Your spoken English was decent, but instead of saying X, you can say Y to sound more professional...",
        "technical_feedback": "Short feedback here...",
        "next_difficulty": "Medium"
    }}
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        response_format={ "type": "json_object" }
    )
    return json.loads(response.choices[0].message.content)

# Start Interview Button
if st.button("Analyze & Start Interview", key="start_btn") and not st.session_state.interview_started:
    if jd_text and uploaded_file:
        resume_text = extract_text_from_pdf(uploaded_file)
        st.session_state['resume'] = resume_text
        st.session_state['jd'] = jd_text
        st.session_state.interview_started = True
        
        with st.spinner("AI is preparing your first question..."):
            first_q = generate_question(resume_text, jd_text, st.session_state.difficulty, st.session_state.asked_questions)
            st.session_state.current_question = first_q
            st.session_state.asked_questions.append(first_q)
            st.session_state.start_time = time.time()
            st.rerun()
    else:
        st.error("Please provide both Job Description and Resume.")

# Live Interview Room Logic
if st.session_state.interview_started and not st.session_state.interview_over:
    st.markdown("---")
    
    if st.session_state.last_feedback:
        st.success("Previous Answer Evaluated!")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.write("### 📊 Performance Analysis")
            st.json(st.session_state.last_feedback["scores"])
        with col_f2:
            st.write("### 🗣️ Communication Coach & Tech Feedback")
            st.info(st.session_state.last_feedback["english_coach_feedback"])
            st.info(st.session_state.last_feedback["technical_feedback"])
        st.markdown("---")
    
    st.header(f"🎙️ Live Interview Room (Question {st.session_state.question_count + 1} of 3)")
    st.info(f"**Difficulty Level:** {st.session_state.difficulty} | ⏱️ *Answer quickly! Target: < 60 seconds*")
    st.write(f"**AI Interviewer:** {st.session_state.current_question}")
    
    # 💥 PUDHU LOGIC: Audio or Text Input
    audio_value = st.audio_input("🎤 Record your answer (Audio):", key=f"audio_{st.session_state.question_count}")
    st.markdown("**OR**")
    candidate_answer = st.text_area("✍️ Type your answer (Text):", key=f"ans_{st.session_state.question_count}")
    
    if st.button("Submit Answer", key="submit_ans_btn"):
        final_answer = ""
        time_taken = round(time.time() - st.session_state.start_time, 2)
        
        if audio_value:
            with st.spinner("Transcribing your audio..."):
                transcription = client.audio.transcriptions.create(
                    file=("audio.wav", audio_value.read()),
                    model="whisper-large-v3",
                )
                final_answer = transcription.text
                st.success(f"**AI heard:** {final_answer}")
        elif candidate_answer.strip() != "":
            final_answer = candidate_answer

        if final_answer == "":
            st.error("Please record an audio or type an answer!")
        else:
            with st.spinner(f"Evaluating answer... (Time taken: {time_taken}s)"):
                evaluation = evaluate_answer(st.session_state.current_question, final_answer, st.session_state.difficulty, time_taken)
                
                st.session_state.last_feedback = evaluation
                st.session_state.difficulty = evaluation["next_difficulty"]
                
                for key in st.session_state.total_scores.keys():
                    st.session_state.total_scores[key] += evaluation["scores"][key]
                
                st.session_state.question_count += 1
                
                if st.session_state.question_count >= 3:
                    st.session_state.interview_over = True
                else:
                    next_q = generate_question(st.session_state['resume'], st.session_state['jd'], st.session_state.difficulty, st.session_state.asked_questions)
                    st.session_state.current_question = next_q
                    st.session_state.asked_questions.append(next_q)
                    st.session_state.start_time = time.time()
                
                time.sleep(1) # Small pause for UI to show transcription
                st.rerun()

# Final Dashboard Logic
if st.session_state.interview_over:
    st.markdown("---")
    st.header("🎯 Interview Completed! Final Readiness Report")
    
    avg_scores = {k: v / st.session_state.question_count for k, v in st.session_state.total_scores.items()}
    readiness_score = int(sum(avg_scores.values()) / 5 * 10)
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.metric(label="Overall Interview Readiness Score", value=f"{readiness_score}/100")
        if readiness_score > 75:
            st.success("Verdict: Strong Hire! You are well prepared.")
        elif readiness_score > 50:
            st.warning("Verdict: Needs Improvement. Work on your weak areas.")
        else:
            st.error("Verdict: Not Ready. Highly recommend more practice.")
            
    with col_r2:
        st.write("### Skill Breakdown")
        st.json(avg_scores)
        
    st.balloons()