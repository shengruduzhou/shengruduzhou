# Profile Metrics configuration

The profile uses local renders from pinned lowlighter/metrics v3.34 and the official GitHub Profile Trophy generator. Successful modules are written to `assets/metrics` and inserted into the README. Unavailable modules are not shown until a valid render exists.

| Module | Configuration |
| --- | --- |
| Isometric Calendar | Automatic; full year, public GitHub data |
| Language Analytics | Automatic; in-depth authored commit patches, programming languages, time-limited analysis. Recent events disabled due to upstream v3.34 parser failure. |
| WakaTime | Existing repository secret `WAKATIME_API_KEY` (same as waka-readme); last 7 days; no project names |
| Screenshot | Automatic; public personal website hero, clickable |
| AniList | Set repository Actions variable `ANILIST_USER` to your public AniList login |
| Stock | Set repository Actions variable `STOCK_SYMBOL` (Yahoo Finance ticker), and secret `STOCK_TOKEN` (RapidAPI Yahoo Finance API key). No holdings or portfolio performance are implied. |

Configure [Actions variables](https://github.com/shengruduzhou/shengruduzhou/settings/variables/actions) and [Actions secrets](https://github.com/shengruduzhou/shengruduzhou/settings/secrets/actions), then manually run [Profile detail metrics](https://github.com/shengruduzhou/shengruduzhou/actions/workflows/metrics-details.yml). Do not commit credentials. The Stock API must support the upstream plugin's profile and chart endpoints; a paid subscription is not automatically created.

Upstream documentation: [isocalendar](https://github.com/lowlighter/metrics/tree/v3.34/source/plugins/isocalendar), [anilist](https://github.com/lowlighter/metrics/tree/v3.34/source/plugins/anilist), [wakatime](https://github.com/lowlighter/metrics/tree/v3.34/source/plugins/wakatime), [stock](https://github.com/lowlighter/metrics/tree/v3.34/source/plugins/community/stock), [screenshot](https://github.com/lowlighter/metrics/tree/v3.34/source/plugins/community/screenshot).
