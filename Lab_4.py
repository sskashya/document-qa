import streamlit as st
from openai import OpenAI
import openai
import os
from PyPDF2 import PdfReader

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb 
chroma_client = chromadb.Client()

# Show title and description.
st.title("MY Lab 4 question answering chatbot with ChromaDB")
st.write(
    "Select your LLM Service from the sidebar"
)
st.write("Select Advanced Model for more expensive LLM Model")

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
#openai_api_key = st.text_input("OpenAI API Key", type="password")
if 'openai_client' not in st.session_state:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.openai_client = OpenAI(api_key=openai_api_key)

language_model = st.sidebar.radio("Select your LLM Service", 
                                  ["OpenAI"
                                   ])

adv_model = st.sidebar.checkbox("Select Advanced Model from Service", None)

topic = st.sidebar.selectbox("Topic", ("Select your topic", "Text Mining", "GenAI", "Data Science"))

if language_model and adv_model:
    st.subheader("You are having a conversation with gpt-4o")
else:
    st.subheader("You are having a conversation with gpt-4o-mini")

if 'messages' not in st.session_state:
    st.session_state['messages'] = [{'role':'assistant', 'content':'How can I help you?'}]

collection = chroma_client.get_or_create_collection(name = "mycollection")

folder_path = "datafiles/"
texts = []
for file in os.listdir(folder_path):
    file_extension = file.name.split('.')[-1]
    if file_extension == 'pdf':
        file_path = os.path.join(folder_path, file)
        with open(file_path, "rb") as pdf_file:
            reader = PdfReader(pdf_file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text = page.extract_text()
    texts += text

filename = []
for file in os.listdir(folder_path):
    filename += file 

def add_to_collection(collection, texts, filename):
    openai_client = st.session_state.openai_client
    response = openai_client.embeddings.create(
        input = (text for text in texts),
        model = "text-embedding-3-small"
    )
    embedding = response.data[0].embedding
    collection.add(
        documents = [texts],
        ids = [filename],
        embeddings = [embedding]
    )

def query_from_collection(collection, topic):
    openai_client = st.session_state.openai_client
    query_response = openai_client.embeddings.create(
        input = topic,
        model = "text-embedding-3-small"
    )
    query_embedding = query_response.data[0].embedding
    results = collection.query(
        query_embeddings = [query_embedding],
        n_results = 3
    )
    for i in range(len(results['documents'][0])):
        doc = results['documents'][0][i]
        doc_id = results['ids'][0][i]
        st.write(f"The following file syllabus may be helpful: {doc_id}")

'''
sys_messages = 
Always ask the user "Do you need more info?" after their first prompt. 
If the user replies with Yes, then provide more info followed by "Do you need more info?" but,
if they reply with No, the assistant should reply with "What else can I help you with?" and nothing else. 
Finally, provide answers so that someone who is 10 years-old will be able to understand.


for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Type Here"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    message = st.session_state.messages[-5:]
    message.append({"role": "system", "content": sys_messages})

    if language_model == "OpenAI" and not adv_model:
        # Generate an answer using the OpenAI API.
        stream = st.session_state.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=message,
            stream=True,
        )
    else:
        stream = st.session_state.client.chat.completions.create(
            model="gpt-4o",
            messages=message,
            stream=True,
        )
    with st.chat_message("assistant"):
        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})
    '''