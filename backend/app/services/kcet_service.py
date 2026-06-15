"""
KCET Rank Prediction Service
Karnataka Common Entrance Test. Max marks: 180.
Rank is derived from marks using historical cutoff data.
Total candidates: ~200,000
"""
import numpy as np
from typing import Dict


TOTAL_CANDIDATES_2026 = 330_000

# KCET approximate composite score percentage scaled to 180 -> rank mapping (reference: 320,000 candidates)
KNOWN_MARKS_RANK = [
    (180.0, 1),
    (176.4, 5),     # 98%
    (172.8, 100),   # 96%
    (171.0, 250),   # 95%
    (169.2, 500),   # 94%
    (167.4, 800),   # 93%
    (165.6, 1200),  # 92%
    (163.8, 1600),  # 91%
    (162.0, 2000),  # 90%
    (160.2, 2500),  # 89%
    (158.4, 3100),  # 88%
    (156.6, 3800),  # 87%
    (154.8, 4500),  # 86%
    (153.0, 5000),  # 85%
    (151.2, 6000),  # 84%
    (149.4, 7200),  # 83%
    (147.6, 8500),  # 82%
    (145.8, 9800),  # 81%
    (144.0, 10000), # 80%
    (142.2, 12000), # 79%
    (140.4, 14000), # 78%
    (138.6, 16000), # 77%
    (136.8, 18000), # 76%
    (135.0, 20000), # 75%
    (133.2, 24000), # 74%
    (131.4, 28000), # 73%
    (129.6, 32000), # 72%
    (127.8, 36000), # 71%
    (126.0, 40000), # 70%
    (122.4, 48000), # 68%
    (118.8, 56000), # 66%
    (115.2, 65000), # 64%
    (111.6, 75000), # 62%
    (108.0, 85000), # 60%
    (99.0, 120000), # 55%
    (90.0, 160000), # 50%
    (81.0, 200000), # 45%
    (72.0, 240000), # 40%
    (54.0, 280000), # 30%
    (0.0, 320000),  # 0%
]

CATEGORY_MULTIPLIERS = {
    "general": 1.0, "gen": 1.0, "gm": 1.0,
    "obc": 0.30, "obcncl": 0.30,
    "sc": 0.15, "st": 0.075,
    "ews": 0.10, "pwd": 0.05,
}


from app.utils.difficulty import difficulty_adjust

class KCETService:
    def __init__(self):
        self._marks = np.array([p[0] for p in KNOWN_MARKS_RANK], dtype=float)[::-1]
        self._ranks = np.array([p[1] for p in KNOWN_MARKS_RANK], dtype=float)[::-1]
        
        # Augment training data with total candidates variations
        x_train_list = []
        y_train_list = []
        candidate_variations = [120_000, 150_000, 200_000, 300_000, 400_000]
        if TOTAL_CANDIDATES_2026 not in candidate_variations:
            candidate_variations.append(TOTAL_CANDIDATES_2026)
            
        for c in candidate_variations:
            for m, r in KNOWN_MARKS_RANK:
                x_train_list.append([float(m), float(c)])
                # Scale from original 320_000 base reference
                y_train_list.append(float(r) * (float(c) / 320000.0))
                
        self.ml_x_train = np.array(x_train_list, dtype=float)
        self.ml_y_train = np.array(y_train_list, dtype=float)

    def marks_to_rank(self, marks: float, total_candidates: int = TOTAL_CANDIDATES_2026) -> int:
        adjusted_score = difficulty_adjust(marks, 180.0, 180.0)
        try:
            from app.utils.ml_model import get_ml_prediction
            rank = get_ml_prediction("kcet_rank", self.ml_x_train, self.ml_y_train, [adjusted_score, total_candidates])
            return max(1, int(np.round(rank)))
        except Exception:
            pass

        # Fallback to exponential decay model
        rank = float(total_candidates) * np.exp(-0.045 * adjusted_score)
        return max(1, int(np.ceil(rank)))

    def marks_to_percentile(self, marks: float, total_candidates: int = TOTAL_CANDIDATES_2026) -> float:
        rank = self.marks_to_rank(marks, total_candidates)
        pct = (1.0 - rank / total_candidates) * 100.0
        return round(max(0.0, min(100.0, pct)), 2)

    def predict(self, marks: float, board_marks: float = None, shift: str = "day1",
                category: str = "general",
                total_candidates: int = TOTAL_CANDIDATES_2026) -> Dict:
        
        # Calculate effective marks if board marks are provided
        board_marks_used = board_marks is not None
        if board_marks is None:
            # Estimate board percentage based on KCET marks
            kcet_pct_full = (marks / 180.0) * 100.0
            estimated_board_pct = 60.0 + 0.38 * kcet_pct_full
            board_marks = (estimated_board_pct / 100.0) * 300.0

        # KCET weight = 50% of (marks/180), Board weight = 50% of (board_marks/300)
        kcet_pct = (marks / 180.0) * 50.0
        board_pct = (board_marks / 300.0) * 50.0
        total_pct = kcet_pct + board_pct
        # Convert back to equivalent 180 scale for the interpolation mapping
        effective_marks = (total_pct / 100.0) * 180.0

        predicted_rank = self.marks_to_rank(effective_marks, total_candidates)
        percentile = self.marks_to_percentile(effective_marks, total_candidates)

        cat_key = category.lower().replace("-", "").replace("_", "").replace(" ", "")
        if cat_key.startswith("sc"):
            multiplier = 0.15
        elif cat_key.startswith("st"):
            multiplier = 0.075
        elif cat_key.startswith("1"):
            multiplier = 0.04
        elif cat_key.startswith("2a"):
            multiplier = 0.15
        elif cat_key.startswith("2b"):
            multiplier = 0.04
        elif cat_key.startswith("3a"):
            multiplier = 0.05
        elif cat_key.startswith("3b"):
            multiplier = 0.05
        elif cat_key.startswith("gm"):
            multiplier = 1.0
        else:
            multiplier = CATEGORY_MULTIPLIERS.get(cat_key, 1.0)

        category_rank = max(1, int(predicted_rank * multiplier))

        return {
            "predicted_rank": predicted_rank,
            "category_rank": category_rank,
            "percentile": percentile,
            "normalized_marks": round(float(effective_marks), 2),
            "confidence": self._confidence(effective_marks),
            "shift": shift,
            "category": category,
            "total_candidates": total_candidates,
            "board_marks_used": board_marks_used
        }

    def _confidence(self, marks: float) -> float:
        if marks >= 170 or marks <= 15:
            return 78.0
        elif 50 <= marks <= 150:
            return 90.0
        return 85.0
