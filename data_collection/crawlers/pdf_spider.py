
from datetime import datetime, timezone
from urllib.parse import urlsplit

import scrapy

from data_management.raw_store import save_raw
from data_collection.parsers.pdf_parser import extract_pdf


class PdfSpider(scrapy.Spider):
    name = "pdf_lubaczow"

    allowed_domains = ["bip.um.lubaczow.pl"]

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 1.5,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "DOWNLOAD_MAXSIZE": 10 * 1024 * 1024,
        "DOWNLOAD_TIMEOUT": 30,
        "FEED_EXPORT_ENCODING": "utf-8",
        "LOG_LEVEL": "INFO",
    }

    def __init__(self, pdf_url=None, **kwargs):
        super().__init__(**kwargs)

        if not pdf_url:
            raise ValueError(
                "Podaj adres PDF przez parametr pdf_url."
            )

        parsed_url = urlsplit(pdf_url)

        if (
            parsed_url.scheme not in ("http", "https")
            or parsed_url.hostname not in self.allowed_domains
        ):
            raise ValueError(
                "Nieprawidłowy adres PDF lub domena."
            )

        self.start_urls = [pdf_url]

    def parse(self, response):
        if b"%PDF-" not in response.body[:1024]:
            self.logger.warning(
                "Odpowiedź nie wygląda na PDF: %s",
                response.url
            )
            return

        raw_path, checksum = save_raw(
            data=response.body,
            municipality="lubaczow",
            resource_type="pdf"
        )

        try:
            parsed = extract_pdf(response.body)

        except Exception as error:
            self.logger.error(
                "Błąd przetwarzania PDF %s: %s",
                response.url,
                error
            )
            return

        yield {
            "municipality": "Lubaczów (gmina miejska)",
            "teryt": "1809011",
            "resource_type": "pdf",
            "url": response.url,
            "raw_path": raw_path,
            "sha256": checksum,
            "retrieved_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "page_count": parsed["page_count"],
            "pages": parsed["pages"],
            "text": parsed["text"],
            "has_extractable_text": parsed["has_extractable_text"],
        }
