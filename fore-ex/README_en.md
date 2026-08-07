# Qianling Zhixuan Chrome Extension

[![Version](https://img.shields.io/badge/version-v1.1-orange)](https://f.fore.vip/download/fore-ex-v1.1.zip)
[![Download](https://img.shields.io/badge/download-Static%20Site-blue)](https://f.fore.vip/download/fore-ex-v1.1.zip)
[![Website](https://img.shields.io/badge/website-fore.vip-green)](https://fore.vip)

**Qianling Zhixuan** Chrome browser extension. Create activities with one click and publish them to the Qianling Zhixuan platform quickly.

---

## 📦 Download

### China Users (Recommended)

Download the latest version from static website:

```
https://f.fore.vip/download/fore-ex-v1.1.zip
```

[👉 Download v1.1](https://f.fore.vip/download/fore-ex-v1.1.zip)

### International Users

Download from GitHub Releases (if available).

---

## 🚀 Installation

### Method 1: Developer Mode (Recommended)

1. **Extract the Plugin Package**
   - Download `fore-ex-v1.1.zip`
   - Extract to any directory, e.g., `/Users/your-username/fore-ex`

2. **Open Chrome Extensions Page**
   - Visit: `chrome://extensions/`
   - Or: Menu → More Tools → Extensions

3. **Enable Developer Mode**
   - Toggle the "Developer mode" switch in the top right corner

4. **Load the Plugin**
   - Click "Load unpacked"
   - Select the extracted `fore-ex` folder
   - Plugin installed successfully, icon appears in the browser toolbar

5. **Use the Plugin**
   - Click the Qianling Zhixuan icon in the top right corner
   - Fill in activity information
   - Click "Create Activity"
   - Automatically jump to the activity detail page

### Method 2: Drag & Drop Installation (.crx file)

If you have a `.crx` file:

1. Visit `chrome://extensions/`
2. Enable "Developer mode"
3. Drag the `.crx` file to the page
4. Confirm installation

---

## 📖 Features

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🎯 Quick Activity Creation | Fill form, publish to Qianling Zhixuan platform |
| 📍 Activity Location | Support detailed address input |
| 💰 Ticket Settings | Free/paid activity flexible configuration |
| 📱 Contact Information | Automatically collect organizer WeChat |
| 🔗 Auto Redirect | Automatically open activity detail page after creation |

### 🎨 UI Optimizations

- ✅ Logo and title displayed in same row
- ✅ Click logo/title to jump to official website
- ✅ Simple form, no redundant fields
- ✅ Responsive layout, adapts to different screens

---

## 📋 User Guide

### Activity Creation Flow

```
1. Click the Qianling Zhixuan plugin icon in browser toolbar
        ↓
2. Fill in activity information:
   - Activity Title (required, min 2 characters)
   - Start Time (required)
   - End Time (optional)
   - Activity Address (required)
   - Contact/WeChat (required)
   - Ticket Price (optional, 0 = free)
        ↓
3. Click "Create Activity" button
        ↓
4. Wait for submission (loading animation shown)
        ↓
5. Success → Auto redirect to activity detail page
```

### Form Fields

| Field | Required | Description |
|-------|----------|-------------|
| Activity Title | ✅ | Min 2 characters, keep it concise |
| Start Time | ✅ | Activity start date and time |
| End Time | ⚪ | Optional, default 2 hours later |
| Activity Address | ✅ | Detailed activity location |
| Contact Info | ✅ | WeChat or other contact method |
| Ticket Price | ⚪ | 0 = free, unit: CNY |

---

## 🔧 Technical Architecture

### Tech Stack

| Technology | Description |
|------------|-------------|
| **Manifest V3** | Latest Chrome extension specification |
| **HTML5 + CSS3** | Modern interface |
| **Vanilla JavaScript** | Lightweight, no framework dependencies |
| **MCP Protocol** | Communication with Qianling Zhixuan API |

### Project Structure

```
fore-ex/
├── manifest.json      # Extension configuration file
├── popup.html         # Popup page HTML
├── popup.js           # Form logic handler
├── icon.png           # Extension icon
├── activity.html      # Activity page
├── check.html         # Check page
├── test.html          # Test page
└── index.html         # Main page
```

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `https://api.fore.vip/mcp/tools/call` | MCP tool call |
| `https://api.fore.vip/mcp/tools/list` | Available tools list |
| `https://fore.vip/st?id={id}` | Activity detail page |

---

## 🔄 Changelog

### v1.1 (2026-03-21)

**Optimizations**
- ✅ Logo and title displayed in same row
- ✅ Removed title emoji, cleaner interface
- ✅ Logo and title clickable to official website
- ✅ Removed external link field, simplified form
- ✅ Optimized form layout, improved user experience

### v1.0 (2025-12-25)

**Initial Release**
- ✅ Basic activity creation feature
- ✅ MCP protocol integration
- ✅ Form validation
- ✅ Auto redirect

---

## ❓ FAQ

### Q: Plugin fails to load?

**A**: Please ensure:
1. ZIP file is extracted, don't load directly from archive
2. Selected folder contains `manifest.json`
3. "Developer mode" is enabled

### Q: Activity creation failed?

**A**: Check the following:
1. Is network connection normal?
2. Are all required fields filled?
3. Is activity title at least 2 characters?
4. Is start time later than current time?
5. Is end time later than start time?

### Q: How to update the plugin?

**A**: 
1. Download the latest ZIP package
2. Extract and overwrite the original directory
3. Click "Refresh" button on the plugin in `chrome://extensions/`

### Q: Is data secure?

**A**: 
- Plugin only collects minimum information required for activity creation
- All data transmission uses HTTPS encryption
- No user privacy data is stored

---

## 📞 Support

| Channel | Link |
|---------|------|
| **Website** | https://fore.vip |
| **API Docs** | https://api.fore.vip/mcp |
| **Project Docs** | https://doc.fore.vip |
| **GitHub** | https://github.com/fore-ex |

---

## 📄 License

MIT License

---

## 🌟 Screenshots

### Plugin Interface

![Plugin Interface](./icon.png)

1. Click icon in browser toolbar
2. Fill activity form
3. Create activity with one click

---

**Enjoy the convenient activity creation experience!** 🎉
