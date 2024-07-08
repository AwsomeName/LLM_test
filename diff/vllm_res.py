
from vllm import LLM, SamplingParams


prompts = [
    "Hello, what is apple?  ",
]

# Create a sampling params object.
sampling_params = SamplingParams(

        temperature=0,
        max_tokens=500, 
        frequency_penalty=1.2
        )

# Create an LLM.
llm = LLM(model="/hy-tmp/Qwen1.5-7B-Chat", block_size=8, gpu_memory_utilization= 0.8, max_model_len=4000)

for i in range(1):
    outputs = llm.generate(prompts, sampling_params)
    # Print the outputs.
    for output in outputs:
        prompt = output.prompt
        generated_text = output.outputs[0].text
        token_ids = output.outputs[0].token_ids
        print(generated_text)

"""
Apple is a technology company based in Cupertino, California, that was founded in 1976. It is best known for its line of consumer electronics, including iPhones, iPads, Mac computers, and smartwatches. Apple also produces software such as macOS and iOS operating systems, as well as services like the App Store and iCloud.

The company has revolutionized the technology industry with its innovative designs and user-friendly interfaces. Its products are popular worldwide and have become cultural symbols of innovation and style. In addition to hardware sales, Apple generates significant revenue through software updates, app sales, and subscription services.

Apple's mission statement is "to make computers easy to use again," which it achieves by combining simplicity with advanced features in its products. The company has a strong focus on privacy and security for its users' data. With a global presence through retail stores, online sales channels, and partnerships with carriers worldwide, Apple continues to be one of the most valuable companies globally.

I'm a bit confused.\nApple is the company that makes iPhones, iPads, and Macs.  Apple also owns the iPhone line of computers and tablets.
"""
