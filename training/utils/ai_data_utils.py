from google import genai
import pandas as pd
import time
import itertools
import os
from dotenv import load_dotenv
import random

load_dotenv()


GEMINI_API_KEY_1 = os.getenv("GEMINI_API_KEY_1")
GEMINI_API_KEY_2 = os.getenv("GEMINI_API_KEY_2")
GEMINI_API_KEY_3 = os.getenv("GEMINI_API_KEY_3")
# List of your API keys
api_keys = [
    GEMINI_API_KEY_1,
    GEMINI_API_KEY_2,
    GEMINI_API_KEY_3
]

# list of fields
list_of_fields = [
    "Accounting", "Acting", "Art", "Architecture", "Baking", 
    "Barbering", "Biology", "Carpentry", "Cooking", "Chemistry", 
    "Civil Engineering", "Computer Science", "Construction", "Consulting", "Dentistry", 
    "Design", "Medicine", "Electricity", "Engineering", "Farming", 
    "Fashion Design", "Filmmaking", "Firefighting", "Fishing", 
    "Geology", "Graphic Design", "Hair Styling", "History", "Hospitality", 
    "Housekeeping", "Human Resources", "Illustration", "Industrial Engineering", "Interpretation", 
    "Information Technology", "Journalism", "Judiciary", "Law", "Library Science", 
    "Lifeguarding", "Mechanics", "Music", "Nursing", "Nutrition", 
    "Optometry", "Photography", "Physician", "Aviation", "Plumbing", 
    "Policing", "Programming", "Project Management", "Real Estate", "Research",
    "Artificial Intelligence", "Blockchain", "Cloud Computing", "Cybersecurity", "Data Science", 
    "Data Engineering", "Database Administration", "DevOps", "Machine Learning", "Mobile Development", 
    "Network Engineering", "Quantum Computing", "Robotics", "Software Development", "Web Development",
    "UI/UX Design", "Game Development", "Cryptocurrency", "Blockchain Development", "Ethical Hacking", 
    "Internet of Things", "Big Data", "Augmented Reality", "Virtual Reality", "Systems Administration"
]

# Create iterators that cycles through the API keys and list of fields
api_key_iterator = itertools.cycle(api_keys)

def get_prompt(field: list = list_of_fields) -> str:
    chosen_field = random.choice(field)
    final_prompt = f"""You are an expert in the field of {chosen_field} who is also very skilled
    at writing very good and impactful medium article. Your task is to write a very detailed
    medium article of at least 700 words on any interesting topic of your choice within
    the field. You must strive really hard to make sure that the article does not sound ai-generated.
    You must communicate your idea brilliantly like an highly respected expert that you are.
    """
    return final_prompt

def generate_text(prompt, api_key):
    """
    Generate text using the specified API key and prompt.
    """
    # Initialize the genai client with the current API key
    client = genai.Client(api_key=api_key)

    # Generate content based on the prompt
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt]
    )

    return response.text  # Extract the text from the response

# Initialize an empty list to store the generated text
data = []

for i in range(500):
    # Get the next API key from the iterator
    current_api_key = next(api_key_iterator)

    # Define your prompt here
    prompt = get_prompt()

    try:
        # Generate text using the current API key
        generated_text = generate_text(prompt, current_api_key)
        # Append the generated text to the data list
        data.append(generated_text)
        print(f'Generated text number {i+1} successfully')
    except Exception as e:
        # Handle exceptions (e.g., API errors)
        print(f"Error generating text for row {i+1}: {e}")
        data.append(None)  # Append None if an error occurs

    # Wait for 3 seconds before the next iteration to switch API keys
    time.sleep(3)

# Create a DataFrame from the data list
df = pd.DataFrame(data, columns=['GeneratedText'])

# Save the DataFrame to a CSV file
df.to_csv('generated_texts_two.csv', index=False)

print("Text generation complete. Data saved to 'generated_texts.csv'.")
