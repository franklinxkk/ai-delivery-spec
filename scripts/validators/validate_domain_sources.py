#!/usr/bin/env python3
"""Validate authoritative-source registry freshness and safe claim semantics."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import yaml


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "references" / "domains" / "domain-sources.yaml"
TRUSTED_HOST_SUFFIXES = (
    "iso.org",
    "nist.gov",
    "cac.gov.cn",
    "nhc.gov.cn",
    "moe.gov.cn",
    "mot.gov.cn",
    "npc.gov.cn",
    "samr.gov.cn",
    "miit.gov.cn",
    "saac.gov.cn",
    "hl7.org",
    "dicomstandard.org",
    "w3.org",
    "openlineage.io",
    "json-schema.org",
    "omg.org",
    "openapis.org",
    "asyncapi.com",
    "cloudevents.io",
)
VENDOR_HOST_SUFFIXES = (
    "weaver.com.cn",
    "seeyon.com",
    "landray.com.cn",
    "open.feishu.cn",
    "open.dingtalk.com",
)
OFFICIAL_GITHUB_PREFIXES = (
    "/open-dingtalk",
    "/larksuite",
)
VENDOR_AUTHORITY_TYPES = {
    "vendor_whitepaper",
    "vendor_product_docs",
    "vendor_case_library",
    "vendor_open_source",
}


def main() -> int:
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    failures: list[str] = []
    seen_ids: set[str] = set()
    seen_urls: set[str] = set()
    today = date.today()

    for source in registry.get("sources", []):
        source_id = source.get("id")
        if not source_id or source_id in seen_ids:
            failures.append(f"missing or duplicate source ID: {source_id}")
        seen_ids.add(source_id)
        for field in (
            "domains",
            "title",
            "issuer",
            "authority_type",
            "url",
            "status",
            "jurisdiction",
            "applicability",
            "product_mapping",
            "last_verified_at",
            "refresh_days",
        ):
            if source.get(field) in (None, "", []):
                failures.append(f"{source_id} missing {field}")

        url = source.get("url", "")
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc:
            failures.append(f"{source_id} must use a valid HTTPS URL: {url}")
        host = parsed.netloc.lower().split(":")[0]
        authority_type = source.get("authority_type")
        government_or_standard = any(
            host == suffix or host.endswith("." + suffix) for suffix in TRUSTED_HOST_SUFFIXES
        )
        vendor_host = any(
            host == suffix or host.endswith("." + suffix) for suffix in VENDOR_HOST_SUFFIXES
        )
        official_github = host == "github.com" and any(
            parsed.path.lower().startswith(prefix) for prefix in OFFICIAL_GITHUB_PREFIXES
        )
        if authority_type in VENDOR_AUTHORITY_TYPES:
            if not (vendor_host or official_github):
                failures.append(f"{source_id} uses an unregistered vendor authority: {host}{parsed.path}")
            for field in ("evidence_role", "claim_limit"):
                if not source.get(field):
                    failures.append(f"{source_id} vendor evidence missing {field}")
        elif not government_or_standard:
            failures.append(f"{source_id} uses an unregistered authority host: {host}")
        if url in seen_urls:
            failures.append(f"duplicate source URL: {url}")
        seen_urls.add(url)

        verified = source.get("last_verified_at")
        if isinstance(verified, str):
            verified = date.fromisoformat(verified)
        if isinstance(verified, date):
            age = (today - verified).days
            if age > int(source.get("refresh_days", 0)):
                failures.append(f"{source_id} source verification is stale by {age} days")
        if "draft" in str(source.get("status", "")).lower() and "hard stop" in str(source.get("product_mapping", "")).lower():
            failures.append(f"{source_id} maps a draft source to a hard-stop rule")

    if len(seen_ids) < 20:
        failures.append("source registry is too small for the declared built-in domains")

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print(f"PASS: {len(seen_ids)} authoritative sources have valid URLs, applicability, and fresh verification metadata")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
