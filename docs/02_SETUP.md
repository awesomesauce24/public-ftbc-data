# Setup Guide

Complete setup instructions for the FTBC Wiki System.

## System Requirements

- **Python**: 3.11 or higher
- **OS**: Windows 10+, macOS, or Linux
- **Disk Space**: ~500MB for repo + dependencies
- **Internet**: Required for publishing to wiki

## Installation Steps

### 1. Clone the Repository

```powershell
git clone https://github.com/awesomesauce24/public-ftbc-data.git
cd public-ftbc-data
```

### 2. Create Virtual Environment

```powershell
python -m venv .venv
```

### 3. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### 4. Install Dependencies

```powershell
pip install -r requirements.txt
```

This installs:
- `requests` - For wiki API communication
- Other utilities

## Configuration

### Wiki Bot Credentials (Optional)

To enable auto-publishing to the wiki, create `.fandom_creds.json`:

```json
{
  "username": "YourBotUsername",
  "password": "YourBotPassword"
}
```

**⚠️ Security**: Never commit this file! It's in `.gitignore`.

### Test Connection

```powershell
python -c "from wiki.publishers import FandomPublisher; print('OK')"
```

## Verification

Test your installation:

```powershell
python wiki/main.py
```

You should see:
```
FTBC Wiki System
================
1. create - Create/edit object pages
2. exit   - Exit program

Choose an option:
```

If you see this, you're ready to go! ✅

## Troubleshooting

### "ModuleNotFoundError: No module named 'wiki'"

**Solution**: Make sure you're in the repo root directory and the virtual environment is activated.

```powershell
cd C:\path\to\public-ftbc-data
.venv\Scripts\Activate.ps1
python wiki/main.py
```

### "Python version is too old"

**Solution**: Update Python to 3.11+

```powershell
# Check your version
python --version

# If you need to upgrade, download from python.org
```

### Dependencies won't install

**Solution**: Ensure pip is updated

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Next Steps

1. Read the [Quick Start](./01_QUICK_START.md) guide
2. Try creating your first object page
3. Review [Wiki Markup Reference](./06_WIKI_MARKUP.md) for formatting tips

## Keeping Updated

Pull latest changes:

```powershell
git pull origin main
pip install -r requirements.txt  # In case new dependencies added
```
