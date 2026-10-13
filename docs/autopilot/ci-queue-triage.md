# GitHub Actions queue triage — engineering hold

Observed on 2026-10-13: the pull request's **Foundry CI / standards** and **Autopilot unit tests / unit** jobs remain `queued`, with no conclusion, including run IDs 38455663413 and 38455663383. These are *not test failures* and *not green test results*.

## Operator checks (GitHub repository admin)
1. Open [Actions](https://github.com/godsun108/turbo-foundry/actions) and inspect both queued jobs. Look for the runner-assignment/queue message and any repository-level banner.
2. Check **Settings → Actions → General** for enabled Actions, allowed actions, and workflow permissions. Confirm `ubuntu-latest` GitHub-hosted jobs are allowed.
3. Check account/org Actions usage, billing and spending limits, and any concurrency restrictions that could prevent scheduling. Do not add a paid runner or incur costs without explicit approval.
4. Review [GitHub Status](https://www.githubstatus.com/) for *current* Actions incidents. GitHub's Oct 12 incident was marked resolved and should not be asserted as the cause of persistent queueing.
5. Once scheduling is restored, execute both workflows against the **same latest PR commit** and inspect the **test logs**. Do not call the branch verified based on older successful checks.
6. If the exact jobs remain indefinitely queued despite valid settings, open a GitHub Support case with the run IDs, repository name, timestamps, and job page messages.

## Release gate
No merge, deployment, messaging, or billing activation until exact-commit tests succeed and read-only staging/security review is approved. Do not repeatedly push no-op commits merely to create another queue item. 
