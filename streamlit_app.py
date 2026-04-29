import os

import streamlit as st
from dotenv import load_dotenv
from google import genai

from app import (
    INSUFFICIENT_MESSAGE,
    INSUFFICIENT_MESSAGE_DE,
    answer_user_input,
    get_simple_response,
)


WELCOME_MESSAGE = (
    "Hi, I'm your Expat Germany AI Assistant - your friendly guide for visas, "
    "work, housing, taxes, family life, and everyday questions in Germany."
)

COVERAGE_MESSAGE = (
    "I can help with common expat questions in Germany - including visas, "
    "work, housing, taxes, health insurance, family life, studying, transport, "
    "daily life, travel, hobbies, and Indian community topics. My answers are "
    "based on the documents currently available in my knowledge base. I can "
    "also help with German culture, rules, holidays, weather basics, work "
    "environment, and day-to-day life. I can understand and reply in English "
    "and German."
)

EXAMPLE_QUESTIONS = [
    "How do I apply for an EU Blue Card?",
    "What documents do I need for Anmeldung?",
    "Wie bekomme ich eine Steuer-ID?",
    "Wie mache ich die Anmeldung?",
    "Kann ich mit der Blue Card den Job wechseln?",
    "Wie funktioniert die Krankenversicherung in Deutschland?",
]


def get_client():
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    return genai.Client(api_key=api_key)


def split_answer_and_sources(answer):
    source_markers = ["\n\nSources:\n", "\n\nQuellen:\n"]
    marker = next((item for item in source_markers if item in answer), None)

    if marker is None:
        return answer, []

    main_answer, source_text = answer.split(marker, 1)
    sources = [
        line.removeprefix("- ").strip()
        for line in source_text.splitlines()
        if line.strip()
    ]

    return main_answer, sources


def show_answer(answer):
    main_answer, sources = split_answer_and_sources(answer)

    if INSUFFICIENT_MESSAGE in main_answer or INSUFFICIENT_MESSAGE_DE in main_answer:
        st.info(main_answer)
    else:
        st.write(main_answer)

    if sources:
        with st.expander("Sources / Quellen", expanded=False):
            for source in sources:
                st.markdown(f"- {source}")


st.set_page_config(
    page_title="Expat Germany AI Assistant",
    page_icon="DE",
    layout="centered",
)

with st.sidebar:
    st.header("What I Can Help With")
    st.markdown(
        "- Immigration, visas, Blue Card, PR, and naturalisation\n"
        "- Jobs, unemployment benefits, taxes, and social security\n"
        "- Anmeldung, renting, utilities, insurance, and health insurance\n"
        "- Family life, pregnancy, Kindergeld, Kita, school, and pets\n"
        "- German culture, rules, holidays, weather basics, and work environment\n"
        "- Day-to-day life, transport, festivals, Vereine, and Indian community topics\n"
        "- English and German questions and answers"
    )

    st.header("Current Limitations")
    st.markdown(
        "- I only answer factual expat questions from the documents currently in this project.\n"
        "- I may not cover every city, authority, or personal situation.\n"
        "- I do not provide live weather or real-time updates yet.\n"
        "- I am not a replacement for legal, tax, immigration, medical, or financial advice."
    )

    st.header("Document Reminder")
    st.write(
        "Answers are based on the available scraped documents and should be "
        "checked against the official source for personal decisions."
    )

st.title("Expat Germany AI Assistant")
st.write(WELCOME_MESSAGE)
st.write(COVERAGE_MESSAGE)

st.markdown("**Try asking / Beispiele:**")
example_columns = st.columns(2)
for index, question in enumerate(EXAMPLE_QUESTIONS):
    with example_columns[index % 2]:
        st.caption(question)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": WELCOME_MESSAGE,
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            show_answer(message["content"])
        else:
            st.write(message["content"])

user_question = st.chat_input("Ask a question in English or German")

if user_question:
    st.session_state.messages.append({"role": "user", "content": user_question})

    with st.chat_message("user"):
        st.write(user_question)

    with st.chat_message("assistant"):
        simple_response = get_simple_response(user_question)

        if simple_response:
            answer = simple_response
        else:
            client = get_client()
            if client is None:
                answer = "Missing GEMINI_API_KEY. Add it to your .env file first."
            else:
                with st.spinner("Searching documents..."):
                    try:
                        answer = answer_user_input(client, user_question)
                    except FileNotFoundError:
                        answer = INSUFFICIENT_MESSAGE
                    except Exception as error:
                        answer = f"Error: {error}"

        show_answer(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
