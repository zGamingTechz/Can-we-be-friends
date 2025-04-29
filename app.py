from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client, Client
from questions import questions
from loading_text import text
import random
import keys

app = Flask(__name__)
app.config["SECRET_KEY"] = keys.secret_key

# Initialize Supabase
supabase_url = keys.url
supabase_key = keys.key
supabase: Client = create_client(supabase_url, supabase_key)


@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']

        # Store the email in session
        session['email'] = email

        # Check if user exists
        user_data = supabase.table('users').select('*').eq('email', email).execute()

        if user_data.data:
            return redirect("/summary")

        # Create a new user
        new_user = {
            'username': username,
            'email': email,
            'score': 0,
            'qid': []  # Initialize the empty array for responses
        }
        supabase.table('users').insert(new_user).execute()

        return redirect(url_for("loading", source="login"))

    return render_template("login.html")


@app.route('/home', methods=["GET", "POST"])
def home():
    if 'qid_index' not in session:
        session['qid_index'] = 0

    qid_index = session['qid_index']
    user_data = supabase.table('users').select('*').eq('email', session['email']).execute()

    if user_data.data:
        user = user_data.data[0]

    if request.method == "POST":
        answer = request.form['answer']

        if answer.lower() == 'yes':
            answer_value = 1
            user['score'] += questions[qid_index]["points"]
        elif answer.lower() == 'no':
            answer_value = 0

        # Update the user's response in the qid array
        qid_array = user['qid']
        if len(qid_array) <= qid_index:
            qid_array.append(answer_value)
        else:
            qid_array[qid_index] = answer_value

        # Update the user record in Supabase
        supabase.table('users').update({
            'qid': qid_array,
            'score': user['score']
        }).eq('email', session['email']).execute()

        session['qid_index'] += 1
        if session['qid_index'] >= len(questions):
            session.pop('qid_index')
            return redirect(url_for("loading", source="home"))

        return redirect("/home")

    return render_template("home.html", question_text=questions[qid_index]["text"], qid=qid_index)


@app.route("/summary")
def summary():
    user_data = supabase.table('users').select('*').eq('email', session['email']).execute()

    if user_data.data:
        user = user_data.data[0]
        return render_template("summary.html", score=user['score'])

    return redirect('/')


@app.route("/loading")
def loading():
    source = request.args.get("source")

    if source == "login":
        messages = ["Setting up your experience...", "Creating unique questions..."]
        duration = 6
        redirect_url = "/home"
    elif source == "home":
        messages = random.sample(text, k=4)
        duration = 12
        redirect_url = "/summary"

    return render_template("loading.html", messages=messages, duration=duration, redirect_url=redirect_url)


@app.route("/clear")
def clear_session():
    session.pop("email", None)
    session.pop("qid_index", None)
    return "Session cleared!"


if __name__ == '__main__':
    app.run(debug=True)