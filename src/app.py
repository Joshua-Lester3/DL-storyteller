from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer
import torch
from huggingface_hub import snapshot_download
import os
import accelerate
from auto_gptq import AutoGPTQForCausalLM

def load_model(model_name="PygmalionAI/Pygmalion-3-12B-GPTQ"):
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

    tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True)

    model = AutoModelForCausalLM.from_quantized(model_path, use_safetensors=True,
                device="cuda:0" if torch.cuda.is_available() else "cpu", trust_remote_code=True,
                low_cpu_mem_usage=True, torch_dtype=torch.float16)

    model.eval()
    return tokenizer, model

def generate_response(prompt, tokenizer, model):
    inputs = tokenizer.encode(prompt, return_tensors="pt")

    device = model.device if hasattr(model, 'device') else torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    inputs = inputs.to(device)

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
