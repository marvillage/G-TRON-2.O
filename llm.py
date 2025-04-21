import torch
from transformers import pipeline

# Initialize the vision pipeline with proper configuration
vision_pipe = pipeline(
    task="image-text-to-text",
    model="Qwen/Qwen2.5-VL-7B-Instruct",
    device="cpu",  # Force CPU usage to avoid memory issues
    torch_dtype=torch.float32  # Use float32 for better compatibility
)
                