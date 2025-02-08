import chromadb
import json

class ChromaDBManager:
    def __init__(self, db_path="./chroma_db"):
        """Initialize ChromaDB client and collection."""
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection = self.chroma_client.get_or_create_collection(name="health_recommendations")

    def load_health_knowledge(self):
        """Load health knowledge from JSON files into ChromaDB."""
        use_cases = {
            "health_monitor": "knowledge_base/health_monitoring.json",
            "fitness_coach": "knowledge_base/fitness_coaching.json",
            "nutrition_tracker": "knowledge_base/nutrition_hydration.json",
            "sleep_analysis": "knowledge_base/sleep_analysis.json",
            "mental_health": "knowledge_base/mental_health.json",
        }

        for category, file_path in use_cases.items():
            if not isinstance(file_path, str):  
                print(f"Invalid file path for {category}: {file_path}")
                continue

            try:
                with open(file_path, "r") as f:
                    knowledge = json.load(f)

                for idx, entry in enumerate(knowledge):
                    self.collection.add(
                        ids=[f"{category}_{idx}"],
                        documents=[json.dumps(entry)],
                        metadatas=[{"category": category}]
                    )

            except FileNotFoundError:
                print(f"Warning: File {file_path} not found. Skipping...")
            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON from {file_path}. Skipping...")

        print("Health knowledge stored successfully in ChromaDB.")

    def get_collection(self):
        """Retrieve the collection instance."""
        return self.collection
