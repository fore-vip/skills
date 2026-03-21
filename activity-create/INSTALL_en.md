# ForeSmart Chrome Extension Installation Guide

[![Version](https://img.shields.io/badge/version-v1.1-orange)](https://f.fore.vip/download/fore-ex-v1.1.zip)
[![Download](https://img.shields.io/badge/download-static_site-blue)](https://f.fore.vip/download/fore-ex-v1.1.zip)
[![Website](https://img.shields.io/badge/website-fore.vip-green)](https://fore.vip)
[![GitHub](https://img.shields.io/badge/GitHub-fore--vip/fore--ex-black?logo=github)](https://github.com/fore-vip/fore-ex)

**ForeSmart** Chrome browser extension - Create and publish activities with one click.

---

## 📦 Download

### China Users (Recommended)

Download the latest version from the static website:

- **Download Link**: https://f.fore.vip/download/fore-ex-v1.1.zip
- **File Size**: ~89KB
- **Last Updated**: 2026-03-21

[👉 Download v1.1](https://f.fore.vip/download/fore-ex-v1.1.zip)

### International Users

Get source code from GitHub repository:

- **Repository**: https://github.com/fore-vip/fore-ex

---

## 🚀 Installation Tutorial

### Method 1: Developer Mode Installation (Recommended)

> ⏱️ Estimated time: 2 minutes

#### Step 1: Download and Extract

1. Download the extension package: [fore-ex-v1.1.zip](https://f.fore.vip/download/fore-ex-v1.1.zip)
2. Extract to any directory, for example:
   - macOS: `/Users/your_username/fore-ex`
   - Windows: `C:\Users\your_username\fore-ex`

#### Step 2: Open Extension Management Page

**Method A: Address Bar Access**
```
chrome://extensions/
```

**Method B: Menu Access**
1. Click the "⋮" menu in the top right corner of Chrome
2. Select "More tools"
3. Select "Extensions"

#### Step 3: Enable Developer Mode

In the top right corner of the extensions page, find the "Developer mode" toggle and turn it on (becomes blue).

#### Step 4: Load Extension

1. Click the "Load unpacked" button in the top left corner
2. In the file selector, find and select your extracted `fore-ex` folder
3. Click "Select" or "Open"

#### Step 5: Verify Installation

- ✅ Extension appears in the extensions list
- ✅ Extension icon appears in the browser's top right toolbar
- ✅ Extension status shows as "Enabled"

#### Step 6: Pin to Toolbar (Optional)

If the icon is not visible:
1. Click the "🧩" extensions icon in Chrome's top right corner
2. Find "ForeSmart" (前凌智选)
3. Click the "📌" pin icon to pin it to the toolbar

---

### Method 2: Git Clone Installation (Developers)

For developers who need to modify the source code:

```bash
# 1. Clone the repository
git clone git@github.com:fore-vip/fore-ex.git
cd fore-ex

# 2. Open Chrome extension management page
# chrome://extensions/

# 3. Enable Developer mode

# 4. Click "Load unpacked"
# 5. Select the fore-ex project root directory
```

---

### Method 3: Drag and Drop Installation (.crx file)

> ⚠️ Note: New Chrome versions may restrict this method

If you have a `.crx` file:

1. Visit `chrome://extensions/`
2. Enable "Developer mode"
3. Drag the `.crx` file to any position on the page
4. Click "Add extension" in the confirmation dialog

---

## 📋 Usage Guide

### Activity Creation Flow

```
1. Click the ForeSmart extension icon in the browser's top right corner
        ↓
2. Fill in activity information:
   - Activity title (required, at least 2 characters)
   - Start time (required)
   - End time (optional)
   - Activity address (required)
   - Contact/WeChat (required)
   - Ticket price (optional, 0 means free)
        ↓
3. Click "Create Activity" button
        ↓
4. Wait for submission (loading animation displayed)
        ↓
5. Success → Automatically redirect to activity detail page
```

### Form Fields

| Field | Required | Description |
|-------|----------|-------------|
| Activity Title | ✅ | At least 2 characters, keep it concise |
| Start Time | ✅ | Activity start date and time |
| End Time | ⚪ | Optional, defaults to 2 hours after start |
| Activity Address | ✅ | Detailed activity location |
| Contact | ✅ | WeChat or other contact method |
| Ticket Price | ⚪ | 0 means free, unit is CNY |

### Quick Fill Tips

- **Start Time**: Defaults to 1 hour from now, can be modified
- **End Time**: Defaults to 2 hours after start time
- **Ticket Price**: Enter 0 or leave blank for free activities

---

## ❓ FAQ

### Q: Extension won't load?

**A**: Please ensure:
1. ✅ ZIP file is extracted, **do not load directly from the compressed package**
2. ✅ Selected folder contains `manifest.json`
3. ✅ "Developer mode" toggle is enabled
4. ✅ Folder path does not contain Chinese or special characters

### Q: Activity creation failed?

**A**: Check the following:
1. ✅ Network connection is normal
2. ✅ All required fields are filled
3. ✅ Activity title has at least 2 characters
4. ✅ Start time is later than current time
5. ✅ End time is later than start time

### Q: How to update the extension?

**A**: 
1. Download the latest version ZIP package
2. Extract and overwrite the original directory
3. Find the extension in `chrome://extensions/`
4. Click the "🔄" refresh button on the extension card

### Q: How to uninstall the extension?

**A**: 
1. Visit `chrome://extensions/`
2. Find "ForeSmart" (前凌智选) extension
3. Click the "Remove" button
4. Click "Remove" in the confirmation dialog

---

## 📞 Support

| Channel | Link |
|---------|------|
| **Website** | https://fore.vip |
| **GitHub** | https://github.com/fore-vip/fore-ex |
| **Issue Tracker** | https://github.com/fore-vip/fore-ex/issues |

---

## 📄 License

MIT License

Copyright (c) 2026 ForeSmart

---

**Enjoy the convenient activity creation experience!** 🎉

Last Updated: 2026-03-21
