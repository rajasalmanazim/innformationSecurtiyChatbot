import time
import streamlit as st
from groq import Groq, APIConnectionError, RateLimitError, APIStatusError

MODEL = "openai/gpt-oss-20b"
TEMPERATURE = 0.4
MAX_TOKENS = 1500
MAX_HISTORY_TURNS = 10

SYSTEM_PROMPT = """
ROLE
You are "SecureTutor", a friendly and patient Information Security and Cryptography tutor
for university students. You explain like an experienced teaching assistant: simple language,
short paragraphs, numbered steps, and a small example for each concept.

CONTEXT
- Audience: undergraduate students (beginner to intermediate) in computer science, ICT and engineering.
- Scope: CIA triad, threats and attacks, malware, authentication, access control,
  classical ciphers (Caesar, substitution, transposition), symmetric and asymmetric
  cryptography, hashing, digital signatures, network security basics, security policies and risk.
- Constraints:
  1. Stay strictly inside information security and cryptography education.
  2. If a question is off-topic, politely decline in one sentence and redirect with an
     example of a related question you can answer.
  3. Do not give working instructions for real attacks, malware, or unauthorized access.
     Explain concepts defensively and suggest legal practice labs instead.
  4. If you are unsure, say so. Never invent facts, standards, or references.
  5. Keep answers under about 250 words unless the student asks for more detail.
- Style: end with one short check question or practice exercise when it helps learning.
"""

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def ask(history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history[-MAX_HISTORY_TURNS * 2:]
    for attempt in range(3):
        try:
            r = client.chat.completions.create(
                model=MODEL, messages=messages,
                temperature=TEMPERATURE, max_tokens=MAX_TOKENS,
                reasoning_effort="low",
            )
            return r.choices[0].message.content
        except RateLimitError:
            time.sleep(2 * (attempt + 1))
            if attempt == 2:
                return "Too many requests right now. Please try again in a minute."
        except APIConnectionError:
            time.sleep(1)
            if attempt == 2:
                return "I can't reach the AI service. Please try again."
        except APIStatusError as e:
            if e.status_code in (401, 403):
                return "API key problem. Check the GROQ_API_KEY secret."
            return f"The AI service returned an error ({e.status_code}). Please try again."
        except Exception as e:
            return f"Something went wrong: {type(e).__name__}. Please try again."

st.set_page_config(page_title="SecureTutor", page_icon="🔐")
st.title("🔐 SecureTutor")
st.caption("Information Security & Cryptography study helper")

if "history" not in st.session_state:
    st.session_state.history = []

for m in st.session_state.history:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Ask about cryptography, authentication, threats..."):
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = ask(st.session_state.history)
        st.markdown(reply)
    st.session_state.history.append({"role": "assistant", "content": reply})