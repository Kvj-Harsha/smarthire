import os
import json
import re
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional


class AssessmentDesigner:
    def __init__(
        self,
        leetcode_data_path="../data/leetcode.json",
        resume_data_path="../data/resume.json",
        jd_data_path="../data/jd.json"
    ):
        # Load API key
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("❌ Missing GROQ_API_KEY in environment or .env file")
        print("✅ GROQ_API_KEY loaded successfully")
        self.client = Groq(api_key=api_key)

        # Load LeetCode profiles
        with open(leetcode_data_path, "r", encoding="utf-8") as f:
            self.leetcode_data = json.load(f)
        print(f"✅ Loaded {len(self.leetcode_data)} candidates from {leetcode_data_path}")

        # Load resume data
        with open(resume_data_path, "r", encoding="utf-8") as f:
            self.resume_data = json.load(f)
        print(f"✅ Loaded {len(self.resume_data)} resumes from {resume_data_path}")

        # Load JD data (optional)
        self.jd_data = []
        if Path(jd_data_path).exists():
            with open(jd_data_path, "r", encoding="utf-8") as f:
                self.jd_data = json.load(f)
            print(f"✅ Loaded {len(self.jd_data)} job descriptions from {jd_data_path}")

    def _get_candidate_profile(self, person_id: str):
        lc_entry = next((c for c in self.leetcode_data if c["person_id"] == person_id), None)
        if not lc_entry:
            raise ValueError(f"❌ No candidate found in leetcode.json with person_id {person_id}")

        resume_entry = next((r for r in self.resume_data if r["person_id"] == person_id), None)
        if not resume_entry:
            raise ValueError(f"❌ No candidate found in resume.json with person_id {person_id}")

        merged = {
            "person_id": person_id,
            "username": lc_entry.get("username"),
            "leetcode_profile": lc_entry,
            "resume_profile": resume_entry
        }
        print(f"✅ Candidate merged: username={merged['username']}, name={resume_entry.get('name')}")
        return merged

    def _get_job(self, job_id: Optional[str]):
        if not self.jd_data or not job_id:
            return {}
        return next((j for j in self.jd_data if j["job_id"] == job_id), {})

    def generate_assessment(self, person_id: str, job_id: Optional[str] = None):
        candidate_profile = self._get_candidate_profile(person_id)
        job_info = self._get_job(job_id) if job_id else {}

        prompt = f"""
You are an assessment generator.
Create a JSON array of 3 coding challenges for the candidate below.

Candidate Profile:
{json.dumps(candidate_profile, indent=2)}

Job Description:
{json.dumps(job_info, indent=2)}

Rules:
- Total 3 questions:
    1-2: Easy to Medium DSA → based on candidate's strengths and LeetCode profile. Avoid trivial questions.
    3: Hard → tailored specifically to the Job Description; assess problem-solving.
- Return ONLY valid JSON (no markdown, no explanation)
- JSON must be a list of objects, each with:
  "title", "difficulty", "description", "instructions", "constraints", "examples", "options"
- Examples must contain "input" and "output"
- Options must include "time_limit_min" and "languages_allowed"
"""

        print("\n📝 Sending prompt to Groq...")
        response = self.client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        raw_text = response.choices[0].message.content
        if not raw_text:
            raise ValueError("❌ Groq response content is None")
        raw_text = raw_text.strip()

        # Remove code fences
        if raw_text.startswith("```") and raw_text.endswith("```"):
            raw_text = raw_text.strip("`").strip()
            if raw_text.lower().startswith("json"):
                raw_text = raw_text[4:].strip()

        # Remove any inline JS-style comments
        raw_text = re.sub(r"//.*$", "", raw_text, flags=re.MULTILINE)

        # Remove trailing commas (before } or ])
        raw_text = re.sub(r",\s*([\]}])", r"\1", raw_text)

        print("\n📨 Cleaned Groq Response:")
        print(raw_text)

        # Parse JSON safely
        try:
            assessment = json.loads(raw_text)
            if not isinstance(assessment, list):
                raise ValueError("❌ Expected Groq JSON to be a list of assessments")
            print("\n✅ Successfully parsed Groq JSON response")
        except json.JSONDecodeError:
            raise ValueError(f"❌ Groq did not return valid JSON:\n{raw_text}")

        return assessment


if __name__ == "__main__":
    designer = AssessmentDesigner(
        leetcode_data_path="./data/leetcode.json",
        resume_data_path="./data/resume.json",
        jd_data_path="./data/jd.json"
    )

    person_id = "CAND002"
    job_id = "JD001"
    package = designer.generate_assessment(person_id, job_id=job_id)

    print("\n🎯 Final Generated Assessment:")
    print(json.dumps(package, indent=2))
