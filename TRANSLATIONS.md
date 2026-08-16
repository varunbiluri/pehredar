# Translation quality process

Pehredar ships complete Android UI resources for English and all 22 languages in the Eighth Schedule of the Constitution of India.

## Quality gates already enforced

- Every locale must contain every user-visible translatable string.
- Blank strings and accidental English fallbacks fail CI.
- Text must use normalized Unicode.
- Kashmiri, Sindhi, and Urdu must contain Arabic-script text for RTL rendering.
- Santali rejects characters from unrelated Indic scripts.
- Android lint compiles every locale and catches malformed resource syntax.
- Android 13 and later receive an explicit per-app language list.

## Translation workflow

Core controls were translated directly. Extended interface copy is generated from short, controlled English source sentences using the local AI4Bharat IndicTrans2 model. The generator preserves existing core translations and can be reproduced with:

```bash
uv run python scripts/translate_low_resource_strings.py
python3 scripts/check_localizations.py
```

## Native review requirement

Machine translation is a starting point, not final linguistic certification. A locale may be called production-verified only after two native speakers review it in context on a physical Android device. Reviewers should check naturalness, terminology, clipping, script choice, RTL layout where applicable, and whether the UI describes the behavior accurately.

Contributors can propose corrections to the relevant `android/app/src/main/res/values-*/strings.xml` file. Re-running the generator is an intentional maintenance operation: its diff must be reviewed so an approved native-speaker correction is never replaced accidentally.
