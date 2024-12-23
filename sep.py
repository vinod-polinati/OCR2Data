import pandas as pd
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Read the CSV file
df = pd.read_csv("trychey.csv", header=None)
data_text = df.to_string()

# Prompt for the LLM
prompt = """Analyze this receipt data and extract structured information:
{data_text}

For each line item, please:
1. Extract the quantity (number before 'x')
2. Clean and standardize the item description
3. Extract the unit price (amount after 'Rs')
4. Verify the total price matches quantity * unit price
5. Format as a structured list with these fields:
   - quantity
   - description 
   - unit_price
   - total_price

Return the data as a list of Python dictionaries."""

# Get LLM response
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a data extraction specialist focused on receipt analysis.",
        },
        {
            "role": "user", 
            "content": prompt.format(data_text=data_text),
        }
    ],
    model="mixtral-8x7b-32768",
    temperature=0.1,
)

# Parse LLM response and convert to DataFrame
response_text = chat_completion.choices[0].message.content
items = eval(response_text)  # Convert string representation of list to actual list
processed_df = pd.DataFrame(items)

# Save to new CSV
processed_df.to_csv("receipt.csv", index=False)
print("Processed data saved to processed_receipt.csv")