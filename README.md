# SortoDoco – Local-First File Organizer

**Keep your desktop and user folders clean, automatically.**
SortoDoco is a lightweight file organizer that declutters your **Desktop, Documents, Downloads, Music, Pictures, and Videos** folders. Unlike cloud-based solutions, SortoDoco runs **fully offline**, designed with **privacy-by-default** principles.

---

## 🚀 Overview

Everyone knows the chaos of a cluttered desktop. SortoDoco fixes this by automatically sorting your files by type and applying custom ignore rules. It’s designed as a **local-first utility**: fast, private, and cross-platform.

* **No cloud dependencies** → 100% local.
* **Automatic organization** → based on file extensions and custom rules.
* **Lightweight MVP** → focused only on file management.

---

## 🛠️ Tech Stack

* **Language:** Python 3.11+
* **Package Manager:** [uv](https://github.com/astral-sh/uv)
* **UI Toolkit:** Ttkbootstrap
* **Testing:** Pytest

---

## 📦 Installation (with `uv`)

```bash
# Clone repository
git clone https://github.com/<your-org>/sortodoco.git
cd sortodoco

# Create & activate virtual environment with uv
uv venv
source .venv/bin/activate   # on Linux/Mac
.venv\Scripts\activate      # on Windows

# Install dependencies
uv pip install -r requirements.txt

# Run the app
python -m src.main
```

---

## 📌 Project Status

* ✅ **Done**

  * File scanning & extension-based sorting
  * Session planning & summary reports
  * Configurable ignore rules (draft)

* 🔄 **In Progress**

  * YAML/JSON-driven ignore rules
  * Improved UI polish with customtkinter

* 🔮 **Planned**

  * AI-assisted file renaming
  * Image classification (local, offline models)
  * Predictive search & auto-fill in the search bar

---

## 🗺️ Roadmap & Early Access

SortoDoco is currently in **MVP development**.
An **Early-Access version** will be released soon for testing.
The goal: gather feedback, improve performance, and validate real-world workflows before v1.0.

---

## 🤝 Contributing

We welcome contributions:

* Follow **PEP8** guidelines.
* Add tests for all new features.
* Submit PRs or open issues.

---

## 📜 License

MIT 
