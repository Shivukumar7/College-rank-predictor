from app.services.kcet_service import KCETService
from app.services.mht_cet_service import MHTCETService

def test_kcet_accuracy():
    print("Testing KCET rank prediction accuracy...")
    service = KCETService()
    
    # Test case 1: High score, with board marks
    # KCET = 150/180, Board = 290/300
    # kcet_pct = (150/180) * 50 = 41.66
    # board_pct = (290/300) * 50 = 48.33
    # total_pct = 90.0% -> rank expected ~2000
    res1 = service.predict(marks=150, board_marks=290)
    print(f"KCET 150/180, Board 290/300: Predicted Rank = {res1['predicted_rank']}, Percentile = {res1['percentile']}%")
    assert 1500 <= res1['predicted_rank'] <= 2500, f"Expected ~2000 rank, got {res1['predicted_rank']}"

    # Test case 2: Average score, with board marks
    # KCET = 100/180, Board = 280/300
    # kcet_pct = (100/180) * 50 = 27.78
    # board_pct = (280/300) * 50 = 46.67
    # total_pct = 74.45% -> rank expected ~22,000
    res2 = service.predict(marks=100, board_marks=280)
    print(f"KCET 100/180, Board 280/300: Predicted Rank = {res2['predicted_rank']}, Percentile = {res2['percentile']}%")
    assert 20000 <= res2['predicted_rank'] <= 25000, f"Expected ~22000 rank, got {res2['predicted_rank']}"

    # Test case 3: Without board marks (should auto-estimate board percentage)
    res3 = service.predict(marks=100)
    print(f"KCET 100/180, Board None: Predicted Rank = {res3['predicted_rank']}, Percentile = {res3['percentile']}%")
    assert 18000 <= res3['predicted_rank'] <= 28000, f"Expected reasonable estimated rank, got {res3['predicted_rank']}"
    print("KCET accuracy tests passed!")

def test_mht_cet_accuracy():
    print("Testing MHT-CET rank prediction accuracy...")
    service = MHTCETService()
    
    # Test case 1: 160 marks -> expected rank ~2200 (percentile ~99.50)
    res1 = service.predict(marks=160)
    print(f"MHT-CET 160 marks: Predicted Rank = {res1['predicted_rank']}, Percentile = {res1['percentile']}%")
    assert 1800 <= res1['predicted_rank'] <= 2600, f"Expected ~2200, got {res1['predicted_rank']}"
    
    # Test case 2: 140 marks -> expected rank ~5500 (percentile ~99.00)
    res2 = service.predict(marks=140)
    print(f"MHT-CET 140 marks: Predicted Rank = {res2['predicted_rank']}, Percentile = {res2['percentile']}%")
    assert 5000 <= res2['predicted_rank'] <= 6000, f"Expected ~5500, got {res2['predicted_rank']}"

    # Test case 3: 100 marks -> expected rank ~27500 (percentile ~95.00)
    res3 = service.predict(marks=100)
    print(f"MHT-CET 100 marks: Predicted Rank = {res3['predicted_rank']}, Percentile = {res3['percentile']}%")
    assert 25000 <= res3['predicted_rank'] <= 30000, f"Expected ~27500, got {res3['predicted_rank']}"
    print("MHT-CET accuracy tests passed!")

if __name__ == "__main__":
    test_kcet_accuracy()
    test_mht_cet_accuracy()
    print("All accuracy tests verified successfully!")
