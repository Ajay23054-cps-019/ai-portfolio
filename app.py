from flask import Flask, render_template, request, jsonify
from ai import genai
import json
import os

app = Flask(__name__)

# This is the same logic from your gen.py, adapted for the web app
def build_final_query(details: dict) -> str:
    """Constructs the final detailed prompt for the AI."""
    prompt = f"Please create a visually stunning, modern, animated, and fully-featured single-file portfolio website with the following details:\n"
    prompt += f"- Name: {details['name']}\n"
    prompt += f"- Title: {details['title']}\n"
    prompt += f"- User's 'About Me' draft (please professionally rewrite and expand this to be more engaging): {details['about']}\n"
    prompt += f"- Skills: {details['skills']}\n"
    
    contact_parts = [f"Email ({details['contact']['email']})"]
    if details['contact']['linkedin']:
        contact_parts.append(f"LinkedIn ({details['contact']['linkedin']})")
    if details['contact']['github']:
        contact_parts.append(f"GitHub ({details['contact']['github']})")
    
    prompt += f"- Contact: {', '.join(contact_parts)}\n"
    
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

@app.route('/')
def index():
    """Renders the new landing page."""
    return render_template('landing.html')

@app.route('/builder')
def builder():
    """Renders the main form page."""
    return render_template('builder.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Handles form submission, calls the AI, and returns the result."""
    try:
        # Collect basic details
        details = {
            "name": request.form.get('name'),
            "title": request.form.get('title'),
            "about": request.form.get('about'),
            "skills": request.form.get('skills'),
            "contact": {
                "email": request.form.get('email'),
                "linkedin": request.form.get('linkedin'),
                "github": request.form.get('github'),
            },
            "projects": []
        }

        # Collect dynamic project details
        project_names = request.form.getlist('project_name[]')
        project_descs = request.form.getlist('project_desc[]')
        project_techs = request.form.getlist('project_tech[]')

        for i in range(len(project_names)):
            if project_names[i]: # Only add if project name is not empty
                details['projects'].append({
                    "name": project_names[i],
                    "description": project_descs[i],
                    "tech": project_techs[i]
                })

        # Build the query and call the AI
        final_query = build_final_query(details)
        ai_instance = genai()
        response = ai_instance.ai(final_query)

        if not response:
            return jsonify({'error': 'Failed to get a response from the AI.'}), 500

        # Parse the AI's response
        clean_response = response.strip().replace("```json", "").replace("```", "")
        data = json.loads(clean_response)

        if "code" in data and data["code"]:
            # Save the file to the user's Downloads folder
            downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
            os.makedirs(downloads_path, exist_ok=True) # Ensure the directory exists
            file_path = os.path.join(downloads_path, "portfolio.html")
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(data["code"])
            
            return jsonify({'success': True, 'message': f'Success! Portfolio saved to {file_path}', 'html_code': data['code']})
        else:
            return jsonify({'error': data.get("info", "AI did not return code. Please try again with more details.")}), 400

    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)