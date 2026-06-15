"""
COMEDK UGET Rank Prediction Service
Karnataka private engineering colleges. Max marks: 180.
Total candidates: ~90,000
"""
import numpy as np
from typing import Dict


TOTAL_CANDIDATES_2024 = 90_000

KNOWN_MARKS_RANK = [
    (180, 1),
    (178, 5),
    (175, 15),
    (172, 30),
    (170, 50),
    (165, 120),
    (160, 250),
    (155, 450),
    (150, 750),
    (145, 1200),
    (140, 1800),
    (135, 2600),
    (130, 3700),
    (125, 5000),
    (120, 6800),
    (115, 9000),
    (110, 11500),
    (105, 14500),
    (100, 18000),
    (95, 22000),
    (90, 26500),
    (85, 31500),
    (80, 37000),
    (75, 42500),
    (70, 48500),
    (65, 54500),
    (60, 60500),
    (55, 66000),
    (50, 71000),
    (45, 75500),
    (40, 79500),
    (35, 83000),
    (30, 86000),
    (20, 89000),
    (10, 89800),
    (0, 90000),
]

CATEGORY_MULTIPLIERS = {
    "general": 1.0, "gen": 1.0, "gm": 1.0,
    "obc": 0.30, "obcncl": 0.30,
    "sc": 0.15, "st": 0.075,
    "ews": 0.10, "pwd": 0.05,
}


from app.utils.difficulty import difficulty_adjust

class COMEDKService:
    def __init__(self):
        self._marks = np.array([p[0] for p in KNOWN_MARKS_RANK], dtype=float)[::-1]
        self._ranks = np.array([p[1] for p in KNOWN_MARKS_RANK], dtype=float)[::-1]

    def marks_to_rank(self, marks: float, total_candidates: int = TOTAL_CANDIDATES_2024) -> int:
        adjusted_score = difficulty_adjust(marks, 180.0, 180.0)
        # Predicted Rank ≈ 1.1L * (1 - Score/180)^2
        if adjusted_score >= 180.0:
            return 1
        rank = 110000.0 * ((1.0 - adjusted_score / 180.0) ** 2)
        # Scale by total candidates
        if total_candidates != TOTAL_CANDIDATES_2024:
            rank = rank * (total_candidates / TOTAL_CANDIDATES_2024)
        return max(1, int(np.ceil(rank)))

    def marks_to_percentile(self, marks: float, total_candidates: int = TOTAL_CANDIDATES_2024) -> float:
        rank = self.marks_to_rank(marks, total_candidates)
        pct = (1.0 - rank / total_candidates) * 100.0
        return round(max(0.0, min(100.0, pct)), 2)

    def predict(self, marks: float, shift: str = "single",
                category: str = "general",
                total_candidates: int = TOTAL_CANDIDATES_2024) -> Dict:
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
        if marks >= 170 or marks <= 15:
            return 78.0
        elif 50 <= marks <= 150:
            return 90.0
        return 85.0
