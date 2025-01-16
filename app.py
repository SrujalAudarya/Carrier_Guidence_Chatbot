from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from google.api_core.exceptions import InternalServerError
from dotenv import load_dotenv
import os

# Initialize the Flask app
app = Flask(__name__)

load_dotenv()
# Configure the Generative AI API
genai.configure(api_key=os.getenv('api_key'))
  # Replace 'YOUR_API_KEY' with your actual API key
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

# System prompt
system_prompt = (
    "You are an AI career advisor. Provide insightful, personalized career guidance to students. "
    "For example, recommend suitable career paths, steps to excel, and important skills. "
    "Focus on technology, engineering, arts, and management. Avoid irrelevant topics."
)

# List of common greetings
greetings = ["hi", "Hello", "hey", "good morning", "good evening", "good afternoon", "my name is"]

def generate_career_path(input_text, ai_response):
    """Generates a structured career path based on AI response."""
    return f"<strong>Suggested Path:</strong><br>The AI has suggested:<br>{ai_response}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json  # Expect JSON body
    user_input = data.get('question', '').strip()

    if not user_input:
        return jsonify({'error': 'Please enter a question.'}), 400

    try:
        # Check if input is a greeting
        if user_input.lower() in greetings:
            return jsonify({
                'ai_response': "Hello! How can I assist you with your career today?",
                'career_path': ""
            })

        # Prepare AI input
        full_input = f"{system_prompt}\n\nUser: {user_input}"
        response = chat.send_message(full_input)
        ai_response = response.text

        # Format AI response for HTML (replace newlines with <br>)
        formatted_response = ai_response.replace('\n', '<br>')

        # Generate career path
        career_path = generate_career_path(user_input, formatted_response)

        return jsonify({
            'ai_response': formatted_response,
            'career_path': career_path,
        })
    except InternalServerError:
        return jsonify({'error': 'The server is currently unavailable. Please try again later.'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset():
    """Clears the chat history."""
    global chat
    chat = model.start_chat(history=[])  # Reset the chat history
    return jsonify({'message': 'Chat history cleared.'})

if __name__ == '__main__':
    app.run(debug=True)
