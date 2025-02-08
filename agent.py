
import chromadb
import json
import os
from groclake.modellake import Modellake

# Environment variable setup
GROCLAKE_API_KEY = '1f0e3dad99908345f7439f8ffabdffc4'
GROCLAKE_ACCOUNT_ID = '769a16ce40a17e373db96c19803c0f4d'

os.environ['GROCLAKE_API_KEY'] = GROCLAKE_API_KEY
os.environ['GROCLAKE_ACCOUNT_ID'] = GROCLAKE_ACCOUNT_ID
# Initialize Modellake instance
model_lake = Modellake()

class HealthPartner:
    def __init__(self, data):
        """Initialize with health data."""
        self.user_data = data

        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_collection(name="health_recommendations")

    # def query_chromadb(self, category, prompt):
    #     """Queries ChromaDB and enhances response with LLM."""
    #     results = self.collection.query(
    #         query_texts=[prompt],
    #         where={"category": category},
    #         n_results=3
    #     )

    #     retrieved_docs = [json.loads(doc) for doc in results["documents"][0]] if results["documents"] else []
        
    #     # Convert retrieved documents into a summary
    #     retrieved_texts = "\n".join([doc["text"] for doc in retrieved_docs])
        
    #     # Pass to LLM for better response generation
    #     return self.generate_llm_response(prompt, retrieved_texts)

    # def generate_llm_response(self, prompt, retrieved_text):
    #     """Uses OpenAI GPT to refine and personalize the response."""
    #     llm_prompt = f"""
    #     You are a health assistant providing personalized recommendations.

    #     User Data: {prompt}

    #     Retrieved Health Knowledge:
    #     {retrieved_text}

    #     Based on the above, generate a highly personalized and friendly recommendation.
    #     """

    #     response = openai.ChatCompletion.create(
    #         model="gpt-4-turbo",
    #         messages=[{"role": "system", "content": llm_prompt}],
    #         temperature=0.7
    #     )

    #     return response["choices"][0]["message"]["content"]




    def query_chromadb(self, category, prompt):
        """Queries ChromaDB and enhances response with LLM."""
        results = self.collection.query(
            query_texts=[prompt],
            where={"category": category},
            n_results=3
        )

        # Debugging: Print what ChromaDB is returning
        print("Raw ChromaDB Results:", results)

        retrieved_docs = []
        
        if results.get("documents"):  # Ensure "documents" key exists
            for doc_list in results["documents"]:
                for doc in doc_list:
                    if isinstance(doc, dict):  # Already a dictionary, use directly
                        retrieved_docs.append(doc)
                    elif isinstance(doc, str):  # String: Try to parse JSON
                        try:
                            parsed_doc = json.loads(doc)
                            if isinstance(parsed_doc, dict):  # Ensure it's a dict after parsing
                                retrieved_docs.append(parsed_doc)
                            else:
                                print(f"Unexpected format after parsing: {parsed_doc}")
                        except json.JSONDecodeError:
                            print(f"Error decoding JSON for doc: {doc}")
                    else:
                        print(f"Unexpected document type: {type(doc)} - {doc}")

        # Debugging: Print parsed documents
        print("Parsed Documents:", retrieved_docs)

        # Extract text safely, ensuring doc is a dictionary
        retrieved_texts = "\n".join(
            [doc["text"] if isinstance(doc, dict) and "text" in doc else str(doc) for doc in retrieved_docs]
        )

        # Pass to LLM for better response generation
        return self.generate_llm_response(prompt, retrieved_texts)


    def generate_llm_response(self, prompt, retrieved_text):
        """Uses Groclake's Modellake to refine and personalize the response."""
        
        # Create the payload for Modellake chat completion
        payload = {
            "messages": [
                {"role": "system", "content": "You are a health assistant providing personalized recommendations."},
                {"role": "user", "content": f"User Data: {prompt}\n\nRetrieved Health Knowledge: {retrieved_text}\n\nGenerate a highly personalized and friendly recommendation."}
            ],
            "token_size": 300  # Adjust max tokens as needed
        }

        # Call Groclake's chat completion API
        response = model_lake.chat_complete(payload)

        # Extract and return the assistant's reply
        return response.get('answer', "I'm sorry, but I couldn't process the request.")


#-------------------------------------------------------------------------------------------------

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