import os
import sys
from dotenv import load_dotenv
from groq import Groq

# Ensure UTF-8 output on Windows terminal
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 1. Load API Key
load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 2. Define the System Prompt (The AI's personality and instructions)
messages = [
    {
        "role": "system",
        "content": "You are a friendly, helpful, and concise AI coding tutor. You answer clearly and help beginners learn step-by-step."
    }
]

print("=" * 50)
print("🤖 Welcome to your AI Assistant! (Type 'quit' or 'exit' to stop)")
print("=" * 50)

# 3. Interactive Chat Loop
while True:
    # Get user input
    user_input = input("\nYou: ").strip()

    # Check if the user wants to exit
    if user_input.lower() in ["quit", "exit"]:
        print("\n👋 Goodbye! Thanks for chatting.")
        break

    # Ignore empty inputs
    if not user_input:
        continue

    # Add user message to conversation history
    messages.append({"role": "user", "content": user_input})

    # Call Groq API with the full conversation history
    print("\nAI is thinking...")
    response = client.chat.completions.create(
        messages=messages,
        model="openai/gpt-oss-20b",
    )

    ai_reply = response.choices[0].message.content

    # Print the AI's reply
    print(f"\nAI: {ai_reply}")

    # Add AI response to history so it remembers for future questions
    messages.append({"role": "assistant", "content": ai_reply})