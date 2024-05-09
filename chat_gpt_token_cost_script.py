import argparse
from transformers import GPT2Tokenizer


def calculate_chat_gpt_cost(input_text, output_text):
    """this function will take the prompt and response strings provided and run them through a GPT cost tokenizer
    library returning the total cost of the GPT API pull"""
    print(input_text)
    print(output_text)
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    input_token_count = len(tokenizer.encode(input_text))
    output_token_count = len(tokenizer.encode(output_text))

    input_price_per_1000_tokens = 0.0010  # $0.0010 per 1000 input tokens
    output_price_per_1000_tokens = 0.0020  # $0.0020 per 1000 output tokens

    input_price_per_token = input_price_per_1000_tokens / 1000
    output_price_per_token = output_price_per_1000_tokens / 1000
    input_cost = input_token_count * input_price_per_token
    output_cost = output_token_count * output_price_per_token
    total_cost = input_cost + output_cost
    return total_cost


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate ChatGPT cost based on text inputs")
    parser.add_argument("--prompt", type=str, required=True, help="Prompt text")
    parser.add_argument("--response", type=str, required=True, help="Response text")
    args = parser.parse_args()

    total_cost = calculate_chat_gpt_cost(args.prompt, args.response)
    print(f"gpt_run_cost: {total_cost:.8f}")
