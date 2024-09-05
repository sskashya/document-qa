import streamlit as st
from openai import OpenAI
import openai

# Show title and description.
st.title("MY Document question answering")
st.write(
    "Upload a document below and your choice of GPT will summarize it to your liking! "
)
st.write(
    "Select your options from the sidebar"
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
#openai_api_key = st.text_input("OpenAI API Key", type="password")
openai_api_key = st.secrets["OPENAI_API_KEY"]

client = OpenAI(api_key=openai_api_key)

summary = st.sidebar.radio("Select your summary style",
                           ["Summarize doc in 100 words",
                            "Summarize doc in 2 connecting paragrpahs",
                            "Summarize doc in 5 bullet points"])

language_model = st.sidebar.radio("Select your Language Model", 
                                  ["gpt-4o", 
                                   "gpt-4o-mini",
                                   "Use Advanced Model"])

if summary and language_model:
# Let the user upload a file via `st.file_uploader`.
    uploaded_file = st.file_uploader(
        "Upload a document (.txt or .md)", type=("txt", "md")
    )

    if uploaded_file:

    # Process the uploaded file and question.
        document = uploaded_file.read().decode()
        messages = [
        {
            "role": "system",
            "content": f"Here's a document: {document} \n\n---\n\n {summary}",
        }
    ]
        if language_model == "Use Advanced Model":
    # Generate an answer using the OpenAI API.
            stream = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            stream=True,
        )
        else:
            stream = client.chat.completions.create(
                model=language_model,
                messages=messages,
                stream=True,
            )
        # Stream the response to the app using `st.write_stream`.
        st.write_stream(stream) 
       
