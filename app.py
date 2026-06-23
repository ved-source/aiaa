from dotenv import load_dotenv
# Load environment variables before importing blueprints or modules that run module-level init code
load_dotenv()

from flask import Flask, render_template, request, redirect, session, jsonify, Response
import os

from chatbot import ask_llm
from memory import save_message, get_chat_history
from upload_routes import upload_bp
from knowledge_routes import knowledge_page, delete_document
from config import supabase, supabase_auth, SECRET_KEY, WHATSAPP_VERIFY_TOKEN
from pinecone_utils import delete_all_tenant_vectors

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Register upload routes
app.register_blueprint(upload_bp)


################################################
# HOME
################################################

@app.route("/")
def home():
    return render_template("home.html")


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

            supabase.table(
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
# LEGAL & STATIC PAGES
################################################

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/deletion")
def deletion():
    return render_template("deletion.html")


@app.route("/app")
def app_entrance():
    if "user_id" in session:
        return redirect("/chat")
    return redirect("/login")


################################################
# API FOR DYNAMIC PAGE INTEGRATIONS
################################################

@app.route("/auth/login", methods=["POST"])
def auth_login_api():
    try:
        # Handle both JSON and form data for maximum compatibility
        if request.is_json:
            data = request.get_json()
            email = data.get("email")
            password = data.get("password")
        else:
            email = request.form.get("email")
            password = request.form.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400

        response = supabase_auth.auth.sign_in_with_password(
            {
                "email": email,
                "password": password
            }
        )
        
        access_token = response.session.access_token
        return jsonify({"access_token": access_token})

    except Exception as e:
        return jsonify({"error": str(e)}), 401


@app.route("/delete-account", methods=["POST"])
def delete_account():
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401

        access_token = auth_header.split(" ")[1]
        
        # Verify token and retrieve user response
        user_res = supabase_auth.auth.get_user(access_token)
        user_id = user_res.user.id

        # 1. Delete all vectors from Pinecone in the tenant_id namespace
        try:
            delete_all_tenant_vectors(user_id)
        except Exception as pe:
            print("Pinecone vectors deletion error:", pe)

        # 2. Delete document records in Supabase
        supabase.table("tenant_documents").delete().eq("tenant_id", user_id).execute()

        # 3. Delete tenant configuration row in Supabase
        supabase.table("tenants").delete().eq("id", user_id).execute()

        # 4. Delete the authentication user using Supabase Admin API
        try:
            supabase.auth.admin.delete_user(user_id)
        except Exception as ae:
            print("Supabase auth user deletion error:", ae)

        return jsonify({"message": "Account and all associated data deleted successfully"})

    except Exception as e:
        print("Account deletion error:", e)
        return jsonify({"error": str(e)}), 400


################################################
# WHATSAPP WEBHOOK
################################################

@app.route("/webhook/whatsapp", methods=["GET", "POST"], strict_slashes=False)
def whatsapp_webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        # Logging all incoming validation details exactly
        print("--- WHATSAPP WEBHOOK VERIFICATION ---")
        print("MODE =", repr(mode))
        print("TOKEN =", repr(token))
        print("ENV TOKEN =", repr(WHATSAPP_VERIFY_TOKEN))
        print("CHALLENGE =", repr(challenge))

        # Safe parsing and comparison
        clean_token = token.strip() if token else ""
        clean_env_token = WHATSAPP_VERIFY_TOKEN.strip() if WHATSAPP_VERIFY_TOKEN else ""

        if mode == "subscribe" and clean_token == clean_env_token:
            print("Verification Success. Returning challenge.")
            # Response must be exact challenge, return as plain text
            return Response(challenge, mimetype="text/plain", status=200)

        print("Verification Failed: Mode or Token mismatch.")
        return Response("Forbidden", mimetype="text/plain", status=403)

    elif request.method == "POST":
        try:
            body = request.get_json()
            print("Received WhatsApp Webhook POST event:", body)
            return jsonify({"status": "received"}), 200
        except Exception as e:
            print("Error parsing WhatsApp Webhook POST payload:", e)
            return jsonify({"error": str(e)}), 400


################################################
# MAIN
################################################

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8080,
        debug=True
    )