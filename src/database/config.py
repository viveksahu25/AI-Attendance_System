import streamlit as st
from supabase import create_client, Client

url = st.secrets["SUPABASE_URL"].strip()
key = st.secrets["SUPABASE_KEY"].strip()

supabase: Client = create_client(url, key)

