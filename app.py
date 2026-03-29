import os
import pandas as pd
import xgboost as xgb
from flask import Flask, render_template, request
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# 1. Load your XGBoost Model
model = xgb.XGBClassifier()
model.load_model("stress_model.json")

# 2. Setup AI Counselor
HF_TOKEN = os.getenv("HF_TOKEN=your_token_here")
client = InferenceClient(model="meta-llama/Meta-Llama-3-8B-Instruct", token=HF_TOKEN)


def get_ai_counselor_advice(prediction, student_data):
    stress_levels = {0: "Low", 1: "Medium", 2: "High"}
    level = stress_levels.get(prediction, "Unknown")

    # We explicitly tell the AI to use Bold Headers and Bullet Points
    messages = [
        {"role": "system",
         "content": "You are a professional School Counselor. Provide a structured assessment with 3 clear sections: **Immediate Actions**, **Long-term Habit**, and **Positive Affirmation**. Use bullet points and bold headers."},
        {"role": "user",
         "content": f"Student Stress: {level}. Data: Anxiety:{student_data['anxiety_level']}, Sleep:{student_data['sleep_quality']}, Bullying:{student_data['bullying']}, Performance:{student_data['academic_performance']}. Give advice in a structured 'Good Points' format."}
    ]
    try:
        response = client.chat_completion(messages, max_tokens=300)
        # The replace('\n', '<br>') is the secret to making it look "propertly" on the web
        return response.choices[0].message.content.replace('\n', '<br>')
    except Exception:
        return "<b>• Focus on Breathing:</b> Practice 4-7-8 breathing.<br><b>• Support:</b> Speak to a mentor today."


@app.route('/', methods=['GET', 'POST'])
def index():
    prediction = None
    advice = None
    if request.method == 'POST':
        user_input = {
            "anxiety_level": int(request.form.get('anxiety_level', 10)),
            "self_esteem": int(request.form.get('self_esteem', 15)),
            "mental_health_history": 0,
            "depression": int(request.form.get('depression', 10)),
            "headache": 2, "blood_pressure": 2,
            "sleep_quality": int(request.form.get('sleep_quality', 3)),
            "breathing_problem": 2, "noise_level": 2, "living_conditions": 3,
            "safety": 3, "basic_needs": 3,
            "academic_performance": int(request.form.get('academic_performance', 3)),
            "study_load": int(request.form.get('study_load', 3)),
            "teacher_student_relationship": 3, "future_career_concerns": 3,
            "social_support": 2, "peer_pressure": 2, "extracurricular_activities": 2,
            "bullying": int(request.form.get('bullying', 0))
        }

        df = pd.DataFrame([user_input])
        prediction = int(model.predict(df)[0])
        advice = get_ai_counselor_advice(prediction, user_input)

    return render_template('index.html', prediction=prediction, advice=advice)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)