import time
import json
import os

# This script simulates a live data source by writing to a JSON file every 10 seconds.

DATA_SOURCE_FILE = "./data/live/news.json"

def generate_mock_data():
    """Generate a stream of mock news articles."""
    articles = [
        {"id": 1, "content": "TechCorp announces a breakthrough in AI-powered research tools.", "source": "TechNews"},
        {"id": 2, "content": "Global markets respond to new inflation data.", "source": "BusinessBeat"},
        {"id": 3, "content": "Science Today: The future of space exploration looks bright.", "source": "ScienceWeekly"},
        {"id": 4, "content": "Health Watch: New study on the benefits of a balanced diet.", "source": "HealthMagazine"},
    ]
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(DATA_SOURCE_FILE), exist_ok=True)

    while True:
        with open(DATA_SOURCE_FILE, "w") as f:
            for article in articles:
                f.write(json.dumps(article) + '\n')

        time.sleep(10) # Update every 10 seconds
        articles.append({
            "id": len(articles) + 1,
            "content": f"New article content {time.time()}",
            "source": "LiveData"
        })

if __name__ == "__main__":
    generate_mock_data()
