from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'secret'

# Make zip function available in Jinja templates
app.jinja_env.globals.update(zip=zip)

# -------------------------
# Predefined interview data
# -------------------------

questions = [
    "Tell me about yourself.",
    "What are your strengths and weaknesses?",
    "Why do you want to work with us?",
    "Describe a challenge you faced and how you handled it.",
    "Where do you see yourself in 5 years?",
]

keyword_scores = {
    0: ['experience', 'background', 'skills'],
    1: ['strength', 'weakness', 'improve'],
    2: ['culture', 'mission', 'growth'],
    3: ['challenge', 'solution', 'result'],
    4: ['goal', 'future', 'career'],
}

# -------------------------
# Scoring Logic
# -------------------------

def evaluate_answer(index, answer):
    score = 0
    feedback = ""

    if not answer.strip():
        return 0, "You didn't answer this question."

    keywords = keyword_scores.get(index, [])
    for word in keywords:
        if word.lower() in answer.lower():
            score += 3  # Each keyword matched gives 3 points

    if score > 9:
        score = 10
        feedback = "Excellent and detailed answer!"
    elif score >= 6:
        feedback = "Good answer, but could use more depth."
    elif score >= 3:
        feedback = "Fair attempt. Try to be more specific."
    else:
        feedback = "Needs improvement. Try including more relevant details."

    return score, feedback

# -------------------------
# Routes
# -------------------------

@app.route('/')
def landing():
    flash("Welcome to the AI Interviewer!")  # Optional flash message
    return render_template('landing.html')

@app.route('/start')
def start():
    session['current_question'] = 0
    session['answers'] = [''] * len(questions)
    return redirect(url_for('interview'))

@app.route('/interview', methods=['GET', 'POST'])
def interview():
    if request.method == 'POST':
        q_index = session.get('current_question', 0)
        answer = request.form['answer']
        answers = session.get('answers', [''] * len(questions))
        answers[q_index] = answer
        session['answers'] = answers

        if 'next' in request.form and q_index < len(questions) - 1:
            session['current_question'] += 1
        elif 'prev' in request.form and q_index > 0:
            session['current_question'] -= 1
        elif 'submit' in request.form:
            return redirect(url_for('feedback'))

    q_index = session.get('current_question', 0)
    question = questions[q_index]
    answer = session.get('answers', [''])[q_index]

    return render_template(
        'interview.html',
        question=question,
        q_index=q_index,
        total=len(questions),
        answer=answer
    )

@app.route('/feedback')
def feedback():
    answers = session.get('answers', [])
    data = []

    for i, answer in enumerate(answers):
        score, feedback_text = evaluate_answer(i, answer)
        data.append((questions[i], answer, feedback_text, score))

    return render_template('feedback.html', data=data)

# -------------------------
# Run App
# -------------------------

if __name__ == '__main__':
    app.run(debug=True)
