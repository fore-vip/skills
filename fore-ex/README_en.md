# Qianling Zhixuan Chrome Extension (fore-ex)

A Chrome browser extension to browse outdoor activities, discover great content, jump to activity details in one click, and open the key management page to get your API key.

## Download & Install

### China Users (Recommended)

Download the latest version from the static site:

- Download: https://f.fore.vip/download/fore-ex-v2.0.zip
- Size: ~90KB

If the download link is not yet updated, you can load the source folder in "Developer mode" (see tutorial below).

### International Users

Get the source from GitHub: https://github.com/fore-vip/fore-ex

## Installation

### Method 1: Developer Mode (Recommended)

1. Download the extension package and extract it to any folder
2. Open Chrome extensions page: visit `chrome://extensions/`, or Menu → More Tools → Extensions
3. Toggle "Developer mode" on (top right)
4. Click "Load unpacked", then select the `fore-ex` folder containing `manifest.json`
5. Verify: the extension appears in the list, its icon shows in the toolbar, status is "Enabled"
6. (Optional) Click the "🧩" icon → find "Qianling Zhixuan" → click "📌" to pin it to the toolbar

### Method 2: Git Clone (Developers)

```bash
git clone git@github.com:fore-vip/fore-ex.git
cd fore-ex
# Then follow Method 1, steps 2-4 to load
```

## Features

| Feature | Description |
|---------|-------------|
| Activity Search | Search activities by keyword |
| Activity List | Shows cover, content, address, tags, view/participant counts |
| Cover Image | Cover shown on top of card (auto-hidden if load fails) |
| Click to Open | Tap a card to jump to the activity detail page |
| Infinite Scroll | More activities load automatically as you scroll |
| Publish Guide | "Publish" menu opens the key management page to get an API key |

## User Guide

1. Click the extension icon in the toolbar
2. Type a keyword in the search box (optional)
3. Browse the auto-loaded activity list
4. Click a card to open the detail page — screenshot or copy the link
5. Scroll down to load more

### How to publish an activity?

The extension does not create activities by itself. Click "Publish" in the menu → open the key management page → sign in to generate / copy your API key, then create your own activity via the web app or an AI assistant.

## FAQ

### Extension fails to load?

- Extract the ZIP first; don't load directly from the archive
- Select the folder that contains `manifest.json`
- "Developer mode" is enabled
- Folder path has no Chinese or special characters

### Activity list is blank?

- Check your network connection
- After editing source, click the refresh button on `chrome://extensions/`

### How to update?

Download the latest ZIP, extract over the old folder, then click "Refresh" on the extension card at `chrome://extensions/`.

### Is my data safe?

- Only reads the minimum info needed for the activity list
- All transfers use HTTPS encryption
- No user privacy data is stored

### How to uninstall?

`chrome://extensions/` → find "Qianling Zhixuan" → click "Remove".

## Support

| Channel | Link |
|---------|------|
| Website | https://fore.vip |
| GitHub | https://github.com/fore-vip/fore-ex |
| Issues | https://github.com/fore-vip/fore-ex/issues |

## License

MIT License · Copyright (c) 2026 Qianling Zhixuan

Last updated: 2026-08-07
