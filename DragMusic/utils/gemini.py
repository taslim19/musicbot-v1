import google.generativeai as genai
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

async def get_gemini_fix(error_message, code, mode="python"):
    prompt = (
        f"I tried to run the following {mode} code/command and got this error.\n"
        f"Code/Command:\n{code}\n\n"
        f"Error:\n{error_message}\n\n"
        "Please provide a corrected version of the code/command only. Do not explain, just output the fixed code/command."
    )
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return None 