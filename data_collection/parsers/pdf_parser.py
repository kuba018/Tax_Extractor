
import pymupdf


def extract_pdf(pdf_bytes: bytes) -> dict:
    pages = []

    with pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf"
    ) as document:

        for page_number, page in enumerate(document, start=1):
            page_text = page.get_text(
                "text",
                sort=True
            ).strip()

            pages.append({
                "page_number": page_number,
                "text": page_text,
            })

    full_text = "\n\n".join(
        page["text"]
        for page in pages
        if page["text"]
    )

    return {
        "page_count": len(pages),
        "pages": pages,
        "text": full_text,
        "has_extractable_text": bool(full_text),
    }
