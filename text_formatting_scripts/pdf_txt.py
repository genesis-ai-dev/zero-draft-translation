import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

def pdf_to_txt_chunked(pdf_path, txt_path, start_page=0, end_page=None, chunk_size=50):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    
    # If no end_page specified, process till the last page
    if end_page is None or end_page > len(doc):
        end_page = len(doc)
    
    # Process the document in chunks
    for chunk_start in range(start_page, end_page, chunk_size):
        chunk_end = min(chunk_start + chunk_size, end_page)
        print(f"Processing pages: {chunk_start + 1} to {chunk_end}")
        
        # Prepare the output file for appending text
        with open(txt_path, "a", encoding="utf-8") as out_file:
            for page_num in range(chunk_start, chunk_end):
                # Convert PDF page to image
                page = doc.load_page(page_num)
                pix = page.get_pixmap()
                img = Image.open(io.BytesIO(pix.tobytes()))
                
                # Use OCR to extract text with a PSM that encourages line-by-line reading
                custom_config = r'--psm 6'

                # Use OCR to extract text, specifying English as default language
                # You can add multiple language codes separated by + if necessary
                text = pytesseract.image_to_string(img, config=custom_config) # lang='eng',
                
                # Write the extracted text to the output file
                out_file.write(text)
    
    # Close the PDF after processing
    doc.close()
    print(f"Completed. The text has been saved to {txt_path}")

# Example usage
pdf_path = "../No Code/dokumen.pub_maranao-dialogs-and-drills-9781931546652.pdf"
txt_path = "dictionary/english-maranao-dialogs-drills.txt"
pdf_to_txt_chunked(pdf_path, txt_path)
