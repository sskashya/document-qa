import streamlit as st
from openai import OpenAI
import openai
import os
import requests
from PyPDF2 import PdfReader

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb 
chroma_client = chromadb.PersistentClient()

# Show title and description.
st.title("MY Lab 4 question answering chatbot with ChromaDB")
language_model = st.sidebar.radio("Select your LLM Service", 
                                  ["OpenAI"
                                   ])
adv_model = st.sidebar.checkbox("Select Advanced Model from Service", None)
st.write(
    "Select your LLM Service from the sidebar"
)
if language_model and not adv_model:
    st.subheader("You are having a conversation with gpt-4o-mini")

st.write("Select Advanced Model for more expensive LLM Model")
if language_model and adv_model:
    st.subheader("You are having a conversation with gpt-4o")

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
#openai_api_key = st.text_input("OpenAI API Key", type="password")
if 'openai_client' not in st.session_state:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.openai_client = OpenAI(api_key=openai_api_key)

city = st.text_input(label = "Enter your city - Ex. Syracuse")
state = st.text_input(label = "Enter your state - Ex. NY")
location = city + " " + state

def get_current_weather(location, API_key):
    if "," in location:
        location = location.split(",")[0].strip()
    urlbase = "https://api.openweathermap.org/data/2.5/"
    urlweather = f"weather?q={location}&appid={API_key}"
    url = urlbase + urlweather
    response = requests.get(url)
    data = response.json()
# Extract temperatures & Convert Kelvin to Celsius
    temp = data['main']['temp'] - 273.15
    feels_like = data['main']['feels_like'] - 273.15
    temp_min = data['main']['temp_min'] - 273.15 
    temp_max = data['main']['temp_max'] - 273.15
    humidity = data['main']['humidity']
    return {
        "location": location,
        "temperature": round(temp, 2),
        "feels_like": round(feels_like, 2),
        "temp_min": round(temp_min, 2), "temp_max": round(temp_max, 2),
        "humidity": round(humidity, 2)
        }


weather_function_definition = {
    "type" : "function",
    "function" : {
        "name" : "get_current_weather",
        "description" : "Get the current weather",
        "parameters": {
            "type" : "object",
            "properties" : {
                "location" : {
                    "type" : "string",
                    "description" : "The city and state. E.g. Syracuse NY"
                },
                "format" : {
                    "type" : "string",
                    "enum" : ["celsius", "farenheit"],
                    "description": "The temperature unit to use. Infer this from the user's location"
                },
            },
            "required" : ["location", "format"]
        }
    }
}

tools = []

def add_to_tools(function_definition):
    tools.append(function_definition)

def chat_completion_requests(model, messages, tools = None, tool_choice = None):
    try:
        response = st.session_state.openai_client.chat.completions.create(
            model = model,
        )








# Code from Lab 4

ignore = '''
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

if topic == "Select your topic":
    st.warning("Select a topic from the sidebar to continue")

else:
    search = st.button(f"Click here to search for helpful documents related to {topic}")

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

if search:
    query_from_collection(st.session_state['Lab4_vectorDB'], topic)
'''
