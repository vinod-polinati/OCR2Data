import streamlit as st
from PIL import Image
import os
import tempfile
from io import BytesIO

# Import your pipeline here if needed
from pipeline import ReceiptProcessor

# Streamlit UI setup
st.title("OCR 2 Data")

# Add the image upload button
uploaded_image = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

# Initialize file storage and processing functions
if uploaded_image is not None:
    # Open the uploaded image with PIL
    img = Image.open(uploaded_image)

    # Convert the image to RGB if it has an alpha channel
    if img.mode == "RGBA":
        img = img.convert("RGB")

    # Save the uploaded image temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        temp_image_path = temp_file.name
        img.save(temp_image_path)

    # Display the uploaded image
    st.image(img, caption="Uploaded Image", use_column_width=True)

    # Add a submit button
    if st.button("Submit"):
        # Here you would call your ReceiptProcessor or pipeline function
        try:
            processor = ReceiptProcessor()  # Assuming the pipeline is integrated
            processed_path = processor.process_receipt(temp_image_path)

            # Provide download link for the CSV
            with open(processed_path, "rb") as file:
                st.download_button(
                    label="Download Processed CSV",
                    data=file,
                    file_name="processed_receipt.csv",
                    mime="text/csv"
                )
            st.success(f"Receipt processed successfully. Processed data saved to {processed_path}")

        except Exception as e:
            st.error(f"Error processing receipt: {str(e)}")
