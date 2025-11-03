import os
from PyPDF2 import PdfMerger

def combine_pdfs_in_directory(directory, output_filename="combined.pdf"):
    merger = PdfMerger()
    
    # Get all PDF files in the directory (sorted alphabetically)
    pdf_files = [f for f in os.listdir(directory) if f.lower().endswith(".pdf")]
    pdf_files.sort()

    if not pdf_files:
        print("No PDF files found in the specified directory.")
        return

    for pdf in pdf_files:
        pdf_path = os.path.join(directory, pdf)
        print(f"Adding: {pdf_path}")
        merger.append(pdf_path)

    output_path = os.path.join(directory, output_filename)
    merger.write(output_path)
    merger.close()

    print(f"\nAll PDFs combined successfully into: {output_path}")

if __name__ == "__main__":
    directory = input("Enter the directory path containing PDF files: ").strip('"')
    combine_pdfs_in_directory(directory)
