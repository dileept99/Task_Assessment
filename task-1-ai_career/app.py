from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

genai.configure(api_key="AIzaSyAzuMF1AFn-Z3DYJMX_20A8rem_mPgvH7A")

model = genai.GenerativeModel("gemini-3-flash-preview")

PROGRAM_LINKS = {
    "Leadership Essentials Program": "https://iamironlady.com/individualPrograms/Leadership_Essentials_Program",
    "100 Board Members Program": "https://iamironlady.com/individualPrograms/100_Board_Members_Program",
    "C-Suite League": "https://iamironlady.com/individualPrograms/C-Suite_League_%E2%80%93_Master_of_Business_Warfare",
    "2-Day Leadership Masterclass": "https://workshops.iamironlady.com/masterclass_app"
}

SYSTEM_PROMPT = """
You are an AI Career Clarity Companion for Iron Lady, a women-focused leadership
and career advancement organization.

Iron Lady offers the following programs:

1) Leadership Essentials Program  
   - For early to mid-level professionals
   - Focus on leadership fundamentals, confidence, communication, and decision-making

2) 100 Board Members Program (Master Politics & Lead in 6 Months)  
   - For senior professionals and aspiring board members
   - Focus on governance, influence, organizational politics, and strategic leadership

3) C-Suite League – Master of Business Warfare  
   - For senior leaders and founders
   - Focus on business strategy, power dynamics, high-stakes decision-making, and executive leadership

4) 2-Day Leadership Masterclass  
   - Short, intensive exposure program
   - Ideal for exploration or initial leadership mindset building

Your role is to:
- Understand the learner’s background, experience level, and concerns
- Recommend the MOST suitable program from the list above
- Clearly explain WHY that program fits
- Outline the learner journey (enquiry → learning → support)
- Respond in a warm, confident, and empowering tone

Only recommend from the programs listed above.
Do not invent or assume additional programs.
Always clearly mention the recommended program name exactly as listed,
using the format:
"Recommended Program: <Program Name>"
Do not use markdown formatting (no **, ###, or bullet symbols).
Use plain text with short headings written normally.

"""

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.json

    prompt = f"""
{SYSTEM_PROMPT}

Learner Background:
{data['background']}

Career Goal:
{data['goal']}

Experience / Career Break:
{data['experience']}

Biggest Concern:
{data['concern']}

Recommend the most suitable program and explain the learner journey.
"""

    response = model.generate_content(prompt)
    ai_text = response.text

    # Detect recommended program
    selected_link = None
    for program, link in PROGRAM_LINKS.items():
        if program.lower() in ai_text.lower():
            selected_link = link
            break

    # Append link safely
    if selected_link:
        ai_text += f"\n\n🔗 Learn more about this program:\n{selected_link}\n\n🌐 Official website:\nhttps://www.iamironlady.com"

    return jsonify({
        "response": ai_text
    })

if __name__ == "__main__":
    app.run(debug=True)
