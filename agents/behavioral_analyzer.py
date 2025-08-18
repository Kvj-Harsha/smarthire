import os
import json
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional


class BehavioralAnalyzer:
    """Analyze candidate behavioral & cultural fit from textual data using Groq."""

    def __init__(self, candidate_text_path: Optional[str | Path] = None):
        # Default path relative to this script
        if candidate_text_path is None:
            candidate_text_path = Path(__file__).parent.parent / "data" / "candidate_text.json"

        candidate_text_path = Path(str(candidate_text_path)).resolve()

        # Load environment variables
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("❌ Missing GROQ_API_KEY in environment or .env file")
        print("✅ GROQ_API_KEY loaded successfully")

        self.client = Groq(api_key=api_key)

        # Load candidate text
        if not candidate_text_path.exists():
            raise FileNotFoundError(f"❌ candidate_text.json not found at {candidate_text_path}")
        with open(candidate_text_path, "r", encoding="utf-8") as f:
            self.candidate_texts = json.load(f)
        print(f"✅ Loaded candidate text data ({len(self.candidate_texts)} entries)")

    def _get_candidate_text(self, person_id: str) -> str:
        """Retrieve candidate text safely."""
        entry = next((c for c in self.candidate_texts if c.get("person_id") == person_id), None)
        if not entry:
            raise ValueError(f"❌ No candidate text found for person_id {person_id}")

        # Support both 'text' key or 'texts' list (merge into single string)
        if "text" in entry:
            return entry["text"]
        elif "texts" in entry:
            return " ".join(entry["texts"])
        else:
            raise KeyError(f"❌ Candidate entry missing 'text' or 'texts': {entry}")

    def analyze(self, person_id: str) -> dict:
        """Run behavioral analysis and return structured insights."""
        candidate_text = self._get_candidate_text(person_id)

        prompt = f"""
You are an AI behavioral and cultural fit analyzer.

Candidate Text:
{candidate_text}

Task:
- Analyze candidate's soft skills based on text.
- Identify keywords and themes related to:
    - Collaboration
    - Problem-solving
    - Communication
- Provide a high-level summary of behavioral strengths.
- Include a bias mitigation protocol.
- Return ONLY valid JSON (no markdown, no explanation).

Structure JSON as:
{{
  "person_id": "{person_id}",
  "soft_skill_analysis": {{"collaboration": "...","problem_solving": "...","communication": "..."}},
  "keywords": ["...", "..."],
  "themes": ["...", "..."],
  "high_level_insights": "...",
  "bias_mitigation_protocol": {{"guidelines": ["...", "..."]}}
}}
"""

        print("\n📝 Sending prompt to Groq...")
        response = self.client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        raw_text = response.choices[0].message.content
        if not raw_text:
            raise ValueError("❌ Groq response message content is None")

        raw_text = raw_text.strip()
        # Remove code fences if present
        if raw_text.startswith("```") and raw_text.endswith("```"):
            raw_text = raw_text[3:-3].strip()

        try:
            analysis = json.loads(raw_text)
            print("✅ Successfully parsed Groq JSON response")
        except json.JSONDecodeError:
            raise ValueError(f"❌ Groq did not return valid JSON:\n{raw_text}")

        return analysis


if __name__ == "__main__":
    candidate_json_path = Path(__file__).parent.parent / "data" / "candidate_text.json"
    analyzer = BehavioralAnalyzer(candidate_text_path=candidate_json_path)
    person_id = "CAND001"
    report = analyzer.analyze(person_id)

    print("\n🎯 Behavioral & Cultural Fit Analysis:")
    print(json.dumps(report, indent=2))
