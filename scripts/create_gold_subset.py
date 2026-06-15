import json
import csv
import os

def main():
    json_path = "e:/HackAIthon/data/public-test_1780368312.json"
    csv_path = "e:/HackAIthon/data/gold_subset.csv"
    
    if not os.path.exists(json_path):
        print(f"Error: JSON file not found at {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    first_50 = data[:50]
    
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["qid", "ground_truth"])
        for item in first_50:
            writer.writerow([item["qid"], ""])
            
    print(f"Successfully created template at {csv_path} with {len(first_50)} rows.")
    print("\nMANUAL STEP REQUIRED:")
    print("Please manually fill the 'ground_truth' column in data/gold_subset.csv with the correct answer (A, B, C, D) for each of the 50 questions. Then re-run the comparison script.")

if __name__ == "__main__":
    main()
