import logging
import requests
import json

def generate_answer(retrieved_chunks: str, user_question: str, history: list = None) -> str:
    """
    Generates an answer using a local LLM via Ollama's API.
    Uses the chat endpoint to support conversation memory.
    """
    if history is None:
        history = []

    # Improved System Prompt for better "ability"
    system_prompt = f"""You are an advanced Data Intelligence Assistant. Your goal is to provide accurate, insightful, and helpful answers based ONLY on the provided document context.

CONTEXT FROM DOCUMENTS:
{retrieved_chunks}

GUIDELINES:
1. Use the provided context to answer the user's question in detail.
2. If the context contains the information, explain it clearly and provide relevant data points (numbers, dates, names).
3. If the answer is absolutely NOT in the context, say: "I'm sorry, I don't see that specific information in the uploaded documents. Could you provide more details or upload another file?"
4. Maintain a professional yet conversational tone.
5. If the user asks a general question NOT related to the data, politely remind them that your primary function is to analyze the documents they've uploaded.
"""

    # Ollama Chat API endpoint (local)
    url = "http://localhost:11434/api/chat"
    # Upgrading to a more capable model (3B is much smarter than 0.5B)
    model_name = "qwen2.5:3b" 

    # Build the messages array
    messages = [{"role": "system", "content": system_prompt}]
    
    # Context window management: last 10 messages for better memory
    for msg in history[-10:]:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        
    messages.append({"role": "user", "content": user_question})

    payload = {
        "model": model_name,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.3, # Lower temperature for factual accuracy
            "num_predict": 1000 # Allow for longer, detailed responses
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=90)
        response.raise_for_status()
        
        result = response.json()
        return result.get("message", {}).get("content", "No response from LLM.")
        
    except requests.exceptions.ConnectionError:
        error_msg = (f"Error: Could not connect to Ollama. Please ensure Ollama is running and '{model_name}' is installed.")
        logging.error(error_msg)
        return error_msg
    except Exception as e:
        logging.error(f"Error in LLM generation: {e}")
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Test simulation
    test_context = "The company's revenue in 2023 was $10 million. The growth rate was 15%."
    test_question = "What was the growth rate in 2023?"
    
    print("Sending request to local LLM...")
    answer = generate_answer(test_context, test_question)
    print(f"Generated Answer:\n{answer}")
