from transformers import M2M100ForConditionalGeneration
from tokenization_small100 import SMALL100Tokenizer
from transformers.utils import logging

logging.set_verbosity_error()

model = None
tokenizer = None

def translate(text: str, target_language: str, device: str = 'cpu'):
    global model, tokenizer
    if model is None:
        model = M2M100ForConditionalGeneration.from_pretrained("alirezamsh/small100", device_map=device)
    if tokenizer is None:
        tokenizer = SMALL100Tokenizer.from_pretrained("alirezamsh/small100", device_map=device)
    
    tokenizer.tgt_lang = target_language
    encoded = tokenizer(text, return_tensors="pt").to(device)
    generated_tokens = model.generate(**encoded)
    article_hi = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
    return article_hi

if __name__ == "__main__":
    print(translate("Life is a box of chocolates", "hi", "cuda"))