# CHSP Allied Health Dashboard

This repository contains a dashboard for CHSP (Commonwealth Home Support Programme) Allied Health mandatory compliances.

## GitHub Pages Deployment

This repository is configured to automatically deploy to GitHub Pages. The deployment happens via GitHub Actions.

### Setup Instructions

To enable GitHub Pages for this repository:

1. Go to your repository's Settings
2. Navigate to "Pages" in the left sidebar
3. Under "Build and deployment":
   - Set **Source** to "GitHub Actions"
4. The site will be automatically deployed when changes are pushed to the `main` or `master` branch

### Workflow

The GitHub Actions workflow (`.github/workflows/deploy.yml`) will:
- Trigger on pushes to `main` or `master` branches
- Can also be manually triggered via workflow_dispatch
- Deploy the entire repository content (including `index.html`) to GitHub Pages

### Accessing the Dashboard

Once deployed, the dashboard will be accessible at:
```
https://<username>.github.io/<repository-name>/
```

For example: `https://BitecodesHub.github.io/CHSP/`

## Local Development

The dashboard is generated from an Excel file (`Report.xlsx`) using Python scripts.

### Generating the Dashboard

To regenerate the dashboard from the Excel data:

```bash
python build_dashboard.py
# or
python generate_dashboard.py
```

This will update the `index.html` file with the latest data from `Report.xlsx`.

## Files

- `index.html` - The main dashboard page
- `Report.xlsx` - Source data file
- `build_dashboard.py` - Script to build the dashboard
- `generate_dashboard.py` - Alternative dashboard generation script
- `tmpl_head.html` - HTML head template
- `tmpl_body.html` - HTML body template
- `tmpl_script.js` - JavaScript template

## License

This project is maintained for CHSP Allied Health mandatory compliance tracking.
