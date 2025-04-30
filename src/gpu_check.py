"""
Simple script to check for GPU support in your environment.
Run this script to verify if your system has GPU support properly configured.
"""

import platform
import os

def check_system():
    """Print basic system information"""
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python version: {platform.python_version()}")
    
    # Check if running in a container
    in_container = os.path.exists("/.dockerenv")
    print(f"Running in container: {in_container}")
    
    # Check Azure-specific environment variables
    if any(k.startswith('AZURE_') for k in os.environ):
        print("Azure environment detected")
        
    print("\n" + "="*50)

def check_gpu_torch():
    """Check for GPU support using PyTorch"""
    try:
        import torch
        print("PyTorch version:", torch.__version__)
        cuda_available = torch.cuda.is_available()
        print(f"CUDA available: {cuda_available}")
        
        if cuda_available:
            device_count = torch.cuda.device_count()
            print(f"GPU count: {device_count}")
            
            for i in range(device_count):
                print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
                print(f"  Memory: {torch.cuda.get_device_properties(i).total_memory / 1024**3:.2f} GB")
        else:
            print("No CUDA devices detected by PyTorch")
    except ImportError:
        print("PyTorch not installed")
    except Exception as e:
        print(f"Error checking PyTorch GPU: {e}")
    
    print("\n" + "="*50)

def check_gpu_tensorflow():
    """Check for GPU support using TensorFlow"""
    try:
        import tensorflow as tf
        print("TensorFlow version:", tf.__version__)
        
        gpus = tf.config.list_physical_devices('GPU')
        print(f"TensorFlow GPU devices: {len(gpus)}")
        
        if gpus:
            for gpu in gpus:
                print(f"  {gpu}")
            
            # Try to allocate memory on GPU
            try:
                with tf.device('/GPU:0'):
                    a = tf.constant([[1.0, 2.0], [3.0, 4.0]])
                    b = tf.constant([[5.0, 6.0], [7.0, 8.0]])
                    c = tf.matmul(a, b)
                print("Successfully executed TensorFlow operation on GPU")
            except Exception as e:
                print(f"Failed to run TensorFlow operation on GPU: {e}")
        else:
            print("No GPU devices detected by TensorFlow")
    except ImportError:
        print("TensorFlow not installed")
    except Exception as e:
        print(f"Error checking TensorFlow GPU: {e}")
    
    print("\n" + "="*50)

def check_system_resources():
    """Check system resources"""
    try:
        import psutil
        
        # CPU info
        cpu_count = psutil.cpu_count(logical=False)
        cpu_count_logical = psutil.cpu_count(logical=True)
        print(f"CPU cores: {cpu_count} physical, {cpu_count_logical} logical")
        
        # Memory info
        virtual_memory = psutil.virtual_memory()
        print(f"RAM: {virtual_memory.total / (1024**3):.2f} GB total")
        print(f"RAM usage: {virtual_memory.percent}%")
        
        # Disk info
        disk = psutil.disk_usage('/')
        print(f"Disk: {disk.total / (1024**3):.2f} GB total")
        print(f"Disk usage: {disk.percent}%")
    except ImportError:
        print("psutil not installed")
    except Exception as e:
        print(f"Error checking system resources: {e}")
    
    print("\n" + "="*50)

def check_nvidia_tools():
    """Check for NVIDIA tools"""
    try:
        # Check for nvidia-smi
        import subprocess
        result = subprocess.run(['nvidia-smi'], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE,
                                text=True)
        
        if result.returncode == 0:
            print("nvidia-smi found and working:")
            print(result.stdout.split('\n')[0:10])  # Show first 10 lines
        else:
            print("nvidia-smi failed:")
            print(result.stderr)
    except FileNotFoundError:
        print("nvidia-smi not found in PATH")
    except Exception as e:
        print(f"Error checking nvidia-smi: {e}")
    
    print("\n" + "="*50)

def check_ollama():
    """Check Ollama installation and GPU support"""
    try:
        import subprocess
        result = subprocess.run(['ollama', '--version'], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE,
                                text=True)
        
        if result.returncode == 0:
            print(f"Ollama version: {result.stdout.strip()}")
            
            # Check if GPU is enabled in Ollama
            try:
                gpu_check = subprocess.run(['ollama', 'list'], 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE,
                                          text=True)
                print("Ollama models:")
                print(gpu_check.stdout)
                
                if "FAILED" in gpu_check.stderr:
                    print("Ollama errors:")
                    print(gpu_check.stderr)
            except Exception as e:
                print(f"Error checking Ollama models: {e}")
        else:
            print("Ollama not found or error:")
            print(result.stderr)
    except FileNotFoundError:
        print("Ollama not found in PATH")
    except Exception as e:
        print(f"Error checking Ollama: {e}")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    print("\nGPU SUPPORT CHECKER")
    print("="*50)
    
    check_system()
    check_system_resources()
    check_nvidia_tools()
    check_gpu_torch()
    check_gpu_tensorflow()
    check_ollama()
    
    print("\nCheck complete!")
