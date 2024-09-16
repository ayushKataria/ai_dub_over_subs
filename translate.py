from transformers import M2M100ForConditionalGeneration
from tokenization_small100 import SMALL100Tokenizer

model = None
tokenizer = None

def translate(text: str, target_language: str):
    global model, tokenizer
    if model is None:
        model = M2M100ForConditionalGeneration.from_pretrained("alirezamsh/small100")
    if tokenizer is None:
        tokenizer = SMALL100Tokenizer.from_pretrained("alirezamsh/small100")
    
    tokenizer.tgt_lang = target_language
    encoded = tokenizer(text, return_tensors="pt")
    generated_tokens = model.generate(**encoded)
    article_hi = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
    return article_hi