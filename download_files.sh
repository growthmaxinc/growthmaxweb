#!/bin/bash

# Get the file contents and save them
curl -s "file:///Users/chris.angelltrajectdata.com/Library/Application%20Support/Claude/local-agent-mode-sessions/6047d703-ea1c-4007-a5f8-48cc39006cb5/ff0919f9-b556-4827-b647-6dee1444afad/local_551260bd-2d14-4086-9405-b7510eaff3ed/outputs/index-updated.html" > index.html
curl -s "file:///Users/chris.angelltrajectdata.com/Library/Application%20Support/Claude/local-agent-mode-sessions/6047d703-ea1c-4007-a5f8-48cc39006cb5/ff0919f9-b556-4827-b647-6dee1444afad/local_551260bd-2d14-4086-9405-b7510eaff3ed/outputs/blog-why-ai-implementations-fail.html" > blog-why-ai-implementations-fail.html
curl -s "file:///Users/chris.angelltrajectdata.com/Library/Application%20Support/Claude/local-agent-mode-sessions/6047d703-ea1c-4007-a5f8-48cc39006cb5/ff0919f9-b556-4827-b647-6dee1444afad/local_551260bd-2d14-4086-9405-b7510eaff3ed/outputs/blog-where-do-i-fit-crisis.html" > blog-where-do-i-fit-crisis.html
curl -s "file:///Users/chris.angelltrajectdata.com/Library/Application%20Support/Claude/local-agent-mode-sessions/6047d703-ea1c-4007-a5f8-48cc39006cb5/ff0919f9-b556-4827-b647-6dee1444afad/local_551260bd-2d14-4086-9405-b7510eaff3ed/outputs/blog-partnership-not-replacement.html" > blog-partnership-not-replacement.html
curl -s "file:///Users/chris.angelltrajectdata.com/Library/Application%20Support/Claude/local-agent-mode-sessions/6047d703-ea1c-4007-a5f8-48cc39006cb5/ff0919f9-b556-4827-b647-6dee1444afad/local_551260bd-2d14-4086-9405-b7510eaff3ed/outputs/blog-your-first-ai-agent.html" > blog-your-first-ai-agent.html

echo "Files downloaded!"
ls -la index.html blog-*.html
