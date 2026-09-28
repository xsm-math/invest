# Local market data

Run `python -m gold_research download` from the repository root. This retrieves GLD daily adjusted closes from Yahoo Finance for 2005-01-01 through 2025-12-31. Requires internet; the public endpoint may change or rate-limit. Failure is explicit and never replaced with synthetic prices.

CSV schema: `Date,AdjClose,Close`. Dates must be increasing and unique; prices positive and finite. Original JSON and source/hash metadata are written alongside the CSV. The research uses AdjClose. Historical adjustments may be revised by the provider. Data is not cross-validated against an exchange feed.

Market data is not committed to Git. The personal download package includes the earlier local snapshot so its reference results can be reproduced offline. Provider data is separate from project code and is not granted an open-source license by this project. Reference aggregate results and charts are committed for review.
