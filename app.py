from flask import Flask, request, render_template
import tempfile
from pdf2image import convert_from_bytes
from PIL import Image, ImageEnhance
import pytesseract

app = Flask(__name__)

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Set the path to the custom traineddata file
custom_traineddata_path = r'C:\Program Files\Tesseract-OCR\tessdata\eng_bank_statement_1.traineddata'

@app.route('/')
def home():
    return render_template("home.html")

@app.route("/predict", methods=["POST"])
def predict():
    if request.method == 'POST' and 'pdf' in request.files:
        # Open the uploaded PDF file
        pdf_file = request.files['pdf']

        # Read the PDF file as bytes
        pdf_bytes = pdf_file.read()

        # Create a temporary directory to store the converted images
        with tempfile.TemporaryDirectory() as temp_dir:
            # Convert the PDF bytes into images
            images = convert_from_bytes(pdf_bytes, output_folder=temp_dir)

            # Initialize an empty list to store the OCR results
            extracted_text = []

            # Process each image
            for image in images:
                # Preprocess the image (convert to grayscale)
                image = image.convert('L')

                # Enhance image contrast (optional)
                enhancer = ImageEnhance.Contrast(image)
                enhanced_image = enhancer.enhance(2.0)  # Adjust the enhancement factor as needed

                # Perform OCR using the custom traineddata
                text = pytesseract.image_to_string(enhanced_image, lang='eng_bank_statement_1')
                extracted_text.append(text)

            # Join the extracted text from all images
            result_text = '\n'.join(extracted_text)

            # Pass the extracted text to the home.html template
            return render_template("home.html", extracted_text=result_text)

    # Return an error response for unsupported methods or missing PDF file
    return "Invalid request"

if __name__ == "__main__":
    app.run(debug=True)