# Claude Instructions for this repo

## NEVER touch files outside this repo

All source files live here. Do NOT copy, edit, or write files to locations
outside `/Users/johnfx/projects/scratch/` — including `~/agent-sandbox/`,
`~/bin/`, or any other home directory path.

The user runs `init-shell` (or equivalent) to install changes from this repo
into their environment. That is their job, not yours. When you make changes,
edit the repo files only and let the user handle deployment.

## Exception: session files

It is acceptable to read and write session files under `~/agent-workspaces/.agent-sandbox/`
when the user explicitly asks (e.g. to create a session file for an older workspace
so it can be resumed). These are runtime data files, not managed by init-shell.
