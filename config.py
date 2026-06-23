import os
from dotenv import load_dotenv
from supabase import create_client
from pinecone import Pinecone

# Load environment variables first
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
SECRET_KEY = os.getenv("SECRET_KEY")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "aiaa-secret-token")

# Supabase Admin/Service-Role Client
supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY
)

# Supabase Public/Anon Client (for Auth)
supabase_auth = create_client(
    SUPABASE_URL,
    SUPABASE_ANON_KEY
)

# Pinecone client init
pc = None
index = None
if PINECONE_API_KEY and PINECONE_INDEX_NAME:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)