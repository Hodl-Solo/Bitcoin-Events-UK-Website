# Updating the Meetup Directory

## How it works

1. Edit `meetups-directory.md` — change status to `active`, `paused`, or `deleted`
2. Run the generator: `python3 generate-meetups.py`
3. Push changes to GitHub

## Status Options

- **active** — shows on website with green "Active" tag
- **paused** — shows on website with yellow "Paused" tag  
- **deleted** — removed from website

## To add a new meetup

Add a new entry in the appropriate region section:
```yaml
- name: New Meetup Name
  schedule: "Day · Time · Location"
  status: active
  region: RegionName
```


## Publish flow

1. In Obsidian, edit `Bitcoin Events UK/UK-Bitcoin-Meetups-Directory.md` and push the `bill-mission-control` repo.
2. On the server, run `cp ../bill-mission-control/Bitcoin\ Events\ UK/UK-Bitcoin-Meetups-Directory.md .`.
3. Run `python3 generate-meetups.py`.
4. Commit `UK-Bitcoin-Meetups-Directory.md` + `index.html` and push `Bitcoin-Events-UK-Website`.

The generator only includes rows with `Status = Active`. Links are taken from the `Links` column as Markdown links.
