
import json
from collections import Counter
from pathlib import Path

# Load crawler output
file_path = Path("data/processed/lubaczow_pages.jsonl")

pages = []

with file_path.open(encoding="utf-8") as file:
    for line_number, line in enumerate(file, start=1):
        try:
            pages.append(json.loads(line))
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Nieprawidłowy JSON w linii {line_number}"
            ) from error

# Analyze collected resources
visited_urls = {page["url"] for page in pages}

depth_counts = Counter(
    page["depth"] for page in pages
)

all_links = [
    link
    for page in pages
    for link in page.get("links", [])
]

pdf_urls = {
    link["url"]
    for link in all_links
    if link["url"].lower().endswith(".pdf")
}

# Check target page
target_url = (
    "https://bip.um.lubaczow.pl/"
    "186,podatki-i-oplaty-lokalne"
)

print("=== CRAWLER REPORT ===")

print(f"Pobrane strony: {len(pages)}")
print(f"Unikalne adresy stron: {len(visited_urls)}")
print(f"Znalezione hiperłącza: {len(all_links)}")
print(f"Unikalne odnośniki PDF: {len(pdf_urls)}")

print("\nStrony według głębokości:")
for depth, count in sorted(depth_counts.items()):
    print(f"  Głębokość {depth}: {count}")

print("\nStrona podatkowa:")
print(f"  Odkryta: {any(link['url'] == target_url for link in all_links)}")
print(f"  Pobrana: {target_url in visited_urls}")
