import os
import re

from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import DEBUG, IMPORTANT_NOTE, INSUFFICIENT_MESSAGE, MODEL_NAMES
from rag import format_context, format_sources, search_documents

INSUFFICIENT_MESSAGE_DE = (
    "Ich habe in den aktuellen Dokumenten nicht gen\u00fcgend Informationen, "
    "um diese Frage zuverl\u00e4ssig zu beantworten."
)

IMPORTANT_NOTE_DE = (
    "Wichtiger Hinweis: Dies ist eine allgemeine Information auf Basis der "
    "verf\u00fcgbaren Dokumente. Pr\u00fcfe f\u00fcr deinen pers\u00f6nlichen Fall die "
    "offizielle Quelle oder kontaktiere die zust\u00e4ndige Stelle."
)

INVESTING_NOTE_EN = "Important note: This is general information, not financial advice."
INVESTING_NOTE_DE = "Wichtiger Hinweis: Dies ist eine allgemeine Information, keine Finanzberatung."

SYSTEM_INSTRUCTION = (
    "You are a helpful assistant for expats in Germany. "
    "You sound friendly, calm, practical, and expert-like. "
    "Use simple language and start answers naturally. "
    "Understand English and German. Reply in the user's language by default, "
    "unless the user explicitly asks for another language. "
    "In German, use polite and clear German. For formal German replies, use Sie. "
    "You help with visa, jobs, PR, and general life questions. "
    "For factual expat answers, answer only from the provided document context. "
    "For translation or reply-writing tasks, use only the user's provided text and instructions. "
    "Keep answers concise, useful, and grounded. "
    "Use clear bullet points where useful. "
    "Do not overclaim, use outside knowledge, or guess. "
    f"If the context is insufficient, say: \"{INSUFFICIENT_MESSAGE}\""
)

ASSISTANT_INTRO_RESPONSE = (
    "Hi! I\u2019m your Expat Germany AI Assistant. You can ask me about visas, "
    "Blue Card, PR, taxes, Anmeldung, renting, health insurance, family "
    "benefits, study, car rental, utilities, pets, pregnancy, Kita, "
    "unemployment benefits, or day-to-day life in Germany. I can understand "
    "and reply in English and German."
)

ASSISTANT_INTRO_RESPONSE_DE = (
    "Hallo! Ich bin dein Expat Germany AI Assistant. Du kannst mich zu Visa, "
    "Blue Card, Niederlassungserlaubnis, Steuern, Anmeldung, Miete, "
    "Krankenversicherung, Familienleistungen, Studium oder Alltag in "
    "Deutschland fragen. Ich kann Englisch und Deutsch verstehen und antworten."
)

THANKS_RESPONSE = "You\u2019re welcome! Ask me anytime you have another Germany question."
THANKS_RESPONSE_DE = "Gern! Frag mich jederzeit, wenn du noch eine Frage zu Deutschland hast."

HELP_RESPONSE = (
    "I can help with common expat questions in Germany \u2014 including visas, "
    "work, housing, taxes, health insurance, family life, studying, transport, "
    "daily life, travel, hobbies, and Indian community topics. My answers are "
    "based on the documents currently available in my knowledge base. I can "
    "also help with German culture, rules, holidays, weather basics, work "
    "environment, and day-to-day life."
)

HELP_RESPONSE_DE = (
    "Ich kann dir bei typischen Expat-Fragen in Deutschland helfen, zum "
    "Beispiel zu Visa, Arbeit, Wohnen, Steuern, Krankenversicherung, Familie, "
    "Studium, Verkehr, Alltag, Reisen, Hobbys und indischen Community-Themen. "
    "Meine Antworten basieren auf den Dokumenten in meiner aktuellen "
    "Wissensbasis. Ich kann auch bei deutscher Kultur, Regeln, Feiertagen, "
    "Wetter-Grundlagen, Arbeitsumfeld und Alltag helfen."
)

LIVE_WEATHER_RESPONSE = (
    "I don\u2019t provide live weather yet because this assistant answers from "
    "saved documents, not a current weather service. For today\u2019s weather, "
    "please check a live weather app, Deutscher Wetterdienst, or another "
    "current weather service."
)

LIVE_WEATHER_RESPONSE_DE = (
    "Ich biete noch kein Live-Wetter an, weil dieser Assistent aus "
    "gespeicherten Dokumenten antwortet und keinen aktuellen Wetterdienst "
    "nutzt. F\u00fcr das heutige Wetter pr\u00fcfe bitte eine Wetter-App, den "
    "Deutschen Wetterdienst oder einen anderen aktuellen Wetterdienst."
)

GREETING_INPUTS = {
    "hi",
    "hello",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
}

GERMAN_GREETING_INPUTS = {
    "hallo",
    "guten morgen",
    "guten tag",
    "guten abend",
    "servus",
    "moin",
}

THANKS_INPUTS = {
    "thanks",
    "thank you",
    "thank you very much",
    "thanks a lot",
}

GERMAN_THANKS_INPUTS = {
    "danke",
    "vielen dank",
    "danke sehr",
    "dankesch\u00f6n",
}

HELP_INPUTS = {
    "who are you",
    "what can you help with",
    "what can you do",
    "help",
}

GERMAN_HELP_INPUTS = {
    "wer bist du",
    "wobei kannst du mir helfen",
    "was kannst du",
    "hilfe",
}


def get_response_language(user_input):
    text = user_input.lower()

    english_requests = (
        "answer in english",
        "reply in english",
        "explain this in english",
        "in english",
        "auf englisch",
        "antworte auf englisch",
        "bitte antworte auf englisch",
        "erkl\u00e4re das auf englisch",
    )
    german_requests = (
        "answer in german",
        "reply in german",
        "explain this in german",
        "in german",
        "auf deutsch",
        "antworte auf deutsch",
        "bitte antworte auf deutsch",
        "erkl\u00e4re das auf deutsch",
    )

    if any(phrase in text for phrase in english_requests):
        return "German" if "in german" in text or "auf deutsch" in text else "English"

    if any(phrase in text for phrase in german_requests):
        return "German"

    german_markers = (
        " der ",
        " die ",
        " das ",
        " ich ",
        " wie ",
        " was ",
        " kann ",
        " bekomme ",
        " brauche ",
        " steuer",
        " anmeldung",
        " krankenversicherung",
        " deutschland",
        " bitte",
        " du ",
        " sie ",
        " f\u00fcr ",
        " \u00fcber ",
        " k\u00f6nnen ",
        " arbeits",
    )
    german_chars = ("ä", "ö", "ü", "ß")

    if any(char in text for char in german_chars):
        return "German"

    padded = f" {text} "
    german_score = sum(marker in padded for marker in german_markers)
    return "German" if german_score >= 2 else "English"


def is_live_weather_question(user_input):
    clean_input = user_input.strip().lower()
    weather_words = (
        "weather",
        "temperature",
        "forecast",
        "rain",
        "snow",
        "wetter",
        "temperatur",
        "vorhersage",
        "regen",
        "schnee",
    )
    live_words = (
        "today",
        "now",
        "current",
        "currently",
        "tomorrow",
        "this week",
        "live",
        "heute",
        "jetzt",
        "aktuell",
        "morgen",
        "diese woche",
    )

    return any(word in clean_input for word in weather_words) and any(
        word in clean_input for word in live_words
    )


def get_simple_response(user_input):
    response_language = get_response_language(user_input)

    if is_live_weather_question(user_input):
        return LIVE_WEATHER_RESPONSE_DE if response_language == "German" else LIVE_WEATHER_RESPONSE

    clean_input = user_input.strip().lower()
    clean_input = re.sub(r"[^\w\s]", "", clean_input)
    clean_input = re.sub(r"\s+", " ", clean_input).strip()

    if clean_input in GREETING_INPUTS:
        return ASSISTANT_INTRO_RESPONSE

    if clean_input in GERMAN_GREETING_INPUTS:
        return ASSISTANT_INTRO_RESPONSE_DE

    if clean_input in THANKS_INPUTS:
        return THANKS_RESPONSE

    if clean_input in GERMAN_THANKS_INPUTS:
        return THANKS_RESPONSE_DE

    if clean_input in HELP_INPUTS:
        return HELP_RESPONSE

    if clean_input in GERMAN_HELP_INPUTS:
        return HELP_RESPONSE_DE

    return None


def is_language_task(user_input):
    text = user_input.lower()
    language_task_words = (
        "translate",
        "\u00fcbersetze",
        "uebersetze",
        "draft",
        "write a reply",
        "write an answer",
        "formuliere",
        "schreibe eine antwort",
        "antwortschreiben",
    )
    official_text_words = (
        "letter",
        "email",
        "mail",
        "official letter",
        "brief",
        "e-mail",
        "amt",
        "beh\u00f6rde",
        "jobcenter",
        "ausl\u00e4nderbeh\u00f6rde",
    )

    language_reply_request = (
        ("reply in" in text or "antworte auf" in text)
        and any(word in text for word in official_text_words)
    )

    return any(word in text for word in language_task_words) or language_reply_request or (
        ("explain this" in text or "erkl\u00e4re" in text)
        and any(word in text for word in official_text_words)
    )


def split_user_questions(user_input):
    text = user_input.strip()
    if not text:
        return []

    question_parts = re.split(r"(?<=[?])\s+", text)
    if len(question_parts) > 1:
        return [part.strip() for part in question_parts if part.strip()]

    connector_pattern = r"\s+(?:and|also|plus|as well as|und|auch|au\u00dferdem)\s+"
    parts = re.split(connector_pattern, text, flags=re.IGNORECASE)

    question_words = (
        "what",
        "when",
        "where",
        "who",
        "why",
        "how",
        "can",
        "do",
        "does",
        "is",
        "are",
        "should",
        "wie",
        "was",
        "wann",
        "wo",
        "wer",
        "warum",
        "kann",
        "brauche",
        "muss",
        "soll",
        "ist",
        "sind",
    )

    if len(parts) > 1 and sum(
        part.strip().lower().startswith(question_words) for part in parts
    ) >= 2:
        return [part.strip() for part in parts if part.strip()]

    return [text]


def get_insufficient_message(response_language):
    return INSUFFICIENT_MESSAGE_DE if response_language == "German" else INSUFFICIENT_MESSAGE


def build_prompt(user_input, search_results, response_language):
    context = format_context(search_results)
    insufficient_message = get_insufficient_message(response_language)
    important_note = IMPORTANT_NOTE_DE if response_language == "German" else IMPORTANT_NOTE
    investing_note = INVESTING_NOTE_DE if response_language == "German" else INVESTING_NOTE_EN
    language_instruction = (
        "Answer in German. Use polite, clear German."
        if response_language == "German"
        else "Answer in English."
    )

    return f"""
Use only the document context below to answer the user's question.
Do not use outside knowledge.
{language_instruction}
Keep the answer friendly, calm, concise, and practical.
Use simple language.
Start naturally, like a helpful expert friend, not with robotic phrases.
Do not overclaim. If the document context is limited, say so plainly.
Use clear bullet points when listing requirements or steps.
If multiple documents are relevant, combine them into one clean answer.
Do not write phrases like "the provided documents say" or "based on the context".
Always present the main answer first.
For immigration, legal, visa, residence, naturalisation, work permit, tax, health,
pregnancy, unemployment, or housing topics, include this exact note after the
main answer and before the source section:
{important_note}
For investing-related topics, include this exact note after the main answer and
before the source section:
{investing_note}
Do not include a Sources or Quellen section in your answer; the app adds sources at the end.
If the context does not contain enough information, answer exactly:
{insufficient_message}

Document context:
{context}

User question:
{user_input}
""".strip()


def build_language_task_prompt(user_input, response_language):
    language_instruction = (
        "Respond in German. Use formal Sie for official letters or replies unless the user asks for informal German."
        if response_language == "German"
        else "Respond in English."
    )

    return f"""
You are helping with a language task for an expat in Germany.
{language_instruction}
You may translate, summarize, explain, or draft a reply using only the text and instructions the user provides.
Do not add factual claims about German law, immigration, taxes, health, housing, or benefits unless the user provided them.
If important details are missing, keep the draft general and say what should be checked.
Keep the tone friendly, calm, practical, and clear.

User request:
{user_input}
""".strip()


def print_debug_results(user_input, search_results):
    if not DEBUG:
        return

    print("\nDebug: Retrieved chunks")
    print(f"User question: {user_input}")

    if not search_results:
        print("- No chunks retrieved.")
        return

    for number, result in enumerate(search_results, start=1):
        print(f"\nChunk {number}")
        print(f"Score: {result.get('score', 0):.4f}")
        print(f"Filename: {result['filename']}")

        source_urls = result.get("source_urls", [])
        if not source_urls and result.get("source_url"):
            source_urls = [result["source_url"]]

        if source_urls:
            print(f"Source URLs: {'; '.join(source_urls)}")
        else:
            print("Source URLs: Not available")

        preview = result["text"][:300].replace("\n", " ")
        if len(result["text"]) > 300:
            preview += "..."

        print(f"Text: {preview}")


def call_gemini_with_prompt(client, prompt):
    user_message = types.Content(
        role="user",
        parts=[types.Part(text=prompt)],
    )

    for model_name in MODEL_NAMES:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[user_message],
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                ),
            )

            return response.text.strip()
        except Exception as error:
            error_message = str(error)
            can_try_next_model = (
                "503" in error_message
                or "UNAVAILABLE" in error_message
                or "404" in error_message
                or "NOT_FOUND" in error_message
            )

            if not can_try_next_model or model_name == MODEL_NAMES[-1]:
                raise error

    return "Sorry, I could not get a response right now."


def ask_gemini(client, user_input, search_results, response_language):
    prompt = build_prompt(user_input, search_results, response_language)
    answer = call_gemini_with_prompt(client, prompt).strip()
    insufficient_message = get_insufficient_message(response_language)

    if insufficient_message in answer or INSUFFICIENT_MESSAGE in answer:
        return insufficient_message

    sources = format_sources(search_results)
    source_heading = "Quellen" if response_language == "German" else "Sources"
    source_text = "\n".join(f"- {source}" for source in sources)

    return f"{answer}\n\n{source_heading}:\n{source_text}"


def answer_language_task(client, user_input):
    response_language = get_response_language(user_input)
    prompt = build_language_task_prompt(user_input, response_language)
    return call_gemini_with_prompt(client, prompt).strip()


def translate_query_to_english(client, question):
    prompt = f"""
Translate this German search query into concise English for document retrieval.
Return only the translated query, with no explanation.

Query:
{question}
""".strip()

    return call_gemini_with_prompt(client, prompt).strip()


def answer_single_question(client, question, response_language=None):
    response_language = response_language or get_response_language(question)
    search_results = search_documents(client, question)

    if not search_results and response_language == "German":
        english_question = translate_query_to_english(client, question)
        search_results = search_documents(client, english_question)

    print_debug_results(question, search_results)

    if not search_results:
        return get_insufficient_message(response_language)

    return ask_gemini(client, question, search_results, response_language)


def answer_user_input(client, user_input):
    simple_response = get_simple_response(user_input)
    if simple_response:
        return simple_response

    if is_language_task(user_input):
        return answer_language_task(client, user_input)

    response_language = get_response_language(user_input)
    questions = split_user_questions(user_input)

    if len(questions) == 1:
        return answer_single_question(client, questions[0], response_language)

    answers = []
    for number, question in enumerate(questions, start=1):
        try:
            answer = answer_single_question(client, question, response_language)
        except FileNotFoundError:
            raise
        except Exception as error:
            answer = f"Error: {error}"

        question_label = "Frage" if response_language == "German" else "Question"
        answers.append(f"{question_label} {number}: {question}\n\n{answer}")

    return "\n\n---\n\n".join(answers)


def main():
    load_dotenv()
    client = None

    print("Expat AI Assistant")
    print(
        "I can help with common expat questions in Germany \u2014 including visas, "
        "work, housing, taxes, health insurance, family life, studying, "
        "transport, daily life, travel, hobbies, and Indian community topics. "
        "My answers are based on the documents currently available in my "
        "knowledge base."
    )
    print(
        "I can also help with German culture, rules, holidays, weather basics, "
        "work environment, and day-to-day life."
    )
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        if not user_input:
            continue

        try:
            simple_response = get_simple_response(user_input)
            if simple_response:
                print(f"\nAssistant: {simple_response}\n")
                continue

            if client is None:
                api_key = os.getenv("GEMINI_API_KEY")
                if not api_key:
                    print("\nError: Missing GEMINI_API_KEY. Add it to your .env file first.\n")
                    continue

                client = genai.Client(api_key=api_key)

            response_text = answer_user_input(client, user_input)
            print(f"\nAssistant: {response_text}\n")
        except FileNotFoundError as error:
            print(f"\nError: {error}\n")
        except Exception as error:
            print(f"\nError: {error}\n")


if __name__ == "__main__":
    main()
