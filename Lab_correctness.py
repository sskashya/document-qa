import os
from bespokelabs import BespokeLabs
import streamlit as st
from openai import OpenAI
import openai
from PyPDF2 import PdfReader

st.title("MY Document question answering")
st.write(
    "Upload a document below and ask a question about it – GPT will answer! "
)

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
        auth_token=bespoke_key,
    )

if 'openai_client' not in st.session_state:
    st.session_state.openai_client = OpenAI(api_key=openai_api_key)

uploaded_files = os.listdir("datafiles/")

question = st.text_area(
"Now ask a question about the document!",
placeholder="Can you give me a short summary?",
disabled=not uploaded_files,
)

if uploaded_files and question:
    document = ""
    for file in uploaded_files:
        file_path = os.path.join("datafiles", file)
        text = extract_text_from_pdf(file_path)
        document += text 
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

    if factcheck_create_response.support_prob > 0.75:
        st.write(response)
    else:
        st.write("GPT 4o is not confident it can answer this question without any doubt")