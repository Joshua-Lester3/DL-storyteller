from transformers import pipeline

class BertContextExtractor:
    def __init__(self):
        # Hugging Face pipeline for question answering
        self.qa_pipeline = pipeline("question-answering", model="timpal0l/mdeberta-v3-base-squad2")
    
    def extract(self, context):
        # context will be a string of text

        # These are the questions we want to ask the model
        intents = {
            "intent": "What is the player trying to do?",
            "object": "What object is involved?",
            "direction": "Is there any direction or location?",
            "character": "Is there a character or person mentioned?"
        }

        # Store the results in a dictionary
        results = {}

        # Loop through the intents and ask the model each question
        for key, question in intents.items():
            # ask the model the question
            answer = self.qa_pipeline(question=question, context=context)

            # if the answer score is greater than 0.3, add it to the results
            # print(answer['score'])
            if answer["score"] > 0.3:
                results[key] = answer["answer"]

        # results will be a dict with keys "intent", "object", "direction", or "character", with the values being the answers from the model
        return results


if __name__ == "__main__":
    # Example usage
    inputs = [
        "Go north towards the forest",
        "Take the rusty key",
        "Talk to the mysterious stranger",
        "Open the ancient chest",
        "Use the key to unlock the door"
    ]
    extractor = BertContextExtractor()

    for text in inputs:
        # Call the extract method with the text as context
        results = extractor.extract(text)
        print(results)
    