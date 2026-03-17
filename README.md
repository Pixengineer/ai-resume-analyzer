# 🚀 AI Resume Analyzer

An AI-powered Resume Analyzer that evaluates resumes, calculates ATS score, detects skills, and provides intelligent feedback using modern NLP models.

---

## 🌐 Live Demo

🔗 https://ai-resume-analyzer-by-satyam.streamlit.app

---

## 📌 Features

* 📄 Upload Resume (PDF)
* 📊 ATS Score Calculation
* 🛠️ Skill Detection (Category-wise)
* ❌ Missing Skills Identification
* 🎯 Job Description Matching
* 🤖 AI-Powered Feedback:

  * Strengths
  * Weaknesses
  * Improvements
  * Resume Writing Tips
* ✍️ AI-based Resume Improvement Suggestions
* 📥 Download Full Analysis Report

---

## 🧠 Tech Stack

* **Frontend/UI:** Streamlit
* **Backend:** Python
* **AI Integration:** Hugging Face Inference API
* **Libraries Used:**

  * PyPDF2
  * Matplotlib
  * NumPy
  * Requests

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

git clone https://github.com/Pixengineer/ai-resume-analyzer.git
cd ai-resume-analyzer

---

### 2️⃣ Install dependencies

pip install -r requirements.txt

---

### 3️⃣ Add API Key

Open `ai_module.py` and add your Hugging Face API key:

HF_API_KEY = "your_api_key_here"

---

### 4️⃣ Run the application

streamlit run app.py

---

## 📊 How It Works

1. Extracts text from uploaded PDF resume
2. Cleans and processes text data
3. Detects skills using keyword-based matching
4. Calculates ATS score based on:

   * Skill coverage
   * Keyword density
   * Section presence
   * Resume length
5. Matches resume with job description
6. Generates AI-based feedback using NLP model

---

## 🚀 Deployment

This project is deployed using **Streamlit Cloud** for fast and scalable access.

---

## 📈 Future Improvements

* 🔍 OCR support for scanned resumes
* 🌐 Multi-language support
* 🧑‍💼 Job recommendation system
* 📊 Advanced analytics dashboard
* 🔐 User authentication system

---

## 🤝 Contributing

Contributions are welcome!
Feel free to fork this repository and improve the project.

---

## 📬 Contact

👤 Satyam Bhardwaj
🔗 LinkedIn: https://linkedin.com/in/satyam-bhardwaj-94a07631b/
📧 Email: bhardwajsatyamofficial@gmail.com

---

## ⭐ Support

If you like this project, please give it a ⭐ on GitHub!
