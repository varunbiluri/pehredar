# Seed dataset card

## Summary

`data/call_screening_seed.jsonl` contains 63 synthetic dialogue examples from
early fine-tuning experiments. It is parked research and is not used by the
Android application or included in the APK.

## Intended use

The data supports reproducibility of the documented experiments. It is not
sufficient for training or evaluating a production call screener and must not
be presented as representative of India's languages, accents, fraud patterns,
or calling contexts.

## Personal data

Examples are intended to be synthetic. Never add real phone numbers, contacts,
call transcripts, recordings, credentials, or other personal data.

## Known limitations

- Very small sample size and narrow scenario coverage
- No demographic or geographic representativeness study
- No native-speaker annotation or inter-annotator agreement
- No production safety or bias evaluation

## License

Original committed examples are Apache-2.0 licensed. External additions require
documented provenance and compatible redistribution rights.
