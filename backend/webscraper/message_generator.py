from transformers import T5Tokenizer, T5ForConditionalGeneration

# Initialize T5 model and tokenizer only once to save resources
model_name = "t5-small"
model = T5ForConditionalGeneration.from_pretrained(model_name)
tokenizer = T5Tokenizer.from_pretrained(model_name)

def generate_message(company_name, mission):
    """Generate a personalized message for a company using T5 model."""
    prompt = f"Write a professional introductory message for {company_name}. Their mission is {mission}."
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    outputs = model.generate(inputs.input_ids, max_length=150)
    message = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return message