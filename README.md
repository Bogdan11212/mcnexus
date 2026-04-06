<p align="center">
  <img src="https://i127.fastpic.org/big/2026/0406/02/ced1b0369b33bd583f822ba82a5c0502.png?md5=gTbekEAYxGucHAWj6uslQQ&expires=1775440800" alt="mcnexus logo" width="180" />
</p>

<h1 align="center">mcnexus</h1>

<p align="center">
  <strong>Production-ready, high-performance asynchronous Minecraft library for Python.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/mcnexus/"><img src="https://img.shields.io/pypi/v/mcnexus?color=4CAF50&style=for-the-badge" alt="PyPI version"></a>
  <a href="https://github.com/Bogdan11212/mcnexus/actions/workflows/ci.yml"><img src="https://github.com/Bogdan11212/mcnexus/actions/workflows/ci.yml/badge.svg" alt="CI Status"></a>
  <a href="https://github.com/Bogdan11212/mcnexus/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Bogdan11212/mcnexus?color=4CAF50&style=for-the-badge" alt="License"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/pypi/pyversions/mcnexus?color=4CAF50&style=for-the-badge" alt="Python Versions"></a>
</p>

---

## 🚀 Overview

**mcnexus** is a modern Python library built from the ground up to provide reliable, asynchronous tools for interacting with Minecraft servers. Whether you are building a monitoring dashboard, a cross-server chat system, or a complex management bot, mcnexus has you covered.

### Key Features

*   ✅ **Robust RCON**: Handles multi-packet responses (up to 4KB+) and automatic reconnection.
*   🌍 **Server Status (SLP)**: Full support for Modern (1.7+) and Legacy (pre-1.7) protocols.
*   📡 **DNS & SRV Support**: Automatically resolves records like `mc.hypixel.net` to the correct IP and port.
*   ⚡ **Async-First**: Built on top of `asyncio` for high-concurrency environments.
*   💎 **Clean API**: Beautiful, documented models and developer-friendly error messages.

---

## 📦 Installation

```bash
pip install mcnexus
```

---

## 📖 Documentation

For full documentation and API reference, visit:  
👉 **[https://bogdan11212.github.io/mcnexus/](https://bogdan11212.github.io/mcnexus/)**

---

## ⚡ Quick Start

### Get Server Status
```python
import asyncio
from mcnexus import status

async def main():
    info = await status("mc.hypixel.net")
    if info.online:
        print(f"[{info.ping:.1f}ms] {info.players_online}/{info.players_max} players online.")
        print(f"MOTD: {info.motd_clean}")

asyncio.run(main())
```

### Run RCON Commands
```python
from mcnexus import RCONClient

async def run_rcon():
    async with RCONClient("127.0.0.1", 25575, "secret_password") as rcon:
        response = await rcon.command("list")
        print(response.clean)
```

---

## 🤝 Contributing

Contributions are welcome! Please check out our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md).

## 📄 License

mcnexus is released under the **MIT License**. See [LICENSE](LICENSE) for details.
