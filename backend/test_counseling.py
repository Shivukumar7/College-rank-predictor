import sys
from app.services.college_service import JEEMainCollegeService, MHTCETCollegeService, COMEDKCollegeService
from app.services.counseling_service import CounselingService

def test_trends():
    print("Testing cutoff trends...")
    
    # 1. JEE Main
    jee_service = JEEMainCollegeService()
    # Let's search for any data in full_df
    if not jee_service._full_df.empty:
        # get first row to get real names
        row = jee_service._full_df.iloc[0]
        inst = row["Institute"]
        branch = row["Branch"]
        cat = row["Category"]
        quota = row.get("Quota", "Other State")
        print(f"Querying JEE Main trends for: {inst}, {branch}, {cat}, {quota}")
        trends = jee_service.get_cutoff_trends(inst, branch, cat, quota)
        print(f"JEE Main trends retrieved: {len(trends)} records.")
        assert len(trends) > 0, "Should have trends data"
    else:
        print("JEE Main dataframe is empty.")

    # 2. MHT-CET
    mht_service = MHTCETCollegeService()
    if not mht_service._full_df.empty:
        row = mht_service._full_df.iloc[0]
        inst = row["College"]
        branch = row["Branch"]
        cat = row["Category"]
        print(f"Querying MHT-CET trends for: {inst}, {branch}, {cat}")
        trends = mht_service.get_cutoff_trends(inst, branch, cat)
        print(f"MHT-CET trends retrieved: {len(trends)} records.")
        assert len(trends) > 0, "Should have trends data"
    else:
        print("MHT-CET dataframe is empty.")

    # 3. COMEDK
    comedk_service = COMEDKCollegeService()
    if not comedk_service._full_df.empty:
        row = comedk_service._full_df.iloc[0]
        inst = row["College"]
        branch = row["Branch"]
        cat = row["Category"]
        print(f"Querying COMEDK trends for: {inst}, {branch}, {cat}")
        trends = comedk_service.get_cutoff_trends(inst, branch, cat)
        print(f"COMEDK trends retrieved: {len(trends)} records.")
        assert len(trends) > 0, "Should have trends data"
    else:
        print("COMEDK dataframe is empty.")

def test_optimize():
    print("Testing Choice Preference Optimizer...")
    counseling = CounselingService()
    colleges = [
        {"name": "National Institute of Technology Calicut", "branch": "Computer Science", "type": "NIT", "closing_rank": 15000, "opening_rank": 8000, "chance": 75, "quota": "Other State"},
        {"name": "Indian Institute of Technology Bombay", "branch": "Computer Science", "type": "IIT", "closing_rank": 600, "opening_rank": 1, "chance": 10, "quota": "All India"},
        {"name": "International Institute of Information Technology Hyderabad", "branch": "Computer Science", "type": "IIIT", "closing_rank": 2000, "opening_rank": 500, "chance": 45, "quota": "All India"},
    ]
    optimized = counseling.optimize_choices(colleges, ["Computer Science"])
    print(f"Optimized sequence choices count: {len(optimized)}")
    assert optimized[0]["type"] == "IIT", "IIT should be ranked first due to tier"
    print("Optimization test passed.")

def test_chatbot():
    print("Testing AI Chatbot...")
    counseling = CounselingService()
    reply = counseling.chat_response("what documents do I need?")
    print(f"Chatbot reply snippet: {reply[:100]}...")
    assert "marksheet" in reply.lower() or "document" in reply.lower() or "provisional" in reply.lower()
    
    # Context-aware test
    context_reply = counseling.chat_response("what are my chances?", {"exam": "jee-main", "rank": 15000, "category": "general"})
    print(f"Chatbot context reply snippet: {context_reply[:100]}...")
    assert "15,000" in context_reply, "Should personalize response with rank"
    print("Chatbot test passed.")

if __name__ == "__main__":
    try:
        test_trends()
        test_optimize()
        test_chatbot()
        print("\nALL SERVICES VERIFIED SUCCESSFULLY!")
    except AssertionError as e:
        print(f"Assertion failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Exception raised: {e}")
        sys.exit(1)
