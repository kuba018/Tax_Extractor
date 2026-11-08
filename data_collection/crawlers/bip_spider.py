
from datetime import datetime, timezone
from urllib.parse import urldefrag, urlsplit

import scrapy
from scrapy.http import HtmlResponse

from data_management.raw_store import save_raw


class BipSpider(scrapy.Spider):
    name = "bip_lubaczow"

    allowed_domains = ["bip.um.lubaczow.pl"]
    start_urls = ["https://bip.um.lubaczow.pl/"]

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 1.5,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "AUTOTHROTTLE_ENABLED": True,
        "DEPTH_LIMIT": 2,
        "CLOSESPIDER_PAGECOUNT": 120,
        "FEED_EXPORT_ENCODING": "utf-8",
        "LOG_LEVEL": "INFO",
        "DEPTH_PRIORITY": 1,
        "SCHEDULER_DISK_QUEUE": "scrapy.squeues.PickleFifoDiskQueue",
        "SCHEDULER_MEMORY_QUEUE": "scrapy.squeues.FifoMemoryQueue",
    }

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            self.logger.info(
                "Pomijam zasób inny niż HTML: %s",
                response.url
            )
            return
        raw_path, checksum = save_raw(
            data=response.body,
            municipality="lubaczow",
            resource_type="html"
        )
        

        links = []
        follow_urls = []
        seen_urls = set()

        excluded_extensions = (
            ".pdf", ".doc", ".docx", ".xls", ".xlsx",
            ".zip", ".jpg", ".jpeg", ".png", ".gif"
        )

        for anchor in response.css("a[href]"):
            href = anchor.attrib.get("href", "").strip()

            if not href:
                continue

            absolute_url = urldefrag(response.urljoin(href)).url
            parsed_url = urlsplit(absolute_url)

            if parsed_url.scheme not in ("http", "https"):
                continue

            if absolute_url in seen_urls:
                continue

            seen_urls.add(absolute_url)

            link_text = anchor.xpath(
                "normalize-space(.)"
            ).get(default="")

            is_internal = (
                parsed_url.hostname in self.allowed_domains
            )

            links.append({
                "url": absolute_url,
                "text": link_text,
                "is_internal": is_internal,
            })

            if (
                is_internal
                and not parsed_url.path.lower().endswith(
                    excluded_extensions
                )
            ):
                follow_urls.append(absolute_url)

        text_parts = response.xpath(
            "//body//text()[not(ancestor::script "
            "or ancestor::style or ancestor::noscript)]"
        ).getall()

        page_text = "\n".join(
            part.strip()
            for part in text_parts
            if part.strip()
        )

        yield {
            "municipality": "Lubaczów (gmina miejska)",
            "teryt": "1809011",
            "resource_type": "html",
            "url": response.url,
            "raw_path": raw_path,
            "sha256": checksum,
            "title": response.css(
                "title::text"
            ).get(default="").strip(),
            "depth": response.meta.get("depth", 0),
            "retrieved_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "text": page_text,
            "links": links,
        }

        for url in follow_urls:
            yield response.follow(
                url,
                callback=self.parse
            )
