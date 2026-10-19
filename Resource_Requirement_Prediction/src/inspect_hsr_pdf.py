from pathlib import Path
from pypdf import PdfReader

PDF_FILE = Path(
    r"D:\Y4S1\RP\PP1\RESOURCES\1. Revised HSR-2026-Analysis-Colombo.pdf"
)

OUTPUT_FILE = (
    Path(__file__).resolve().parent.parent
    / "outputs"
    / "hsr_analysis_extracted.txt"
)

def main():
    if not PDF_FILE.is_file():
        raise FileNotFoundError(f"PDF not found: {PDF_FILE}")

    reader = PdfReader(str(PDF_FILE))
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    keywords = (
        "labour", "labor", "material", "equipment",
        "maintenance", "pothole", "crack sealing",
        "rate", "asphalt", "drain", "worker",
    )

    matching_pages = []

    with OUTPUT_FILE.open("w", encoding="utf-8") as output:
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            output.write(f"\n\n--- PAGE {page_number} ---\n")
            output.write(text)

            if any(word in text.lower() for word in keywords):
                matching_pages.append((page_number, text))

    print(f"PDF pages: {len(reader.pages)}")
    print(f"Pages with relevant keywords: {len(matching_pages)}")
    print(f"Extracted text saved to: {OUTPUT_FILE}")

    for page_number, text in matching_pages[:8]:
        print(f"\n--- PAGE {page_number} ---")
        print(" ".join(text.split())[:900])

if __name__ == "__main__":
    main()
