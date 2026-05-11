# Dataset Schema

`companies.json` stores the offline question database used by the Dooma CLI.
The top-level value is a JSON object keyed by company name. Each company maps to
an array of question objects.

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
