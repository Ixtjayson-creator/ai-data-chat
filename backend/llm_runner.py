import logging
import requests
import json

def generate_answer(retrieved_chunks: str, user_question: str, history: list = None) -> str:
    """
    Generates an answer using a local LLM via Ollama's API.
    Uses the chat endpoint to support conversation memory.
    
    Args:
        retrieved_chunks (str): The context text retrieved from the vector store.
        user_question (str): The user's original question.
        history (list): A list of dictionaries containing past user/assistant messages.
        
    Returns:
        str: The generated answer from the LLM.
    """
    if history is None:
        history = []

    # System prompt to set boundaries based on retrieved context
    system_prompt = f"""You are a professional Data Analyst.

Instructions:
1. Answer the question using ONLY the provided context below.
2. If the answer is not contained within the context, strictly respond with: "I don't know based on the provided data."
3. Keep your response concise and direct.
4. Do not use outside knowledge or hallucinate details.

Context:
{retrieved_chunks}"""

    # Ollama Chat API endpoint (local)
    url = "http://localhost:11434/api/chat"
    model_name = "qwen2.5:0.5b"

    # Build the messages array with system prompt, history, and current question
    messages = [{"role": "system", "content": system_prompt}]
    
    # Append the last 6 messages from history to keep context but save memory
    for msg in history[-6:]:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        
    messages.append({"role": "user", "content": user_question})

    payload = {
        "model": model_name,
        "messages": messages,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result.get("message", {}).get("content", "No response from LLM.")
        
    except requests.exceptions.ConnectionError:
        error_msg = ("Error: Could not connect to Ollama. "
                     "Please ensure Ollama is installed and running locally with "
                     f"the command: 'ollama run {model_name}'")
        logging.error(error_msg)
        return error_msg
    except Exception as e:
        logging.error(f"Error in LLM generation: {e}")
        return f"Error: An unexpected error occurred: {str(e)}"

if __name__ == "__main__":
    # Test simulation
    test_context = "The company's revenue in 2023 was $10 million. The growth rate was 15%."
    test_question = "What was the growth rate in 2023?"
    
    print("Sending request to local LLM...")
    answer = generate_answer(test_context, test_question)
    print(f"Generated Answer:\n{answer}")
