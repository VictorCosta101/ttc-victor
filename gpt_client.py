import openai
import os

class GPTClient:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", temperature: float = 0.2, max_tokens: int = 1000):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate_content(self, assistant_prompt: str, user_prompt: str) -> dict:
        messages = [
            {"role": "assistant", "content": assistant_prompt},
            {"role": "user", "content": user_prompt}
        ]
        print(user_prompt)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            return {
                "response": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens
            }

        except openai.OpenAIError as e:
            return {"error": str(e)}
