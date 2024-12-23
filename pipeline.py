import pytesseract
from PIL import Image
import csv
import pandas as pd
import os
import json
from groq import Groq
from dotenv import load_dotenv
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

class ReceiptProcessor:
    def __init__(self, groq_api_key: Optional[str] = None):
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load environment variables if API key not provided
        if not groq_api_key:
            load_dotenv()
            groq_api_key = os.getenv("GROQ_API_KEY")
            
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found")
            
        # Initialize Groq client
        self.client = Groq(api_key=groq_api_key)
        
    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image using OCR"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        try:
            img = Image.open(image_path)
            extracted_text = pytesseract.image_to_string(img)
            if not extracted_text.strip():
                raise ValueError("No text extracted from image")
            self.logger.info("Successfully extracted text from image")
            return extracted_text
        except Exception as e:
            self.logger.error(f"Error extracting text from image: {str(e)}")
            raise

    def save_text_to_csv(self, text: str, output_path: str) -> str:
        """Save extracted text to CSV"""
        try:
            lines = text.split('\n')
            with open(output_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Extracted Text"])
                for line in lines:
                    if line.strip():
                        writer.writerow([line])
            self.logger.info(f"Saved extracted text to {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Error saving text to CSV: {str(e)}")
            raise

    def clean_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Clean and validate the API response"""
        try:
            # Remove code blocks if present
            response_text = response_text.strip()
            if response_text.startswith("```") and response_text.endswith("```"):
                response_text = response_text[3:-3].strip()
            if response_text.startswith("json"):
                response_text = response_text[4:].strip()

            # Parse JSON
            items = json.loads(response_text)
            if not isinstance(items, list):
                raise ValueError("Response is not a list")

            # Validate structure
            required_fields = {"quantity", "description", "unit_price", "total_price"}
            for item in items:
                if not isinstance(item, dict):
                    raise ValueError("Item is not a dictionary")
                if set(item.keys()) != required_fields:
                    raise ValueError(f"Missing required fields. Got: {set(item.keys())}")

            return items
        except Exception as e:
            self.logger.error(f"Error cleaning response: {str(e)}")
            self.logger.debug(f"Raw response: {response_text}")
            raise

    def process_with_groq(self, csv_path: str, output_path: str) -> str:
        """Process CSV data using Groq API"""
        try:
            df = pd.read_csv(csv_path, header=None)
            data_text = df.to_string()

            prompt = """Analyze this receipt data and return ONLY a JSON array.
            
            Input text:
            {data_text}

            Required JSON structure:
            [
                {{
                    "quantity": 1,
                    "description": "example item",
                    "unit_price": 100.00,
                    "total_price": 100.00
                }}
            ]

            Rules:
            - Each item must have exactly these fields
            - Numbers must be valid floats
            - Descriptions must be strings
            - No additional commentary
            """

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a JSON parser that returns only valid JSON arrays containing receipt data."
                    },
                    {
                        "role": "user",
                        "content": prompt.format(data_text=data_text)
                    }
                ],
                model="mixtral-8x7b-32768",
                temperature=0.1,
            )

            response_text = chat_completion.choices[0].message.content
            self.logger.debug(f"Raw API response: {response_text}")
            
            items = self.clean_response(response_text)
            processed_df = pd.DataFrame(items)
            
            processed_df.to_csv(output_path, index=False)
            self.logger.info(f"Saved processed data to {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Error processing with Groq: {str(e)}")
            raise

    def process_receipt(self, image_path: str, intermediate_csv: Optional[str] = None, 
                       final_csv: Optional[str] = None) -> str:
        """Complete pipeline to process receipt image"""
        try:
            # Set default paths if not provided
            if intermediate_csv is None:
                intermediate_csv = "extracted_text.csv"
            if final_csv is None:
                final_csv = "processed_receipt.csv"

            # Run pipeline
            extracted_text = self.extract_text_from_image(image_path)
            csv_path = self.save_text_to_csv(extracted_text, intermediate_csv)
            processed_path = self.process_with_groq(csv_path, final_csv)
            
            self.logger.info("Receipt processing completed successfully")
            return processed_path
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            raise

def main():
    # Get image path from user
    image_path = input("Enter image path: ")
    
    try:
        processor = ReceiptProcessor()
        output_path = processor.process_receipt(image_path)
        print(f"Receipt processed successfully. Output saved to: {output_path}")
    except Exception as e:
        print(f"Error processing receipt: {str(e)}")

if __name__ == "__main__":
    main()