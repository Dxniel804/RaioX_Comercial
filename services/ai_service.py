from google import genai

def ler_prompt():
    with open('knowledge/prompt.txt', 'r') as file:
        return file.read()