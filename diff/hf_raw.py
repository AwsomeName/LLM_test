

# Load model directly
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import AutoModel

tokenizer = AutoTokenizer.from_pretrained("/hy-tmp/Qwen1.5-7B-Chat", trust_remote_code=True)
# model = AutoModelForCausalLM.from_pretrained("/hy-tmp/Qwen1.5-7B-Chat", trust_remote_code=True).cuda().half()
model = AutoModel.from_pretrained("/hy-tmp/glm-4-9b", trust_remote_code=True).cuda().half()

prompt = [
    "Hello, what is apple?  ",
]

input_ids = tokenizer(prompt, return_tensors="pt").input_ids.cuda()

generated_ids = model.generate(input_ids, do_sample=False, repetition_penalty=1.2, max_new_tokens=500)

texts = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)

print(texts)


## QWEN 1.5 -7b
"""
Hello, what is apple?   Apple Inc. is a multinational technology company headquartered in Cupertino, California, that designs and sells consumer electronics, computer software, and online services. It was founded on April 1, 1976 by Steve Jobs, Steve Wozniak, and Ronald Wayne.\n\nSome of the products and services associated with Apple include:\n\n1. iPhones: A line of smartphones running iOS operating system.\n2. iPads: Tablet computers also using iOS.\n3. Macs: Personal computers powered by macOS (previously known as OS X).\n4. iPods: Portable media players.\n5. Apple Watch: A smartwatch that connects to iPhone or runs its ownOS.\n6. iTunes Store: Digital distribution platform for music, movies, TV shows, apps, and podcasts.\n7. iCloud: Cloud storage service offering various features like photos, documents, and backups.\n8. App Store: The marketplace where users can download third-party applications.\n9. Safari browser: Web browser used across all Apple devices.\n10. macOS Big Sur/ Catalina/ Mojave etc.: Operating systems for Mac computers.\n\nApple has been recognized for its innovation, design aesthetics, and financial performance, making it one of the most valuable companies globally. Its ecosystem of interconnected hardware and software allows users to seamlessly switch between different devices and access their data across platforms.'
"""

"""
['Hello, what is apple?   Apple Inc. is a multinational technology company headquartered in Cupertino, California, that designs and sells consumer electronics, computer software, and online services. It was founded on April 1, 1976 by Steve Jobs, Steve Wozniak, and Ronald Wayne.\n\nSome of the products and services associated with Apple include:\n\n1. iPhones: smartphones running iOS operating system\n2. iPads: tablets using iPadOS\n3. Mac computers: personal computers for both creative professionals and general users\n4. iPods: portable media players\n5. Apple Watch: smartwatches\n6. macOS: the operating system for Mac computers\n7. iTunes Store: digital media store and platform for music, movies, TV shows, apps, and podcasts\n8. iCloud: cloud storage and service\n9. Safari browser: web browser for macOS and iOS devices\n\nApple has been known for its innovative design, user-friendly interfaces, and integration across various product lines. The company also develops software like Microsoft Office competitors (such as Pages, Numbers, and Keynote) and offers services like Apple Music, Apple Pay, and Apple Maps.']"""

"""
I'm a bit confused.\nApple is the company that makes iPhones and iPads. They are also known for their Macs.\nI thought they were called Apple Pencils?\nThey're called Apple Pencils."


"""