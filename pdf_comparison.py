import fitz  # PyMuPDF
import camelot
import os
import json
import argparse
from collections import defaultdict
import difflib
import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity  # Import for SSIM

class PDFData:
    def __init__(self, file_path):
        self.file_path = file_path
        self.pages = {}
        self.extract_data()

    def extract_data(self):
        try:
            pdf_document = fitz.open(self.file_path)
            for page_number in range(len(pdf_document)):
                page = pdf_document[page_number]

                # Extract text
                page_text = page.get_text("words")  

                # Extract images and save them
                images = []
                image_dir = os.path.join(os.path.dirname(self.file_path), "images")
                os.makedirs(image_dir, exist_ok=True)  # Create the directory if it doesn't exist
                for image_index in range(len(page.get_images())):
                    image = page.get_images()[image_index]
                    xref = image[0]
                    base_image = pdf_document.extract_image(xref)
                    image_data = base_image["image"]
                    image_name = f"image_{page_number + 1}_{image_index}.png"
                    image_path = os.path.join(image_dir, image_name)
                    with open(image_path, "wb") as f:
                        f.write(image_data)
                    images.append(image_name)

                # Extract tables (basic extraction, might need adjustments)
                tables = []
                tables_found = camelot.read_pdf(self.file_path, pages=f"{page_number + 1}")  
                for table in tables_found:
                    tables.append(table.df)

                # Organize data for the page
                self.pages[f"page_{page_number+1}"] = {
                    "text": page_text,
                    "images": images,
                    "metadata": pdf_document.metadata,
                    "tables": tables
                }
            pdf_document.close()
        except fitz.fitz.FileNotFoundError:
            print(f"Error: File not found: {self.file_path}")
        except fitz.fitz.FileFormatError:
            print(f"Error: Invalid PDF format: {self.file_path}")
        except Exception as e:
            print(f"Error during PDF processing: {e}")

def create_benchmark(main_file_path):
    """Creates a benchmark library from a main PDF file.

    Args:
        main_file_path (str): Path to the main PDF file.
    """

    pdf_data = PDFData(main_file_path)

    # Save the benchmark library to a JSON file
    with open("benchmark_library.json", "w") as f:
        json.dump(pdf_data.pages, f)

    print("Benchmark library created successfully!")

def compare_to_benchmark(comparison_file_path):
    """Compares a PDF file to the benchmark library.

    Args:
        comparison_file_path (str): Path to the PDF file to compare.
    """
    try:
        # Load the benchmark library
        with open("benchmark_library.json", "r") as f:
            benchmark_data = json.load(f)

        pdf_data = PDFData(comparison_file_path)

        # Compare text and images
        text_differences = []
        sameness_percentages = []
        total_sameness = 0
        element_location_differences = []
        barcode_sameness_count = 0  # Count of similar barcodes
        barcode_comparison_count = 0  # Count of total barcodes compared

        for page_number in range(1, len(pdf_data.pages) + 1):  # Iterate through pages
            page_key = f"page_{page_number}"
            
            # Text Comparison (including structure)
            text1 = pdf_data.pages[page_key]["text"]
            text2 = benchmark_data[page_key]["text"]
            matcher = difflib.SequenceMatcher(None, text1, text2)
            sameness_percentage = matcher.ratio() * 100
            sameness_percentages.append(sameness_percentage)
            total_sameness += sameness_percentage
            diff = difflib.ndiff(text1, text2)
            for line in diff:
                if line.startswith('+'):
                    text_differences.append((page_number, 'Added', line[2:]))
                elif line.startswith('-'):
                    text_differences.append((page_number, 'Removed', line[2:]))

            # Element Location Comparison
            words1 = fitz.open(comparison_file_path).loadPage(page_number - 1).get_text("words")
            words2 = fitz.open("benchmark_library.json").loadPage(page_number - 1).get_text("words")

            for i, word in enumerate(words1):
                bbox1 = word[0]
                bbox2 = words2[i][0] if i < len(words2) else None 

                if bbox1 != bbox2:
                    element_location_differences.append((page_number, bbox1, bbox2)) 

            # Image Comparison (Using SSIM)
            for image_index, image_name in enumerate(pdf_data.pages[page_key]["images"]):
                image_path1 = os.path.join(os.path.dirname(comparison_file_path), "images", image_name)
                image_path2 = os.path.join(os.path.dirname("benchmark_library.json"), "images", image_name)

                if os.path.exists(image_path1) and os.path.exists(image_path2):
                    try:
                        img1 = plt.imread(image_path1)
                        img2 = plt.imread(image_path2)
                        # Calculate SSIM
                        ssim_score = structural_similarity(img1, img2, multichannel=True)
                        # You can set a threshold for similarity
                        similarity_threshold = 0.95  # Example threshold

                        if ssim_score >= similarity_threshold:
                            print(f"Page {page_number}: Image {image_index + 1} is similar (SSIM: {ssim_score:.4f}).")
                        else:
                            print(f"Page {page_number}: Image {image_index + 1} is different (SSIM: {ssim_score:.4f}).")
                    except Exception as e:
                        print(f"Error comparing image {image_name}: {e}")
            # Barcode Comparison
            doc1 = fitz.open(comparison_file_path)
            doc2 = fitz.open("benchmark_library.json")
            page1 = doc1.loadPage(page_number - 1)
            page2 = doc2.loadPage(page_number - 1)

            barcodes_page1 = page1.get_text("blocks", flags=fitz.TEXT_BBOX).filter(lambda x: 'Barcode' in x[0])
            for barcode_info1 in barcodes_page1:
                decoded_value1 = barcode_info1[4]
                bounding_box1 = barcode_info1[1]

                # Find corresponding barcode in the benchmark PDF
                barcodes_page2 = page2.get_text("blocks", flags=fitz.TEXT_BBOX).filter(lambda x: 'Barcode' in x[0])
                for barcode_info2 in barcodes_page2:
                    decoded_value2 = barcode_info2[4]
                    bounding_box2 = barcode_info2[1]

                    barcode_comparison_count += 1

                    if bounding_box1 == bounding_box2 and decoded_value1 == decoded_value2:
                        barcode_sameness_count += 1

            doc1.close()
            doc2.close()

        # Calculate overall percentage sameness
        overall_sameness = total_sameness / len(pdf_data.pages)
        print(f"Overall Text Sameness: {overall_sameness:.2f}%")

    # Calculate barcode similarity percentage
        if barcode_comparison_count > 0:
            barcode_sameness_percentage = (barcode_sameness_count / barcode_comparison_count) * 100
            print(f"Barcode Similarity: {barcode_sameness_percentage:.2f}%")
        else:
            print("No barcodes found for comparison.")

                # Visualize element location differences (You can adapt this as needed)
        if element_location_differences:
            page_numbers, bbox1s, bbox2s = zip(*element_location_differences)
            for i, (page, bbox1, bbox2) in enumerate(element_location_differences):
                plt.figure(figsize=(8, 4))
                plt.title(f"Page {page}: Element Location Comparison")

    except FileNotFoundError:
        print(f"Error: PDF file not found: {comparison_file_path}")
    except Exception as e:
        print(f"Error during comparison: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create benchmark library and compare PDFs.")
    parser.add_argument("main_file", help="Path to the main PDF file")
    parser.add_argument("comparison_file", help="Path to the PDF file to compare (optional)")
    args = parser.parse_args()

    main_file_path = args.main_file
    comparison_file_path = args.comparison_file

    create_benchmark(main_file_path)

    if comparison_file_path:
        compare_to_benchmark(comparison_file_path)