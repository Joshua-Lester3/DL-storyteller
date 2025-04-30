from ollama import create, generate, Client
import os
import time
import psutil
import platform
from huggingface_hub import hf_hub_download

class ChatBot():
    def __init__(self, model_name="Pygmalion-3-12B-Q3_K.gguf", use_gpu=True):
        """
        Initialize the chatbot with the specified model.
        
        Args:
            model_name: Name of the GGUF model file to use
            use_gpu: Whether to try using GPU acceleration
        """
        self.model_alias = os.path.basename(model_name)
        self.use_gpu = use_gpu
        
        # Print system information
        self.print_system_info()
        
        # Path to your local GGUF model file
        model_path = self.load_model(model_name)
        
        # Ensure the model is available in Ollama
        self.ensure_model(model_path)
        
        # Log that initialization is complete
        print(f"ChatBot initialization complete. Model '{self.model_alias}' is ready.")

    def print_system_info(self):
        """Print information about the system this is running on."""
        print(f"\n{'='*50}")
        print(f"System Information:")
        print(f"  OS: {platform.system()} {platform.version()}")
        print(f"  CPU: {platform.processor()}")
        print(f"  Physical cores: {psutil.cpu_count(logical=False)}")
        print(f"  Logical cores: {psutil.cpu_count(logical=True)}")
        print(f"  RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB")
        
        # Try to detect if CUDA/GPU is available
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            if cuda_available:
                gpu_count = torch.cuda.device_count()
                gpu_name = torch.cuda.get_device_name(0) if gpu_count > 0 else "Unknown"
                print(f"  GPU: {gpu_name} (CUDA available: {cuda_available}, Count: {gpu_count})")
            else:
                print(f"  GPU: Not detected with PyTorch")
        except ImportError:
            print(f"  GPU: Could not detect (PyTorch not installed)")
        print(f"{'='*50}\n")

    def prompt(self, prompt_text):
        """Process a prompt and return the response with timing information."""
        print(f"\nProcessing prompt ({len(prompt_text)} chars)...")
        
        start_time = time.time()
        response = self.generate_response(prompt_text)
        elapsed_time = time.time() - start_time
        
        print(f"Response generated in {elapsed_time:.2f} seconds")
        return prompt_text, response

    def load_model(self, model_name):
        """Download the model from Hugging Face if needed."""
        print(f"Loading model {model_name}... 🧠")
        start_time = time.time()

        model_dir = os.path.expanduser("~/models")
        os.makedirs(model_dir, exist_ok=True)

        model_path = hf_hub_download(
            repo_id="PygmalionAI/Pygmalion-3-12B-GGUF",
            filename=model_name,
            local_dir=model_dir,
            cache_dir=model_dir,
        )

        elapsed_time = time.time() - start_time
        print(f"Model loaded from {model_path} in {elapsed_time:.2f} seconds")

        return model_path

    def ensure_model(self, model_path):
        """Pull the model into Ollama."""
        print(f"Ensuring Ollama model '{self.model_alias}' from '{model_path}'...")
        start_time = time.time()
        
        client = Client()
        digest = client.create_blob(model_path)
        
        # Create a modelfile with GPU configuration if requested
        modelfile_content = f"""
FROM {self.model_alias}
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
"""
        
        # Add GPU configuration if requested
        if self.use_gpu:
            modelfile_content += "PARAMETER gpu_layers 99\n"  # Use all available layers on GPU
        
        create(
            model=self.model_alias, 
            modelfile=modelfile_content,
            files={self.model_alias: digest}
        )
        
        elapsed_time = time.time() - start_time
        print(f"Model '{self.model_alias}' prepared in {elapsed_time:.2f} seconds.")

    def generate_response(self, prompt_text: str) -> str:
        """Generate a response using Ollama."""
        print("Generating response...")
        start_time = time.time()
        
        # Monitor memory usage before generation
        mem_before = psutil.virtual_memory()
        
        # Generate the response
        resp = generate(
            model=self.model_alias,
            prompt=prompt_text,
            options={
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "num_predict": 2048,  # Max tokens to generate
            }
        )
        
        # Check memory usage after generation
        mem_after = psutil.virtual_memory()
        mem_used = (mem_before.available - mem_after.available) / (1024**2)  # MB
        
        elapsed_time = time.time() - start_time
        response_text = resp['response'].strip()
        
        print(f"Response generated ({len(response_text)} chars)")
        print(f"  Time: {elapsed_time:.2f} seconds")
        print(f"  Memory used: {mem_used:.2f} MB")
        print(f"  System memory: {mem_after.percent:.1f}% used")
        
        return response_text

# For testing the chatbot directly
if __name__ == "__main__":
    chatbot = ChatBot(use_gpu=True)
    test_prompt = "Tell me a short story about a wizard."
    _, response = chatbot.prompt(test_prompt)
    print(f"\nResponse:\n{response}")
