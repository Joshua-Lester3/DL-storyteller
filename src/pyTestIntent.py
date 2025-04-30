# intent_parser.py

# REQUIRES NUMPY 1.26.0
from transformers import pipeline
import spacy
import spacy.cli

# Download spaCy model
spacy.cli.download("en_core_web_sm")

# Load NLP models
nlp = spacy.load("en_core_web_sm") # noun extractor model we want to use
classifier = pipeline("zero-shot-classification") # intent classifier model from huggingface

# Define possible intents
intents = [    
    "Move",
    "Use",
    "Take",
    "Drop",
    "Examine",
    "Inventory",
    "Unknown"
]

# This function uses spaCy to extract nouns and proper nouns from the input text
# returns all of the nouns as a list
def extract_nouns(text):
    # text is a str
    doc = nlp(text)
    return [token.text.lower() for token in doc if token.pos_ in ("NOUN", "PROPN")]

def classify_intent(text):
    # Use the hugging face pipeline to classify the intent of the text
    # possible intents are defined in the intents list above
    result = classifier(text, candidate_labels=intents)

    # result is a dict with the keys "labels" and "scores"
    # return the result label with the highest score
    return result["labels"][0]

def find_object(nouns, inventory, environment):
    for noun in nouns:

        # Return if the noun is in the inventory or environment
        if noun in inventory:
            return "inventory", noun
        elif noun in environment:
            return "environment", noun
        
    # If no noun is not in inventory or environment, return None
    return None, None


# Main function to call to hanldle user input
def handle_input(text):
    # Get intent
    intent = classify_intent(text)
    # get nouns from sentence
    nouns = extract_nouns(text)
    # Get where the object is, and what object it is
    # Will be none if the user input was not valid with the surroundings
    source, obj = find_object(nouns, inventory, environment)

    print(f"\nUser Input: {text}")
    print(f"Detected Intent: {intent}")
    print(f"Extracted Nouns: {nouns}")

    # prints inventory
    if intent == "Inventory":
        print("Inventory contains:", ", ".join(inventory))

    # Only uses object if it is in your inventory
    elif intent == "Use":
        if source == "inventory":
            print(f"Using {obj}.")
        else:
            print(f"{obj} is not in your inventory.")

    # Only takes or examines object if it is in the environment
    elif intent in {"Take", "Examine"}:
        if source == "environment":
            print(f"{intent} the {obj}.")

            # Adds object to inventory and removes from environment if taking
            if intent == "Take":
                inventory.add(obj)
                environment.remove(obj)
        else:
            print(f"No {obj} found in the environment.")
    
    # Move direction
    elif intent == "Move":
        print(f"Moving... (Direction)")
    
    # Drop object from inventory to environment
    elif intent == "Drop":
        if source == "inventory":
            print(f"Dropping {obj}.")
            inventory.remove(obj)
            environment.add(obj)
        else:
            print(f"{obj} is not in your inventory.")

    # For other intents that may not be defined
    else:
        print("Unknown intent or no action matched.")


# Test it with sample input
user_inputs = [
    "Use the key on the door",
    "Show me my inventory",
    "Take the sword",
    "Examine the gate",
    "Go north",
    "Drop armor"
]

# Sample inventory and environment
inventory = {"key", "torch", "map"}
environment = {"guard", "gate", "sword", "chest"}

# Go through each element in user_inputs and call the handle_input function
# Each function will automatically print the results
for text in user_inputs:
    handle_input(text)
