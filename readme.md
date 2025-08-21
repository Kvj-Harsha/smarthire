
# Talent Intelligence Platform

An AI-powered pipeline for **candidate profiling**, **job matching**, and **market intelligence**, using **Groq LLM API** and **Streamlit dashboard** for visualization.

---

### Features
- **Candidate Profiler**
  - Generates a Talent Intelligence Report (TIR) using resume, LinkedIn, GitHub, and LeetCode data.
  - AI-based skills confidence scoring.
  - Career summary and recruiter-style insights.

- **Job Match Analysis**
  - AI-powered comparison between candidate skills & job description (JD).
  - Provides match percentage, strengths, gaps, and role fit analysis.

- **Behavioral Analysis**
  - Analyzes candidate's behavioral traits using textual evidence.

- **Market Intelligence**
  - Provides sourcing recommendations and market insights for roles.

- **Streamlit Dashboard**
  - Visualizes profiles, assessments, and online presence.

---

## System Architecture

<img width="7176" height="4916" alt="diagram (8)" src="https://github.com/user-attachments/assets/3357cced-46b8-41c1-9764-4ca837dd5b38" />

---

### Project Structure
```
.
├── agents/
│   ├── candidate_profiler.py      # Candidate profiling and TIR generation
│   ├── assessment_designer.py     # Assessment generation logic
│   ├── behavioral_analyzer.py     # Behavioral analysis module
│   ├── market_optimizer.py        # Market insights & sourcing strategy
│
├── data/
│   ├── resume.json                # Candidate data
│   ├── linkedin.json              # LinkedIn profile data
│   ├── github.json                # GitHub profile data
│   ├── leetcode.json              # LeetCode profile data
│   ├── jd.json                    # Job descriptions
│   └── candidate_text.json        # Textual evidence for behavioral analysis
│
├── talent-intelligence-report/    # Generated reports (TIRs and orchestrated outputs)
│
├── app/
|    ├──orchestrator.py                # Main pipeline runner
├── dashboard.py                   # Streamlit app for visualization
├── .env                           # API keys and environment variables
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation
```

---

### Installation
#### 1. Clone the Repository
```bash
git clone https://github.com/your-org/talent-intelligence-platform.git
cd talent-intelligence-platform
```

#### 2. Create Virtual Environment & Install Dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Set Up Environment Variables
Create a `.env` file in the root directory:
```bash
GROQ_API_KEY=your_groq_api_key_here
```

---

### Usage
#### Generate Reports
```bash
python app/orchestrator.py
```
This will:
- Load candidate & job data.
- Run profiling, behavioral analysis, assessment design, and market intelligence.
- Save orchestrated output to `talent-intelligence-report/`.

#### Run Dashboard
```bash
streamlit run app.py
```
Open the provided local URL to view reports.

---

### Output
- Reports are saved in:
```
talent-intelligence-report/TIR_<PERSON_ID>_<JOB_ID>.json
```
and combined outputs:
```
talent-intelligence-report/<PERSON_ID>_<JOB_ID>_orchestrated.json
```

---

### Dependencies
Add to `requirements.txt`:
```
groq
python-dotenv
streamlit
```

---

### Future Enhancements
- Visualization of AI-based match percentage using charts.
- Integration with external HRIS or ATS.
- Role benchmarking using real-time market data.

---

## Contributors

> @Kvj-Harsha
