# Airline Sentiment Analysis

## What This Does
This pipeline reads airline tweets from a CSV, sends each one to an LLM to classify the sentiment as positive, negative, or neutral, and saves the results to S3. It runs on AWS Lambda and processes at least 100 randomly sampled tweets at a max rate of 10 per second.

## AWS Services Used
- **CSV File** — the input tweet data
- **AWS Lambda** — runs the pipeline and enforces the rate limit
- **AWS Bedrock (Amazon Nova Lite)** — the LLM that classifies each tweet
- **AWS S3** — stores the output as a JSON file

## How to Set This Up
You need an AWS account. Create an S3 bucket, upload the tweets CSV to `data/airline_tweets.csv` inside it, and create a Lambda function with Python 3.12. Add the `AWSSDKPandas-Python312` layer, give the Lambda role Bedrock and S3 access, set the timeout to 5 minutes, upload the two files from `src/`, and set the handler to `pipeline.lambda_handler`.

## How to Run It
Go to the Lambda function, open the Test tab, and use this as the test event:

```json
{
  "csv_key": "data/airline_tweets.csv"
}
```

It will process 100 tweets and save results to S3.

## Output
Results get saved to `results/sentiment_results.json` in the S3 bucket. Each record looks like:

```json
{
  "tweet_id": "570284308210032640",
  "text": "@united why does your app suck so bad?",
  "predicted_sentiment": "negative",
  "timestamp": "2026-05-14T03:23:00Z"
}
```

## Files
- `src/pipeline.py` — main Lambda handler, reads tweets, calls Bedrock, saves results
- `src/prompt.py` — builds the prompt sent to the LLM for each tweet

## Challenges
- I think the hardest part was figuring out why the pipeline kept failing when testing. It threw an error saying that the data must be greater than zero and it was pretty hard to debug. It took a couple of tries to figure out the issue, which was that I had uploaded the columns instead of the actual data.
