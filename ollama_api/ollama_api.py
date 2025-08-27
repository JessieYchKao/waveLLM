import requests
import json
import re

# curl --location 'http://localhost:11434/api/generate' --data '{ "model": "llama3.2:latest", "prompt": "Why is the sky blue?", "stream": false }'

class Completions:
    '''
        Completeion class to post API request to ollama
    '''
    def __init__(self, client):
        self._client = client

    def create(self, model, messages, stream=False):
        """
        Creates a model response for the given chat conversation.

        This method sends a request to the Ollama /api/generate endpoint.

        Args:
            model (str): The name of the model to use (e.g., 'llama3.2:latest').
            messages (list): A list of message objects, where each object has
                                a 'role' and 'content'.
            stream (bool): Whether to stream the response. Defaults to False.

        Returns:
            A response object that mimics the OpenAI structure, containing the
            model's reply.
        """
        api_url = f"{self._client.base_url}/api/generate"
        
        # Extract system and user prompts from the messages list
        system_prompt = next((msg['content'] for msg in messages if msg['role'] == 'system'), None)
        user_prompt = next((msg['content'] for msg in reversed(messages) if msg['role'] == 'user'), '')
        
        payload = {
            "model": model,
            "prompt": user_prompt,
            "stream": stream
        }
        
        # Add the system prompt to the payload if it exists
        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(api_url, json=payload)
            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status() 
            
            # Parse the JSON response from Ollama
            ollama_response = response.json()

            # Format the Ollama response to mimic the OpenAI response structure
            return self._format_as_openai_response(ollama_response)

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while communicating with the Ollama API: {e}")
            return None
    
    def _format_as_openai_response(self, ollama_response):
        """
        Converts a single Ollama response into an OpenAI-like object structure.
        """
        # Create a simple class to mimic the nested object structure
        class Message:
            def __init__(self, role, content):
                self.role = role
                self.content = content
        
        class Choice:
            def __init__(self, message):
                self.message = message
        
        class Response:
            def __init__(self, choices):
                self.choices = choices
        
        assistant_message = Message(
            role="assistant",
            content=ollama_response.get("response", "")
        )
        
        # message = Choice(message=assistant_message)

        think_matches = re.findall(r"<think>(.*?)</think>", assistant_message.content, re.DOTALL)
        think = " ".join(m.strip() for m in think_matches)

        # Remove think tags to get the visible response
        response = re.sub(r"<think>.*?</think>", "", assistant_message.content, flags=re.DOTALL).strip()

        # Wrap into your Choice/Response structure
        response_choice = Choice(message=Message(role="agent", content=response))
        think_choice = Choice(message=Message(role="agent", content=think))

        return Response(choices=[response_choice, think_choice])

class Chat:
    '''
        Serves no purpose other than to add another layer to match the openai api request format
    '''
    def __init__(self, client):
        self.completions = Completions(client)

class Ollama:
    """
    A helper API wrapper for Ollama that mimics the OpenAI client structure.
    
    This client translates the OpenAI-like method calls into the corresponding 
    Ollama API requests.
    """

    def __init__(self, base_url="http://localhost:11434"):
        """
        Initializes the Ollama client.

        Args:
            base_url (str): The base URL of the Ollama API server.
        """
        self.base_url = base_url
        self.chat = Chat(self)
   

# --- Example Usage ---

if __name__ == "__main__":
    # 1. Initialize the client
    # This assumes your Ollama server is running on the default address.
    client = Ollama(base_url="http://biaslab0.ics.uci.edu:11434")

    # 2. Define the model and messages
    MODEL_NAME_OLLAMA = "deepseek-r1:671b"
    greet_message = "You are a helpful assistant."
    user_prompt = "Why is the sky blue?"

    # 3. Call the create method with the OpenAI-like structure
    print(f"Sending prompt to model: '{MODEL_NAME_OLLAMA}'...")
    response = client.chat.completions.create(
        model=MODEL_NAME_OLLAMA,
        messages=[
            {"role": "system", "content": greet_message},
            {"role": "user", "content": user_prompt},
        ],
        stream=False
    )

    # 4. Access the response content
    if response:
        # The response object can be accessed just like the OpenAI library's response
        assistant_reply = response.choices[0].message.content
        print("\n--- Assistant's Response ---")
        print(assistant_reply)
        print("----------------------------\n")