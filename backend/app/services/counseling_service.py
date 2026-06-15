from typing import List, Dict
import re


# ──────────────────────────────────────────────────────────────────────────────
# COLLEGE FACTS DATABASE — for AI counselor responses
# sourced from official portals, NIRF reports, student reviews (Reddit/Quora 2024)
# ──────────────────────────────────────────────────────────────────────────────
COLLEGE_FACTS_DB: Dict[str, Dict] = {
    "iit bombay": {
        "hostel": "Excellent hostel facilities. 13 hostels, all students get accommodation. AC rooms available in some hostels. World-class sports complex and gymkhana.",
        "coding_culture": "Outstanding. Regular inter-hostel coding competitions, Techfest (Asia's largest tech fest), ACM-ICPC participants, many open-source contributors.",
        "campus": "550 acres in Mumbai. Adjacent to IIT Powai lake. Dense green cover. Full self-sufficient campus with hospitals, markets, sports.",
        "notable": "Alumni include Nandan Nilekani (Infosys co-founder), Manohar Parrikar. IITB is #3 in QS Asia Rankings.",
        "ranking": "NIRF #3, QS World #118 (2024)",
    },
    "iit delhi": {
        "hostel": "13 hostels. All students guaranteed hostel. Proximity to South Delhi is a big advantage for internships/jobs. Aravalli range view.",
        "coding_culture": "Top-tier. IIT Delhi consistently produces top coders. Strong Microsoft Research presence on campus. Many FAANG alumni.",
        "campus": "325 acres in South Delhi. Urban location. All facilities within campus including hospital, bank, market.",
        "notable": "Alumni: Sachin Bansal (Flipkart), Vinod Dham (Intel Pentium). QS World #197 (2024).",
        "ranking": "NIRF #2, QS World #197 (2024)",
    },
    "iit madras": {
        "hostel": "Exceptional. All 18 hostels inside the campus forest. Deer spotted within campus! Very lively hostel culture with Saarang (cultural) and Shaastra (tech).",
        "coding_culture": "Excellent. IIT Madras has a strong competitive programming culture. Research Park on campus gives startup/industry exposure.",
        "campus": "617 acres in Chennai — the largest IIT campus. Inside a forest; frequent deer and peacock sightings. A unique campus experience.",
        "notable": "Alumni: Raghuram Rajan (RBI Governor), Kris Gopalakrishnan (Infosys). NIRF #1 for 8 consecutive years.",
        "ranking": "NIRF #1 (Engineering), QS World #227 (2024)",
    },
    "iit kharagpur": {
        "hostel": "19 hostels, largest IIT. Very vibrant hostel culture. Gymkhana with Olympic-size swimming pool. Kgp culture is legendary.",
        "coding_culture": "Strong. Hosts Codeforces rounds, has Kharagpur Winter of Code (like Google Summer of Code). Many competitive programmers.",
        "campus": "2100 acres — largest campus of any IIT. Has its own railway station. Full township with schools, hospital, markets.",
        "notable": "Alumni: Sundar Pichai (CEO Google/Alphabet), Vinod Gupta. First IIT (1951).",
        "ranking": "NIRF #5, QS World #271 (2024)",
    },
    "iit kanpur": {
        "hostel": "13 hostels. Strong academic culture. Antaragni (cultural fest) and Techkriti (tech fest) are major events. Good hostel life.",
        "coding_culture": "Legendary competitive programming hub. IITK consistently ranked among top 10 globally in ICPC. Many world-class researchers.",
        "campus": "1055 acres in Kanpur. Research-oriented atmosphere. Has its own airstrip. Strong CS department nationally.",
        "notable": "Alumni: Manmohan Singh was faculty, Rajat Gupta (McKinsey). Pioneered India's first CS department.",
        "ranking": "NIRF #4, QS World #278 (2024)",
    },
    "iit roorkee": {
        "hostel": "Good facilities. 12 hostels. Strong alumni network in core engineering (civil/mechanical). Thomso (cultural) and Cognizance (tech) are big events.",
        "coding_culture": "Good but more core/research focused. Strong in robotics and electronics clubs.",
        "campus": "365 acres. Oldest technical institution in Asia (1847). Heritage buildings and modern labs coexist beautifully.",
        "notable": "Alumni: N.R. Narayana Murthy, many top civil engineers in India. Established 1847.",
        "ranking": "NIRF #7, QS World #369 (2024)",
    },
    "iit guwahati": {
        "hostel": "Beautiful campus on Brahmaputra riverbanks. 11 hostels, picturesque views. Techniche (tech fest), Alcheringa (cultural) are excellent.",
        "coding_culture": "Growing rapidly. Northeast's premier tech institution. Strong open-source culture.",
        "campus": "704 acres on Brahmaputra. Stunning natural location. Research labs in biotech, design, astronomy.",
        "notable": "Strong focus on design and biotech. Alumni in major tech companies.",
        "ranking": "NIRF #8",
    },
    "nit trichy": {
        "hostel": "Excellent hostels — 14 hostels with good facilities. Pragyan (tech fest) is South India's largest NIT tech fest. Very strong alumni culture.",
        "coding_culture": "Best among NITs. Strong placement culture. Annual hackathons. Many FAANG/core engineering placements.",
        "campus": "800 acres in Tiruchirappalli. Full self-contained campus. NIRF's top NIT consistently.",
        "notable": "Best NIT in NIRF rankings (2024). Alumni in every major tech company.",
        "ranking": "NIRF #9 (Engineering), Best NIT",
    },
    "nit warangal": {
        "hostel": "Good facilities. 10 hostels. Strong alumni network in Hyderabad tech hub. Technozion (tech fest), Aurora (cultural).",
        "coding_culture": "Excellent. Very active coding community. Close proximity to Hyderabad gives internship advantages.",
        "campus": "475 acres. Oldest NIT (1959). Beautiful campus with lakes.",
        "notable": "2nd Best NIT in NIRF. 65 years of legacy. Strong in CSE/ECE.",
        "ranking": "NIRF #26, #2 NIT",
    },
    "nit surathkal": {
        "hostel": "Great. 10+ hostels. Beach proximity (coastal Karnataka). Engineer (tech fest). Good hostel-life balance.",
        "coding_culture": "Very good. Strong competitive programming and open-source culture. Many top placements in tech.",
        "campus": "295 acres, coastal Karnataka. Beautiful beach nearby. Very pleasant climate.",
        "notable": "Top 3 NIT consistently. Strong CS/ECE/Chemical programs. IIT-adjacent outcomes for CS.",
        "ranking": "NIRF #12 (Engineering), #3 NIT",
    },
    "nit calicut": {
        "hostel": "Good hostels. Nice Kerala campus culture. Tathva (tech fest) and Ragam (cultural) are major events.",
        "coding_culture": "Good. Kerala's tech culture advantage. UST Global, TCS hire heavily.",
        "campus": "300 acres in Kozhikode. Pleasant tropical climate. Strong Architecture and Civil programs.",
        "notable": "Top NIT in South India. Strong Architecture + CS programs. Kerala IT sector ties.",
        "ranking": "NIRF #28, Top-5 NIT",
    },
    "iiit hyderabad": {
        "hostel": "Good hostel facilities. Small campus but very high research density. Felicity (tech+cultural) is the annual fest.",
        "coding_culture": "LEGENDARY — arguably the best coding culture in India. Research Gate model: students publish papers. Many Google Research interns.",
        "campus": "66 acres in Gachibowli (Hyderabad's IT hub). Perfect location for tech internships. Research-first culture.",
        "notable": "Produces some of India's top competitive programmers. Faculty are world-renowned researchers in AI/NLP/CV.",
        "ranking": "NIRF Top-10 IIIT. Best research IIIT in India.",
    },
    "iiit bangalore": {
        "hostel": "Limited on-campus hostel. Most students take apartments near campus in Bangalore's Electronic City area.",
        "coding_culture": "Exceptional. 100% placement rate. Bangalore location = constant industry exposure. Industry-linked projects from Day 1.",
        "campus": "Small 5-acre campus in Electronic City, Bangalore. What it lacks in size it makes up in industry proximity.",
        "notable": "iMTech program only (integrated Masters). 100% placements consistently. Best industry-academia integration.",
        "ranking": "Top IIIT for placements",
    },
    "iiit allahabad": {
        "hostel": "Good hostel facilities. Effervescence (cultural fest) and IIIT-A Tech Fest.",
        "coding_culture": "Top coding culture. IIIT-A has produced many competitive programming world finalists. Often ranked #2 after IIIT-H for coding.",
        "campus": "100 acres in Prayagraj. Good research environment.",
        "notable": "IIIT-A alumni in Google, Microsoft, Goldman Sachs. Top competitive programmers.",
        "ranking": "Top IIIT, NIRF ranked",
    },
    "dtu delhi": {
        "hostel": "Hostels available. Delhi location gives massive advantage for placements, internships. Engifest is major fest.",
        "coding_culture": "Very good. Delhi's proximity means regular hackathons and startup exposure. Many startup founders from DTU.",
        "campus": "164 acres in Northwest Delhi. Urban campus with Delhi connectivity.",
        "notable": "Formerly Delhi College of Engineering (1941). Many startup founders. Strong alumni in Flipkart, Amazon.",
        "ranking": "NIRF Top-20 Government Eng College",
    },
    "aiims delhi": {
        "hostel": "All MBBS students guaranteed hostel. Very affordable. Located in prime South Delhi near Safdarjung.",
        "coding_culture": "N/A — medical institution. However, strong research culture in biomedical sciences.",
        "campus": "135 acres in central New Delhi. Massive hospital complex. Premier medical research in India.",
        "notable": "India's most prestigious medical institution. MBBS fees ~₹1,628/year. Alumni: top doctors worldwide.",
        "ranking": "NIRF #1 Medical",
    },
    "jipmer": {
        "hostel": "Good hostel for medical students. Affordable. Pondicherry's coastal location is a bonus.",
        "coding_culture": "N/A — medical. Strong clinical research culture.",
        "campus": "195 acres in Puducherry. Coastal city with pleasant climate. Bilingual (Tamil/English/French) culture.",
        "notable": "Second oldest medical institution after AIIMS. Excellent PG programs. Puducherry's French heritage nearby.",
        "ranking": "NIRF #2 Medical",
    },
}


def _find_college_fact(message: str) -> tuple:
    """Return (college_key, fact_dict) if a known college is mentioned."""
    msg_lower = message.lower()
    
    # Map of name fragments to DB keys
    name_map = {
        "iit bombay": "iit bombay", "iitb": "iit bombay",
        "iit delhi": "iit delhi", "iitd": "iit delhi",
        "iit madras": "iit madras", "iitm": "iit madras",
        "iit kharagpur": "iit kharagpur", "iitkgp": "iit kharagpur", "kgp": "iit kharagpur",
        "iit kanpur": "iit kanpur", "iitk": "iit kanpur",
        "iit roorkee": "iit roorkee", "iitr": "iit roorkee",
        "iit guwahati": "iit guwahati", "iitg": "iit guwahati",
        "nit trichy": "nit trichy", "nitt": "nit trichy", "tiruchirappalli": "nit trichy",
        "nit warangal": "nit warangal", "nitw": "nit warangal",
        "nit surathkal": "nit surathkal", "nitk": "nit surathkal",
        "nit calicut": "nit calicut", "nitc": "nit calicut",
        "iiit hyderabad": "iiit hyderabad", "iiit-h": "iiit hyderabad",
        "iiit bangalore": "iiit bangalore", "iiitb": "iiit bangalore",
        "iiit allahabad": "iiit allahabad", "iiit-a": "iiit allahabad",
        "dtu": "dtu delhi", "delhi technological": "dtu delhi",
        "aiims delhi": "aiims delhi", "aiims": "aiims delhi",
        "jipmer": "jipmer",
    }
    
    for fragment, key in name_map.items():
        if fragment in msg_lower and key in COLLEGE_FACTS_DB:
            return key, COLLEGE_FACTS_DB[key]
    
    return None, None


class CounselingService:
    def optimize_choices(self, colleges: List[Dict], branch_preferences: List[str] = None) -> List[Dict]:
        """
        Optimizes choice preference order based on an advanced 'ExamRank Choice Score':
        1. Placement Score (Average LPA)
        2. Reputation & ROI (Tier and ROI Index)
        3. Branch Match (Custom preferences)
        4. Admissions Strategy (Dream colleges placed higher)
        """
        def get_tier_multiplier(type_str: str) -> float:
            t = type_str.upper()
            if "IIT" in t: return 1.0
            if "NIT" in t or "AIIMS" in t: return 0.9
            if "IIIT" in t or "JIPMER" in t: return 0.85
            if "GFTI" in t or "GOVT" in t: return 0.75
            return 0.6

        def get_fallback_lpa(type_str: str) -> float:
            t = type_str.upper()
            if "IIT" in t: return 18.0
            if "NIT" in t: return 12.0
            if "IIIT" in t: return 14.0
            if "AIIMS" in t or "JIPMER" in t: return 15.0
            if "GFTI" in t or "GOVT" in t: return 7.0
            return 5.0

        def calculate_score(col: Dict) -> float:
            # 1. Placement Score (Max 35 points)
            avg_lpa = col.get("avg_lpa") or get_fallback_lpa(col.get("type", ""))
            placement_score = min(avg_lpa / 40.0, 1.0) * 35.0
            
            # 2. Reputation & ROI Score (Max 25 points)
            roi = col.get("roi_index") or 5.0
            roi_score = min(roi / 20.0, 1.0) * 15.0
            tier_score = get_tier_multiplier(col.get("type", "")) * 10.0
            
            # 3. Branch Match (Max 30 points)
            branch_score = 0.0
            if branch_preferences:
                for idx, pref in enumerate(branch_preferences):
                    if pref.lower() in col.get("branch", "").lower():
                        # Higher preference (earlier in list) = higher score
                        weight = (len(branch_preferences) - idx) / len(branch_preferences)
                        branch_score = weight * 30.0
                        break
            else:
                # Default logic if no preferences provided
                b = col.get("branch", "").upper()
                if "COMPUTER" in b or "CSE" in b or "CS" in b: branch_score = 30.0
                elif "INFORMATION" in b or "IT" in b: branch_score = 25.0
                elif "ELECTRONICS" in b or "ECE" in b: branch_score = 20.0
                elif "ELECTRICAL" in b or "EE" in b: branch_score = 15.0
                elif "MECHANICAL" in b or "ME" in b: branch_score = 10.0
                elif "CIVIL" in b or "CE" in b: branch_score = 5.0
            
            # 4. Aspirational Strategy (Max 10 points)
            # Lower closing rank means harder to get into -> should be higher in choice list
            closing_rank = col.get("closing_rank", 999999)
            aspirational_score = max(0.0, (100000 - closing_rank) / 100000.0) * 10.0
            
            return placement_score + roi_score + tier_score + branch_score + aspirational_score

        # Sort descending by calculated score
        sorted_colleges = sorted(colleges, key=lambda c: calculate_score(c), reverse=True)
        
        # Add optimized choice number
        for idx, col in enumerate(sorted_colleges):
            col["choice_number"] = idx + 1
            
        return sorted_colleges

    def chat_response(self, message: str, context: Dict = None) -> str:
        """Advanced Admissions Counselor Chatbot with college-specific knowledge."""
        m = message.lower().strip()
        
        # ── Greetings ──────────────────────────────────────────────────────────
        if any(w in m for w in ["hello", "hi", "hey", "namaste", "good morning", "good evening"]):
            return (
                "Hello! 👋 I'm your AI Admissions Counselor for Indian engineering and medical admissions.\n\n"
                "I can help you with:\n"
                "🎓 College comparisons (e.g., 'NIT Trichy vs NIT Warangal?')\n"
                "🏠 Hostel & campus life queries\n"
                "💻 Coding culture at specific colleges\n"
                "📋 JoSAA/NEET counseling process\n"
                "📄 Document requirements\n"
                "💰 Fees & ROI analysis\n\n"
                "What would you like to know?"
            )
        
        # ── Context-aware rank/college query ───────────────────────────────────
        if context and any(k in m for k in ["my chances", "colleges", "rank", "where", "admission", "predict", "get", "option"]):
            exam = context.get("exam", "")
            rank = context.get("rank")
            category = context.get("category", "")
            if exam and rank:
                return (
                    f"With your rank of **{rank:,}** ({category.upper()}) in **{exam.upper()}**, you have competitive options! 🎯\n\n"
                    "📊 Check the **College Predictions** section above — I've sorted them into High/Moderate/Low chance tiers.\n"
                    "📈 Click **'View Full Trend'** on any college to see how cutoffs evolved 2010–2024.\n"
                    "💹 Check the **ROI Analytics** section to find value-for-money picks.\n"
                    "📋 Use the **Choice Optimizer** to auto-sort your JoSAA choices.\n\n"
                    "Do you want to know about a specific college's hostel life, coding culture, or placement stats?"
                )

        # ── Hostel queries ─────────────────────────────────────────────────────
        if any(w in m for w in ["hostel", "accommodation", "dorm", "room", "stay", "living"]):
            college_key, facts = _find_college_fact(m)
            if facts:
                return (
                    f"🏠 **Hostel & Campus Life at {college_key.title()}:**\n\n"
                    f"{facts['hostel']}\n\n"
                    f"📍 Location: {facts.get('campus', 'N/A')}\n\n"
                    "Need more details about any other college?"
                )
            return (
                "🏠 **Hostel Information:**\n\n"
                "Most IITs and NITs guarantee hostel accommodation to all students. Key points:\n"
                "• **IITs**: All students get hostel. Facilities are excellent with sports complexes, gymkhana.\n"
                "• **NITs**: 60–80% students get hostel. Early application recommended.\n"
                "• **IIITs**: Varies — IIIT-H and IIIT-A have on-campus hostels; IIIT-B limited.\n"
                "• **Medical colleges (AIIMS/JIPMER)**: All MBBS students get affordable hostels.\n\n"
                "Ask about a specific college, e.g., 'What are hostels like at IIT Madras?'"
            )
        
        # ── Coding culture queries ─────────────────────────────────────────────
        if any(w in m for w in ["coding", "programming", "competitive", "cp", "codeforces", "leetcode", "hackathon", "tech culture", "coding culture"]):
            college_key, facts = _find_college_fact(m)
            if facts:
                return (
                    f"💻 **Coding Culture at {college_key.title()}:**\n\n"
                    f"{facts['coding_culture']}\n\n"
                    f"🏆 Ranking: {facts.get('ranking', 'N/A')}\n\n"
                    "Want to compare with another college?"
                )
            return (
                "💻 **Coding Culture Rankings (Approximate):**\n\n"
                "🥇 **Legendary**: IIIT Hyderabad, IIT Kanpur, IIT Bombay, IIIT Allahabad\n"
                "🥈 **Excellent**: IIT Delhi, IIT Madras, IIIT Bangalore, NIT Trichy, NIT Warangal\n"
                "🥉 **Very Good**: IIT Kharagpur, IIT Roorkee, NIT Surathkal, IIT Hyderabad\n\n"
                "IIIT-H is considered the best for pure competitive programming + research. "
                "IIT Kanpur is legendary for ICPC performance. NIT Trichy is best among NITs.\n\n"
                "Ask about a specific college, e.g., 'What is the coding culture at IIIT Hyderabad?'"
            )
        
        # ── Comparison queries ─────────────────────────────────────────────────
        if " vs " in m or " or " in m:
            college_key1, facts1 = _find_college_fact(m)
            # Check if two colleges mentioned
            parts = re.split(r'\s+vs\s+|\s+or\s+', m)
            if len(parts) >= 2 and college_key1:
                key2, facts2 = None, None
                for part in parts[1:]:
                    k, f = _find_college_fact(part)
                    if k and k != college_key1:
                        key2, facts2 = k, f
                        break
                
                if facts1 and facts2:
                    return (
                        f"⚖️ **{college_key1.title()} vs {key2.title()}:**\n\n"
                        f"**{college_key1.title()}**\n"
                        f"• Ranking: {facts1.get('ranking', 'N/A')}\n"
                        f"• Coding Culture: {facts1['coding_culture'][:120]}...\n"
                        f"• Hostel: {facts1['hostel'][:100]}...\n\n"
                        f"**{key2.title()}**\n"
                        f"• Ranking: {facts2.get('ranking', 'N/A')}\n"
                        f"• Coding Culture: {facts2['coding_culture'][:120]}...\n"
                        f"• Hostel: {facts2['hostel'][:100]}...\n\n"
                        "💡 **Recommendation:** Use the **College Comparer** feature above to see a side-by-side comparison including cutoff trends, fees, and ROI data!"
                    )
        
        # ── Campus/location ────────────────────────────────────────────────────
        if any(w in m for w in ["campus", "location", "city", "area", "size", "acre", "infrastructure"]):
            college_key, facts = _find_college_fact(m)
            if facts:
                return (
                    f"📍 **Campus Info — {college_key.title()}:**\n\n"
                    f"{facts.get('campus', 'N/A')}\n\n"
                    f"🏆 {facts.get('ranking', '')}\n"
                    f"⭐ Notable: {facts.get('notable', 'N/A')}"
                )

        # ── Documents ──────────────────────────────────────────────────────────
        if any(w in m for w in ["document", "certificate", "paper", "josaa document", "required"]):
            return (
                "📄 **Documents Required for JoSAA Reporting:**\n\n"
                "1. **Provisional Seat Allotment Letter** (from JoSAA portal)\n"
                "2. **Seat Acceptance Fee** payment receipt\n"
                "3. **JEE Main/Advanced Admit Card** + Rank Card\n"
                "4. **Class 10 Marksheet** (for date of birth)\n"
                "5. **Class 12 Marksheet** + Certificate\n"
                "6. **Category Certificate** (OBC-NCL must be issued AFTER April 1 of current year)\n"
                "7. **EWS Certificate** (if applicable, issued in current financial year)\n"
                "8. **PwD Certificate** (if applicable, from CMO/District Medical Board)\n"
                "9. **3 Passport size photographs**\n"
                "10. **Annexure Medical Certificate** (Form provided by institute)\n\n"
                "⚠️ **Critical:** OBC-NCL certificate must be issued **AFTER April 1, 2026** for 2026 admissions. Check our 📋 Document Scanner to verify your certificates!"
            )
        
        # ── OBC/Category certificate ────────────────────────────────────────────
        if any(w in m for w in ["obc", "obc-ncl", "category certificate", "caste certificate", "sc certificate", "st certificate"]):
            return (
                "📋 **Category Certificate Requirements:**\n\n"
                "**OBC-NCL (Other Backward Class - Non-Creamy Layer):**\n"
                "• Must be issued by a Competent Authority (SDM/Tehsildar level)\n"
                "• **Must be issued AFTER April 1 of the year of admission** (e.g., April 1, 2026 for 2026 batch)\n"
                "• Family income must be below ₹8 Lakh per annum\n"
                "• Must state 'Non-Creamy Layer' explicitly\n\n"
                "**SC/ST Certificates:**\n"
                "• Lifetime valid once issued\n"
                "• Must be issued by Tehsildar/SDM or higher authority\n\n"
                "**EWS Certificate:**\n"
                "• Valid only for the financial year it's issued\n"
                "• Income from all sources < ₹8 LPA\n\n"
                "💡 Use the 📋 **Document Scanner** above to upload and verify your certificate automatically!"
            )
        
        # ── NIT vs IIIT ────────────────────────────────────────────────────────
        if "nit vs iiit" in m or "nit or iiit" in m or "iiit vs nit" in m:
            return (
                "⚖️ **NIT vs IIIT — Complete Comparison:**\n\n"
                "**NITs (National Institutes of Technology):**\n"
                "✅ Lower fees (₹1.3–1.6 LPA total course)\n"
                "✅ Wider branch diversity (Civil, Mech, ECE, CS, Chemical)\n"
                "✅ Strong core engineering placements\n"
                "✅ Larger campuses with better infrastructure\n"
                "❌ Average packages lower than IIITs (for CS)\n\n"
                "**IIITs (Indian Institutes of Information Technology):**\n"
                "✅ Specialized CS/IT/AI curriculum (perfect for software roles)\n"
                "✅ IIIT-H, IIIT-A, IIIT-Gwalior have exceptional coding culture\n"
                "✅ Higher average CS packages than most NITs\n"
                "✅ Better research output per student\n"
                "❌ Usually only CS/IT branches available\n"
                "❌ Some PPP IIITs have higher fees\n\n"
                "**Verdict:** If you want CS/IT specifically → top IIIT. If you want core branches or campus life → top NIT."
            )
        
        # ── IIT vs NIT ─────────────────────────────────────────────────────────
        if "iit vs nit" in m or "nit vs iit" in m:
            return (
                "⚖️ **IIT vs NIT — Key Differences:**\n\n"
                "**IITs:**\n"
                "• Avg package: ₹17–30 LPA (college-wide)\n"
                "• Fees: ₹8–10 LPA total\n"
                "• Research culture, global recognition\n"
                "• FAANG/global companies visit frequently\n"
                "• Better GATE scores, MS abroad prospects\n\n"
                "**NITs:**\n"
                "• Avg package: ₹8–22 LPA (varies by NIT)\n"
                "• Fees: ₹1.3–1.6 LPA total ← Much lower!\n"
                "• **Best ROI in India** (NITs are incredibly value-for-money)\n"
                "• Top NITs (Trichy, Warangal, Surathkal) → comparable to lower IITs\n\n"
                "💡 **ROI Perspective:** NIT Trichy CSE at ₹1.5L total fees with ₹22L avg package = **ROI of ~14.7x**. That's exceptional for middle-class families!"
            )
        
        # ── JoSAA counseling process ────────────────────────────────────────────
        if any(w in m for w in ["josaa", "counseling", "counselling", "rounds", "float", "freeze", "slide"]):
            return (
                "📋 **JoSAA 2026 Counseling Process:**\n\n"
                "**6 Rounds of Allotment:**\n"
                "1. Register & fill choices (rank order of college+branch)\n"
                "2. Provisional allotment based on rank + choices\n"
                "3. Choose: **Float**, **Slide**, or **Freeze**\n\n"
                "**Understanding Options:**\n"
                "🔵 **Float** — Keep current seat AND try for higher-preference choices in next round\n"
                "🟡 **Slide** — Keep college, try for better branch in same college\n"
                "🟢 **Freeze** — Lock current seat permanently (no more upgrades)\n\n"
                "**Strategy Tips:**\n"
                "• Use 'Float' in early rounds if you got a decent college but want better\n"
                "• 'Freeze' once you get your target college/branch\n"
                "• Fill 50+ choices in your list for maximum coverage\n"
                "• Use the **Choice Optimizer** above to auto-sort your choices!\n\n"
                "⏰ Registration usually opens in June after JEE results."
            )
        
        # ── Fees / ROI queries ─────────────────────────────────────────────────
        if any(w in m for w in ["fee", "cost", "expensive", "roi", "return", "investment", "value", "money", "afford"]):
            return (
                "💰 **Fees & ROI Guide for Indian Engineering:**\n\n"
                "| Institute | Total Fees | Avg Package | ROI |\n"
                "|-----------|-----------|-------------|-----|\n"
                "| NIT Trichy | ₹1.5L | ₹22L/yr | **14.7x** 🏆|\n"
                "| NIT Surathkal | ₹1.5L | ₹16L/yr | **10.8x** |\n"
                "| DTU Delhi | ₹0.8L | ₹12L/yr | **15x** 🥇|\n"
                "| IIT Bombay | ₹10L | ₹23.5L/yr | **2.35x** |\n"
                "| IIIT-H | ₹3.5L | ₹36L/yr | **10.3x** |\n"
                "| AIIMS Delhi | ₹0.01L | ₹15L/yr | **1500x** 🏆|\n\n"
                "💡 **Best value for middle-class families:**\n"
                "1. **Government NITs** — Low fees, strong placements\n"
                "2. **DTU/NSUT Delhi** — Very low fees, great Delhi location\n"
                "3. **AIIMS** — Almost free MBBS, govt stipend during internship!\n\n"
                "Check the **📊 ROI Analytics** section above for your personalized ranking!"
            )
        
        # ── Computer Science specific ───────────────────────────────────────────
        if any(w in m for w in ["computer science", "cse", "cs branch", "software", "coding job", "sde", "it branch"]):
            return (
                "💻 **CS/CSE Branch Strategy:**\n\n"
                "**Tier-1 CS Picks (if rank allows):**\n"
                "• IIT Bombay/Delhi/Madras CSE → ₹23–27L avg\n"
                "• IIIT Hyderabad CSE → ₹36L avg (Best!)\n"
                "• IIIT Bangalore → ₹28L avg\n\n"
                "**Smart Middle-Rank CS Picks:**\n"
                "• NIT Trichy CSE → ₹22L avg (Best NIT for CS)\n"
                "• NIT Warangal/Surathkal CSE → ₹15–16L avg\n"
                "• IIIT Allahabad/Gwalior → ₹16–18L avg\n\n"
                "**Budget-Friendly CS:**\n"
                "• DTU Delhi CSE → ₹12L avg, only ₹80K total fees!\n"
                "• State IIITs → ₹2–3L fees, ₹10–14L placements\n\n"
                "⚡ **Pro Tip:** Branch > College for CS. A lower-ranked college's CS often beats a top college's Mechanical in placements!"
            )
        
        # ── NEET specific ──────────────────────────────────────────────────────
        if any(w in m for w in ["neet", "mbbs", "medical", "aiims", "jipmer", "doctor"]):
            return (
                "🏥 **NEET/Medical Admission Guide:**\n\n"
                "**Top Government Medical Colleges (AIQ):**\n"
                "1. **AIIMS Delhi** — Fees ~₹1,628/year! Best medical college in India\n"
                "2. **JIPMER Puducherry** — Fees ~₹6,770/year. Coastal + great research\n"
                "3. **AIIMS Jodhpur/Bhopal/Rishikesh** — New AIIMS, excellent infrastructure\n"
                "4. **Maulana Azad Medical (Delhi)** — Top state medical\n\n"
                "**ROI for Medical (Long-term):**\n"
                "• MBBS takes 5.5 years (5 yr + 1 yr internship)\n"
                "• Internship stipend: ₹17,000–40,000/month (varies by state)\n"
                "• After MBBS: PG (MD/MS) or Practice or Abroad\n"
                "• AIIMS graduates: Excellent PG prospects\n\n"
                "**NEET Counseling:** Done through MCC (Medical Counseling Committee) for AIQ (15% seats). State counseling for 85% seats."
            )
        
        # ── Placement queries ──────────────────────────────────────────────────
        if any(w in m for w in ["placement", "package", "salary", "lpa", "recruiter", "company"]):
            college_key, facts = _find_college_fact(m)
            if college_key:
                return (
                    f"💼 **Placements at {college_key.title()}:**\n\n"
                    f"{facts.get('notable', 'Strong placements with top companies.')}\n\n"
                    f"🏆 Ranking: {facts.get('ranking', 'N/A')}\n\n"
                    "Check the **📊 ROI Analytics** section on the dashboard for exact fee/package/ROI data for this college!"
                )
            return (
                "💼 **Placement Overview 2024:**\n\n"
                "**Top Avg Packages:**\n"
                "• IIIT Hyderabad: ₹36 LPA 🏆\n"
                "• IIT Delhi: ₹27 LPA\n"
                "• IIT Kanpur: ₹26 LPA\n"
                "• IIT Bombay: ₹23.5 LPA\n"
                "• NIT Trichy: ₹22 LPA (Best NIT)\n\n"
                "**Top Recruiters (Engineering):**\n"
                "Google, Microsoft, Amazon, Goldman Sachs, Qualcomm, Texas Instruments, Adobe, Flipkart\n\n"
                "📊 Use the **ROI Analytics** section above to see fees vs packages for your predicted colleges!"
            )
        
        # ── Default / fallback ─────────────────────────────────────────────────
        college_key, facts = _find_college_fact(m)
        if college_key and facts:
            return (
                f"ℹ️ **About {college_key.title()}:**\n\n"
                f"📍 Campus: {facts.get('campus', 'N/A')}\n"
                f"🏠 Hostel: {facts['hostel'][:150]}...\n"
                f"💻 Coding Culture: {facts['coding_culture'][:150]}...\n"
                f"🏆 Ranking: {facts.get('ranking', 'N/A')}\n"
                f"⭐ Notable: {facts.get('notable', 'N/A')}\n\n"
                "Ask me about placements, fees, hostel life, or coding culture at any specific college!"
            )
        
        return (
            "That's a great question! Here are some quick tips:\n\n"
            "🎓 **College Choice Strategy:**\n"
            "• If targeting software roles → prioritize branch (CSE) over college tier\n"
            "• If targeting core roles (ISRO, BARC, infra) → prioritize institute reputation\n"
            "• **Best ROI:** Government NITs have the best value-for-money ratio\n\n"
            "Ask me something specific like:\n"
            "• 'What is the hostel at NIT Trichy like?'\n"
            "• 'Compare IIT Bombay vs NIT Warangal'\n"
            "• 'What documents do I need for JoSAA?'\n"
            "• 'Which college has better coding culture — IIIT Hyderabad or IIIT Bangalore?'"
        )
