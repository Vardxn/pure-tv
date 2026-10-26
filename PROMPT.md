# Install Pure TV with an AI assistant

Paste the prompt below into [Claude Code](https://claude.com/claude-code) (or another coding assistant
that can run commands) on a computer on the same Wi-Fi as the TV. First do the three steps under
**Before you start** in the [README](README.md): developer options, USB debugging, the TV's IP address.

This prompt only installs Pure TV with its own installer. For a full, model-by-model debloat of any
Android TV, use the prompt it grew out of: [cleanyourtv's PROMPT.md](https://github.com/Gathin23/cleanyourtv/blob/main/PROMPT.md).

---

I want to install Pure TV (https://github.com/Vardxn/pure-tv), a clean home screen, on my Android TV.
My TV model is: <MODEL> and its IP address is: <IP, or "please find it">.

- Clone https://github.com/Vardxn/pure-tv and read its README before doing anything.
- If I didn't give the IP, run `./install.sh find` (Windows: `.\install.ps1 find`), which lists the
  devices on my network with debugging on, and confirm the TV with me before connecting.
- Run `./install.sh probe <ip>` (Windows: `.\install.ps1 probe <ip>`) and tell me when the
  "Allow USB debugging?" prompt will appear on the TV so I can accept it. If the stock adb binary is
  blocked ("No route to host" on macOS while ping works), that's fine: the installer uses its own
  Python client.
- Run `./install.sh install <ip>` and relay every question it asks me, word for word, including what
  each optional extra cannot do. Don't answer for me.
- Afterwards, take a screenshot from the TV (`screencap -p` through `tools/tv.py`, then `--pull`) and
  show it to me, and check that the remote's Home button returns to Pure TV.
- Remind me to turn USB debugging off on the TV, and tell me the rollback command.
- Don't change anything on the TV that the installer didn't do, and don't uninstall any app.
