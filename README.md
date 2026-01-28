# Tax Contribution Advisor Pro

A comprehensive tool to help determine whether Roth or Traditional retirement contributions are more beneficial based on your tax situation.

## ✨ Features

- **📊 Tax Analysis** — Get personalized Roth vs Traditional recommendations
- **📈 Projections** — Visualize growth over 5-45 years with interactive charts
- **⚖️ Scenario Comparison** — Compare multiple income/state combinations side-by-side
- **📄 PDF Export** — Download professional reports of your analysis
- **🌐 Deployment Ready** — Single HTML file, ready for GitHub Pages or Netlify

## 📁 Files Included

| File | Description |
|------|-------------|
| `index.html` | **Pro version** — Full-featured web app (deploy this!) |
| `tax_advisor_pro.html` | Same as index.html (for reference) |
| `tax_advisor.html` | Basic web app version |
| `tax_advisor.py` | Python CLI version |
| `tax_advisor_v2.py` | Python version with JSON data loading |
| `tax_data_updater.py` | Script to update tax data annually |
| `tax_data/` | JSON files with 2025 tax rates |
| `DEPLOY.md` | Deployment instructions for GitHub Pages/Netlify |

## 🚀 Quick Start

### Option 1: Web App (Easiest)
Simply open `tax_advisor.html` in any browser. No installation required.

### Option 2: Python CLI
```bash
# Basic version
python tax_advisor.py

# Version with JSON data (recommended)
python tax_advisor_v2.py
```

### Option 3: Import as Module
```python
from tax_advisor_v2 import analyze_contribution, print_analysis

results = analyze_contribution(
    gross_income=50000,
    state='WA',
    filing_status='single',
    age=30
)
print_analysis(results)
```

## 🔄 Updating Tax Data

Run annually (typically in January) to get the latest tax brackets:

```bash
python tax_data_updater.py
```

This will:
1. Generate updated JSON files in `tax_data/`
2. Optionally download Tax Foundation's Excel file for detailed data

### Data Sources

| Data | Source | Update Frequency |
|------|--------|-----------------|
| Federal brackets | IRS Revenue Procedures | Annual (Q4 for next year) |
| State rates | Tax Foundation | Annual (February) |

### Manual Updates

If automatic scraping isn't needed, you can manually update:

1. **Federal rates**: Check IRS.gov for Revenue Procedures (e.g., Rev. Proc. 2024-40 for 2025)
2. **State rates**: Download Excel from [Tax Foundation](https://taxfoundation.org/data/all/state/state-income-tax-rates/)

Edit `tax_data/tax_data.json` or run `tax_data_updater.py` to regenerate.

## 📊 How It Works

The tool analyzes your situation based on:

1. **Federal tax bracket** - Lower brackets favor Roth
2. **State tax rate** - No-tax states favor Roth
3. **Expected retirement rate** - Compare current vs. future rates
4. **Age** - Affects contribution limits (catch-up at 50+)

### Recommendation Logic

| Situation | Recommendation |
|-----------|---------------|
| 10-12% federal bracket | ROTH |
| 22% federal bracket | CONSIDER BOTH |
| 24%+ federal bracket | TRADITIONAL |
| No state income tax | Leans ROTH |
| High state tax (7%+) | Leans TRADITIONAL |

## 🛠️ Extending the App

### Add Full State Brackets
The current version uses simplified top rates. To add full bracket data:

1. Install openpyxl: `pip install openpyxl`
2. Download Tax Foundation Excel
3. Modify `tax_data_updater.py` to parse detailed brackets

### Deploy Web Version
The HTML file can be deployed to:
- GitHub Pages (free)
- Netlify (free)
- Any static hosting

### Add Features
Ideas for expansion:
- Retirement projections with compound growth
- Side-by-side Roth vs. Traditional comparison
- Tax-loss harvesting calculator
- State-specific deductions and credits

## 🌐 Deploy Online (Free)

### GitHub Pages (Recommended)
1. Create a new GitHub repository
2. Upload `index.html` to the repo
3. Go to Settings → Pages → Enable from main branch
4. Your site is live at `https://username.github.io/repo-name`

### Netlify (Easiest)
1. Go to [netlify.com](https://netlify.com)
2. Drag and drop `index.html`
3. Done! Instant URL provided

See **DEPLOY.md** for detailed instructions.

## ⚠️ Disclaimer

This tool is for educational purposes only and should not be considered financial or tax advice. Tax situations vary by individual. Consult a qualified tax professional for personalized advice.

## 📝 License

MIT License - Feel free to use and modify.
