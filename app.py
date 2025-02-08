from flask import Flask, jsonify, render_template
import pandas as pd
import random
import os

# Ensure ChromaDB is initialized
import chroma_db  # This runs the script and loads knowledge into ChromaDB
from agent import HealthPartner  # Import the HealthPartner class

app = Flask(__name__)

# Load the CSV file once when the server starts
CSV_FILE_PATH = "dataset/healthband_data.csv"
if not os.path.exists(CSV_FILE_PATH):
    raise FileNotFoundError(f"CSV file '{CSV_FILE_PATH}' not found.")

df = pd.read_csv(CSV_FILE_PATH)

def fetch_healthband_data():
    """Fetch a random row from the CSV and return it as a dictionary."""
    if df.empty:
        return None, {"error": "CSV file is empty"}
    
    random_index = random.randint(0, len(df) - 1)
    random_data = df.iloc[random_index].to_dict()
    return random_data, None

@app.route('/')
def home():
    """Serve the main HTML page."""
    return render_template('index.html')

@app.route('/get_health_recommendation', methods=['GET'])
def get_health_recommendation():
    """API endpoint to return raw health data and health recommendations."""
    data, error = fetch_healthband_data()
    if error:
        return jsonify(error), 400

    # Create a HealthPartner instance and get recommendations automatically
    health_agent = HealthPartner(data)
    health_report = health_agent.get_recommendations()

    return jsonify({
        "raw_data": data,
        "health_report": health_report
    })

if __name__ == '__main__':
    app.run(debug=True)
