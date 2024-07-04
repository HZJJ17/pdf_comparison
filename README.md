# PDF_Comparison
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/PyMuPDF?style=flat-square&labelColor=black&color=grey&link=https%3A%2F%2Fpymupdf.readthedocs.io%2Fen%2Flatest%2F)
## Description

This Python tool compares two PDF documents, highlighting differences in text, images, tables, and element positions. It provides detailed output and visualizations to help identify discrepancies between PDFs.

## Features

* **Text Comparison:** Identifies added, removed, or modified text content.
* **Image Comparison:** Uses SSIM (Structural Similarity) to assess image similarity.
* **Table Comparison:** Extracts tables and highlights differences in table structure and data.
* **Element Location Comparison:** Visualizes discrepancies in the positioning of elements like text, images, and barcodes.
* **Detailed Output:** Prints comparison results, including text differences, image similarity scores, and element position discrepancies.
* **Visualization:** Provides visual representations of differences, making it easy to understand and identify problematic areas.


## Requirements
 *Python 3.x
 
 *pymupdf
 
 *camelot-py
 
 *scikit-image
 
 *matplotlib
 
 *imagehash

## Installation for local development
  
  **Clone the repository:**

   ```Bash
     https://github.com/HZJJ17/pdf_comparison.git
   ```
    
## Usage
 1. **Run the Script:**
  ```Bash
   python pdf_comparison.py [main_pdf_file] [comparison_pdf_file]
  ```
  *Replace [main_pdf_file] and [comparison_pdf_file] with the paths to your PDF files.
 
 2. **View Results:**
    
   *The script will output comparison results and generate visualizations (if enabled) in the images directory. 

## Examples:

 1. **Run the Script:**

  ```Bash
  python pdf_comparison.py document1.pdf document2.pdf
  ```

2. **Run the Script with Visualization (Optional):**

```Bash
python pdf_comparison.py document1.pdf document2.pdf -o output_dir -v
```

   * The -v flag enables visualization of the differences, saving images to the output directory.
     

## Contributing
   *Contributions are welcome! Please feel free to open issues or submit pull requests.

## License
   *This project is licensed under the [MIT License](https://opensource.org/license/mit)
