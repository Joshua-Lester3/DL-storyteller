from ollama import create, generate, Client, chat
import os
import subprocess
from huggingface_hub import hf_hub_download

class ChatBot():

    def __init__(self):
        # Path to your local GGUF model file
        model_path = self.load_model()
        # Alias under which Ollama will store the model
        self.model_alias = "Pygmalion-3-12B-Q3_K.gguf"

        self.chat_history = []

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
        try:
            
            digest = client.create_blob(model_path)

            create(model=self.model_alias, files={self.model_alias: digest})

            try:
                print("Attempting to enable GPU acceleration via command line...")
                # Create a temporary modelfile
                modelfile_path = "/tmp/modelfile.txt"
                with open(modelfile_path, "w") as f:
                    f.write(f"""FROM {self.model_alias}
                            PARAMETER temperature 0.7
                            PARAMETER top_p 0.9
                            SYSTEM gpu
                            """)
                # Use the Ollama CLI to create model with GPU support
                cmd = f"ollama create {self.model_alias} -f {modelfile_path}"
                process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if process.returncode == 0:
                    print("Successfully enabled GPU acceleration for the model.")
                else:
                    print(f"Warning: Could not enable GPU via modelfile: {process.stderr}")
                
                # Clean up
                os.remove(modelfile_path)
            except Exception as e:
                print(f"Warning: Could not enable GPU via CLI: {e}")
                print("Falling back to runtime GPU activation.")
        except Exception as e:
            print(f"Error ensuring model: {e}")
            raise

        print(f"Model '{self.model_alias}' is ready to use.")


    def generate_response(self, prompt: str) -> str:
        """
        Generates a one-shot response using Ollama's generate API.
        """
        message = {"role": "user", "content": prompt}

        resp = chat(
            model=self.model_alias,
            messages=[*self.chat_history, message],
            options={
                "gpu_layers": 99,  # Use as many layers on GPU as possible
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 2048  # Max tokens to generate
            }
        )

        # resp = generate(
        #     model=self.model_alias,
        #     prompt=prompt,
        #     options={
        #         "gpu_layers": 99,  # Use as many layers on GPU as possible
        #         "temperature": 0.7,
        #         "top_p": 0.9,
        #         "num_predict": 2048  # Max tokens to generate
        #     }
        # )
        
        assistant_message = resp['message']

        if 'role' not in assistant_message or assistant_message['role'] != 'assistant':
            assistant_message = {
                "role": "assistant",
                "content": assistant_message['content']
            }

        self.chat_history.append(message)
        self.chat_history.append(assistant_message)

        return resp['message']['content'].strip()