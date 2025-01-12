# OCR2Data
### The website is live at ``bills.streamlit.app```


This project provides a pipeline to process receipt images, extract text using OCR, and analyze the extracted data using the Groq API. The pipeline includes the following steps: 

1. Extract text from the receipt image using OCR.
2. Save the extracted text to a CSV file.
3. Process the CSV data using the Groq API to generate structured JSON data.
4. Save the processed data to a final CSV file.

## Requirements

- Python 3.7+
- `pytesseract`
- `Pillow`
- `pandas`

- `python-dotenv`
- `groq`
- `logging`
- `pathlib`

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/vinod-polinati/OCR2Data.git
    cd OCR2Data
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Set up the environment variables:
    - Create a `.env` file in the project root directory.
    - Add your Groq API key to the `.env` file:
        ```
        GROQ_API_KEY=your_groq_api_key
        ```

## Usage

1. Run the pipeline:
    ```sh
    python pipeline.py
    ```

2. Enter the path to the receipt image when prompted.





## Pipeline Architecture 

![pipeline-architecture](https://github.com/user-attachments/assets/d4652bff-5768-443c-a245-720b58b656bd)

## Project Structure

- `pipeline.py`: Contains the `ReceiptProcessor` class and the main function to run the pipeline.
- `README.md`: Project documentation.

## Example

```sh
$ python pipeline.py
Enter image path: /path/to/receipt.jpg
Receipt processed successfully. Output saved to: processed_receipt.csv
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
