from ollama import pull, generate
import os
from huggingface_hub import hf_hub_download

def load_model():
    print("Loading model... 🧠")

    model_dir = os.path.expanduser("~/models")

    model_path = hf_hub_download(
        repo_id="PygmalionAI/Pygmalion-3-12B-Q3_K",
        filename="Pygmalion-3-12B-Q3_K.gguf",
        local_dir=model_dir,
        cache_dir=model_dir,
    )

    print(f"model is ready at: {model_path}")

    return model_path

def ensure_model(model_path, model_alias):
    """
    Pulls a local GGUF model into Ollama's registry under the given alias.
    If already present, this is a no-op.
    """
    print(f"Ensuring Ollama model '{model_alias}' from '{model_path}'...")
    pull(model=model_path, name=model_alias)
    print(f"Model '{model_alias}' is ready to use.")


def generate_response(prompt: str, model_alias: str) -> str:
    """
    Generates a one-shot response using Ollama's generate API.
    """
    resp = generate(
        model=model_alias,
        prompt=prompt,
        max_tokens=50,
        temperature=0.8,
        top_p=0.95,
        stop=["\n"]
    )
    return resp.message.content.strip()


def chatbot():
    # Path to your local GGUF model file
    model_path = load_model()
    # Alias under which Ollama will store the model
    model_alias = "pygmalion-3-12b-gguf"

    # Ensure the model is available in Ollama
    ensure_model(model_path, model_alias)

    print("Welcome to Pygmalion (via Ollama)! Type 'quit' to exit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in {"quit", "exit", "bye"}:
            print("Pygmalion: See you later! 👋")
            break

        # For chat-style interaction, you could use chat(), but here we do simple one-shot generate
        prompt = f"User: {user_input} Pygmalion: "
        response = generate_response(prompt, model_alias)
        print(f"Pygmalion: {response}")

if __name__ == "__main__":
    chatbot()

