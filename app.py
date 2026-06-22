from flask import Flask, render_template, request, redirect, session
from dotenv import load_dotenv
from supabase import create_client
import os

from chatbot import ask_llm
from memory import save_message, get_chat_history
from upload_routes import upload_bp
from knowledge_routes import knowledge_page, delete_document

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

# Register upload routes
app.register_blueprint(upload_bp)

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


################################################
# HOME
################################################

@app.route("/")
def home():

    if "user_id" in session:
        return redirect("/chat")

    return redirect("/login")


################################################
# SIGNUP
################################################

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        company_name = request.form["company_name"]
        email = request.form["email"]
        password = request.form["password"]

        try:

            response = supabase_auth.auth.sign_up(
                {
                    "email": email,
                    "password": password
                }
            )

            user_id = response.user.id

            supabase_admin.table(
                "tenants"
            ).insert(
                {
                    "id": user_id,
                    "company_name": company_name,
                    "pinecone_index_name": user_id,
                    "is_active": True
                }
            ).execute()

            return redirect("/login")

        except Exception as e:

            return str(e)

    return render_template("signup.html")


################################################
# LOGIN
################################################

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

            session["user_id"] = response.user.id
            session["tenant_id"] = response.user.id
            session["email"] = response.user.email

            return redirect("/chat")

        except Exception as e:

            return str(e)

    return render_template("login.html")


################################################
# CHAT
################################################

@app.route("/chat", methods=["GET", "POST"])
def chat():

    if "user_id" not in session:
        return redirect("/login")

    tenant_id = session["tenant_id"]
    user_id = session["user_id"]

    if request.method == "POST":

        question = request.form["message"]

        save_message(
            tenant_id,
            user_id,
            "user",
            question
        )

        answer = ask_llm(
            question,
            tenant_id,
            user_id
        )

        save_message(
            tenant_id,
            user_id,
            "assistant",
            answer
        )

    messages = get_chat_history(
        tenant_id,
        user_id
    )

    return render_template(
        "chat.html",
        messages=messages,
        email=session["email"]
    )


################################################
# KNOWLEDGE BASE
################################################

@app.route("/knowledge")
def knowledge():

    return knowledge_page()


################################################
# DELETE DOCUMENT
################################################

@app.route("/delete_document/<document_id>")
def delete_doc(document_id):

    return delete_document(
        document_id
    )


################################################
# LOGOUT
################################################

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


################################################
# MAIN
################################################

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8080,
        debug=True
    )