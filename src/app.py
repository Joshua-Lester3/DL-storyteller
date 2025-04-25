from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

def load_model(model_name="distilgpt2"):
    print("Loading model... 🧠")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model.eval()
    return tokenizer, model

def generate_response(prompt, tokenizer, model):
    inputs = tokenizer.encode(prompt, return_tensors="pt")
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
    print("Hi! I'm powered by GPT 🤖")
    history = ""

    while True:
        user_input = input("You: ")
        if user_input.lower() in {"bye", "exit", "quit"}:
            print("GPT: See you later! 👋")
            break

        history += f"You: {user_input}\nGPT:"
        response = generate_response(history, tokenizer, model)
        print(f"GPT: {response}")
        history += f" {response}\n"

if __name__ == "__main__":
    chatbot()
