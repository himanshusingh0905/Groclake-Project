
import chromadb
import json

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="health_recommendations")

# Load health knowledge from files
use_cases = {
    "health_monitor": "knowledge_base/health_monitoring.json",
    "fitness_coach": "knowledge_base/fitness_coaching.json",
    "nutrition_tracker": "knowledge_base/nutrition_hydration.json",
    "sleep_analysis": "knowledge_base/sleep_analysis.json",
    "mental_health": "knowledge_base/mental_health.json",
}

# Store each file in ChromaDB
for category, file_path in use_cases.items():
    with open(file_path, "r") as f:
        knowledge = json.load(f)  # Load knowledge content
        for idx, entry in enumerate(knowledge):
            collection.add(
                ids=[f"{category}_{idx}"],
                documents=[json.dumps(entry)],
                metadatas=[{"category": category}]
            )

print("Health knowledge stored successfully in ChromaDB.")
