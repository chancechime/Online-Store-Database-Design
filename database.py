import os
from dotenv import load_dotenv
import supabase

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
PROJECT_NAME = os.getenv('PROJECT_NAME', 'Default Project Name')

message_printed = False

def get_connection():
    global message_printed
    try:
        connection = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)
        if not message_printed:
            print(f"Successfully connected to Supabase | {PROJECT_NAME}\n")
            message_printed = True
        return connection
    except Exception as e:
        print("Error while connecting to Supabase:", e)
        return None