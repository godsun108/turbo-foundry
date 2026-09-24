# Scout v0.4 — Active Listing Feed Ready

Scout now has a standards-based RESO Web API adapter and a dormant live GitHub Actions workflow.

## Activation

The workflow activates when these repository secrets exist:

- `RESO_ENDPOINT` — licensed provider Web API root
- `RESO_TOKEN` — authorized bearer token

No credential is committed to Git.

The default query requests active listings in Port St. Lucie / Port Saint Lucie, Jensen Beach, and Stuart, then passes normalized candidates into the existing Scout watcher.

## Why RESO

RESO defines the industry Web API standard but does not itself provide MLS listing data. Credentials and authorization come from the relevant MLS/data provider under its licensing rules.

Until valid credentials are installed, the live workflow exits safely and makes no claim that current listings were searched.
