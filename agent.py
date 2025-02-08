import json
import os
from groclake.modellake import Modellake
from chroma_db import ChromaDBManager 

# Environment variable setup
GROCLAKE_API_KEY = '1f0e3dad99908345f7439f8ffabdffc4'
GROCLAKE_ACCOUNT_ID = '769a16ce40a17e373db96c19803c0f4d'

os.environ['GROCLAKE_API_KEY'] = GROCLAKE_API_KEY
os.environ['GROCLAKE_ACCOUNT_ID'] = GROCLAKE_ACCOUNT_ID

# Initialize Modellake instance
model_lake = Modellake()

class HealthPartner:
    def __init__(self, data):
        """Initialize with health data and ChromaDB."""
        self.user_data = data
        # Initialize ChromaDBManager
        self.chroma_manager = ChromaDBManager()
        self.chroma_manager.load_health_knowledge() 

        self.collection = self.chroma_manager.get_collection()
        print("Existing collections:", self.collection)

    def query_chromadb(self, category, prompt):
        """Queries ChromaDB and enhances response with LLM."""
        results = self.collection.query(
            query_texts=[prompt],
            where={"category": category},
            n_results=3
        )

        retrieved_docs = []
        if results.get("documents"):
            for doc_list in results["documents"]:
                for doc in doc_list:
                    try:
                        parsed_doc = json.loads(doc) if isinstance(doc, str) else doc
                        if isinstance(parsed_doc, dict):
                            retrieved_docs.append(parsed_doc)
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON for doc: {doc}")

        print("Parsed Documents:", retrieved_docs)

        # Extract text safely
        retrieved_texts = "\n".join(
            [doc.get("text", str(doc)) for doc in retrieved_docs]
        )

        return self.generate_llm_response(prompt, retrieved_texts)

    def generate_llm_response(self, prompt, retrieved_text):
        """Uses Groclake's Modellake to refine and personalize the response."""
        payload = {
            "messages": [
                {"role": "system", "content": "You are a health assistant providing personalized recommendations."},
                {"role": "user", "content": f"User Data: {prompt}\n\nRetrieved Health Knowledge: {retrieved_text}\n\nGenerate a highly personalized and friendly recommendation."}
            ],
            "token_size": 300
        }

        response = model_lake.chat_complete(payload)
        return response.get('answer', "I'm sorry, but I couldn't process the request.")

    def health_monitor(self):
        """Generates health monitoring recommendations using ChromaDB."""
        prompt = f"""
        The user has the following vitals:
        - Heart Rate: {self.user_data.get("heart_rate")} BPM
        - Blood Pressure: {self.user_data.get("blood_pressure")}
        - Oxygen Saturation: {self.user_data.get("oxygen_saturation")}%
        Based on this, detect any health abnormalities and suggest improvements.
        """
        return self.query_chromadb("health_monitor", prompt)

    def fitness_coach(self):
        """Provides fitness recommendations using ChromaDB."""
        prompt = f"""
        The user has an activity level of {self.user_data.get("activity_level")}/10.
        - Steps Taken: {self.user_data.get("steps_taken")}
        - Distance Covered: {self.user_data.get("distance_covered")} km
        - Calories Burned: {self.user_data.get("calories_burned")}
        - Heart Rate: {self.user_data.get("heart_rate")} BPM
        Recommend a personalized fitness plan.
        """
        return self.query_chromadb("fitness_coach", prompt)

    def nutrition_tracker(self):
        """Provides nutrition recommendations using ChromaDB."""
        prompt = f"""
        The user has a calorie burn of {self.user_data.get("calories_burned")} kcal.
        - Stress Level: {self.user_data.get("stress_level")}/10
        - Body Temperature: {self.user_data.get("body_temperature")}°C
        Suggest a personalized meal and hydration plan.
        """
        return self.query_chromadb("nutrition_tracker", prompt)

    def sleep_analysis(self):
        """Provides sleep analysis and improvement suggestions."""
        prompt = f"""
        The user has the following sleep data:
        - Sleep Duration: {self.user_data.get("sleep_duration")} hours
        - Sleep Quality: {self.user_data.get("sleep_quality")}
        - Respiration Rate: {self.user_data.get("respiration_rate")} breaths/min
        Recommend sleep optimization strategies.
        """
        return self.query_chromadb("sleep_analysis", prompt)

    def mental_health(self):
        """Provides stress management and mental health tips."""
        prompt = f"""
        The user has a stress level of {self.user_data.get("stress_level")}/10.
        Suggest mental relaxation techniques and exercises.
        """
        return self.query_chromadb("mental_health", prompt)

    def get_recommendations(self):
        """Generates AI-powered health recommendations using ChromaDB."""
        return {
            "health_monitor": self.health_monitor(),
            "fitness_coach": self.fitness_coach(),
            "nutrition_tracker": self.nutrition_tracker(),
            "sleep_analysis": self.sleep_analysis(),
            "mental_health": self.mental_health()
        }
