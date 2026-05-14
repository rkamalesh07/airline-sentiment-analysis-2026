def build_prompt(tweet_text):
    system_prompt = (
        "You are a sentiment classifier for airline tweets. "
        "Classify the sentiment as exactly one of: positive, negative, or neutral. "
        "Respond with one word only. Do not explain your answer."
    )
    user_message = f'Tweet: "{tweet_text}"\nSentiment:'
    return system_prompt, user_message