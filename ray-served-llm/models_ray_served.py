import ray
import torch
import logging
import transformers

from starlette.requests import Request
from transformers import AutoTokenizer

LOGGER = logging.getLogger(__name__)

def get_torch_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    elif torch.backends.mps.is_available():
        return torch.device("mps")
    else:
        return torch.device("cpu")


@ray.serve.deployment
class ModelServer:
    def __init__(self, model_id: str):
        # Load model
        self.model_id = model_id
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.tokenizer=tokenizer
        self.model = transformers.pipeline(
            "text-generation",
            model=model_id,
            tokenizer=tokenizer,
            torch_dtype=torch.bfloat16, # this will probably won't work for M1, use torch.float16 instead
            trust_remote_code=True,
            device_map= get_torch_device(), # "auto" may be used as well
        ) 


    def generate_text(self, input_text):
        # Tokenize the input text
        input_tokens = self.tokenizer(input_text, return_tensors='pt')

        # Move the input tokens to the same device as the model
        input_tokens = input_tokens.to(self.model.device)

        # Generate text using the fine-tuned model
        output_tokens = self.model.generate(**input_tokens, max_new_tokens=200)

        # Decode the generated tokens to text
        output_text = self.tokenizer.decode(output_tokens[0], skip_special_tokens=True)
        return output_text

    async def __call__(self, http_request: Request) -> str:
        data = await http_request.json()
        output = self.generate_text(data["inputs"])
        LOGGER.warning(f"Output: {output}")
        return output
