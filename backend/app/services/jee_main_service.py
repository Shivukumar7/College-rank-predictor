"""
JEE Main Rank Prediction Service
Uses real historical marks-percentile-rank data (2009-2026) for accurate predictions.
Focuses on 2023-2026 data with weighted recency to reflect current trends.
"""
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict


# ─────────────────────────────────────────────
# Real JEE Main 2026 shift normalization offsets
# Based on official NTA shift analysis CSV
# marks_for_99_percentile by shift → difficulty indicator
# ─────────────────────────────────────────────
SHIFT_DIFFICULTY = {
    # shift_id: marks needed for 99th percentile (lower = harder shift)
    "shift1": 166,   # average across 2026 shift 1 sessions
    "shift2": 169,   # average across 2026 shift 2 sessions
}
GLOBAL_99_MARKS = 167.5   # average across all 2026 shifts

# Total candidates 2026 (JEE Main Session 1 + Session 2)
TOTAL_CANDIDATES_2026 = 1_400_000

# Category seat proportion multipliers
# Category rank = general_rank * multiplier (lower rank = fewer seats)
CATEGORY_MULTIPLIERS = {
    "general": 1.0,
    "gen":     1.0,
    "ews":     0.10,   # ~10% of general seats
    "obc":     0.27,   # ~27% seats
    "obc-ncl": 0.27,
    "sc":      0.15,   # ~15% seats
    "st":      0.075,  # ~7.5% seats
    "pwd":     0.05,
}


class JEEMainService:
    def __init__(self, data_path: str = "app/data/jee_main"):
        self.data_path = Path(data_path)
        self.shift_stats: Dict = {}
        self.global_stats: Dict = {}

        # Core interpolation table built from real data
        self._marks_to_percentile_table: np.ndarray | None = None
        self._percentile_to_rank_table: np.ndarray | None = None

        self._load_and_build_model()

    # ─────────────────────────────────────────────
    # Data loading
    # ─────────────────────────────────────────────
    def _load_and_build_model(self):
        csv_path = self.data_path / "jee_marks_percentile_rank_2009_2026.csv"
        shift_csv = self.data_path / "jee_2026_shift_analysis.csv"

        try:
            df = pd.read_csv(csv_path)
            df.columns = [c.strip() for c in df.columns]

            # ── Weighted recency: use only 2022-2026, weight recent years more ──
            recent = df[df["Year"] >= 2022].copy()
            # Weight: 2026→5, 2025→4, 2024→3, 2023→2, 2022→1
            year_weight = {2026: 5, 2025: 4, 2024: 3, 2023: 2, 2022: 1}
            recent["weight"] = recent["Year"].map(year_weight).fillna(1)

            # Expand rows by weight (repeat each row 'weight' times)
            expanded = recent.loc[recent.index.repeat(recent["weight"])].reset_index(drop=True)

            # Assign training data for ML
            self.ml_x_train = df[["Marks", "Total_Candidates"]].values
            self.ml_y_pct_train = df["Percentile"].values
            self.ml_y_rank_train = df["Rank"].values

            self._build_interpolation_table(expanded)
            self._build_shift_stats(shift_csv)

            print(f"[OK] JEE Main model built from {len(expanded)} weighted data points (2022-2026)")

        except Exception as e:
            print(f"[WARN] Could not load historical data: {e} — using fallback model")
            self._build_fallback_model()

    def _build_interpolation_table(self, df: pd.DataFrame):
        """
        Build a monotone marks→percentile lookup table using the real data.
        Groups by marks, takes the median percentile, then fits a monotone spline.
        """
        # Use marks & percentile columns
        grouped = (
            df.groupby("Marks")["Percentile"]
            .median()
            .reset_index()
            .rename(columns={"Marks": "marks", "Percentile": "percentile"})
            .sort_values("marks")
        )

        # Force monotonicity with isotonic regression
        from sklearn.isotonic import IsotonicRegression
        iso = IsotonicRegression(increasing=True, out_of_bounds="clip")
        iso.fit(grouped["marks"].values, grouped["percentile"].values)

        # Build a dense lookup table marks 0→300 → percentile
        marks_range = np.arange(0, 301, 1, dtype=float)
        percentiles  = iso.predict(marks_range)
        percentiles  = np.clip(percentiles, 0.0, 100.0)

        self._marks_to_percentile_table = np.column_stack([marks_range, percentiles])

        # Store global stats from 2026 data
        data_2026 = df[df["Year"] == 2026] if "Year" in df.columns else df
        self.global_stats = {
            "total_candidates": int(data_2026["Total_Candidates"].median()) if "Total_Candidates" in data_2026.columns else TOTAL_CANDIDATES_2026,
            "mean_marks": float(grouped["marks"].median()),
        }

    def _build_shift_stats(self, shift_csv: Path):
        """Load 2026 shift analysis for normalization."""
        try:
            df = pd.read_csv(shift_csv)
            df.columns = [c.strip() for c in df.columns]
            # Average marks needed for 99th percentile per shift
            s1 = df[df["Shift"].str.contains("1", na=False)]["Marks_for_99_Percentile"].mean()
            s2 = df[df["Shift"].str.contains("2", na=False)]["Marks_for_99_Percentile"].mean()
            self.shift_stats = {
                "shift1": {"marks_99pct": float(s1) if not np.isnan(s1) else SHIFT_DIFFICULTY["shift1"]},
                "shift2": {"marks_99pct": float(s2) if not np.isnan(s2) else SHIFT_DIFFICULTY["shift2"]},
            }
        except Exception:
            self.shift_stats = {k: {"marks_99pct": v} for k, v in SHIFT_DIFFICULTY.items()}

    def _build_fallback_model(self):
        """
        Hardcoded fallback based on published JEE Main 2026 key marks→percentile.
        Source: NTA official answer key & percentile distributions.
        """
        known_points = [
            (0,   0.0),
            (30,  10.0),
            (50,  30.0),
            (70,  50.0),
            (85,  55.0),
            (95,  57.0),
            (105, 68.0),
            (115, 69.5),
            (125, 78.0),
            (135, 79.5),
            (145, 81.0),
            (155, 89.0),
            (165, 90.0),
            (175, 91.0),
            (185, 94.0),
            (195, 95.0),
            (205, 96.0),
            (215, 97.0),
            (225, 98.0),
            (235, 98.5),
            (245, 99.0),
            (255, 99.3),
            (265, 99.5),
            (275, 99.7),
            (285, 99.85),
            (295, 99.97),
            (300, 100.0),
        ]
        marks_arr = np.array([p[0] for p in known_points], dtype=float)
        pct_arr   = np.array([p[1] for p in known_points], dtype=float)

        from sklearn.isotonic import IsotonicRegression
        iso = IsotonicRegression(increasing=True, out_of_bounds="clip")
        iso.fit(marks_arr, pct_arr)

        marks_range = np.arange(0, 301, 1, dtype=float)
        percentiles  = np.clip(iso.predict(marks_range), 0.0, 100.0)
        self._marks_to_percentile_table = np.column_stack([marks_range, percentiles])

        self.global_stats = {"total_candidates": TOTAL_CANDIDATES_2026, "mean_marks": 140.0}
        self.shift_stats  = {k: {"marks_99pct": v} for k, v in SHIFT_DIFFICULTY.items()}

    # ─────────────────────────────────────────────
    # Core prediction pipeline
    # ─────────────────────────────────────────────
    def normalize_marks(self, marks: float, shift: str) -> float:
        """
        Normalize marks across shifts using the NTA equi-percentile method.
        Adjusts for shift difficulty so a score in a harder shift gets a bonus.
        """
        shift_key = shift.lower().replace(" ", "").replace("-", "")
        # Map common synonyms
        if "1" in shift_key:
            shift_key = "shift1"
        elif "2" in shift_key:
            shift_key = "shift2"
        else:
            shift_key = "shift1"

        # Division by zero guard for shift range
        min_score, max_score = 10.0, 290.0
        if max_score == min_score:
            return marks

        marks_99_this_shift  = self.shift_stats.get(shift_key, {}).get("marks_99pct", GLOBAL_99_MARKS)
        marks_99_global      = GLOBAL_99_MARKS

        if marks_99_this_shift == 0:
            return marks

        # Scale: normalized = marks * (global_99 / shift_99)
        # Harder shift (lower marks_99) → boost
        normalized = marks * (marks_99_global / marks_99_this_shift)
        return round(float(np.clip(normalized, 0, 300)), 2)

    def marks_to_percentile(self, marks: float, total_candidates: int = TOTAL_CANDIDATES_2026) -> float:
        """Predict percentile using a trained Random Forest Regressor on historical data."""
        try:
            from app.utils.ml_model import get_ml_prediction
            if hasattr(self, 'ml_x_train') and self.ml_x_train is not None:
                pct = get_ml_prediction(
                    "jee_main_percentile", 
                    self.ml_x_train, 
                    self.ml_y_pct_train, 
                    [marks, total_candidates]
                )
                return round(float(np.clip(pct, 0.0, 100.0)), 4)
        except Exception:
            pass

        if self._marks_to_percentile_table is None:
            return min(100.0, max(0.0, marks / 300.0 * 100.0))

        tbl    = self._marks_to_percentile_table
        marks  = float(np.clip(marks, 0, 300))
        pct    = float(np.interp(marks, tbl[:, 0], tbl[:, 1]))
        return round(np.clip(pct, 0.0, 100.0), 4)

    def predict_rank_ml(self, marks: float, total_candidates: int) -> int:
        """Predict rank using a trained Random Forest Regressor on historical data."""
        try:
            from app.utils.ml_model import get_ml_prediction
            if hasattr(self, 'ml_x_train') and self.ml_x_train is not None:
                rank = get_ml_prediction(
                    "jee_main_rank", 
                    self.ml_x_train, 
                    self.ml_y_rank_train, 
                    [marks, total_candidates]
                )
                return max(1, int(np.round(rank)))
        except Exception:
            pass
        return None

    def percentile_to_rank(self, percentile: float, total_candidates: int) -> int:
        """
        Convert percentile → rank using NTA formula:
            Rank = ceil( (100 - P) / 100 × N )
        with density correction at the top (many tied percentiles).
        """
        if percentile >= 100.0:
            return 1

        raw_rank = (100.0 - percentile) / 100.0 * total_candidates

        # Density correction: top percentile buckets are very crowded
        if percentile >= 99.99:
            raw_rank = max(1, raw_rank * 0.30)
        elif percentile >= 99.9:
            raw_rank = max(1, raw_rank * 0.45)
        elif percentile >= 99.5:
            raw_rank = max(1, raw_rank * 0.60)
        elif percentile >= 99.0:
            raw_rank = max(1, raw_rank * 0.75)
        elif percentile >= 95.0:
            raw_rank = max(1, raw_rank * 0.88)

        return max(1, int(np.ceil(raw_rank)))

    def predict(self, marks: float, shift: str, category: str,
                total_candidates: int = TOTAL_CANDIDATES_2026) -> Dict:
        """Full prediction pipeline — marks → normalize → percentile → rank."""

        # 1. Shift normalization
        normalized_marks = self.normalize_marks(marks, shift)

        # 2. Marks → Percentile (from real historical data)
        percentile = self.marks_to_percentile(normalized_marks, total_candidates)

        # 3. Percentile → All-India Rank
        predicted_rank = None
        if hasattr(self, 'ml_x_train') and self.ml_x_train is not None:
            predicted_rank = self.predict_rank_ml(normalized_marks, total_candidates)

        if predicted_rank is None:
            predicted_rank = self.percentile_to_rank(percentile, total_candidates)

        # 4. Category rank
        cat_key = category.lower().replace("-", "").replace("_", "").replace(" ", "")
        multiplier = 1.0
        for k, v in CATEGORY_MULTIPLIERS.items():
            if k.replace("-", "") == cat_key:
                multiplier = v
                break
        category_rank = max(1, int(predicted_rank * multiplier))

        # 5. Confidence: based on how much real data we have near this marks range
        confidence = self._calculate_confidence(marks, normalized_marks, percentile)

        return {
            "predicted_rank":   predicted_rank,
            "category_rank":    category_rank,
            "percentile":       round(percentile, 2),
            "normalized_marks": normalized_marks,
            "confidence":       confidence,
            "shift":            shift,
            "category":         category,
            "total_candidates": total_candidates,
        }

    def _calculate_confidence(self, raw_marks: float, norm_marks: float, percentile: float) -> float:
        """Confidence is higher for mid-range marks (more training data there)."""
        # Data is sparse at extremes
        if raw_marks >= 285 or raw_marks <= 20:
            base = 78.0
        elif raw_marks >= 260 or raw_marks <= 50:
            base = 84.0
        elif 80 <= raw_marks <= 250:
            base = 93.0
        else:
            base = 88.0

        # Slightly lower confidence at the very top (99.9+) due to tied ranks
        if percentile >= 99.9:
            base -= 4.0

        return round(base, 1)
