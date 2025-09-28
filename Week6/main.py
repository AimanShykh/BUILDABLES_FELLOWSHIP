import os
import base64
import re
from email.mime.text import MIMEText
import streamlit as st
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from langchain_helper import create_vector_db, get_qa_chain

# Gmail API Scope
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


# ---- Gmail API Authentication ----
def gmail_authenticate():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


# ---- Send Email ----
def send_email(to_email, subject, body):
    try:
        service = gmail_authenticate()
        message = MIMEText(body)
        message["to"] = to_email
        message["subject"] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        body = {"raw": raw}
        result = service.users().messages().send(userId="me", body=body).execute()
        return f"✅ Appointment confirmation sent! Message ID: {result['id']}"
    except Exception as e:
        return f"❌ Email sending failed: {str(e)}"


# ---- Appointment Scheduler ----
def schedule_appointment(query):
    try:
        # Expected pattern: "... with Dr. XYZ on DATE for NAME, email EMAIL"
        pattern = r"with (.*?) on (.*?) for (.*?), email (.*)"
        match = re.search(pattern, query, re.IGNORECASE)

        if not match:
            return "❌ Could not understand appointment request. Please follow: 'with Dr. XYZ on DATE for NAME, email EMAIL'"

        doctor_name, date, patient_name, email = match.groups()

        confirmation = f"Appointment scheduled for {patient_name} with {doctor_name} on {date}."
        email_status = send_email(email, "Appointment Confirmation", confirmation)

        return confirmation + " " + email_status

    except Exception as e:
        return f"❌ Could not parse appointment request: {str(e)}"


# ---- Streamlit UI ----
st.set_page_config(page_title="Healthcare Agent", page_icon="🩺")
st.title("🩺 Aga Khan Hospital Healthcare Assistant")

if "chain" not in st.session_state:
    create_vector_db()
    st.session_state.chain = get_qa_chain()

query = st.text_input("Ask me anything (FAQ, Doctor info, or Schedule appointment with [Doctor Name] on [Date] for [Patient Name], email [Your Email]):")

if st.button("Submit") and query:
    if "schedule appointment" in query.lower():
        response = schedule_appointment(query)
    else:
        response = st.session_state.chain.invoke({"query": query})["result"]

    st.write("### Response:")
    st.write(response)
