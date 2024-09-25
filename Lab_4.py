import streamlit as st
from openai import OpenAI
import openai
import os
from PyPDF2 import PdfReader

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb 
chroma_client = chromadb.PersistentClient()

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

#topic = st.sidebar.selectbox("Topic", ("Select your topic", "Text Mining", "GenAI", "Data Science"))

if language_model and adv_model:
    st.subheader("You are having a conversation with gpt-4o")
else:
    st.subheader("You are having a conversation with gpt-4o-mini")

def add_to_collection(collection, texts, filename):
        openai_client = st.session_state.openai_client
        response = openai_client.embeddings.create(
            input = (texts),
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
        query_embeddings = [query_embedding]
    )
    docs_id = []
    for i in range(len(results['documents'][0])):
        doc = results['documents'][0][i]
        doc_id = results['ids'][0][i]
        docs_id.append(doc_id)
    #return docs_id
    extracted_texts = {}
    for doc_id in docs_id:
        file_path = os.path.join(folder_path, doc_id)
        with open(file_path, "rb") as pdf_file:
            reader = PdfReader(pdf_file)
            full_text = ""
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                full_text += page.extract_text()
            extracted_texts[doc_id] = full_text
    return extracted_texts

#if topic == "Select your topic":
    #st.warning("Select a topic from the sidebar to continue")

#else:
    #search = st.button(f"Click here to search for helpful documents related to {topic}")

if 'Lab4_vectorDB' not in st.session_state:
    st.session_state['Lab4_vectorDB'] = chroma_client.get_or_create_collection(name = "Mycollection")

folder_path = "datafiles/"
for file in os.listdir(folder_path):
    file_extension = file.split('.')[-1]
    if file_extension.lower() == 'pdf':
        file_path = os.path.join(folder_path, file)
        texts = ""
        with open(file_path, "rb") as pdf_file:
            reader = PdfReader(pdf_file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text = page.extract_text()
                texts += text
        add_to_collection(st.session_state['Lab4_vectorDB'], texts, file)

#if search:
    #query_from_collection(st.session_state['Lab4_vectorDB'], topic)

if 'messages' not in st.session_state:
    st.session_state['messages'] = [{'role':'assistant', 'content':'How can I help you?'}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Type Here"):
    st.session_state.messages.append({"role":"user", "content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    retrieved_docs = query_from_collection(st.session_state['Lab4_vectorDB'], prompt)

    sys_messages = f"Here are the related files: {', '.join(retrieved_docs)}. Use this information to answer the user question."

    message = st.session_state.messages[-11:]
    message.append({"role":"system", "content":sys_messages})

    if language_model == "OpenAI" and not adv_model:
    # Generate an answer using the OpenAI API.
        stream = st.session_state.openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=message,
        stream=True,
        )
    else:
        stream = st.session_state.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=message,
                stream=True,
            ) 
    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    
    st.session_state.messages.append({"role":"assistant", "content": response})
