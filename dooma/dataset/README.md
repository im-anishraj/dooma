# Legacy Dataset Snapshot

`companies.json` is a legacy source snapshot. The canonical dataset lives in
YAML files under `dooma/data/`:

- `questions/*.yaml` for canonical question metadata
- `companies/*.yaml` for company metadata
- `patterns/*.yaml` for pattern metadata
- `sheets/*.yaml` for curated roadmaps

Released packages also include `dooma/data/index.json`, a generated compact
runtime index built from those YAML files. Keep editing YAML, then run
`python scripts/build_index.py` before release.

The active dataset currently contains 3,310 unique questions and 17,931
company-question mappings across 662 companies.

The legacy JSON shape is:

```json
{
  "Company Name": [
    {
      "id": "2938",
      "title": "Separate Black and White Balls",
      "url": "https://leetcode.com/problems/separate-black-and-white-balls",
      "difficulty": "Medium",
      "frequency": "100.0%"
    }
  ]
}
```

## Fields

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | LeetCode problem identifier. |
| `title` | string | Display title shown in the terminal table. |
| `url` | string | Direct LeetCode problem URL. |
| `difficulty` | string | Problem difficulty, usually `Easy`, `Medium`, or `Hard`. |
| `frequency` | string | Interview frequency percentage displayed by the CLI. |

## Contribution Notes

- Keep company names as top-level object keys.
- Keep each company's value as an array, even when there is only one question.
- Use strings for every question field to match the current dataset format.
- Ensure the file remains valid JSON before opening a pull request.
