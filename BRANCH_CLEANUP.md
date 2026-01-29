# Branch Cleanup Guide

This document provides instructions for cleaning up external branches in the BMAD_Forge repository.

## Branches to Delete

The following branches should be deleted to leave only the `main` branch:

| Branch Name | Associated PR | PR Status |
|-------------|---------------|-----------|
| `copilot/identify-aitrg-template-usage` | #18 | Closed |
| `copilot/update-code-analysis` | #6 | Closed |
| `copilot/close-external-branches` | #20 | Open (this PR) |

## How to Delete Branches

### Option 1: Via GitHub UI
1. Navigate to [Branches page](https://github.com/DXCSithlordPadawan/BMAD_Forge/branches)
2. Find each branch listed above
3. Click the trash icon next to each branch to delete it

### Option 2: Via Git Command Line
```bash
# Delete remote branches
git push origin --delete copilot/identify-aitrg-template-usage
git push origin --delete copilot/update-code-analysis

# After merging this PR, delete the current branch
git push origin --delete copilot/close-external-branches
```

### Option 3: Via GitHub CLI
```bash
gh api -X DELETE repos/DXCSithlordPadawan/BMAD_Forge/git/refs/heads/copilot/identify-aitrg-template-usage
gh api -X DELETE repos/DXCSithlordPadawan/BMAD_Forge/git/refs/heads/copilot/update-code-analysis

# After merging this PR, delete the current branch
gh api -X DELETE repos/DXCSithlordPadawan/BMAD_Forge/git/refs/heads/copilot/close-external-branches
```

## Post-Cleanup Verification

After cleanup, run:
```bash
git fetch --prune origin
git branch -r
```

This should show only:
```
origin/main
```

## Notes

- The `copilot/close-external-branches` branch will be automatically deleted if "Automatically delete head branches" is enabled in repository settings
- Consider enabling this setting to auto-cleanup branches after PR merges
