from ollama import create, generate, Client
import os
from huggingface_hub import hf_hub_download

class ChatBot():

    def __init__(self):
        # Path to your local GGUF model file
        model_path = self.load_model()
        # Alias under which Ollama will store the model
        self.model_alias = "Pygmalion-3-12B-Q3_K.gguf"

        # Ensure the model is available in Ollama
        self.ensure_model(model_path)   

    def prompt(self, prompt):
        response = self.generate_response(prompt)
        return prompt, response

    def load_model(self):
        print("Loading model... 🧠")

        model_dir = os.path.expanduser("~/models")

        model_path = hf_hub_download(
            repo_id="PygmalionAI/Pygmalion-3-12B-GGUF",
            filename="Pygmalion-3-12B-Q3_K.gguf",
            local_dir=model_dir,
            cache_dir=model_dir,
        )

        print(f"model is ready at: {model_path}")

        return model_path

    def ensure_model(self, model_path):
        """
        Pulls a local GGUF model into Ollama's registry under the given alias.
        If already present, this is a no-op.
        """
        print(f"Ensuring Ollama model '{self.model_alias}' from '{model_path}'...")
        client = Client()
        digest = client.create_blob(model_path)

        modelfile_content = f"""
              FROM {self.model_alias}
              PARAMETER temperature 0.7
              PARAMETER top_p 0.9
              PARAMETER gpu_layers 99
        """
        create(model=self.model_alias, modelfile=modelfile_content, files={self.model_alias: digest})
        print(f"Model '{self.model_alias}' is ready to use.")


    def generate_response(self, prompt: str) -> str:
        """
        Generates a one-shot response using Ollama's generate API.
        """
        resp = generate(
            model=self.model_alias,
            prompt=prompt,
            options={
                "gpu_layers": 99,  # Use as many layers on GPU as possible
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 2048  # Max tokens to generate
            }
        )
        return resp['response'].strip()