# Contribution Guidelines

Thanks for helping travelers get around China.

## Adding a link

- Open a pull request that edits `README.md`.
- Add one link per pull request, or a small group of closely related links.
- Use this format: `- [Title](https://example.com/) - Short description ending with a period.`
- Put the link in the most relevant section. Create a new section only if no existing one fits.
- Check that the link works and the content is current (written or updated within the last two years).

## What we accept

- Free, practical guides in English for travel in mainland China, Hong Kong or Macau.
- Official government, transport or service pages.
- Apps and tools that work for foreign visitors.

## What we don't accept

- Affiliate-only landing pages with no useful content.
- Paywalled or login-only content.
- Outdated visa or entry information.

## Reporting a broken link

Open an issue with the section name and the broken URL. The link-check workflow also runs weekly and on every pull request.

The automated check also runs on pushes to `main`. It checks HTTP responses, local files and table-of-contents anchors, and saves a JSON report with redirects and page titles. A 403 or 429 response requires review; it is not counted as a working link. A successful response confirms availability, not the accuracy of travel advice.
