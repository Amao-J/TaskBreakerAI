import requests

GEMINI_API_KEY ='AIzaSyBDZ2FpKjLo2L20lhHfWZE4XoqGaStDn1E'



import requests
import os
import json


GEMINI_API_ENDPOINT = "https://aistudio.google.com/app/prompts/11eEJij2g90vhbjQbNw2M2x8d88d_l6MR" # Placeholder URL - update when available

def generate_subtasks(goal_description, num_subtasks=3):
    """Generates subtasks using the Gemini API."""

    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",  # Replace with actual auth method
        "Content-Type": "application/json"
    }

    prompt = f"""
    Generate {num_subtasks} actionable and specific subtasks for this goal:
    {goal_description}
    """

    data = {
        "prompt": prompt,
        "model": "gemini-pro", # Or appropriate model name
        "parameters": {  # Add any specific parameters Gemini supports
           "temperature": 0.7, 
           "max_tokens": 150 # adjust as needed.
           # ... other parameters...
        }
    }


    response = requests.post(GEMINI_API_ENDPOINT, headers=headers, json=data)
    response.raise_for_status() # Raise an exception for bad status codes

    generated_text = response.json()['generated_text'] # Assuming the structure of the response
    subtasks = generated_text.strip().splitlines()
    return subtasks

 

def estimate_timeframe(subtask_description):
    """Estimates timeframe (in minutes) using Gemini."""

    headers = {
        "Authorization": f"Bearer {os.getenv('GEMINI_API_KEY')}",  # Replace with actual auth method
        "Content-Type": "application/json" }

    prompt = f"""
    Estimate the time in minutes to complete this subtask:
    {subtask_description}

    Provide only the number of minutes as an integer.
    """  # Highly specific prompt to help with parsing

    data = {
        "prompt": prompt,
        "model": "gemini-pro", # Or appropriate model name
        "parameters": {  # Add any specific parameters Gemini supports
           "temperature": 0.7, 
           "max_tokens": 150 }
        }


    response = requests.post(GEMINI_API_ENDPOINT, headers=headers, data=data) # Sending the request
    response.raise_for_status()
    try:
        time_estimate = int(response.json()['generated_text'].strip()) # Attempt direct integer conversion
        return time_estimate
    except (ValueError, KeyError, json.JSONDecodeError): # Handle errors
        return None
    
    
    
    
