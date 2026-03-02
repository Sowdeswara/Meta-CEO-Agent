from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Smaller model for 6GB GPU
model_id = "microsoft/phi-2"

print("CUDA Available:", torch.cuda.is_available())
print("GPU:", torch.cuda.get_device_name(0))

print("\nLoading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_id)

print("Loading model in 8-bit on GPU...")
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    load_in_8bit=True,
    device_map="auto"
)

model.eval()

print("\nModel loaded successfully.")
print("VRAM used:", round(torch.cuda.memory_allocated()/1024**3, 2), "GB")

prompt = "Explain why profit margin is important in business in 3 short sentences."

inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=120,
        temperature=0.7
    )

print("\n=== MODEL OUTPUT ===\n")
print(tokenizer.decode(outputs[0], skip_special_tokens=True))