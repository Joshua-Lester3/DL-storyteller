# pip install transformers sentence-transformers faiss-cpu

from transformers import pipeline, AutoTokenizer
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class VectorDB:
    def __init__(self):
        # HuggingFace summarization pipeline
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

        # Sentence embedding model
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

        # Tokenizer for token length check
        self.tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")

        # FAISS index setup. MiniLM embedding creates a vector of length 384
        self.summaries = []  
        # Stores actual summaries for lookup
        self.index = faiss.IndexFlatL2(384)

    def add_text(self, text):
        '''Summarizes output text from the language model, and adds it to the vdb
        text is a string (should be output from the language model)
        '''

        # Tokenize the input text and get the token count
        tokenized_input = self.tokenizer.encode(text)
        token_count = len(tokenized_input)
        
        # If the input is too short (e.g., less than 30 tokens), do not summarize
        if token_count < 30:
            summary = text
        else: # If the text is long enough, summarize this
            summary = self.summarizer(text, min_length = 10, max_length = 30)[0]['summary_text']

        # Create a vector based on the summary
        sum_embedding = self.embedder.encode([summary])

        # Add the summary embedding to faiss
        self.index.add(np.array(sum_embedding, dtype='float32'))

        # Keep a list of summaries. Stored as a string
        self.summaries.append(summary)

        # Return the summarized text
        return summary

    def query(self, text, top_k = 3):
        '''Returns summaries that are similar to the text
        text is a string that you want to query
        top_k is an int that queries for top_k similar summaries'''

        # Get the embedding of input text
        txt_embedding = self.embedder.encode([text])

        # Make the embedding of the input text a np array
        txt_embedding_np = np.array(txt_embedding, dtype='float32')

        # Query the vdb, returning the top_k elements that are similar to the input text
        D, I = self.index.search(txt_embedding_np, top_k)

        # List comprehension, fetching all the summaries 
        # index is in I, and self.summaries store the text summaries
        return [self.summaries[i] for i in I[0]]


if __name__ == "__main__":
    vdb = VectorDB()

    sample_texts = [
    # Technology
    "Artificial intelligence is rapidly transforming industries worldwide, enabling companies to analyze vast amounts of data and automate processes with unprecedented efficiency. Through machine learning algorithms, AI systems are capable of recognizing patterns, predicting outcomes, and continuously improving their performance. In sectors like healthcare, finance, and retail, AI is being used to enhance customer experiences, improve decision-making, and optimize operations. However, the widespread adoption of AI also raises concerns about job displacement, data privacy, and ethical implications, which need to be addressed as the technology continues to evolve.",
    "Quantum computing represents a groundbreaking shift in the field of computing, leveraging the principles of quantum mechanics to perform computations that would be impossible for traditional computers. Unlike classical bits, which represent either a 0 or a 1, quantum bits, or qubits, can exist in multiple states simultaneously, allowing quantum computers to solve certain complex problems exponentially faster than classical counterparts. While quantum computing holds great promise for fields such as cryptography, optimization, and drug discovery, the technology is still in its infancy, with many technical challenges to overcome before it becomes widely accessible.",
    "Blockchain technology ensures data integrity through decentralized consensus mechanisms and cryptographic security. It allows for transparent and immutable transactions, making it ideal for applications such as financial transactions, supply chain tracking, and secure voting systems. By eliminating the need for intermediaries, blockchain has the potential to reduce costs and increase trust across industries. However, concerns about scalability, energy consumption, and regulatory issues remain challenges that need to be addressed for blockchain to reach its full potential.",

    # Science
    "CRISPR-Cas9 technology has revolutionized the field of genetic engineering, providing scientists with an efficient and precise tool to modify DNA at the molecular level. By utilizing the natural defense mechanisms of bacteria, researchers can target specific genes and either activate, deactivate, or alter them with incredible accuracy. This breakthrough has vast potential for treating genetic disorders, improving agricultural crops, and advancing biomedical research. However, ethical concerns surrounding the use of CRISPR, especially in human germline editing, continue to spark debate about the potential risks and long-term consequences of manipulating the genetic code.",
    "Climate change is one of the most pressing challenges facing humanity today, driven primarily by the increasing concentration of greenhouse gases in the atmosphere, such as carbon dioxide (CO2), methane (CH4), and nitrous oxide (N2O). These gases trap heat and cause the Earth's average temperature to rise, leading to melting polar ice, rising sea levels, and more extreme weather events. The primary sources of greenhouse gas emissions are the burning of fossil fuels for energy, deforestation, and industrial activities. Tackling climate change requires urgent global cooperation to reduce emissions, transition to renewable energy sources, and implement policies to mitigate its impacts.",
    "Vaccines stimulate the immune system to recognize and fight pathogens without causing disease. They work by introducing a weakened or inactivated form of the pathogen or its components into the body, prompting the immune system to produce antibodies. This helps the body develop immunity against the pathogen, which can prevent future infections. Vaccines have been instrumental in reducing the spread of infectious diseases such as polio, measles, and smallpox, and they continue to play a crucial role in public health efforts worldwide.",

    # History
    "The Renaissance was a cultural and intellectual movement that began in Italy in the 14th century and spread across Europe over the following centuries. This period saw a renewed interest in the classical art, literature, and philosophy of ancient Greece and Rome, as well as significant advancements in science, politics, and exploration. The Renaissance produced some of the most famous artists in history, such as Leonardo da Vinci, Michelangelo, and Raphael, whose works continue to inspire awe and admiration. It also led to the rise of humanism, which emphasized the value of the individual and the pursuit of knowledge. The Renaissance laid the foundation for the modern world, influencing the development of Western civilization.",
    "World War II was one of the most devastating conflicts in human history, involving more than 30 countries and causing the deaths of millions of people. The war began in 1939 with the invasion of Poland by Nazi Germany, followed by the involvement of the Soviet Union, the United States, and other nations. The war's outcome reshaped global politics, with the defeat of the Axis powers and the establishment of two superpowers: the United States and the Soviet Union. The war also led to the creation of the United Nations, an international organization designed to promote peace and prevent future conflicts. The legacy of World War II continues to shape global relations and international policy to this day.",
    "The Industrial Revolution was a period of profound economic and social change that began in the late 18th century in Great Britain and spread to other parts of the world. It marked the transition from agrarian economies to industrialized societies, characterized by the growth of factories, mechanized production, and the rise of urbanization. This period saw the invention of new technologies, such as the steam engine and the spinning jenny, which revolutionized manufacturing processes and transportation. The Industrial Revolution significantly impacted social structures, leading to the growth of the middle class, but also created challenges such as poor working conditions and child labor.",

    # Society
    "Social media has had a profound impact on the way people communicate, connect, and share information. Platforms like Facebook, Twitter, Instagram, and TikTok allow individuals to instantly share their thoughts, photos, and videos with a global audience. While social media has democratized information and facilitated social movements, it has also contributed to the spread of misinformation, echo chambers, and cyberbullying. The rapid dissemination of news and opinions on social media can influence public opinion, political elections, and even social norms. As the influence of social media continues to grow, it raises important questions about privacy, accountability, and its role in society.",
    "Universal basic income (UBI) is a policy proposal in which a government guarantees a regular, unconditional cash payment to all citizens, regardless of their income or employment status. The idea behind UBI is to reduce poverty and income inequality by ensuring that everyone has a basic level of financial security. Proponents argue that UBI could also provide people with the freedom to pursue education, entrepreneurship, or creative endeavors without the fear of financial instability. Critics, however, question the economic feasibility of UBI and whether it would lead to disincentives to work. While no country has fully implemented UBI, some pilot programs are being tested to assess its potential impact.",
    "Education inequality continues to be a major social issue, often reflecting broader disparities in wealth and access to resources. In many countries, children from low-income families are less likely to have access to quality education, which can perpetuate cycles of poverty and inequality. Factors such as inadequate school funding, lack of access to technology, and limited educational opportunities can contribute to this problem. Addressing education inequality requires systemic changes in the education system, as well as policies that ensure all students have access to the resources and opportunities they need to succeed."
    ]


    for i, text in enumerate(sample_texts):
        vdb.add_text(text)
        print(f'Just summarized and added {i+1} to FAISS')

    query_text = "How do vaccines protect people from diseases?"

    similar_texts = vdb.query(query_text)

    print(similar_texts)


