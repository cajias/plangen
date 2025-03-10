"""
Simple intent test for PlanGEN using AWS Bedrock
"""

import json
import os

import boto3
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def main():
    """Run a simple test with AWS Bedrock."""

    # Calendar scheduling problem from the paper
    calendar_problem = """
    Schedule a 30-minute meeting for Alexander, Elizabeth, and Walter on Monday between 9:00 and 17:00.
    Alexander: Busy at 9:30-10:00, 10:30-11:00, 12:30-13:00, 14:30-15:00, 16:00-17:00.
    Elizabeth: Busy at 9:00-9:30, 11:30-12:30, 13:00-14:30.
    Walter: Busy at 9:00-14:30, 15:30-17:00.
    Find an earliest time slot that works for all participants.
    """

    # Initialize Bedrock client
    client = boto3.client("bedrock-runtime", region_name="us-east-1")

    # Prepare the prompt
    prompt = f"""
    You are an expert scheduler. Please solve the following scheduling problem:
    
    {calendar_problem}
    
    First, identify all the constraints in the problem.
    Then, determine the availability of each person.
    Finally, find the earliest time slot that works for all participants.
    
    Provide your answer in the following format:
    
    CONSTRAINTS:
    [List all constraints]
    
    AVAILABILITY:
    [Show availability for each person]
    
    SOLUTION:
    [Provide the earliest time slot that works for all participants]
    """

    # Prepare the request body
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    print("Sending request to AWS Bedrock...")

    try:
        # Make the API call
        response = client.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )

        # Parse the response
        response_body = json.loads(response["body"].read())
        result = response_body["content"][0]["text"]

        print("\n=== Claude 3 Response ===")
        print(result)

        # Save the results to a file
        with open("calendar_scheduling_bedrock_result.txt", "w") as f:
            f.write(result)

        print("\nResults saved to calendar_scheduling_bedrock_result.txt")

    except Exception as e:
        print(f"\nError calling AWS Bedrock: {str(e)}")


if __name__ == "__main__":
    main()
