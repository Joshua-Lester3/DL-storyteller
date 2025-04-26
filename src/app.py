from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from huggingface_hub import snapshot_download
import os
import accelerate

def load_model(model_name="PygmalionAI/Pygmalion-3-12B"):
    print("Loading model... 🧠")

    model_dir = "/mnt/models/pygmalion"

    if not os.path.isdir(model_dir) or not os.path.exists(os.path.join(model_dir, "config.json")):
        print("Model not found locally - downloading to persistent disk...")
        model_path = snapshot_download(
            repo_id=model_name,
            local_dir=model_dir,
            local_dir_use_symlinks=False,
            resume_download=True
        )
    else:
        print("Found model at:", model_dir)
        model_path = model_dir

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path, low_cpu_mem_usage=True, torch_dtype=torch.float16, device_map="auto")

    print("CUDA available:", torch.cuda.is_available())
    print("GPU name:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None")

    model.eval()
    return tokenizer, model

def generate_response(prompt, tokenizer, model):
    inputs = tokenizer.encode(prompt, return_tensors="pt")

    if hasattr(model, 'hf_device_map'):
        first_device = list(model.hf_device_map.values())[0]
    else:
        first_device = model.device
    inputs = inputs.to(first_device)

    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_length=inputs.shape[1] + 50,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=0.8,
            pad_token_id=tokenizer.eos_token_id
        )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response[len(prompt):].strip()

def chatbot():
    tokenizer, model = load_model()
    history = ""

    while True:
        user_input = input("You: ")
        if user_input.lower() in {"bye", "exit", "quit"}:
            print("Pygmalion: See you later! 👋")
            break

        history += f"You: {user_input}\nPygmalion:"
        response = generate_response(history, tokenizer, model)
        print(f"Pygmalion: {response}")
        history += f" {response}\n"

if __name__ == "__main__":
    chatbot()
