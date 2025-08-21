import os
import json
from pathlib import Path
from collections import defaultdict
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class CandidateProfilerAI:
    def __init__(self, data_dir="data", report_dir="talent-intelligence-report", use_ai=True):
        print("🔧 Initializing CandidateProfilerAI...")
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)

        # Load datasets
        self.resume = self._load_json("resume.json")
        self.linkedin = self._load_json("linkedin.json")
        self.github = self._load_json("github.json")
        self.leetcode = self._load_json("leetcode.json")
        self.jd_data = self._load_json("jd.json")  # Job descriptions
        self.use_ai = use_ai

        # Initialize Groq AI client
        if use_ai:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("❌ GROQ_API_KEY not found in environment variables")
            print("🔧 Initializing Groq client...")
            self.client = Groq(api_key=api_key)
            print("✅ Groq client initialized")

    def _load_json(self, filename):
        path = self.data_dir / filename
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _get_candidate(self, dataset, person_id):
        return next((d for d in dataset if d["person_id"] == person_id), None)

    def _get_job(self, job_id):
        return next((j for j in self.jd_data if j["job_id"] == job_id), {})

    def _ai_analyze(self, prompt, temp=0.2):
        """Utility to call Groq for text output"""
        if not self.use_ai:
            return "AI disabled, no analysis available."
        try:
            response = self.client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=temp
            )
            content = response.choices[0].message.content
            return content.strip() if content is not None else "No AI response."
        except Exception as e:
            print(f"❌ AI analysis failed: {e}")
            return "AI analysis error."

    def generate_tir(self, person_id, job_id=None):
        """Generate Talent Intelligence Report for a candidate (optionally with job match)"""
        resume = self._get_candidate(self.resume, person_id)
        linkedin = self._get_candidate(self.linkedin, person_id)
        github = self._get_candidate(self.github, person_id)
        leetcode = self._get_candidate(self.leetcode, person_id)
        job = self._get_job(job_id) if job_id is not None else {}

        if not resume:
            return {"error": f"No resume data found for {person_id}"}

        # --- Build Evidence Map ---
        evidence_map = defaultdict(lambda: {"resume": 0, "linkedin": 0, "github": 0, "leetcode": 0})
        for s in resume.get("skills", []):
            evidence_map[s]["resume"] += 1
        if linkedin:
            for s in linkedin.get("skills", []):
                evidence_map[s]["linkedin"] += 1
        if github and github.get("top_languages"):
            for s in github["top_languages"]:
                evidence_map[s]["github"] += 1
        if leetcode and leetcode.get("strengths"):
            for s in leetcode["strengths"]:
                evidence_map[s]["leetcode"] += 1

        # --- Skills Report (AI confidence scoring) ---
        skills_report = []
        for skill, ev in evidence_map.items():
            confidence = self._ai_analyze(
                f"Rate proficiency confidence (0-1) for skill '{skill}' "
                f"given evidence {ev}. Only output a number.",
                temp=0
            )
            try:
                confidence = float(confidence)
            except:
                confidence = 0.5
            skills_report.append({"skill": skill, "confidence": round(confidence, 2)})

        # --- Work History & YOE ---
        work_history = resume.get("experience", [])
        if linkedin and linkedin.get("jobs"):
            work_history += linkedin["jobs"]
        yoe = resume.get("YOE", None)

        # --- AI-Based Job Match Analysis ---
        ai_job_comparison = None
        if job:
            ai_job_comparison = self._ai_analyze(
                f"""
                Compare candidate's skills and experience with the job description.
                Candidate Skills: {json.dumps(skills_report, indent=2)}
                Candidate Work History: {json.dumps(work_history, indent=2)}
                Candidate Projects: {json.dumps(resume.get("projects", []), indent=2)}
                Job Description: {json.dumps(job, indent=2)}
                Provide:
                1. Overall match percentage
                2. Key strengths
                3. Gaps to be addressed
                4. Role fit analysis in 2-3 sentences.
                """,
                temp=0.4
            )

        # --- Career Summary ---
        career_summary = self._ai_analyze(
            f"Summarize candidate's career in 2-3 recruiter-style sentences.\n"
            f"Work History: {json.dumps(work_history, indent=2)}\n"
            f"Projects: {json.dumps(resume.get('projects', []), indent=2)}\n"
            f"YOE: {yoe}",
            temp=0.3
        )

        # --- AI Insights ---
        ai_insights = self._ai_analyze(
            f"""Analyze candidate strengths, risks, and potential role fit. 
            Resume: {json.dumps(resume, indent=2)}
            LinkedIn: {json.dumps(linkedin, indent=2)}
            GitHub: {json.dumps(github, indent=2)}
            LeetCode: {json.dumps(leetcode, indent=2)}
            Work History: {json.dumps(work_history, indent=2)}
            YOE: {yoe}
            Job Description: {json.dumps(job, indent=2)}""",
            temp=0.4
        )

        # --- Final Structured Report ---
        tir = {
            "person_id": person_id,
            "job_id": job_id,
            "profile": {
                "name": resume.get("name"),
                "email": resume.get("email"),
                "social_profiles": resume.get("social_profiles", {}),
            },
            "education": resume.get("education", []),
            "YOE": yoe,
            "work_history": work_history,
            "skills_analysis": skills_report,
            "projects": resume.get("projects", []),
            "online_activity": {
                "linkedin": linkedin or {},
                "github": github or {},
                "leetcode": leetcode or {}
            },
            "career_summary": career_summary,
            "ai_job_comparison": ai_job_comparison,  # NEW
            "ai_insights": ai_insights,
            "job_info": job
        }

        # Save JSON
        out_path = self.report_dir / f"TIR_{person_id}_{job_id if job_id else 'nojob'}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(tir, f, indent=2)
        print(f"✅ Talent Intelligence Report saved at {out_path}")

        return tir

    def generate_all_tirs(self):
        """Generate reports for all candidates"""
        for candidate in self.resume:
            pid = candidate["person_id"]
            print(f"\n📋 Generating TIR for {pid}...")
            self.generate_tir(pid)

if __name__ == "__main__":
    profiler = CandidateProfilerAI(use_ai=True)
    # Example: generate TIR for a candidate with a specific job
    profiler.generate_tir("CAND007", job_id="JD001")
