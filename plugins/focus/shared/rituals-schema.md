# Rituals JSON Schema

The `.focus/rituals.json` file is committed to the target repo. Both the `/focus:rituals` skill and the `rituals.yml` GitHub Action read from it.

## Schema

```json
{
  "version": 1,
  "updated": "YYYY-MM-DD",
  "rituals": {
    "morning": {
      "items": [
        {"text": "Activity description", "minutes": 10}
      ],
      "total_minutes": 10
    },
    "workday-startup": {
      "items": [...],
      "total_minutes": 20
    },
    "workday-shutdown": {
      "items": [...],
      "total_minutes": 15
    },
    "evening": {
      "items": [...],
      "total_minutes": 7
    }
  }
}
```

## Fields

| Field                     | Type   | Description                                                         |
| ------------------------- | ------ | ------------------------------------------------------------------- |
| `version`                 | number | Schema version (currently 1)                                        |
| `updated`                 | string | ISO date of last update                                             |
| `rituals`                 | object | 4 keys: `morning`, `workday-startup`, `workday-shutdown`, `evening` |
| `rituals.*.items`         | array  | Checklist items, each with `text` (string) and `minutes` (number)   |
| `rituals.*.total_minutes` | number | Sum of all item minutes                                             |

## Comment format

When posted to a daily thread, each ritual renders as:

```markdown
## Morning Ritual (~15 min)

- [ ] Meditate for 10 minutes (10 min)
- [ ] Journal 3 gratitudes (5 min)
```

The `## <Ritual Name>` heading and checkbox format are required for the daily skill to parse completion percentage.

## Ritual names (display)

| Key                | Display name     |
| ------------------ | ---------------- |
| `morning`          | Morning Ritual   |
| `workday-startup`  | Workday Startup  |
| `workday-shutdown` | Workday Shutdown |
| `evening`          | Evening Ritual   |
