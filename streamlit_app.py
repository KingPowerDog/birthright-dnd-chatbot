import streamlit as st
import requests
from typing import Optional


FLOW_ID = "c26ad923-d203-45d3-ba39-b70619ea5880"
ENDPOINT = "dnd_bot_chat" # You can set a specific endpoint name in the flow settings

# You can tweak the flow by adding a tweaks dictionary
# e.g {"OpenAI-XXXXX": {"model_name": "gpt-4"}}
TWEAKS = {
  "ChatInput-HNgdh": {},
  "ChatOutput-DIptw": {},
  "OllamaModel-fKOfL": {},
  "ParseData-uNNzh": {},
  "Prompt-6oxDV": {},
  "Chroma-FuShZ": {},
  "OllamaEmbeddings-Lyoon": {},
  "pgvector-NRZEs": {}
}

def run_flow(message: str,
  endpoint: str,
  output_type: str = "chat",
  input_type: str = "chat",
  tweaks: Optional[dict] = None,
  api_key: Optional[str] = None) -> dict:
    """
    Run a flow with a given message and optional tweaks.

    :param message: The message to send to the flow
    :param endpoint: The ID or the endpoint name of the flow
    :param tweaks: Optional tweaks to customize the flow
    :return: The JSON response from the flow
    """
    BASE_API_URL = st.secrets["base_api_url"]
    api_url = f"{BASE_API_URL}/api/v1/run/{endpoint}"
    api_secret_key = st.secrets["langflow_key"]

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    if api_key:
        headers = {"x-api-key": api_key}
    elif not api_key:
        headers = {"x-api-key": api_secret_key}
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()


def chat(prompt: str):
  with current_chat_message:
    # Block input to prevent sending messages whilst AI is responding
    st.session_state.disabled = True

    # Add user message to chat history
    st.session_state.messages.append(("human", prompt))

    # Display user message in chat message container
    with st.chat_message("human"):
      st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("ai"):
      # Get complete chat history, including latest question as last message
      history = "\n".join(
        [f"{role}: {msg}" for role, msg in st.session_state.messages]
      )

      query = f"{history}\nAI:"

      # Setup any tweaks you want to apply to the flow
      inputs = {"question": query}
      output = run_flow(prompt, ENDPOINT, tweaks=TWEAKS)
 
      #print(output.get("outputs")[0]["outputs"][0]["results"]["message"]["data"]["text"])
      message_output = output.get("outputs")[0]["outputs"][0]["results"]["message"]["data"]["text"]

      placeholder = st.empty()

      # write response without "▌" to indicate completed message.
      with placeholder:
        st.markdown(message_output)

    # Log AI response to chat history
    st.session_state.messages.append(("ai", message_output))
    # Unblock chat input
    st.session_state.disabled = False

    st.rerun()


st.set_page_config(page_title="Birthright D&D Bot")
st.title("Birthright D&D Assistant DM")

system_prompt = ""
if "messages" not in st.session_state:
    st.session_state.messages = [("system", system_prompt)]
if "disabled" not in st.session_state:
    # `disable` flag to prevent user from sending messages whilst the AI is responding
    st.session_state.disabled = False


with st.chat_message("ai"):
  st.markdown(
    f"Hi! I'm your Birthright AI assistant."
  )

# Display chat messages from history on app rerun
for role, message in st.session_state.messages:
    if role == "system":
        continue
    with st.chat_message(role):
        st.markdown(message)

current_chat_message = st.container()
prompt = st.chat_input("Ask your question here...", disabled=st.session_state.disabled)

if prompt:
    chat(prompt)
