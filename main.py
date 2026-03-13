import os
import openai
from dotenv import load_dotenv

def run_api_call():
    """
    Loads configuration from .env and executes the chat completion API call.
    """
    # Load all variables from the .env file
    load_dotenv() 
    
    # --- 1. Get Configuration Details ---
    # We retrieve the key directly, as per the simplified setup
    api_base = os.getenv("NAI_BASE_URL")
    api_key = os.getenv("NAI_API_KEY")      
    model_name = os.getenv("NAI_MODEL_NAME")

    # --- 2. Validation Check (with the last successful model name) ---
    if not all([api_base, api_key, model_name]):
        print("\n❌ ERROR: Missing required configuration in .env file (URL, Key, or Model).")
        print(f"DEBUG - Base URL status: {'LOADED' if api_base else 'MISSING'}")
        print(f"DEBUG - Key status: {'LOADED' if api_key else 'MISSING'}")
        print(f"DEBUG - Model Name status: {'LOADED' if model_name else 'MISSING'}")
        return

    # --- 3. Configure the client and make the API call ---
    try:
        # Instantiate the client
        client = openai.OpenAI(
            base_url=api_base,
            api_key=api_key,
        )
        
        print(f"\nAttempting to connect to {api_base} using model {model_name}...")
        
        # Request a chat completion
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a concise, helpful assistant."},
                {"role": "user", "content": "Explain why you are the best model for McNuggets analysis in three points."}
            ]
        )
        
        # --- 4. Print the result ---
        print("\n✅ API Call Successful!")
        print("---------------------------------")
        print("Response:")
        print(response.choices[0].message.content)
        print("---------------------------------")

    # --- 5. Handle potential errors ---
    except openai.AuthenticationError:
        print("\n❌ API Error: Authentication Failed (401). Check your NAI_API_KEY.")
    except openai.NotFoundError:
        print(f"\n❌ API Error: Model '{model_name}' not found (404). Check NAI_MODEL_NAME.")
    except openai.APIConnectionError as e:
        print(f"\n❌ API Error: Connection Failed. Check NAI_BASE_URL or your network. Details: {e}")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    run_api_call()
