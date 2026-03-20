# Fore-Vip Agent Skills Collection

A collection of Agent skills created for the Fore-Vip (fore.vip) platform.

## 📦 Available Skills

| Skill | Description | Install Command |
|-------|-------------|-----------------|
| [activity-create](skills/activity-create/SKILL.md) | Create Fore-Vip offline events | `npx skills add fore-vip/skills -s activity-create` |

## 🚀 Quick Start

### Install All Skills

```bash
npx skills add fore-vip/skills
```

### Install Single Skill

```bash
npx skills add fore-vip/skills -s activity-create
```

### List Available Skills

```bash
npx skills add fore-vip/skills --list
```

## 📁 Directory Structure

```
skills/
├── README.md
├── README_cn.md
├── LICENSE
├── SKILL_TEMPLATE.md       # SKILL.md Standard Template
├── PUBLISH_GUIDE.md        # Publishing Guide
└── skills/
    ├── activity-create/
    │   └── SKILL.md        # Activity Creation Skill
    └── ...                 # More Skills
```

## 🛠️ Developing New Skills

1. Refer to [SKILL_TEMPLATE.md](SKILL_TEMPLATE.md) for the standard format
2. Create a new skill folder under the `skills/` directory
3. Write the `SKILL.md` file
4. Submit a PR

## 📚 Related Projects

| Project | Description |
|---------|-------------|
| [Fore-Vip](https://fore.vip) | Main Platform |
| [MCP Cloud Functions](https://github.com/fore-vip/skills) | Server-side Skill Implementation |

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

---

**Website**: https://fore.vip  
**Documentation**: https://doc.fore.vip
