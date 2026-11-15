# The Midnight Archive — start here

The AI-Escape-Room folder contains both versions, Windows/macOS/Linux setup,
architecture diagrams, 50 automated tests, a three-page report and an offline demo.

1. Read AI-Escape-Room/README.md.
2. Run Version 2 offline first. It needs no key.
3. Configure your own free-tier Gemini key in a local .env and run Version 1.
   No real key has been included. Live API validation is still pending.
4. Review the source and docs/walkthrough.md so you can explain the implementation.
5. Publish to GitHub using the preserved staged history below, then submit the URL.

## Keep the four real development commits when uploading to GitHub

Install Git from https://git-scm.com/ if needed. Create an EMPTY repository called
AI-Escape-Room in your GitHub account; do not add a README, license or .gitignore
on GitHub. Extract this ZIP, then open PowerShell in the extracted parent folder:

```powershell
git clone -b main .\AI-Escape-Room-history.bundle .\AI-Escape-Room-git
cd .\AI-Escape-Room-git
git remote remove origin
git remote add origin https://github.com/anishcodes17/AI-Escape-Room.git
git push -u origin main
git push origin --tags
```

Authenticate to GitHub when Git requests it. The two tags v1.0 and v2.0 mark the
versions. The bundle is a standard Git backup containing the same tracked files
and genuine implementation commits. It contains no credentials. `git clone`
restores the commit history; uploading files through the website would create
new history and lose the staged-development evidence.

If the repository already contains work, do not force-push. Use another empty
repository or integrate the existing history deliberately.

The report and demo truthfully distinguish automated offline results from live
LLM behavior. Add your live recording and observations after testing with your
own key. Ensure your instructor can access the repository before submitting.
