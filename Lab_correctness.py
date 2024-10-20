import os
from bespokelabs import BespokeLabs
import streamlit as st
from openai import OpenAI
import openai
from PyPDF2 import PdfReader
import json

st.title("MY Document question answering")
st.write(
    "Upload a document below and ask a question about it – GPT will answer! "
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
#openai_api_key = st.text_input("OpenAI API Key", type="password")
openai_api_key = st.secrets["OPENAI_API_KEY"]
bespoke_key = st.secrets["BESPOKE_KEY"]

extracted_text = {}
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

if 'bespoke_client' not in st.session_state:
    st.session_state.bespoke_client = BespokeLabs(
        # This is the default and can be omitted
        auth_token=bespoke_key,
    )

if 'openai_client' not in st.session_state:
    st.session_state.openai_client = OpenAI(api_key=openai_api_key)

uploaded_file = st.file_uploader(
            "Upload a document (.pdf)", type=("pdf")
    )
    # Ask the user for a question via `st.text_area`.
question = st.text_area(
"Now ask a question about the document!",
placeholder="Can you give me a short summary?",
disabled=not uploaded_file,
)

if uploaded_file and question:
# Process the uploaded file and question.
    document = extract_text_from_pdf(uploaded_file)
    st.session_state.messages = [
    {
        "role": "system",
        "content": f"Here's a document: {document}",
    },
    {
        "role":"user",
        "content": question
    }
    ]
# Generate an answer using the OpenAI API.
    stream = st.session_state.openai_client.chat.completions.create(
    model="gpt-4o-mini",
    messages=st.session_state.messages,
    #stream=False,
    )
    
    response = stream.choices[0].message.content

    factcheck_create_response = st.session_state.bespoke_client.minicheck.factcheck.create(
        claim=response,
        context=document,
    )
    st.write(factcheck_create_response.support_prob)

    if factcheck_create_response.support_prob > 0.8:
        st.write(response)
    else:
        st.write("GPT 4o is not confident it can answer this question without any doubt")