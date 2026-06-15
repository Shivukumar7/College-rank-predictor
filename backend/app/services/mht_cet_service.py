"""
MHT-CET Rank Prediction Service
Maharashtra Common Entrance Test. Max marks: 200.
Total candidates: ~450,000
"""
import numpy as np
from typing import Dict


TOTAL_CANDIDATES_2024 = 450_000

# MHT-CET 2024 approximate marks→rank mapping (percentile-based system)
KNOWN_MARKS_RANK = [
    (200.0, 1),
    (195.0, 10),
    (190.0, 50),
    (180.0, 250),
    (170.0, 800),
    (160.0, 2200),
    (150.0, 3800),
    (140.0, 5500),
    (135.0, 8000),
    (130.0, 11000),
    (125.0, 13800),
    (120.0, 16500),
    (115.0, 19200),
    (110.0, 22000),
    (105.0, 24800),
    (100.0, 27500),
    (95.0, 44000),
    (90.0, 60000),
    (85.0, 72000),
    (80.0, 82500),
    (75.0, 110000),
    (70.0, 137500),
    (65.0, 165000),
    (60.0, 192500),
    (50.0, 250000),
    (40.0, 300000),
    (30.0, 350000),
    (20.0, 400000),
    (0.0, 450000),
]

CATEGORY_MULTIPLIERS = {
    "general": 1.0, "gen": 1.0, "open": 1.0,
    "ews": 0.10,
    "obc": 0.27, "obcncl": 0.27,
    "sc": 0.15, "st": 0.075,
    "pwd": 0.05,
}


from app.utils.difficulty import difficulty_adjust

class MHTCETService:
    def __init__(self):
        self._marks = np.array([p[0] for p in KNOWN_MARKS_RANK], dtype=float)[::-1]
        self._ranks = np.array([p[1] for p in KNOWN_MARKS_RANK], dtype=float)[::-1]

    def get_group_candidates(self, shift: str) -> int:
        s_lower = shift.lower().strip()
        if "pcb" in s_lower:
            return 250000
        return 450000

    def marks_to_rank(self, marks: float, total_candidates: int = 450000) -> int:
        adjusted_score = difficulty_adjust(marks, 200.0, 200.0)
        # Interpolate percentile first from known marks-to-rank mapping
        rank_2024 = float(np.interp(adjusted_score, self._marks, self._ranks))
        percentile = (1.0 - rank_2024 / 450000.0) * 100.0
        
        # Rank ≈ Total Group * (1 - Percentile/100) + 1
        rank = float(total_candidates) * (1.0 - percentile / 100.0) + 1.0
        return max(1, int(np.ceil(rank)))

    def marks_to_percentile(self, marks: float, total_candidates: int = 450000) -> float:
        rank = self.marks_to_rank(marks, total_candidates)
        pct = (1.0 - rank / total_candidates) * 100.0
        return round(max(0.0, min(100.0, pct)), 2)

    def predict(self, marks: float, shift: str = "pcm",
                category: str = "general",
                total_candidates: int = None) -> Dict:
        # Detect PCM vs PCB total candidates if default was passed
        if total_candidates is None or total_candidates == TOTAL_CANDIDATES_2024:
            total_candidates = self.get_group_candidates(shift)
            
        predicted_rank = self.marks_to_rank(marks, total_candidates)
        percentile = self.marks_to_percentile(marks, total_candidates)

        cat_key = category.lower().replace("-", "").replace("_", "").replace(" ", "")
        multiplier = CATEGORY_MULTIPLIERS.get(cat_key, 1.0)
        category_rank = max(1, int(predicted_rank * multiplier))

        return {
            "predicted_rank": predicted_rank,
            "category_rank": category_rank,
            "percentile": percentile,
            "normalized_marks": round(float(marks), 2),
            "confidence": self._confidence(marks),
            "shift": shift,
            "category": category,
            "total_candidates": total_candidates,
        }

    def _confidence(self, marks: float) -> float:
        if marks >= 190 or marks <= 15:
            return 78.0
        elif 60 <= marks <= 170:
            return 91.0
        return 85.0
