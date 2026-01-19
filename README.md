# 🚀 PRD Propagator

Automatically update thousands of websites from a single Product Requirements Document using Claude AI.

## How It Works

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Edit prd.md   │────▶│  GitHub Action   │────▶│   Claude AI     │
│   & Push        │     │  Triggers        │     │   Updates Code  │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                              ┌────────────────────────────┘
                              ▼
              ┌───────────────────────────────────────┐
              │  For each site:                       │
              │  1. Clone repo                        │
              │  2. Claude analyzes & updates code    │
              │  3. Commit & push changes             │
              │  4. Lovable auto-deploys! 🎉          │
              └───────────────────────────────────────┘
```

## Quick Start

### 1. Create This as a New GitHub Repository

```bash
# Create new repo on GitHub called "prd-central" (or any name)
# Then push this folder to it:

cd prd-propagator
git init
git add .
git commit -m "Initial PRD propagator setup"
git remote add origin https://github.com/YOUR_USERNAME/prd-central.git
git push -u origin main
```

### 2. Add GitHub Secrets

Go to your repo → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

| Secret Name | Value |
|------------|-------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key from [console.anthropic.com](https://console.anthropic.com) |
| `GH_PAT` | GitHub Personal Access Token with `repo` scope |

#### Creating a GitHub PAT:
1. Go to GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
2. Generate new token with `repo` scope
3. Copy the token and add as `GH_PAT` secret

### 3. Add Your Sites

Edit `sites.json` to add all your Lovable sites:

```json
{
  "sites": [
    {
      "repo": "aaronshapiro33/ammaperozomorles",
      "name": "Amma Peroz Omorles",
      "enabled": true
    },
    {
      "repo": "aaronshapiro33/site2",
      "name": "Another Site",
      "enabled": true
    }
  ]
}
```

Or use the helper script:
```bash
python scripts/add-site.py aaronshapiro33/my-site "My Site Name"
```

### 4. Update Your PRD

Edit `prd.md` with your requirements. This is the single source of truth that all sites will follow.

### 5. Deploy!

**Option A: Automatic** - Just push changes to `prd.md`:
```bash
git add prd.md
git commit -m "Update PRD with new requirements"
git push
```

**Option B: Manual** - Go to Actions tab → "Propagate PRD to All Sites" → Run workflow

## File Structure

```
prd-propagator/
├── prd.md                    # 📝 Your master PRD (edit this!)
├── sites.json                # 🌐 List of all site repositories
├── requirements.txt          # 📦 Python dependencies
├── .github/
│   └── workflows/
│       └── propagate.yml     # ⚙️ GitHub Action workflow
└── scripts/
    ├── update-sites.py       # 🤖 Main orchestrator script
    ├── add-site.py           # ➕ Helper to add sites
    └── list-sites.py         # 📋 Helper to list sites
```

## Workflow Options

### Run on Specific Site Only

In the GitHub Actions UI, you can specify a single site to update:
- Go to Actions → Run workflow
- Enter the repo name in "specific_site" field (e.g., `aaronshapiro33/my-site`)

### Dry Run Mode

Test without making any changes:
- Go to Actions → Run workflow
- Check "Dry run" option

### Disable a Site Temporarily

In `sites.json`, set `"enabled": false`:
```json
{
  "repo": "aaronshapiro33/site-to-skip",
  "name": "Temporarily Disabled Site",
  "enabled": false
}
```

## Local Development

Run locally for testing:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="your-key"
export GH_PAT="your-github-pat"

# Dry run (no changes)
export DRY_RUN=true
python scripts/update-sites.py

# Update single site
export SPECIFIC_SITE="aaronshapiro33/my-site"
python scripts/update-sites.py
```

## Cost Estimation

- ~$0.01-0.03 per site update (depending on codebase size)
- 1000 sites ≈ $10-30 per PRD deployment
- GitHub Actions: Free tier includes 2000 minutes/month

## Tips for Writing Good PRDs

1. **Be specific** - Claude follows instructions literally
2. **Include examples** - Show desired code patterns
3. **Mention what to preserve** - "Keep existing contact information"
4. **Describe structure** - "Each page should have a hero, features, and CTA"

### Example PRD Structure:

```markdown
# PRD v1.2

## Design Requirements
- Color scheme: Navy (#1a365d) and Gold (#d69e2e)
- Typography: Playfair Display for headings, Inter for body
- Style: Modern, professional, clean

## Page Structure
### Home Page
- Hero with headline, subheadline, and CTA button
- 3-column features grid
- Testimonials carousel
- Contact form

## Technical Requirements
- Mobile responsive
- < 3 second load time
- SEO meta tags on all pages
```

## Troubleshooting

### "Permission denied" errors
- Make sure your `GH_PAT` has `repo` scope
- Verify the token hasn't expired

### "Rate limited" by Anthropic
- Reduce `MAX_WORKERS` in update-sites.py
- Add delays between API calls

### Changes not deploying on Lovable
- Verify the push succeeded (check GitHub repo)
- Lovable should auto-deploy from git pushes

## Security Notes

- Never commit your API keys
- Use GitHub Secrets for all sensitive values
- The `GH_PAT` only needs access to your own repos
- Consider using a dedicated bot account for the PAT

---

Made with ❤️ for scaling your Lovable empire
