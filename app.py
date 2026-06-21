from flask import Flask, render_template, request, redirect, session
from supabase import create_client
from dotenv import load_dotenv
from chatbot import ask_llm
import os
from memory import save_message,get_chat_history
from chatbot import ask_llm
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Auth client
supabase_auth = create_client(
    SUPABASE_URL,
    SUPABASE_ANON_KEY
)

# Admin client
supabase_admin = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY
)


@app.route("/")
def home():

    if "user_id" not in session:
        return redirect("/login")

    if "email" not in session:
        session.clear()
        return redirect("/login")

    return redirect("/chat")


@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        company_name = request.form["company_name"]
        email = request.form["email"]
        password = request.form["password"]

        try:

            auth_response = supabase_auth.auth.sign_up(
                {
                    "email": email,
                    "password": password
                }
            )

            if auth_response.user is None:
                return "Signup failed"

            user_id = auth_response.user.id

            pinecone_index_name = (
                company_name.lower()
                .replace(" ", "_")
                .replace("-", "_")
            )

            supabase_admin.table("tenants").insert(
                {
                    "id": user_id,
                    "company_name": company_name,
                    "pinecone_index_name": pinecone_index_name,
                    "is_active": True
                }
            ).execute()

            return redirect("/login")

        except Exception as e:
            return f"Error: {str(e)}"

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        try:

            response = supabase_auth.auth.sign_in_with_password(
                {
                    "email": email,
                    "password": password
                }
            )

            if response.session is None:
                return "Invalid credentials"

            session["access_token"] = response.session.access_token
            session["user_id"] = response.user.id
            session["email"] = response.user.email

            return redirect("/chat")

        except Exception as e:
            return f"Error: {str(e)}"

    return render_template("login.html")





@app.route("/chat", methods=["GET","POST"])
def chat():

    if "user_id" not in session:

        return redirect("/login")

    tenant_id=session["user_id"]

    user_id=session["user_id"]


    if request.method=="POST":

        question=request.form["message"]

        save_message(
            tenant_id,
            user_id,
            "user",
            question
        )

        answer=ask_llm(question)

        save_message(
            tenant_id,
            user_id,
            "assistant",
            answer
        )


    messages=get_chat_history(
        tenant_id,
        user_id
    )


    return render_template(

        "chat.html",

        email=session.get(
            "email",
            ""
        ),

        messages=messages

    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


if __name__ == "__main__":

    port = int(os.getenv("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )