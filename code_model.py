from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
import torch
from threading import Thread
from typing import TypedDict, List, Any


def get_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    else:
        return torch.device("cpu")


class CodingModel:
    model_name = "Qwen/Qwen3-0.6B"

    def __init__(self):
        device = get_device()
        dtype = torch.float16 if device == "mps" else torch.float32
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_fast=True)
        self.streamer = TextIteratorStreamer(self.tokenizer, skip_special_tokens=True, skip_prompt=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=dtype,
            low_cpu_mem_usage=True,
            attn_implementation="eager",
            device_map=None
        )

    def prepare_model_input(self, messages):
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False # thinking switch
        )
        model_inputs = self.tokenizer([text], return_tensors="pt", truncation=True, max_length=8192).to(self.model.device)
        return model_inputs

    def forward(self, model_inputs):
        generated_ids = self.model.generate(**model_inputs, max_new_tokens = 1024)
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
        try:
            index = len(output_ids) - output_ids[::-1].index(151668)
        except ValueError:
            index = 0
        content = self.tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")
        return content

    def forward_with_thread(self, model_inputs):
        print("Forward pass...")
        gen_kwargs = dict(**model_inputs,
                          max_new_tokens=1024,
                          do_sample=False,
                          use_cache=True,
                          pad_token_id=self.tokenizer.pad_token_id,
                          )

        thread = Thread(target=self.model.generate,
                        kwargs={**gen_kwargs, "streamer": self.streamer})
        thread.start()
        content = ""
        for text_chunk in self.streamer:
            content += text_chunk
            print(text_chunk, end="", flush=True)
        thread.join()

        return content

