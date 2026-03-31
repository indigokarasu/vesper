# Changelog

## [2.4.0] - 2026-03-30

### Changed
- `vesper:morning` schedule shifted from 7am to 6am PT (`0 6 * * *`)
- `vesper:evening` schedule shifted from 6pm to 8pm PT (`0 20 * * *`)
- Updated `skill.json` `scheduled_tasks` to reflect new times
- Added config override note: schedules are configurable via `vesper.config.set morning_hour <H>` and `vesper.config.set evening_hour <H>`

## [2.3.1] - prior release
