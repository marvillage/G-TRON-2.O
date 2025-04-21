import os
from diffusers import StableDiffusionPipeline
import torch
import random

# Load the Stable Diffusion model
pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
pipe = pipe.to("cpu")

# Ensure directories exist
os.makedirs("dataset/toxic", exist_ok=True)
os.makedirs("dataset/non_toxic", exist_ok=True)

# Define base prompts for toxic e-waste images
toxic_base_prompts = [
    "Hazardous electronic waste dumped in landfill, leaking chemicals",
    "Poisonous e-waste with exposed circuit boards and broken batteries",
    "Toxic computer parts with corrosion and dangerous chemicals",
    "Environmentally harmful electronic waste with damaged components",
    "Dangerous pile of discarded electronics with toxic materials",
    "Harmful e-waste pollution affecting soil and water, environmental damage",
    "Unsafe electronic waste disposal with lead and mercury contamination",
    "Improperly discarded computers and electronics leaking harmful chemicals",
    "Toxic electronic circuit boards with exposed heavy metals",
    "Hazardous chemicals leaching from electronics into environment"
]

# Define base prompts for non-toxic e-waste images
non_toxic_base_prompts = [
    "Neatly sorted recyclable electronic waste, clean circuit boards",
    "Properly disposed of batteries in a recycling center",
    "Eco-friendly electronic waste disposal, sustainable recycling bins",
    "Safe e-waste collection with reusable electronics and green technology",
    "Organized electronic component recycling, environmentally friendly",
    "Clean tech recycling facility with properly handled electronics",
    "Sustainable e-waste management with sorted components",
    "Professional electronic waste recycling center with safe practices",
    "Responsibly managed computer recycling with proper containment",
    "Green technology recycling with proper safety measures"
]

# Adjectives to add variety
adjectives = [
    "modern", "industrial", "clean", "organized", "professional", 
    "detailed", "high-resolution", "realistic", "photorealistic", "urban"
]

# Detail phrases to add variation
detail_phrases = [
    "in a recycling facility", "with clear lighting", "with visible details",
    "in high definition", "with natural lighting", "in a warehouse setting",
    "with proper labeling", "in an industrial environment", "with workers present",
    "with safety equipment", "during daytime", "with proper containers"
]

# Style modifiers for image variety
style_modifiers = [
    "photo", "digital photograph", "documentary photography", 
    "industrial photography", "environmental photography", 
    "professional photograph", "detailed image", "high quality picture",
    "4K resolution", "high detail photography"
]

# Generate 100 unique prompts for each category
def generate_unique_prompts(base_prompts, count=100):
    unique_prompts = []
    
    while len(unique_prompts) < count:
        # Select a random base prompt
        base = random.choice(base_prompts)
        
        # Add random adjective (70% chance)
        if random.random() < 0.7:
            base = f"{random.choice(adjectives)} {base}"
        
        # Add random detail phrase (60% chance)
        if random.random() < 0.6:
            base = f"{base} {random.choice(detail_phrases)}"
        
        # Add style modifier (80% chance)
        if random.random() < 0.8:
            base = f"{base}, {random.choice(style_modifiers)}"
        
        # Only add if the prompt is unique
        if base not in unique_prompts:
            unique_prompts.append(base)
    
    return unique_prompts

# Generate prompts
toxic_prompts = generate_unique_prompts(toxic_base_prompts, 50)
non_toxic_prompts = generate_unique_prompts(non_toxic_base_prompts, 50)

print(f"Generated {len(toxic_prompts)} unique toxic prompts")
print(f"Generated {len(non_toxic_prompts)} unique non-toxic prompts")

# Function to generate and save images
def generate_images(prompts, save_dir, prefix, num_inference_steps=50, batch_size=4):
    total_prompts = len(prompts)
    
    # Process in batches to show progress
    for i in range(0, total_prompts, batch_size):
        batch_end = min(i + batch_size, total_prompts)
        batch_prompts = prompts[i:batch_end]
        print(f"Generating {prefix} images {i+1}-{batch_end} of {total_prompts}...")
        
        # Generate images one by one to avoid memory issues
        for j, prompt in enumerate(batch_prompts):
            idx = i + j
            try:
                # Set a random seed for reproducibility
                generator = torch.Generator().manual_seed(random.randint(1, 10000))
                
                # Generate image
                image = pipe(
                    prompt, 
                    num_inference_steps=num_inference_steps,
                    generator=generator
                ).images[0]
                
                # Save image
                image_path = f"{save_dir}/{prefix}_{idx+1:03d}.jpg"
                image.save(image_path)
                print(f"Saved {image_path}")
                
            except Exception as e:
                print(f"Error generating image for prompt: {prompt}")
                print(f"Error details: {e}")

# Generate and save toxic images
generate_images(toxic_prompts, "dataset/toxic", "toxic")
print("✅ Generated Toxic E-Waste Images")

# Generate and save non-toxic images
generate_images(non_toxic_prompts, "dataset/non_toxic", "non_toxic")
print("✅ Generated Non-Toxic E-Waste Images")

# Save prompts for reference
with open("toxic_prompts.txt", "w") as f:
    for i, prompt in enumerate(toxic_prompts):
        f.write(f"{i+1:03d}: {prompt}\n")

with open("non_toxic_prompts.txt", "w") as f:
    for i, prompt in enumerate(non_toxic_prompts):
        f.write(f"{i+1:03d}: {prompt}\n")

print("✅ Saved prompt lists to text files")
print("Dataset generation complete!")