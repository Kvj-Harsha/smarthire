import os
import json
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from groq import Groq
from statistics import median


class MarketOptimizer:
    """Analyze market data + generate sourcing strategy using Groq."""

    def __init__(self, market_data_path: Optional[str | Path] = None, jd_data_path: Optional[str | Path] = None):
        # Default paths
        if market_data_path is None:
            market_data_path = Path(__file__).parent.parent / "data" / "market_intelligence.json"
        if jd_data_path is None:
            jd_data_path = Path(__file__).parent.parent / "data" / "jd.json"

        self.market_data_path = Path(market_data_path).resolve()
        self.jd_data_path = Path(jd_data_path).resolve()

        if not self.market_data_path.exists():
            raise FileNotFoundError(f"❌ Market intelligence file not found: {self.market_data_path}")
        if not self.jd_data_path.exists():
            raise FileNotFoundError(f"❌ Job description file not found: {self.jd_data_path}")

        with open(self.market_data_path, "r", encoding="utf-8") as f:
            self.market_data = json.load(f)
        with open(self.jd_data_path, "r", encoding="utf-8") as f:
            self.jd_data = json.load(f)

        self.roles = self.market_data.get("roles", [])

        # Groq client
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("❌ Missing GROQ_API_KEY in .env")
        self.client = Groq(api_key=api_key)

    # ---------- helper ----------
    def _get_job_info(self, job_id: str) -> dict:
        return next((j for j in self.jd_data if j.get("job_id") == job_id), {})

    def _filter_market(self, role: str, location: str, seniority: str):
        return [
            r for r in self.roles
            if r.get("role", "").lower() == role.lower()
            and r.get("location", "").lower() == location.lower()
            and r.get("seniority", "").lower() == seniority.lower()
        ]

    def _comp_benchmarks(self, rows):
        samples = []
        for r in rows:
            samples.extend([float(x) for x in r.get("salary_samples_inr_lpa", [])])
        if not samples:
            return {"p25": 0, "median": 0, "p75": 0, "sample_size": 0}
        samples.sort()

        def pct(values, p): 
            return values[int(p * (len(values) - 1))]

        return {
            "p25": pct(samples, 0.25),
            "median": median(samples),
            "p75": pct(samples, 0.75),
            "sample_size": len(samples)
        }

    # ---------- main ----------
    def analyze(self, job_id: str) -> dict:
        job = self._get_job_info(job_id)
        if not job:
            raise ValueError(f"❌ job_id {job_id} not found in jd.json")

        role = job.get("role_title") or job.get("title") or job.get("role") or ""
        location = job.get("location", "")
        seniority = job.get("seniority", "Mid")

        rows = self._filter_market(role, location, seniority)
        if not rows:
            return {
                "job_id": job_id, 
                "role": role, 
                "location": location, 
                "seniority": seniority, 
                "error": "No market data found"
            }

        # Compensation
        comp = self._comp_benchmarks(rows)

        # Talent trends
        total_openings = sum(r.get("openings", 0) for r in rows)
        avg_tsi = sum(r.get("talent_supply_index", 0) for r in rows) / len(rows)
        hotspots = sorted(
            [{"location": r["location"], "openings": r["openings"]} for r in rows],
            key=lambda x: x["openings"], reverse=True
        )

        # Recommended channels
        channel_scores = {}
        for r in rows:
            for ch, sc in r.get("channels", {}).items():
                channel_scores.setdefault(ch, []).append(sc)
        ranked_channels = sorted(
            [{"channel": ch, "effectiveness": sum(v) / len(v)} for ch, v in channel_scores.items()],
            key=lambda x: x["effectiveness"], reverse=True
        )

        # ---------- Groq summary ----------
        prompt = f"""
You are a Market Intelligence & Talent Sourcing expert.

Job role: {role}
Location: {location}
Seniority: {seniority}

Market Data:
- Compensation Benchmarks (LPA): p25 {comp['p25']}, median {comp['median']}, p75 {comp['p75']}
- Total openings: {total_openings}
- Avg Talent Supply Index: {avg_tsi:.2f}
- Hotspot locations: {hotspots}
- Recommended sourcing channels: {ranked_channels}

Task:
- Provide a high-level **market summary** with recommendations.
- Highlight pay competitiveness, talent availability, and top sourcing channels.
- Strictly avoid demographic or affinity biases.
- Return ONLY JSON.

JSON schema:
{{
  "job_id": "{job_id}",
  "summary": "...",
  "recommendations": ["...", "..."]
}}
"""
        response = self.client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        raw = (response.choices[0].message.content or "").strip()

        # 🔧 Fix: strip code fences if Groq wrapped response
        if raw.startswith("```"):
            raw = raw.split("```json")[-1].split("```")[0].strip()

        try:
            ai_summary = json.loads(raw)
        except Exception:
            ai_summary = {"job_id": job_id, "summary": raw, "recommendations": []}

        return {
            "job_id": job_id,
            "role": role,
            "location": location,
            "seniority": seniority,
            "compensation": comp,
            "talent_trends": {
                "total_openings": total_openings,
                "avg_talent_supply_index": avg_tsi,
                "hotspots": hotspots,
            },
            "recommended_channels": ranked_channels,
            "ai_summary": ai_summary,
            "updated_at": self.market_data.get("updated_at")
        }


if __name__ == "__main__":
    opt = MarketOptimizer()
    result = opt.analyze("JD001")
    print(json.dumps(result, indent=2))
