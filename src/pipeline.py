import json
import time
import boto3
import pandas as pd
from datetime import datetime, timezone
from prompt import build_prompt

BUCKET_NAME = "airline-sentiment-results-rishab"
MODEL_ID = "us.amazon.nova-lite-v1:0"
MAX_RATE = 10

def classify_tweet(bedrock, tweet_text):
    system_prompt, user_message = build_prompt(tweet_text)
    response = bedrock.converse(
        modelId=MODEL_ID,
        system=[{"text": system_prompt}],
        messages=[{"role": "user", "content": [{"text": user_message}]}]
    )
    return response["output"]["message"]["content"][0]["text"].strip().lower()


def lambda_handler(event, context):
    # Read CSV from S3
    s3 = boto3.client("s3")
    csv_key = event.get("csv_key", "data/airline_tweets.csv")
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=csv_key)
    df = pd.read_csv(obj["Body"])

    # Randomly sample 100 tweets without replacement
    df_sample = df[["tweet_id", "text"]].dropna(subset=["text"]).sample(n=100, replace=False)

    # Set up Bedrock and classify each tweet
    bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
    results = []

    for _, row in df_sample.iterrows():
        start = time.time()
        tweet_id = str(row["tweet_id"])
        tweet_text = str(row["text"])

        try:
            sentiment = classify_tweet(bedrock, tweet_text)
        except Exception as e:
            sentiment = "error"
            print(f"Error on tweet {tweet_id}: {e}")

        results.append({
            "tweet_id": tweet_id,
            "text": tweet_text,
            "predicted_sentiment": sentiment,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        print(f"{tweet_id}: {sentiment}")

        # Rate limit to max 10 tweets per second
        elapsed = time.time() - start
        if elapsed < 1.0 / MAX_RATE:
            time.sleep(1.0 / MAX_RATE - elapsed)

    # Save results to S3
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key="results/sentiment_results.json",
        Body=json.dumps(results, indent=2),
        ContentType="application/json"
    )

    return {
        "statusCode": 200,
        "body": json.dumps(f"Processed {len(results)} tweets")
    }