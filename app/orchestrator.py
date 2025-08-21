import os
import json
from agents.candidate_profiler import CandidateProfilerAI
from agents.assessment_designer import AssessmentDesigner
from agents.behavioral_analyzer import BehavioralAnalyzer
from agents.market_optimizer import MarketOptimizer  # NEW

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "talent-intelligence-report")

def list_profiles():
    resume_path = os.path.join(DATA_DIR, "resume.json")
    if not os.path.exists(resume_path):
        return []
    with open(resume_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [c["person_id"] for c in data]

def list_jds():
    jd_path = os.path.join(DATA_DIR, "jd.json")
    if not os.path.exists(jd_path):
        return []
    with open(jd_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [jd["job_id"] for jd in data]

def run_orch(person_id: str, job_id: str):
    # --- Load JD Info ---
    jd_path = os.path.join(DATA_DIR, "jd.json")
    job_info = {}
    if os.path.exists(jd_path):
        with open(jd_path, "r", encoding="utf-8") as f:
            jds = json.load(f)
        job_info = next((j for j in jds if j.get("job_id") == job_id), {})

    # --- Candidate Profiler ---
    profiler = CandidateProfilerAI(use_ai=True)
    tir = profiler.generate_tir(person_id=person_id, job_id=job_id)

    # --- Assessment Designer ---
    designer = AssessmentDesigner(
        leetcode_data_path=os.path.join(DATA_DIR, "leetcode.json"),
        resume_data_path=os.path.join(DATA_DIR, "resume.json"),
        jd_data_path=os.path.join(DATA_DIR, "jd.json")
    )
    assessment = designer.generate_assessment(person_id=person_id, job_id=job_id)

    # --- Behavioral Analyzer ---
    behavior_agent = BehavioralAnalyzer(
        candidate_text_path=os.path.join(DATA_DIR, "candidate_text.json")
    )
    behavioral_analysis = behavior_agent.analyze(person_id)

    # --- Market Intelligence & Sourcing Optimizer (NEW) ---
    role = job_info.get("role_title") or job_info.get("title") or job_info.get("role") or "Backend Engineer"
    location = job_info.get("location") or "Bengaluru, IN"
    seniority = job_info.get("seniority") or "Mid"

    market_agent = MarketOptimizer(
        market_data_path=os.path.join(DATA_DIR, "market_intelligence.json")
    )
    market_intel = market_agent.analyze(job_id=job_id)

    # --- Merge Results ---
    orchestrated_output = {
        "person_id": person_id,
        "job_id": job_id,
        "job_info": job_info,
        "tir": tir,
        "assessment": assessment,
        "behavioral_analysis": behavioral_analysis,
        "market_intelligence": market_intel  # NEW
    }

    # --- Save to file ---
    os.makedirs(REPORT_DIR, exist_ok=True)
    out_path = os.path.join(REPORT_DIR, f"{person_id}_{job_id}_orchestrated.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(orchestrated_output, f, indent=2)

    print(f"✅ Orchestration complete. Saved: {out_path}")
    return orchestrated_output
