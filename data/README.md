# Real Corpus

The repository does not commit downloaded legal PDFs. The manifest records the official source URL, document date, authority and role in the temporal experiment.

## Initial temporal pair

The first real-data experiment uses the **Prevention of Electronic Crimes Act, 2016** as the base version and the **Prevention of Electronic Crimes (Amendment) Act, 2025** as the update.

Download the two PDFs from the URLs in `real_corpus_manifest.json` into a local directory such as:

```text
data/raw/
  peca-2016-original.pdf
  peca-2025-amendment.pdf
```

`data/raw/` should remain local and should not be committed unless the source/licensing policy explicitly permits redistribution.

The 2025 amendment is an especially useful first test because the official Gazette PDF identifies it as Act No. II of 2025 and states that it further amends the Prevention of Electronic Crimes Act, 2016.

## Ingestion order

For the temporal experiment, ingest the 2016 document first and the 2025 amendment second, using their actual publication/assent dates. Then run questions against both the current state and an `as_of` date before the amendment.

## Verification

Before using extracted claims in research results:

1. verify the source PDF checksum,
2. verify the publication date,
3. inspect extracted pages,
4. manually verify evidence spans for the evaluation questions,
5. record any OCR or extraction errors.

The corpus is for research evaluation only and is not legal advice.
