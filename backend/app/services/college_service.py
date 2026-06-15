"""
Universal College Prediction Service
Reads real CSV cutoff data and predicts admission chances based on rank + category.
Supports: JEE Main (NITs/IIITs/GFTIs), JEE Advanced (IITs), NEET, KCET, MHT-CET, COMEDK.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
from functools import lru_cache


# ──────────────────────────────────────────────────────────────────────────────
# PLACEMENT & FEES DATABASE (sourced from NIRF 2024, official placement reports)
# Keys are normalised lowercase college name fragments for fuzzy matching.
# fees_lpa  = total 4-year B.Tech course fee in LPA (Lakhs)
# avg_lpa   = average placement package in LPA (college-wide)
# high_lpa  = highest domestic package in LPA
# roi       = avg_lpa / fees_lpa  (computed on access)
# ──────────────────────────────────────────────────────────────────────────────
PLACEMENT_DB: Dict[str, Dict] = {
    # ── IITs ──────────────────────────────────────────────────────────────────
    "iit bombay": {
        "fees_lpa": 10.0, "avg_lpa": 23.5, "high_lpa": 170.0,
        "top_recruiters": ["Google", "Microsoft", "Goldman Sachs", "Uber", "Apple", "Amazon", "DE Shaw", "Tower Research"],
        "hostel": True, "campus_acres": 550, "student_faculty_ratio": 11,
        "location": "Mumbai, Maharashtra", "coding_culture": 5,
        "specialization": "Strong in CS, Finance, Core Engg, Research",
    },
    "iit delhi": {
        "fees_lpa": 8.5, "avg_lpa": 27.0, "high_lpa": 170.0,
        "top_recruiters": ["Google", "Microsoft", "Amazon", "McKinsey", "Bain", "Samsung Research", "NVIDIA"],
        "hostel": True, "campus_acres": 325, "student_faculty_ratio": 10,
        "location": "New Delhi, Delhi", "coding_culture": 5,
        "specialization": "CS, Electrical, Chemical, Management",
    },
    "iit madras": {
        "fees_lpa": 9.4, "avg_lpa": 24.2, "high_lpa": 150.0,
        "top_recruiters": ["Google", "Microsoft", "Qualcomm", "Texas Instruments", "Goldman Sachs", "Amazon"],
        "hostel": True, "campus_acres": 617, "student_faculty_ratio": 11,
        "location": "Chennai, Tamil Nadu", "coding_culture": 5,
        "specialization": "Exceptional in CS, Electrical, Ocean Engg, Research",
    },
    "iit kharagpur": {
        "fees_lpa": 10.0, "avg_lpa": 20.5, "high_lpa": 260.0,
        "top_recruiters": ["Google", "Microsoft", "Amazon", "McKinsey", "ISRO", "BARC", "Samsung"],
        "hostel": True, "campus_acres": 2100, "student_faculty_ratio": 13,
        "location": "Kharagpur, West Bengal", "coding_culture": 5,
        "specialization": "Largest IIT; Strong Core Engg, Management (VGSoM), Law",
    },
    "iit kanpur": {
        "fees_lpa": 9.0, "avg_lpa": 26.0, "high_lpa": 200.0,
        "top_recruiters": ["Google", "Microsoft", "NVIDIA", "Qualcomm", "D.E. Shaw", "Goldman Sachs"],
        "hostel": True, "campus_acres": 1055, "student_faculty_ratio": 11,
        "location": "Kanpur, Uttar Pradesh", "coding_culture": 5,
        "specialization": "CS, Physics, Math, Aerospace, Research Culture",
    },
    "iit roorkee": {
        "fees_lpa": 8.5, "avg_lpa": 21.0, "high_lpa": 140.0,
        "top_recruiters": ["Google", "Amazon", "Microsoft", "Samsung", "BHEL", "ONGC", "Deloitte"],
        "hostel": True, "campus_acres": 365, "student_faculty_ratio": 13,
        "location": "Roorkee, Uttarakhand", "coding_culture": 4,
        "specialization": "Oldest tech institute; Civil, EE, CS, Earthquake Engg",
    },
    "iit guwahati": {
        "fees_lpa": 8.0, "avg_lpa": 18.5, "high_lpa": 80.0,
        "top_recruiters": ["Amazon", "Microsoft", "TCS", "Infosys", "Samsung", "Qualcomm", "DRDO"],
        "hostel": True, "campus_acres": 704, "student_faculty_ratio": 14,
        "location": "Guwahati, Assam", "coding_culture": 4,
        "specialization": "CS, Biotechnology, Design, Electronics",
    },
    "iit hyderabad": {
        "fees_lpa": 8.0, "avg_lpa": 22.0, "high_lpa": 120.0,
        "top_recruiters": ["Google", "Microsoft", "Amazon", "Samsung", "Qualcomm", "TCS Research"],
        "hostel": True, "campus_acres": 576, "student_faculty_ratio": 12,
        "location": "Sangareddy, Telangana", "coding_culture": 5,
        "specialization": "Strong AI/ML, CS, Material Science, New IIT",
    },
    "iit bhubaneswar": {
        "fees_lpa": 8.0, "avg_lpa": 14.0, "high_lpa": 50.0,
        "top_recruiters": ["TCS", "Infosys", "Wipro", "Amazon", "Microsoft"],
        "hostel": True, "campus_acres": 936, "student_faculty_ratio": 14,
        "location": "Bhubaneswar, Odisha", "coding_culture": 3,
        "specialization": "CS, Earth Science, Civil, Electrical",
    },
    "iit gandhinagar": {
        "fees_lpa": 8.0, "avg_lpa": 18.0, "high_lpa": 70.0,
        "top_recruiters": ["Google", "Amazon", "Samsung", "DRDO", "ISRO"],
        "hostel": True, "campus_acres": 400, "student_faculty_ratio": 11,
        "location": "Gandhinagar, Gujarat", "coding_culture": 4,
        "specialization": "Interdisciplinary, Liberal Arts + Tech, CS",
    },
    "iit indore": {
        "fees_lpa": 8.0, "avg_lpa": 17.0, "high_lpa": 65.0,
        "top_recruiters": ["Amazon", "Microsoft", "TCS", "Samsung", "Intel"],
        "hostel": True, "campus_acres": 510, "student_faculty_ratio": 13,
        "location": "Indore, Madhya Pradesh", "coding_culture": 4,
        "specialization": "CS, Electrical, Physics, Astronomy",
    },
    "iit jodhpur": {
        "fees_lpa": 8.0, "avg_lpa": 14.5, "high_lpa": 55.0,
        "top_recruiters": ["TCS", "Infosys", "Amazon", "Wipro", "Samsung"],
        "hostel": True, "campus_acres": 852, "student_faculty_ratio": 14,
        "location": "Jodhpur, Rajasthan", "coding_culture": 3,
        "specialization": "CS, Electrical, Mechanical, Cyber Security",
    },
    "iit mandi": {
        "fees_lpa": 8.0, "avg_lpa": 14.0, "high_lpa": 50.0,
        "top_recruiters": ["TCS", "Wipro", "Amazon", "Samsung", "HCL"],
        "hostel": True, "campus_acres": 529, "student_faculty_ratio": 13,
        "location": "Mandi, Himachal Pradesh", "coding_culture": 3,
        "specialization": "Energy, CS, Civil, Design Thinking",
    },
    "iit patna": {
        "fees_lpa": 8.0, "avg_lpa": 15.0, "high_lpa": 60.0,
        "top_recruiters": ["Amazon", "TCS", "Microsoft", "Flipkart", "Samsung"],
        "hostel": True, "campus_acres": 501, "student_faculty_ratio": 13,
        "location": "Patna, Bihar", "coding_culture": 3,
        "specialization": "CS, Electrical, Mechanical, Chemistry",
    },
    "iit ropar": {
        "fees_lpa": 8.0, "avg_lpa": 14.5, "high_lpa": 55.0,
        "top_recruiters": ["TCS", "Infosys", "Amazon", "HCL", "Samsung"],
        "hostel": True, "campus_acres": 501, "student_faculty_ratio": 14,
        "location": "Ropar, Punjab", "coding_culture": 3,
        "specialization": "CS, Biomedical, Electrical, Chemical",
    },
    "iit tirupati": {
        "fees_lpa": 8.0, "avg_lpa": 13.5, "high_lpa": 45.0,
        "top_recruiters": ["TCS", "Wipro", "Amazon", "Infosys"],
        "hostel": True, "campus_acres": 580, "student_faculty_ratio": 14,
        "location": "Tirupati, Andhra Pradesh", "coding_culture": 3,
        "specialization": "CS, Electrical, Mechanical, Civil",
    },
    "iit dharwad": {
        "fees_lpa": 8.0, "avg_lpa": 13.0, "high_lpa": 42.0,
        "top_recruiters": ["TCS", "Wipro", "Amazon", "Infosys"],
        "hostel": True, "campus_acres": 470, "student_faculty_ratio": 14,
        "location": "Dharwad, Karnataka", "coding_culture": 3,
        "specialization": "CS, Electrical, Mechanical",
    },
    "iit palakkad": {
        "fees_lpa": 8.0, "avg_lpa": 13.0, "high_lpa": 40.0,
        "top_recruiters": ["TCS", "Wipro", "Infosys", "Amazon"],
        "hostel": True, "campus_acres": 534, "student_faculty_ratio": 14,
        "location": "Palakkad, Kerala", "coding_culture": 3,
        "specialization": "CS, Electrical, Mechanical, Physics",
    },
    # ── NITs ──────────────────────────────────────────────────────────────────
    "nit trichy": {
        "fees_lpa": 1.5, "avg_lpa": 22.0, "high_lpa": 88.0,
        "top_recruiters": ["Google", "Microsoft", "Amazon", "Texas Instruments", "Qualcomm", "Goldman Sachs", "JP Morgan"],
        "hostel": True, "campus_acres": 800, "student_faculty_ratio": 20,
        "location": "Tiruchirappalli, Tamil Nadu", "coding_culture": 5,
        "specialization": "Best NIT overall; strong CS, ECE, Mechanical placements",
    },
    "national institute of technology tiruchirappalli": {
        "fees_lpa": 1.5, "avg_lpa": 22.0, "high_lpa": 88.0,
        "top_recruiters": ["Google", "Microsoft", "Amazon", "Texas Instruments", "Qualcomm", "Goldman Sachs"],
        "hostel": True, "campus_acres": 800, "student_faculty_ratio": 20,
        "location": "Tiruchirappalli, Tamil Nadu", "coding_culture": 5,
        "specialization": "Best NIT overall; strong CS, ECE, Mechanical placements",
    },
    "nit warangal": {
        "fees_lpa": 1.5, "avg_lpa": 15.6, "high_lpa": 88.0,
        "top_recruiters": ["Google", "Microsoft", "Amazon", "Qualcomm", "Samsung", "JP Morgan"],
        "hostel": True, "campus_acres": 475, "student_faculty_ratio": 18,
        "location": "Warangal, Telangana", "coding_culture": 5,
        "specialization": "Strong CS, ECE; Excellent alumni network in tech industry",
    },
    "national institute of technology warangal": {
        "fees_lpa": 1.5, "avg_lpa": 15.6, "high_lpa": 88.0,
        "top_recruiters": ["Google", "Microsoft", "Amazon", "Qualcomm", "Samsung"],
        "hostel": True, "campus_acres": 475, "student_faculty_ratio": 18,
        "location": "Warangal, Telangana", "coding_culture": 5,
        "specialization": "Strong CS, ECE; Excellent alumni network in tech industry",
    },
    "nit surathkal": {
        "fees_lpa": 1.5, "avg_lpa": 16.25, "high_lpa": 75.0,
        "top_recruiters": ["Amazon", "Microsoft", "Google", "Flipkart", "Samsung", "Texas Instruments"],
        "hostel": True, "campus_acres": 295, "student_faculty_ratio": 19,
        "location": "Mangaluru, Karnataka", "coding_culture": 5,
        "specialization": "CS, ECE, Chemical Engg; Coastal campus",
    },
    "national institute of technology karnataka": {
        "fees_lpa": 1.5, "avg_lpa": 16.25, "high_lpa": 75.0,
        "top_recruiters": ["Amazon", "Microsoft", "Google", "Flipkart", "Samsung"],
        "hostel": True, "campus_acres": 295, "student_faculty_ratio": 19,
        "location": "Mangaluru, Karnataka", "coding_culture": 5,
        "specialization": "CS, ECE, Chemical Engg; Coastal campus",
    },
    "nit calicut": {
        "fees_lpa": 1.4, "avg_lpa": 12.4, "high_lpa": 65.0,
        "top_recruiters": ["Amazon", "Infosys", "Wipro", "TCS", "Qualcomm", "UST Global"],
        "hostel": True, "campus_acres": 300, "student_faculty_ratio": 20,
        "location": "Kozhikode, Kerala", "coding_culture": 4,
        "specialization": "CS, ECE, Civil, Architecture; Strong Kerala campus culture",
    },
    "national institute of technology calicut": {
        "fees_lpa": 1.4, "avg_lpa": 12.4, "high_lpa": 65.0,
        "top_recruiters": ["Amazon", "Infosys", "Wipro", "TCS", "Qualcomm"],
        "hostel": True, "campus_acres": 300, "student_faculty_ratio": 20,
        "location": "Kozhikode, Kerala", "coding_culture": 4,
        "specialization": "CS, ECE, Civil, Architecture",
    },
    "nit rourkela": {
        "fees_lpa": 1.4, "avg_lpa": 12.0, "high_lpa": 60.0,
        "top_recruiters": ["TCS", "Infosys", "Amazon", "Wipro", "Samsung", "SAIL"],
        "hostel": True, "campus_acres": 636, "student_faculty_ratio": 20,
        "location": "Rourkela, Odisha", "coding_culture": 4,
        "specialization": "Metallurgy, CS, ECE; Mining & Steel industry ties",
    },
    "national institute of technology rourkela": {
        "fees_lpa": 1.4, "avg_lpa": 12.0, "high_lpa": 60.0,
        "top_recruiters": ["TCS", "Infosys", "Amazon", "Wipro", "Samsung"],
        "hostel": True, "campus_acres": 636, "student_faculty_ratio": 20,
        "location": "Rourkela, Odisha", "coding_culture": 4,
        "specialization": "Metallurgy, CS, ECE",
    },
    "nit allahabad": {
        "fees_lpa": 1.4, "avg_lpa": 11.0, "high_lpa": 55.0,
        "top_recruiters": ["TCS", "Infosys", "Amazon", "HCL", "Cognizant"],
        "hostel": True, "campus_acres": 222, "student_faculty_ratio": 21,
        "location": "Prayagraj, Uttar Pradesh", "coding_culture": 4,
        "specialization": "CS, ECE, Civil; Oldest MNNIT",
    },
    "motilal nehru national institute of technology": {
        "fees_lpa": 1.4, "avg_lpa": 11.0, "high_lpa": 55.0,
        "top_recruiters": ["TCS", "Infosys", "Amazon", "HCL", "Cognizant"],
        "hostel": True, "campus_acres": 222, "student_faculty_ratio": 21,
        "location": "Prayagraj, Uttar Pradesh", "coding_culture": 4,
        "specialization": "CS, ECE, Civil; Oldest MNNIT",
    },
    "nit jaipur": {
        "fees_lpa": 1.4, "avg_lpa": 10.5, "high_lpa": 50.0,
        "top_recruiters": ["TCS", "Infosys", "Wipro", "Amazon", "HCL"],
        "hostel": True, "campus_acres": 325, "student_faculty_ratio": 21,
        "location": "Jaipur, Rajasthan", "coding_culture": 4,
        "specialization": "CS, ECE, Mechanical; Smart City proximity",
    },
    "malaviya national institute of technology": {
        "fees_lpa": 1.4, "avg_lpa": 10.5, "high_lpa": 50.0,
        "top_recruiters": ["TCS", "Infosys", "Wipro", "Amazon", "HCL"],
        "hostel": True, "campus_acres": 325, "student_faculty_ratio": 21,
        "location": "Jaipur, Rajasthan", "coding_culture": 4,
        "specialization": "CS, ECE, Mechanical; Smart City proximity",
    },
    "nit nagpur": {
        "fees_lpa": 1.4, "avg_lpa": 10.0, "high_lpa": 45.0,
        "top_recruiters": ["TCS", "Infosys", "Wipro", "Amazon", "Bajaj"],
        "hostel": True, "campus_acres": 240, "student_faculty_ratio": 21,
        "location": "Nagpur, Maharashtra", "coding_culture": 4,
        "specialization": "Mining, CS, ECE, Mechanical",
    },
    "visvesvaraya national institute of technology": {
        "fees_lpa": 1.4, "avg_lpa": 10.0, "high_lpa": 45.0,
        "top_recruiters": ["TCS", "Infosys", "Wipro", "Amazon", "Bajaj"],
        "hostel": True, "campus_acres": 240, "student_faculty_ratio": 21,
        "location": "Nagpur, Maharashtra", "coding_culture": 4,
        "specialization": "Mining, CS, ECE, Mechanical",
    },
    "nit surat": {
        "fees_lpa": 1.4, "avg_lpa": 10.0, "high_lpa": 44.0,
        "top_recruiters": ["TCS", "Infosys", "Amazon", "Adani", "Reliance"],
        "hostel": True, "campus_acres": 280, "student_faculty_ratio": 21,
        "location": "Surat, Gujarat", "coding_culture": 3,
        "specialization": "CS, ECE, Textile, Chemical",
    },
    "sardar vallabhbhai national institute of technology": {
        "fees_lpa": 1.4, "avg_lpa": 10.0, "high_lpa": 44.0,
        "top_recruiters": ["TCS", "Infosys", "Amazon", "Adani"],
        "hostel": True, "campus_acres": 280, "student_faculty_ratio": 21,
        "location": "Surat, Gujarat", "coding_culture": 3,
        "specialization": "CS, ECE, Textile, Chemical",
    },
    "nit kurukshetra": {
        "fees_lpa": 1.4, "avg_lpa": 9.5, "high_lpa": 42.0,
        "top_recruiters": ["TCS", "Infosys", "HCL", "Amazon", "Wipro"],
        "hostel": True, "campus_acres": 300, "student_faculty_ratio": 22,
        "location": "Kurukshetra, Haryana", "coding_culture": 3,
        "specialization": "CS, ECE, Civil, Mechanical",
    },
    "nit silchar": {
        "fees_lpa": 1.4, "avg_lpa": 8.5, "high_lpa": 38.0,
        "top_recruiters": ["TCS", "Infosys", "Wipro", "HCL"],
        "hostel": True, "campus_acres": 330, "student_faculty_ratio": 22,
        "location": "Silchar, Assam", "coding_culture": 3,
        "specialization": "CS, ECE, Civil; Northeast India hub",
    },
    "nit hamirpur": {
        "fees_lpa": 1.3, "avg_lpa": 8.0, "high_lpa": 35.0,
        "top_recruiters": ["TCS", "Infosys", "HCL", "Wipro"],
        "hostel": True, "campus_acres": 440, "student_faculty_ratio": 22,
        "location": "Hamirpur, Himachal Pradesh", "coding_culture": 3,
        "specialization": "CS, ECE, Civil, Electrical",
    },
    # ── IIITs ─────────────────────────────────────────────────────────────────
    "iiit hyderabad": {
        "fees_lpa": 3.5, "avg_lpa": 36.0, "high_lpa": 180.0,
        "top_recruiters": ["Google", "Microsoft", "Amazon", "Apple", "Meta", "Adobe", "Qualcomm", "Goldman Sachs"],
        "hostel": True, "campus_acres": 66, "student_faculty_ratio": 8,
        "location": "Hyderabad, Telangana", "coding_culture": 5,
        "specialization": "Research-focused; Best IIIT; Exceptional CS/AI/ML placements; ACM ICPC strong",
    },
    "international institute of information technology hyderabad": {
        "fees_lpa": 3.5, "avg_lpa": 36.0, "high_lpa": 180.0,
        "top_recruiters": ["Google", "Microsoft", "Amazon", "Apple", "Meta", "Adobe"],
        "hostel": True, "campus_acres": 66, "student_faculty_ratio": 8,
        "location": "Hyderabad, Telangana", "coding_culture": 5,
        "specialization": "Research-focused; Best IIIT; Exceptional CS/AI/ML placements",
    },
    "iiit bangalore": {
        "fees_lpa": 7.5, "avg_lpa": 28.0, "high_lpa": 120.0,
        "top_recruiters": ["Google", "Microsoft", "Amazon", "Adobe", "Flipkart", "Cisco", "Intel", "Oracle"],
        "hostel": True, "campus_acres": 5, "student_faculty_ratio": 10,
        "location": "Bangalore, Karnataka", "coding_culture": 5,
        "specialization": "Silicon Valley of India; iMTech only; 100% placements; Industry-linked research",
    },
    "international institute of information technology bangalore": {
        "fees_lpa": 7.5, "avg_lpa": 28.0, "high_lpa": 120.0,
        "top_recruiters": ["Google", "Microsoft", "Amazon", "Adobe", "Flipkart"],
        "hostel": True, "campus_acres": 5, "student_faculty_ratio": 10,
        "location": "Bangalore, Karnataka", "coding_culture": 5,
        "specialization": "Silicon Valley of India; 100% placements",
    },
    "iiit allahabad": {
        "fees_lpa": 2.5, "avg_lpa": 18.0, "high_lpa": 90.0,
        "top_recruiters": ["Amazon", "Microsoft", "Flipkart", "Samsung", "Adobe", "PayPal"],
        "hostel": True, "campus_acres": 100, "student_faculty_ratio": 15,
        "location": "Prayagraj, Uttar Pradesh", "coding_culture": 5,
        "specialization": "CS, IT; Excellent competitive programming culture",
    },
    "indian institute of information technology allahabad": {
        "fees_lpa": 2.5, "avg_lpa": 18.0, "high_lpa": 90.0,
        "top_recruiters": ["Amazon", "Microsoft", "Flipkart", "Samsung", "Adobe"],
        "hostel": True, "campus_acres": 100, "student_faculty_ratio": 15,
        "location": "Prayagraj, Uttar Pradesh", "coding_culture": 5,
        "specialization": "CS, IT; Competitive programming culture",
    },
    "iiit gwalior": {
        "fees_lpa": 2.5, "avg_lpa": 16.0, "high_lpa": 80.0,
        "top_recruiters": ["Amazon", "Microsoft", "Flipkart", "Adobe", "Samsung"],
        "hostel": True, "campus_acres": 122, "student_faculty_ratio": 15,
        "location": "Gwalior, Madhya Pradesh", "coding_culture": 5,
        "specialization": "CS, IT, Mathematics; Top coding culture in India",
    },
    "atal bihari vajpayee indian institute of information technology": {
        "fees_lpa": 2.5, "avg_lpa": 16.0, "high_lpa": 80.0,
        "top_recruiters": ["Amazon", "Microsoft", "Flipkart", "Adobe", "Samsung"],
        "hostel": True, "campus_acres": 122, "student_faculty_ratio": 15,
        "location": "Gwalior, Madhya Pradesh", "coding_culture": 5,
        "specialization": "CS, IT, Mathematics",
    },
    "iiit design manufacturing kancheepuram": {
        "fees_lpa": 2.0, "avg_lpa": 12.0, "high_lpa": 55.0,
        "top_recruiters": ["TCS", "Infosys", "Wipro", "Amazon", "TVS Motors"],
        "hostel": True, "campus_acres": 90, "student_faculty_ratio": 16,
        "location": "Chennai, Tamil Nadu", "coding_culture": 3,
        "specialization": "Design & Manufacturing; CSE, ECE, Mechanical Design",
    },
    # ── GFTIs / Others ───────────────────────────────────────────────────────
    "dtu delhi": {
        "fees_lpa": 0.8, "avg_lpa": 12.0, "high_lpa": 75.0,
        "top_recruiters": ["Amazon", "Microsoft", "Google", "Samsung", "Flipkart", "Deloitte"],
        "hostel": True, "campus_acres": 164, "student_faculty_ratio": 18,
        "location": "Delhi", "coding_culture": 4,
        "specialization": "CS, ECE, Mechanical; Delhi advantage for placements; Strong alumni",
    },
    "delhi technological university": {
        "fees_lpa": 0.8, "avg_lpa": 12.0, "high_lpa": 75.0,
        "top_recruiters": ["Amazon", "Microsoft", "Google", "Samsung", "Flipkart"],
        "hostel": True, "campus_acres": 164, "student_faculty_ratio": 18,
        "location": "Delhi", "coding_culture": 4,
        "specialization": "CS, ECE, Mechanical; Delhi advantage for placements",
    },
    "nsut": {
        "fees_lpa": 0.8, "avg_lpa": 10.0, "high_lpa": 60.0,
        "top_recruiters": ["Amazon", "Microsoft", "Accenture", "Samsung", "TCS"],
        "hostel": True, "campus_acres": 145, "student_faculty_ratio": 19,
        "location": "Delhi", "coding_culture": 4,
        "specialization": "CS, ECE, Mechanical; Growing placements",
    },
    "netaji subhas university of technology": {
        "fees_lpa": 0.8, "avg_lpa": 10.0, "high_lpa": 60.0,
        "top_recruiters": ["Amazon", "Microsoft", "Accenture", "Samsung"],
        "hostel": True, "campus_acres": 145, "student_faculty_ratio": 19,
        "location": "Delhi", "coding_culture": 4,
        "specialization": "CS, ECE, Mechanical",
    },
    "iiest shibpur": {
        "fees_lpa": 0.5, "avg_lpa": 8.0, "high_lpa": 35.0,
        "top_recruiters": ["TCS", "Infosys", "Wipro", "L&T", "Amazon"],
        "hostel": True, "campus_acres": 70, "student_faculty_ratio": 20,
        "location": "Howrah, West Bengal", "coding_culture": 3,
        "specialization": "Oldest engineering college in Asia; Civil, Mechanical, CS",
    },
    "indian institute of engineering science and technology": {
        "fees_lpa": 0.5, "avg_lpa": 8.0, "high_lpa": 35.0,
        "top_recruiters": ["TCS", "Infosys", "Wipro", "L&T"],
        "hostel": True, "campus_acres": 70, "student_faculty_ratio": 20,
        "location": "Howrah, West Bengal", "coding_culture": 3,
        "specialization": "Oldest engineering college in Asia",
    },
    # ── Medical ───────────────────────────────────────────────────────────────
    "aiims delhi": {
        "fees_lpa": 0.01, "avg_lpa": 15.0, "high_lpa": 30.0,
        "top_recruiters": ["Govt Hospitals", "AIIMS PG", "Apollo", "Fortis", "Max Healthcare", "WHO", "ICMR"],
        "hostel": True, "campus_acres": 135, "student_faculty_ratio": 4,
        "location": "New Delhi, Delhi", "coding_culture": 1,
        "specialization": "World-class research hospital; MBBS fees ~₹1,628/year; Best PG scope",
    },
    "all india institute of medical sciences": {
        "fees_lpa": 0.01, "avg_lpa": 15.0, "high_lpa": 30.0,
        "top_recruiters": ["Govt Hospitals", "AIIMS PG", "Apollo", "Fortis", "Max Healthcare"],
        "hostel": True, "campus_acres": 135, "student_faculty_ratio": 4,
        "location": "New Delhi, Delhi", "coding_culture": 1,
        "specialization": "World-class research hospital; Best PG scope",
    },
    "jipmer": {
        "fees_lpa": 0.01, "avg_lpa": 12.0, "high_lpa": 25.0,
        "top_recruiters": ["Govt Hospitals", "JIPMER PG", "Apollo", "Fortis", "Global Hospitals"],
        "hostel": True, "campus_acres": 195, "student_faculty_ratio": 5,
        "location": "Puducherry", "coding_culture": 1,
        "specialization": "Premier medical research institute; Excellent PG programs; Coastal campus",
    },
    "jawaharlal institute of postgraduate medical education": {
        "fees_lpa": 0.01, "avg_lpa": 12.0, "high_lpa": 25.0,
        "top_recruiters": ["Govt Hospitals", "JIPMER PG", "Apollo", "Fortis"],
        "hostel": True, "campus_acres": 195, "student_faculty_ratio": 5,
        "location": "Puducherry", "coding_culture": 1,
        "specialization": "Premier medical research institute",
    },
    "aiims bhopal": {
        "fees_lpa": 0.01, "avg_lpa": 12.0, "high_lpa": 25.0,
        "top_recruiters": ["Govt Hospitals", "AIIMS PG", "State Govt Hospitals"],
        "hostel": True, "campus_acres": 209, "student_faculty_ratio": 5,
        "location": "Bhopal, Madhya Pradesh", "coding_culture": 1,
        "specialization": "New AIIMS; MBBS, MD/MS PG programs",
    },
    "aiims jodhpur": {
        "fees_lpa": 0.01, "avg_lpa": 12.0, "high_lpa": 25.0,
        "top_recruiters": ["Govt Hospitals", "AIIMS PG", "State Govt Hospitals"],
        "hostel": True, "campus_acres": 225, "student_faculty_ratio": 5,
        "location": "Jodhpur, Rajasthan", "coding_culture": 1,
        "specialization": "New AIIMS; MBBS, MD/MS PG programs; Rajasthan region",
    },
    "aiims rishikesh": {
        "fees_lpa": 0.01, "avg_lpa": 12.0, "high_lpa": 25.0,
        "top_recruiters": ["Govt Hospitals", "AIIMS PG", "Apollo Hospitals"],
        "hostel": True, "campus_acres": 170, "student_faculty_ratio": 5,
        "location": "Rishikesh, Uttarakhand", "coding_culture": 1,
        "specialization": "MBBS; Scenic Himalayan location",
    },
    "aiims nagpur": {
        "fees_lpa": 0.01, "avg_lpa": 12.0, "high_lpa": 25.0,
        "top_recruiters": ["Govt Hospitals", "AIIMS PG", "State Hospitals"],
        "hostel": True, "campus_acres": 200, "student_faculty_ratio": 5,
        "location": "Nagpur, Maharashtra", "coding_culture": 1,
        "specialization": "MBBS; Central India healthcare hub",
    },
    # ── KCET / State ──────────────────────────────────────────────────────────
    "rvce": {
        "fees_lpa": 1.8, "avg_lpa": 11.0, "high_lpa": 55.0,
        "top_recruiters": ["Amazon", "Microsoft", "Infosys", "Wipro", "Accenture", "VMware"],
        "hostel": True, "campus_acres": 16, "student_faculty_ratio": 18,
        "location": "Bangalore, Karnataka", "coding_culture": 4,
        "specialization": "Top private Karnataka college; CS, ECE; Bangalore location advantage",
    },
    "r v college of engineering": {
        "fees_lpa": 1.8, "avg_lpa": 11.0, "high_lpa": 55.0,
        "top_recruiters": ["Amazon", "Microsoft", "Infosys", "Wipro", "Accenture"],
        "hostel": True, "campus_acres": 16, "student_faculty_ratio": 18,
        "location": "Bangalore, Karnataka", "coding_culture": 4,
        "specialization": "Top private Karnataka college; Bangalore location advantage",
    },
    "bms college": {
        "fees_lpa": 1.6, "avg_lpa": 9.0, "high_lpa": 45.0,
        "top_recruiters": ["Infosys", "Wipro", "TCS", "Amazon", "Accenture"],
        "hostel": True, "campus_acres": 22, "student_faculty_ratio": 19,
        "location": "Bangalore, Karnataka", "coding_culture": 3,
        "specialization": "CS, ECE, Mechanical; Bangalore campus",
    },
    "pes university": {
        "fees_lpa": 3.5, "avg_lpa": 12.0, "high_lpa": 60.0,
        "top_recruiters": ["Amazon", "Microsoft", "Google", "Flipkart", "Samsung"],
        "hostel": True, "campus_acres": 25, "student_faculty_ratio": 17,
        "location": "Bangalore, Karnataka", "coding_culture": 4,
        "specialization": "Premium private; CS, ECE; Very strong Bangalore tech network",
    },
    "ms ramaiah institute": {
        "fees_lpa": 2.0, "avg_lpa": 10.0, "high_lpa": 48.0,
        "top_recruiters": ["Infosys", "Wipro", "TCS", "Amazon", "Bosch"],
        "hostel": True, "campus_acres": 15, "student_faculty_ratio": 18,
        "location": "Bangalore, Karnataka", "coding_culture": 3,
        "specialization": "CS, ECE, Mechanical, Medical; Established Bangalore college",
    },
    # ── COMEDK ─────────────────────────────────────────────────────────────────
    "christ university": {
        "fees_lpa": 2.5, "avg_lpa": 8.5, "high_lpa": 40.0,
        "top_recruiters": ["Infosys", "Wipro", "TCS", "Amazon", "Capgemini"],
        "hostel": True, "campus_acres": 50, "student_faculty_ratio": 20,
        "location": "Bangalore, Karnataka", "coding_culture": 3,
        "specialization": "CS, ECE; Good campus culture; Liberal education",
    },
    "manipal institute": {
        "fees_lpa": 5.5, "avg_lpa": 9.5, "high_lpa": 50.0,
        "top_recruiters": ["Amazon", "Infosys", "Wipro", "Accenture", "Samsung"],
        "hostel": True, "campus_acres": 600, "student_faculty_ratio": 16,
        "location": "Manipal, Karnataka", "coding_culture": 3,
        "specialization": "CS, ECE, Biomedical; Excellent campus life; Tier-1 private",
    },
}


def get_placement_info(college_name: str) -> Dict:
    """
    Fuzzy-match a college name to the PLACEMENT_DB and return placement info.
    Returns a default empty dict if no match is found.
    """
    name_lower = college_name.lower().strip()
    
    # Direct key lookup
    if name_lower in PLACEMENT_DB:
        info = dict(PLACEMENT_DB[name_lower])
        info["roi_index"] = round(info["avg_lpa"] / max(info["fees_lpa"], 0.01), 2)
        return info
    
    # Partial / substring match (longest key match wins)
    best_match = None
    best_len = 0
    for key in PLACEMENT_DB:
        # Check if key is a substring of name or vice versa
        if key in name_lower or name_lower in key:
            if len(key) > best_len:
                best_match = key
                best_len = len(key)
        # Also check word overlap
        elif not best_match:
            key_words = set(key.split())
            name_words = set(name_lower.split())
            overlap = key_words & name_words
            if len(overlap) >= 2 and len(overlap) > best_len:
                best_match = key
                best_len = len(overlap)
    
    if best_match:
        info = dict(PLACEMENT_DB[best_match])
        info["roi_index"] = round(info["avg_lpa"] / max(info["fees_lpa"], 0.01), 2)
        return info
    
    return {}


def get_roi_ranked_list(colleges: List[Dict]) -> List[Dict]:
    """Return colleges enriched with placement/ROI data, sorted by ROI index descending."""
    enriched = []
    for col in colleges:
        placement = get_placement_info(col.get("name", ""))
        entry = dict(col)
        if placement:
            entry.update({
                "fees_lpa": placement.get("fees_lpa", 0),
                "avg_lpa": placement.get("avg_lpa", 0),
                "high_lpa": placement.get("high_lpa", 0),
                "roi_index": placement.get("roi_index", 0),
                "top_recruiters": placement.get("top_recruiters", []),
                "hostel": placement.get("hostel", False),
                "location": placement.get("location", ""),
                "coding_culture": placement.get("coding_culture", 0),
                "specialization": placement.get("specialization", ""),
            })
        enriched.append(entry)
    return sorted(enriched, key=lambda x: x.get("roi_index", 0), reverse=True)



def _calc_chance(user_rank: int, closing_rank: int) -> int:
    """Compute admission probability (%) given user's rank and college closing rank."""
    if user_rank <= 0 or closing_rank <= 0:
        return 0
    ratio = user_rank / closing_rank
    if ratio <= 0.60:
        return 98
    elif ratio <= 0.75:
        return 92
    elif ratio <= 0.90:
        return 82
    elif ratio <= 1.00:
        return 70
    elif ratio <= 1.10:
        return 55
    elif ratio <= 1.25:
        return 40
    elif ratio <= 1.50:
        return 22
    elif ratio <= 2.00:
        return 10
    return 5


# ──────────────────────────────────────────────────
# JEE Main colleges (NITs, IIITs, GFTIs)
# ──────────────────────────────────────────────────
class JEEMainCollegeService:
    """Reads jee_college_cutoffs_nits.csv with columns:
    Year, Institute, Branch, Category, Opening_Rank, Closing_Rank, Quota
    """

    def __init__(self, data_path: str = "app/data/jee_main"):
        self.data_path = Path(data_path)
        self._df: Optional[pd.DataFrame] = None
        self._full_df: Optional[pd.DataFrame] = None
        self._load()

    def _load(self):
        csv = self.data_path / "jee_college_cutoffs_nits.csv"
        try:
            df = pd.read_csv(csv)
            df.columns = [c.strip() for c in df.columns]
            self._full_df = df.copy()
            # Use latest year available
            latest_year = df["Year"].max()
            self._df = df[df["Year"] == latest_year].copy()
            print(f"[OK] JEE Main colleges loaded: {len(self._df)} entries (year {latest_year})")
        except Exception as e:
            print(f"[WARN] JEE Main college data error: {e}")
            self._df = pd.DataFrame()
            self._full_df = pd.DataFrame()

    def _map_category(self, cat: str) -> str:
        """Map user-facing category to CSV Category column."""
        cat_lower = cat.lower().strip().replace("-", "").replace("_", "").replace(" ", "")
        mapping = {
            "general": "General", "gen": "General", "ur": "General",
            "ews": "EWS",
            "obc": "OBC-NCL", "obcncl": "OBC-NCL",
            "sc": "SC",
            "st": "ST",
            "pwd": "PwD",
        }
        return mapping.get(cat_lower, "General")

    def predict(self, rank: int, category: str, quota: str = "Other State", limit: int = 50) -> List[Dict]:
        if self._df is None or self._df.empty:
            return []

        cat_csv = self._map_category(category)

        # Filter by category and quota (case insensitive)
        filtered = self._df[
            (self._df["Category"] == cat_csv) &
            (self._df["Quota"].str.lower() == quota.lower())
        ].copy()

        if filtered.empty:
            # fallback: try any quota
            filtered = self._df[self._df["Category"] == cat_csv].copy()

        if filtered.empty:
            return []

        filtered["chance"] = filtered["Closing_Rank"].apply(lambda cr: _calc_chance(rank, cr))
        filtered = filtered.sort_values("chance", ascending=False).head(limit)

        results = []
        for _, row in filtered.iterrows():
            name = row["Institute"]
            placement = get_placement_info(name)
            entry = {
                "name": name,
                "branch": row["Branch"],
                "type": _classify_institute(name),
                "closing_rank": int(row["Closing_Rank"]),
                "opening_rank": int(row["Opening_Rank"]),
                "chance": int(row["chance"]),
                "category": cat_csv,
                "quota": row.get("Quota", ""),
                "fees_lpa": placement.get("fees_lpa"),
                "avg_lpa": placement.get("avg_lpa"),
                "high_lpa": placement.get("high_lpa"),
                "roi_index": placement.get("roi_index"),
                "top_recruiters": placement.get("top_recruiters", []),
                "location": placement.get("location", ""),
                "hostel": placement.get("hostel"),
                "coding_culture": placement.get("coding_culture"),
                "specialization": placement.get("specialization", ""),
            }
            results.append(entry)
        return results

    def get_cutoff_trends(self, institute: str, branch: str, category: str, quota: str = "Other State") -> List[Dict]:
        if self._full_df is None or self._full_df.empty:
            return []
        cat_csv = self._map_category(category)
        filtered = self._full_df[
            (self._full_df["Institute"].str.lower() == institute.lower()) &
            (self._full_df["Branch"].str.lower() == branch.lower()) &
            (self._full_df["Category"] == cat_csv) &
            (self._full_df["Quota"].str.lower() == quota.lower())
        ].copy()
        
        filtered = filtered.sort_values("Year")
        results = []
        for _, row in filtered.iterrows():
            results.append({
                "year": int(row["Year"]),
                "opening_rank": int(row["Opening_Rank"]) if pd.notna(row["Opening_Rank"]) else 0,
                "closing_rank": int(row["Closing_Rank"]) if pd.notna(row["Closing_Rank"]) else 0,
            })
        return results


# ──────────────────────────────────────────────────
# JEE Advanced colleges (IITs)
# ──────────────────────────────────────────────────
class JEEAdvancedCollegeService:
    """Reads jee_advanced_cutoff_2010_2024.csv with columns:
    Institute, Branch, Year, Round, Category, Opening_Rank, Closing_Rank, Gender_Pool, ...
    """

    def __init__(self, data_path: str = "app/data/jee_advanced"):
        self.data_path = Path(data_path)
        self._df: Optional[pd.DataFrame] = None
        self._full_df: Optional[pd.DataFrame] = None
        self._load()

    def _load(self):
        csv = self.data_path / "jee_advanced_cutoff_2010_2024.csv"
        try:
            df = pd.read_csv(csv)
            df.columns = [c.strip() for c in df.columns]
            self._full_df = df.copy()
            latest = df["Year"].max()
            # Use latest year, last round, gender-neutral
            last_round = df[df["Year"] == latest]["Round"].max()
            self._df = df[
                (df["Year"] == latest) &
                (df["Round"] == last_round) &
                (df["Gender_Pool"].str.contains("Neutral", case=False, na=False))
            ].copy()
            print(f"[OK] JEE Advanced colleges loaded: {len(self._df)} entries (year {latest}, round {last_round})")
        except Exception as e:
            print(f"[WARN] JEE Advanced college data error: {e}")
            self._df = pd.DataFrame()
            self._full_df = pd.DataFrame()

    def _map_category(self, cat: str) -> str:
        cat_lower = cat.lower().strip().replace("-", "").replace("_", "").replace(" ", "")
        mapping = {
            "general": "GEN", "gen": "GEN", "ur": "GEN",
            "ews": "GEN-EWS",
            "obc": "OBC-NCL", "obcncl": "OBC-NCL",
            "sc": "SC", "st": "ST", "pwd": "GEN-PwD",
        }
        return mapping.get(cat_lower, "GEN")

    def predict(self, rank: int, category: str, limit: int = 50) -> List[Dict]:
        if self._df is None or self._df.empty:
            return []
        cat_csv = self._map_category(category)
        filtered = self._df[self._df["Category"] == cat_csv].copy()
        if filtered.empty:
            return []

        filtered["chance"] = filtered["Closing_Rank"].apply(lambda cr: _calc_chance(rank, cr))
        filtered = filtered.sort_values("chance", ascending=False).head(limit)

        results = []
        for _, row in filtered.iterrows():
            name = row["Institute"]
            placement = get_placement_info(name)
            entry = {
                "name": name,
                "branch": row["Branch"],
                "type": "IIT",
                "closing_rank": int(row["Closing_Rank"]),
                "opening_rank": int(row["Opening_Rank"]),
                "chance": int(row["chance"]),
                "category": cat_csv,
                "quota": "All India",
                "fees_lpa": placement.get("fees_lpa"),
                "avg_lpa": placement.get("avg_lpa"),
                "high_lpa": placement.get("high_lpa"),
                "roi_index": placement.get("roi_index"),
                "top_recruiters": placement.get("top_recruiters", []),
                "location": placement.get("location", ""),
                "hostel": placement.get("hostel"),
                "coding_culture": placement.get("coding_culture"),
                "specialization": placement.get("specialization", ""),
            }
            results.append(entry)
        return results

    def get_cutoff_trends(self, institute: str, branch: str, category: str, quota: str = "All India") -> List[Dict]:
        if self._full_df is None or self._full_df.empty:
            return []
        cat_csv = self._map_category(category)
        # Filters by gender pool = Neutral
        filtered = self._full_df[
            (self._full_df["Institute"].str.lower() == institute.lower()) &
            (self._full_df["Branch"].str.lower() == branch.lower()) &
            (self._full_df["Category"] == cat_csv) &
            (self._full_df["Gender_Pool"].str.contains("Neutral", case=False, na=False))
        ].copy()
        
        filtered = filtered.sort_values("Year")
        results = []
        for _, row in filtered.iterrows():
            results.append({
                "year": int(row["Year"]),
                "opening_rank": int(row["Opening_Rank"]) if pd.notna(row["Opening_Rank"]) else 0,
                "closing_rank": int(row["Closing_Rank"]) if pd.notna(row["Closing_Rank"]) else 0,
            })
        return results


# ──────────────────────────────────────────────────
# NEET colleges
# ──────────────────────────────────────────────────
class NEETCollegeService:
    """Reads neet_cutoff_2010_2024.csv with columns:
    College, Course, Year, Round, Category, Opening_Marks, Closing_Marks, Seat_Type, ...
    """

    def __init__(self, data_path: str = "app/data/neet"):
        self.data_path = Path(data_path)
        self._df: Optional[pd.DataFrame] = None
        self._full_df: Optional[pd.DataFrame] = None
        self._load()

    def _load(self):
        csv = self.data_path / "neet_cutoff_2010_2024.csv"
        try:
            df = pd.read_csv(csv)
            df.columns = [c.strip() for c in df.columns]
            self._full_df = df.copy()
            latest = df["Year"].max()
            self._df = df[df["Year"] == latest].copy()
            print(f"[OK] NEET colleges loaded: {len(self._df)} entries (year {latest})")
        except Exception as e:
            print(f"[WARN] NEET college data error: {e}")
            self._df = pd.DataFrame()
            self._full_df = pd.DataFrame()

    def _map_category(self, cat: str) -> str:
        cat_lower = cat.lower().strip().replace("-", "").replace("_", "").replace(" ", "")
        mapping = {
            "general": "UR", "gen": "UR", "ur": "UR",
            "ews": "EWS",
            "obc": "OBC", "obcncl": "OBC",
            "sc": "SC", "st": "ST", "pwd": "PH",
        }
        return mapping.get(cat_lower, "UR")

    def predict(self, marks: int, category: str, limit: int = 50) -> List[Dict]:
        """NEET uses marks for cutoff, not ranks."""
        if self._df is None or self._df.empty:
            return []

        cat_csv = self._map_category(category)
        filtered = self._df[self._df["Category"] == cat_csv].copy()

        if filtered.empty:
            # Try without category filter
            filtered = self._df.copy()

        # For NEET, higher marks = better. Chance based on marks vs closing marks.
        filtered = filtered.dropna(subset=["Closing_Marks"])
        filtered["Closing_Marks"] = pd.to_numeric(filtered["Closing_Marks"], errors="coerce")
        filtered = filtered.dropna(subset=["Closing_Marks"])

        def marks_chance(closing: float) -> int:
            if closing <= 0:
                return 0
            if marks >= closing:
                surplus = (marks - closing) / max(closing, 1) * 100
                if surplus >= 10:
                    return 98
                elif surplus >= 5:
                    return 90
                elif surplus >= 2:
                    return 80
                return 70
            deficit = (closing - marks) / max(closing, 1) * 100
            if deficit <= 2:
                return 55
            elif deficit <= 5:
                return 35
            elif deficit <= 10:
                return 15
            return 5

        filtered["chance"] = filtered["Closing_Marks"].apply(marks_chance)
        filtered = filtered.sort_values("chance", ascending=False).head(limit)

        results = []
        for _, row in filtered.iterrows():
            name = row["College"]
            placement = get_placement_info(name)
            entry = {
                "name": name,
                "branch": row.get("Course", "MBBS"),
                "type": _classify_medical(name),
                "closing_rank": int(row["Closing_Marks"]),
                "opening_rank": int(row.get("Opening_Marks", 0)) if pd.notna(row.get("Opening_Marks")) else 0,
                "chance": int(row["chance"]),
                "category": cat_csv,
                "quota": row.get("Seat_Type", "AIQ"),
                "fees_lpa": placement.get("fees_lpa"),
                "avg_lpa": placement.get("avg_lpa"),
                "high_lpa": placement.get("high_lpa"),
                "roi_index": placement.get("roi_index"),
                "top_recruiters": placement.get("top_recruiters", []),
                "location": placement.get("location", ""),
                "hostel": placement.get("hostel"),
                "coding_culture": placement.get("coding_culture"),
                "specialization": placement.get("specialization", ""),
            }
            results.append(entry)
        return results

    def get_cutoff_trends(self, institute: str, branch: str, category: str, quota: str = "AIQ") -> List[Dict]:
        if self._full_df is None or self._full_df.empty:
            return []
        cat_csv = self._map_category(category)
        filtered = self._full_df[
            (self._full_df["College"].str.lower() == institute.lower()) &
            (self._full_df["Course"].str.lower() == branch.lower()) &
            (self._full_df["Category"] == cat_csv)
        ].copy()
        
        filtered = filtered.sort_values("Year")
        results = []
        for _, row in filtered.iterrows():
            results.append({
                "year": int(row["Year"]),
                "opening_rank": int(row["Opening_Marks"]) if pd.notna(row["Opening_Marks"]) else 0,
                "closing_rank": int(row["Closing_Marks"]) if pd.notna(row["Closing_Marks"]) else 0,
            })
        return results


# ──────────────────────────────────────────────────
# KCET colleges
# ──────────────────────────────────────────────────
class KCETCollegeService:
    """Reads KCET_Cutoff_2016_2024_DataAvailable.csv with columns:
    Year, Round, College_Code, College_Name, Branch, Location, College_Type, Data_Source,
    GM, GMK, GMR, 1G, 1K, 1R, 2AG, 2AK, ... (categories as columns with rank values)
    """

    def __init__(self, data_path: str = "app/data/kcet"):
        self.data_path = Path(data_path)
        self._df: Optional[pd.DataFrame] = None
        self._full_df: Optional[pd.DataFrame] = None
        self._load()

    def _load(self):
        csv = self.data_path / "KCET_Cutoff_2016_2024_DataAvailable.csv"
        try:
            df = pd.read_csv(csv, low_memory=False)
            df.columns = [c.strip() for c in df.columns]
            self._full_df = df.copy()
            latest = df["Year"].max()
            # Use round 1 of latest year
            self._df = df[(df["Year"] == latest) & (df["Round"] == "R1")].copy()
            print(f"[OK] KCET colleges loaded: {len(self._df)} entries (year {latest})")
        except Exception as e:
            print(f"[WARN] KCET college data error: {e}")
            self._df = pd.DataFrame()
            self._full_df = pd.DataFrame()

    def _map_category(self, cat: str) -> str:
        """Map category to KCET column name."""
        cat_clean = cat.upper().strip().replace("-", "").replace("_", "").replace(" ", "")
        
        # Valid KCET columns in the dataset
        kcet_cols = {
            "GM", "GMK", "GMR", 
            "1G", "1K", "1R", 
            "2AG", "2AK", "2AR", 
            "2BG", "2BK", "2BR", 
            "3AG", "3AK", "3AR", 
            "3BG", "3BK", "3BR", 
            "SCG", "SCK", "SCR", 
            "STG", "STK", "STR"
        }
        if cat_clean in kcet_cols:
            return cat_clean
            
        # Fallback mappings for generic categories
        mapping = {
            "GENERAL": "GM", "GEN": "GM", "UR": "GM", "GM": "GM",
            "OBC": "2AG", "OBCNCL": "2AG",
            "SC": "SCG", "ST": "STG",
            "EWS": "GM", "PWD": "GM",
        }
        return mapping.get(cat_clean, "GM")

    def predict(self, rank: int, category: str, limit: int = 50) -> List[Dict]:
        if self._df is None or self._df.empty:
            return []

        cat_col = self._map_category(category)
        if cat_col not in self._df.columns:
            cat_col = "GM"

        # Filter rows that have data for this category
        working = self._df[self._df[cat_col].notna()].copy()
        working[cat_col] = pd.to_numeric(working[cat_col], errors="coerce")
        working = working.dropna(subset=[cat_col])

        working["chance"] = working[cat_col].apply(lambda cr: _calc_chance(rank, int(cr)))
        working = working.sort_values("chance", ascending=False).head(limit)

        results = []
        for _, row in working.iterrows():
            name = row["College_Name"]
            placement = get_placement_info(name)
            entry = {
                "name": name,
                "branch": row["Branch"],
                "type": row.get("College_Type", "Engineering"),
                "closing_rank": int(row[cat_col]),
                "opening_rank": int(row[cat_col]),
                "chance": int(row["chance"]),
                "category": category.upper(),
                "quota": "Karnataka",
                "fees_lpa": placement.get("fees_lpa"),
                "avg_lpa": placement.get("avg_lpa"),
                "high_lpa": placement.get("high_lpa"),
                "roi_index": placement.get("roi_index"),
                "top_recruiters": placement.get("top_recruiters", []),
                "location": placement.get("location", ""),
                "hostel": placement.get("hostel"),
                "coding_culture": placement.get("coding_culture"),
                "specialization": placement.get("specialization", ""),
            }
            results.append(entry)
        return results

    def get_cutoff_trends(self, institute: str, branch: str, category: str, quota: str = "") -> List[Dict]:
        if self._full_df is None or self._full_df.empty:
            return []
        cat_col = self._map_category(category)
        if cat_col not in self._full_df.columns:
            cat_col = "GM"
            
        filtered = self._full_df[
            (self._full_df["College_Name"].str.lower() == institute.lower()) &
            (self._full_df["Branch"].str.lower() == branch.lower()) &
            (self._full_df[cat_col].notna()) &
            (self._full_df["Round"] == "R1")
        ].copy()
        
        filtered[cat_col] = pd.to_numeric(filtered[cat_col], errors="coerce")
        filtered = filtered.dropna(subset=[cat_col])
        filtered = filtered.sort_values("Year")
        results = []
        for _, row in filtered.iterrows():
            results.append({
                "year": int(row["Year"]),
                "opening_rank": int(row[cat_col]),
                "closing_rank": int(row[cat_col]),
            })
        return results


# ──────────────────────────────────────────────────
# MHT-CET colleges
# ──────────────────────────────────────────────────
class MHTCETCollegeService:
    """Reads mhtcet_cutoff_2010_2024.csv with columns:
    College, Branch, Year, Round, Category, Opening_Rank, Closing_Rank, ...
    """

    def __init__(self, data_path: str = "app/data/mht_cet"):
        self.data_path = Path(data_path)
        self._df: Optional[pd.DataFrame] = None
        self._full_df: Optional[pd.DataFrame] = None
        self._load()

    def _load(self):
        csv = self.data_path / "mhtcet_cutoff_2010_2024.csv"
        try:
            df = pd.read_csv(csv, low_memory=False)
            df.columns = [c.strip() for c in df.columns]
            self._full_df = df.copy()
            latest = df["Year"].max()
            last_round = df[df["Year"] == latest]["Round"].max()
            self._df = df[(df["Year"] == latest) & (df["Round"] == last_round)].copy()
            print(f"[OK] MHT-CET colleges loaded: {len(self._df)} entries (year {latest})")
        except Exception as e:
            print(f"[WARN] MHT-CET college data error: {e}")
            self._df = pd.DataFrame()
            self._full_df = pd.DataFrame()

    def _map_category(self, cat: str) -> str:
        cat_lower = cat.lower().strip().replace("-", "").replace("_", "").replace(" ", "")
        mapping = {
            "general": "OPEN", "gen": "OPEN", "ur": "OPEN",
            "ews": "EWS",
            "obc": "OBC", "obcncl": "OBC",
            "sc": "SC", "st": "ST", "pwd": "PH",
        }
        return mapping.get(cat_lower, "OPEN")

    def predict(self, rank: int, category: str, limit: int = 50) -> List[Dict]:
        if self._df is None or self._df.empty:
            return []

        cat_csv = self._map_category(category)
        filtered = self._df[self._df["Category"] == cat_csv].copy()
        if filtered.empty:
            filtered = self._df.copy()

        filtered["Closing_Rank"] = pd.to_numeric(filtered["Closing_Rank"], errors="coerce")
        filtered = filtered.dropna(subset=["Closing_Rank"])

        filtered["chance"] = filtered["Closing_Rank"].apply(lambda cr: _calc_chance(rank, int(cr)))
        filtered = filtered.sort_values("chance", ascending=False).head(limit)

        results = []
        for _, row in filtered.iterrows():
            name = row["College"]
            opening = pd.to_numeric(row.get("Opening_Rank", 0), errors="coerce")
            placement = get_placement_info(name)
            entry = {
                "name": name,
                "branch": row["Branch"],
                "type": "Engineering",
                "closing_rank": int(row["Closing_Rank"]),
                "opening_rank": int(opening) if pd.notna(opening) else 0,
                "chance": int(row["chance"]),
                "category": cat_csv,
                "quota": "Maharashtra",
                "fees_lpa": placement.get("fees_lpa"),
                "avg_lpa": placement.get("avg_lpa"),
                "high_lpa": placement.get("high_lpa"),
                "roi_index": placement.get("roi_index"),
                "top_recruiters": placement.get("top_recruiters", []),
                "location": placement.get("location", ""),
                "hostel": placement.get("hostel"),
                "coding_culture": placement.get("coding_culture"),
                "specialization": placement.get("specialization", ""),
            }
            results.append(entry)
        return results

    def get_cutoff_trends(self, institute: str, branch: str, category: str, quota: str = "") -> List[Dict]:
        if self._full_df is None or self._full_df.empty:
            return []
        cat_csv = self._map_category(category)
        filtered = self._full_df[
            (self._full_df["College"].str.lower() == institute.lower()) &
            (self._full_df["Branch"].str.lower() == branch.lower()) &
            (self._full_df["Category"] == cat_csv)
        ].copy()
        
        filtered = filtered.sort_values("Year")
        results = []
        for _, row in filtered.iterrows():
            opening = pd.to_numeric(row.get("Opening_Rank", 0), errors="coerce")
            closing = pd.to_numeric(row.get("Closing_Rank", 0), errors="coerce")
            results.append({
                "year": int(row["Year"]),
                "opening_rank": int(opening) if pd.notna(opening) else 0,
                "closing_rank": int(closing) if pd.notna(closing) else 0,
            })
        return results


# ──────────────────────────────────────────────────
# COMEDK colleges
# ──────────────────────────────────────────────────
class COMEDKCollegeService:
    """Reads comedk_cutoff_2010_2024.csv with columns:
    College, Branch, Year, Round, Category, Opening_Rank, Closing_Rank, ...
    """

    def __init__(self, data_path: str = "app/data/comedk"):
        self.data_path = Path(data_path)
        self._df: Optional[pd.DataFrame] = None
        self._full_df: Optional[pd.DataFrame] = None
        self._load()

    def _load(self):
        csv = self.data_path / "comedk_cutoff_2010_2024.csv"
        try:
            df = pd.read_csv(csv, low_memory=False)
            df.columns = [c.strip() for c in df.columns]
            self._full_df = df.copy()
            latest = df["Year"].max()
            last_round = df[df["Year"] == latest]["Round"].max()
            self._df = df[(df["Year"] == latest) & (df["Round"] == last_round)].copy()
            print(f"[OK] COMEDK colleges loaded: {len(self._df)} entries (year {latest})")
        except Exception as e:
            print(f"[WARN] COMEDK college data error: {e}")
            self._df = pd.DataFrame()
            self._full_df = pd.DataFrame()

    def _map_category(self, cat: str) -> str:
        cat_lower = cat.lower().strip().replace("-", "").replace("_", "").replace(" ", "")
        mapping = {
            "general": "GM", "gen": "GM", "ur": "GM", "gm": "GM",
            "obc": "OBC", "obcncl": "OBC",
            "sc": "SC", "st": "ST",
            "ews": "GM", "pwd": "GM",
        }
        return mapping.get(cat_lower, "GM")

    def predict(self, rank: int, category: str, limit: int = 50) -> List[Dict]:
        if self._df is None or self._df.empty:
            return []

        cat_csv = self._map_category(category)
        filtered = self._df[self._df["Category"] == cat_csv].copy()
        if filtered.empty:
            filtered = self._df.copy()

        filtered["Closing_Rank"] = pd.to_numeric(filtered["Closing_Rank"], errors="coerce")
        filtered = filtered.dropna(subset=["Closing_Rank"])

        filtered["chance"] = filtered["Closing_Rank"].apply(lambda cr: _calc_chance(rank, int(cr)))
        filtered = filtered.sort_values("chance", ascending=False).head(limit)

        results = []
        for _, row in filtered.iterrows():
            name = row["College"]
            opening = pd.to_numeric(row.get("Opening_Rank", 0), errors="coerce")
            placement = get_placement_info(name)
            entry = {
                "name": name,
                "branch": row["Branch"],
                "type": "Private Engineering",
                "closing_rank": int(row["Closing_Rank"]),
                "opening_rank": int(opening) if pd.notna(opening) else 0,
                "chance": int(row["chance"]),
                "category": cat_csv,
                "quota": "Karnataka",
                "fees_lpa": placement.get("fees_lpa"),
                "avg_lpa": placement.get("avg_lpa"),
                "high_lpa": placement.get("high_lpa"),
                "roi_index": placement.get("roi_index"),
                "top_recruiters": placement.get("top_recruiters", []),
                "location": placement.get("location", ""),
                "hostel": placement.get("hostel"),
                "coding_culture": placement.get("coding_culture"),
                "specialization": placement.get("specialization", ""),
            }
            results.append(entry)
        return results

    def get_cutoff_trends(self, institute: str, branch: str, category: str, quota: str = "") -> List[Dict]:
        if self._full_df is None or self._full_df.empty:
            return []
        cat_csv = self._map_category(category)
        filtered = self._full_df[
            (self._full_df["College"].str.lower() == institute.lower()) &
            (self._full_df["Branch"].str.lower() == branch.lower()) &
            (self._full_df["Category"] == cat_csv)
        ].copy()
        
        filtered = filtered.sort_values("Year")
        results = []
        for _, row in filtered.iterrows():
            opening = pd.to_numeric(row.get("Opening_Rank", 0), errors="coerce")
            closing = pd.to_numeric(row.get("Closing_Rank", 0), errors="coerce")
            results.append({
                "year": int(row["Year"]),
                "opening_rank": int(opening) if pd.notna(opening) else 0,
                "closing_rank": int(closing) if pd.notna(closing) else 0,
            })
        return results


# ──────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────
def _classify_institute(name: str) -> str:
    """Classify an institute as NIT / IIIT / GFTI / Private."""
    n = name.upper()
    if "NIT " in n or "MNNIT" in n or "MNIT" in n or "VNIT" in n or "SVNIT" in n:
        return "NIT"
    elif "IIIT" in n or "III T" in n:
        return "IIIT"
    elif "IIT " in n:
        return "IIT"
    elif "DTU" in n or "NSUT" in n or "IGDTUW" in n or "IIESTS" in n:
        return "GFTI"
    return "GFTI"


def _classify_medical(name: str) -> str:
    """Classify a medical college."""
    n = name.upper()
    if "AIIMS" in n:
        return "AIIMS"
    elif "JIPMER" in n:
        return "JIPMER"
    elif "GMC" in n or "GOVERNMENT" in n or "GOVT" in n:
        return "Govt Medical"
    return "Medical"
