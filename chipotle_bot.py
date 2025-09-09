"""Simple helper to submit the Chipotle giveaway keyword.

This module fetches the latest tweet from the official Chipotle account,
extracts the keyword mentioned in the format ``Text KEYWORD to``, and sends
that keyword to the giveaway phone number via the email-to-SMS gateway.

The implementation purposely avoids heavy dependencies such as Selenium.
It relies on the public Nitter service which exposes Twitter content as
regular HTML.  The behaviour is deliberately lightweight to make it easier
to run in restricted environments.
"""

from __future__ import annotations

import os
import re
import requests

from sms import send_sms_via_email

# Public mirror of Twitter; easier to scrape without JavaScript.
TWEETS_URL = "https://nitter.net/ChipotleTweets"

# Phone number used by the Chipotle burrito giveaway campaign.
CHIPOTLE_NUMBER = "888222"


def fetch_latest_keyword(session: requests.Session | None = None) -> str | None:
    """Return the current keyword from the official Chipotle tweet.

    The function searches the HTML for the first occurrence of the phrase
    ``Text WORD to`` and returns ``WORD`` if found.  ``None`` is returned
    when no match is present.
    """

    session = session or requests.Session()
    response = session.get(TWEETS_URL, timeout=10)
    response.raise_for_status()

    match = re.search(r"Text\s+(\w+)\s+to", response.text, re.IGNORECASE)
    return match.group(1) if match else None


def submit_keyword(keyword: str) -> None:
    """Send ``keyword`` to the campaign's phone number via SMS."""

    number = os.environ.get("TARGET_NUMBER")
    provider = os.environ.get("PROVIDER")
    sender_email = os.environ.get("EMAIL_USER")
    sender_password = os.environ.get("EMAIL_PASSWORD")

    if not all([number, provider, sender_email, sender_password]):
        raise RuntimeError(
            "Environment variables TARGET_NUMBER, PROVIDER, EMAIL_USER and "
            "EMAIL_PASSWORD must be set",
        )

    credentials = (sender_email, sender_password)
    send_sms_via_email(number, f"{keyword} to {CHIPOTLE_NUMBER}", provider, credentials)


def main() -> None:
    """Entry point for running from the command line."""

    keyword = fetch_latest_keyword()
    if not keyword:
        raise SystemExit("Could not determine keyword from Chipotle tweet")

    submit_keyword(keyword)
    print(f"Submitted keyword '{keyword}' to {CHIPOTLE_NUMBER}")


if __name__ == "__main__":  # pragma: no cover - manual execution
    main()
