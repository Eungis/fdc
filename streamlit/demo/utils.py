import time
import random


# Streamed response emulator
def response_generator():
    response = random.choice(
        [
            "Hello there! How can I assist you today?",
            "Hi, human! Is there anything I can help you with?",
            "Do you need help?",
        ]
    )
    for i, word in enumerate(response.split()):
        if i == 0:
            yield "AI: " + word + " "
        else:
            yield word + " "
        time.sleep(0.05)
