from dotenv import load_dotenv
import os
import requests
class genai:
    def __init__(self):
        load_dotenv()
        self.api = os.getenv("GEMINI_API")
        # Using a valid and recent model. The API key is checked before the request.
        self.model = "gemini-2.5-flash"
        self.end_point = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def ai(self, query: str) -> str | None:
        """
        Sends a query to the Gemini API and returns the response.
        :param query: The user's query string.
        :return: The text response from the AI, or None if an error occurs.
        """
        if not self.api:
            print("Error: GEMINI_API key not found. Please set it in your .env file.")
            return None

        data = {
            "contents": [{"parts": [{"text": query}]}]
        }
        # The API key is now passed as a query parameter
        response = requests.post(f"{self.end_point}?key={self.api}", json=data)

        if response.status_code == 200:
            response_data = response.json()
            return response_data['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None

if __name__ == '__main__':
    # This block runs only when ai.py is executed directly
    # It allows for interactive testing.
    ai_instance = genai()
    user_query = input("You: ")
    if user_query:
        response = ai_instance.ai(user_query)
        if response:
            print(f"AI: {response}")