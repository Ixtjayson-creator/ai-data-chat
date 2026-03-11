from llama_cpp import Llama

class LlamaRunner:
    def __init__(self, model_path: str, n_ctx: int = 2048, n_threads: int = 4):
        """
        Initializes the llama.cpp local LLM runner.
        """
        print(f"Loading local LLM from {model_path}...")
        self.llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads,
            verbose=False
        )

    def generate_response(self, context: str, question: str) -> str:
        """
        Generates a concise explanation using the context and the question.
        """
        prompt = (
            "You are a data analyst AI.\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{question}\n\n"
            "Provide a clear and concise explanation using the data."
        )

        # Using ChatML generation format or base format depending on what Qwen 2.5 expects.
        # Since the user requested a very specific raw prompt format above, we'll format it exactly as requested
        # using the direct inference method if possible, or wrapping it in standard prompt framing if it's an instruct model.
        # But we will pass the exact prompt given in the requirements explicitly.
        
        # Wrapping in Qwen Im_start format to make it respond properly
        formatted_prompt = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"

        output = self.llm(
            formatted_prompt,
            max_tokens=256,
            temperature=0.1,
            stop=["<|im_end|>"],
            echo=False
        )

        return output['choices'][0]['text'].strip()
