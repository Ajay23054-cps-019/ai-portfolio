from ai import genai
import json
import time
import sys

def ask_question(prompt: str, multi_line: bool = False) -> str:
    """Helper function to ask a question and get user input."""
    print(f"\n{prompt}")
    if multi_line:
        print("(Enter a blank line when you're finished)")
        lines = []
        while True:
            line = input("> ")
            if not line:
                break
            lines.append(line)
        return "\n".join(lines)
    else:
        return input("> ")

def collect_user_info() -> dict:
    """Guides the user through a form to collect portfolio details."""
    print("--- Portfolio Builder ---")
    print("Please provide the following details to build your portfolio.")
    
    details = {
        "name": ask_question("What is your full name?"),
        "title": ask_question("What is your profession/title? (e.g., Software Engineer)"),
        "about": ask_question("Tell me about yourself. (A short introduction)", multi_line=True),
        "skills": ask_question("List your key skills, separated by commas. (e.g., Python, React, SQL)"),
        "projects": [],
        "contact": {
            "email": ask_question("What is your email address?"),
            "linkedin": ask_question("What is your LinkedIn profile URL?"),
            "github": ask_question("What is your GitHub profile URL?"),
        }
    }

    # Collect project details
    while True:
        add_project = ask_question("\nDo you want to add a project? (yes/no)").lower()
        if add_project != 'yes':
            break
        project = {
            "name": ask_question("Project Name:"),
            "description": ask_question("Project Description:", multi_line=True),
            "tech": ask_question("Technologies Used (comma-separated):"),
        }
        details["projects"].append(project)
        
    return details

def build_final_query(details: dict) -> str:
    """Constructs the final detailed prompt for the AI."""
    prompt = f"Please create a professional, animated, single-file portfolio website with the following details:\n"
    prompt += f"- Name: {details['name']}\n"
    prompt += f"- Title: {details['title']}\n"
    prompt += f"- About Me: {details['about']}\n"
    prompt += f"- Skills: {details['skills']}\n"
    prompt += f"- Contact: Email ({details['contact']['email']}), LinkedIn ({details['contact']['linkedin']}), GitHub ({details['contact']['github']})\n"
    
    if details["projects"]:
        prompt += "\n- Projects:\n"
        for i, p in enumerate(details["projects"]):
            prompt += f"  - Project {i+1}: {p['name']}\n"
            prompt += f"    Description: {p['description']}\n"
            prompt += f"    Technologies: {p['tech']}\n"
            
    prompt += """
Give the response in a single JSON object with the following format. Do NOT include any other text or markdown formatting outside of the JSON object.
{
    "info": null,
    "code": "<!-- The complete HTML, CSS, and JS code for the portfolio goes here. Make it look amazing. -->"
}"""
    return prompt

def loading_animation(duration: float):
    """Displays a simple loading animation."""
    animation = "|/-\\"
    start_time = time.time()
    while time.time() - start_time < duration:
        for char in animation:
            sys.stdout.write(f"\rBuilding your portfolio... {char}")
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write("\rDone!                               \n")

def main():
    user_details = collect_user_info()
    final_query = build_final_query(user_details)

    ai_instance = genai()
    
    print("\nThank you! Sending your details to the AI to build your portfolio.")
    
    # Simulate a loading animation while the API call is made in the background
    # In a real GUI app, this would be handled with threading.
    # For a CLI, we'll just show it before the blocking API call.
    loading_animation(2) # Show animation for 2 seconds before the call
    
    response = ai_instance.ai(final_query)

    if response:
        try:
            clean_response = response.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_response)

            if "code" in data and data["code"]:
                with open("portfolio.html", "w", encoding="utf-8") as f:
                    f.write(data["code"])
                print("\nSuccess! Your portfolio has been saved to portfolio.html")
            else:
                print("\nAI did not return code. It might need more info:")
                print(data.get("info", "No additional info provided."))

        except json.JSONDecodeError:
            print("\nAI returned a non-JSON response. Saving raw output to 'response.txt'.")
            with open("response.txt", "w", encoding="utf-8") as f:
                f.write(response)
    else:
        print("\nDid not receive a response from the AI.")

if __name__ == "__main__":
    main()