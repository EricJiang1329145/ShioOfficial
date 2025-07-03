# pip3 install transformers
# python3 deepseek_tokenizer.py
import transformers


def get_tokenize(thestr, path):
    chat_tokenizer_dir = path + "/"

    tokenizer = transformers.AutoTokenizer.from_pretrained(chat_tokenizer_dir, trust_remote_code=True)
    result = tokenizer.encode(thestr)
    print(result)


if __name__ == "__main__":
    get_tokenize("Hell", "./")
