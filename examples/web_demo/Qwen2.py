# Copyright (c) 2023 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
import os

# Ignore Tensor-RT warning from huggingface
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import gradio as gr
import argparse
from demo_utils import ChatDemo, XFT_DTYPE_LIST, XFT_KVCACHE_DTYPE_LIST


parser = argparse.ArgumentParser()
parser.add_argument("-t", "--token_path", type=str, default="/data/models/Qwen1.5-0.5B-Chat", help="Path to token file")
parser.add_argument("-m", "--model_path", type=str, default="/data/models/Qwen1.5-0.5B-Chat-xft", help="Path to model file")
parser.add_argument("-d", "--dtype", type=str, choices=XFT_DTYPE_LIST, default="fp16", help="Data type")
parser.add_argument("--kv_cache_dtype", type=str, choices=XFT_KVCACHE_DTYPE_LIST, default="fp16", help="KV cache dtype")


class Qwen2Demo(ChatDemo):

    def create_chat_input_token(self, query, history):
        if history is None:
            history = []
        print(f"old history = {history}")
        _history = history + [(query, None)]
        print(f"new history = {_history}")
        messages = []
        for idx, (user_msg, model_msg) in enumerate(_history):
            print(f"user_msg={user_msg}, model_msg={model_msg}")
            if idx == len(_history) - 1 and not model_msg:
                messages.append({"role": "user", "content": user_msg})
                break
            if user_msg:
                messages.append({"role": "user", "content": user_msg})
            if model_msg:
                messages.append({"role": "assistant", "content": model_msg})
        
        prompt = self.tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
        model_inputs = self.tokenizer.encode(prompt, add_special_tokens=True, return_tensors="pt").to("cpu")
        return model_inputs

    def config(self):
        return {
            "do_sample": True,
            "top_p": 0.8,
            "top_k": 20,
            "repetition_penalty": 1.1,
            "stop_words_ids": [[151643], [151645]],
        }

    def html_func(self):
        gr.HTML("""<h1 align="center">xFasterTransformer</h1>""")
        gr.HTML("""<h1 align="center">通义千问2</h1>""")


if __name__ == "__main__":
    args = parser.parse_args()
    demo = Qwen2Demo(args.token_path, args.model_path, dtype=args.dtype, kv_cache_dtype=args.kv_cache_dtype)

    demo.launch(False)
