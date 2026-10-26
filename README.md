<h1 align="center">📺 Pure TV</h1>

<p align="center">
  <b>An ad-free, Apple TV–style home screen for Android TV and Google TV.</b><br>
  Free and open source. Installs from your computer in about 10 minutes, and every change can be undone.
</p>

<p align="center">
  <a href="https://github.com/Vardxn/pure-tv/releases/latest"><img src="https://img.shields.io/github/v/release/Vardxn/pure-tv?style=for-the-badge&label=latest&color=34C759" alt="Latest release"></a>
  <a href="https://github.com/Vardxn/pure-tv/releases"><img src="https://img.shields.io/github/downloads/Vardxn/pure-tv/total?style=for-the-badge&color=0A84FF" alt="Downloads"></a>
  <a href="https://github.com/Vardxn/pure-tv/actions/workflows/build.yml"><img src="https://img.shields.io/github/actions/workflow/status/Vardxn/pure-tv/build.yml?branch=main&style=for-the-badge&label=build" alt="Build"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/Vardxn/pure-tv?style=for-the-badge&color=8E8E93" alt="MIT licence"></a>
</p>

<p align="center">
  <img src="docs/puretv/home.jpg" alt="Pure TV home screen" width="900">
</p>

<p align="center">
  <a href="#quick-start"><img src="https://img.shields.io/badge/Install_in_10_minutes-34C759?style=for-the-badge" alt="Install"></a>
  <a href="#screenshots"><img src="https://img.shields.io/badge/Screenshots-1C1C1E?style=for-the-badge" alt="Screenshots"></a>
  <a href="docs/puretv/pure-tv-overview.pdf"><img src="https://img.shields.io/badge/Overview_deck_(PDF)-1C1C1E?style=for-the-badge" alt="Overview deck"></a>
  <a href="https://www.buymeacoffee.com/Vardxn"><img src="https://img.shields.io/badge/Buy_me_a_coffee-FFDD00?style=for-the-badge&logo=buymeacoffee&logoColor=black" alt="Buy me a coffee"></a>
</p>

---

<a id="quick-start"></a>
## ⚡ Quick start: 3 steps, about 10 minutes

Works on Android TV and Google TV (Android 8 or later): Xiaomi, TCL, Hisense, Sony, OnePlus, Realme, Philips and more. You need a computer on the same Wi-Fi as the TV.

**1 · On the TV:** Settings → About → select **Build** 7 times → back → Developer options → switch on **USB debugging** (and **Network debugging**, if you see it).

**2 · On your computer:** paste one line. It finds your TV by itself. Needs [Python 3](https://www.python.org/downloads/).

Mac or Linux, in **Terminal**:

```bash
curl -fsSL https://raw.githubusercontent.com/Vardxn/pure-tv/main/install.sh | bash
```

Windows, in **PowerShell**:

```powershell
irm https://raw.githubusercontent.com/Vardxn/pure-tv/main/install.ps1 | iex
```

**3 · On the TV again:** press **OK** on *"Allow USB debugging?"*, answer a few yes/no questions, then press **Home**.

Nothing is deleted, and one command [undoes everything](#undo). Stuck? See the [step-by-step guide](#install).

## ✨ Why people install it

<table>
  <tr>
    <td width="33%" valign="top"><h3>🚫 No ads</h3>No promoted rows, sponsored banners or trailers playing on their own. Just your apps on a calm photo.</td>
    <td width="33%" valign="top"><h3>⚡ Fast</h3>Opens in about 0.75 s. Apps you were just using stay warm, so switching back takes about 0.2 s.</td>
    <td width="33%" valign="top"><h3>🌤️ Useful weather</h3>The next six hours, a 24-hour rain warning, feels like, humidity, wind and air quality.</td>
  </tr>
  <tr>
    <td valign="top"><h3>🎛️ Your dock</h3>Press and hold any tile to swap in any app. Full-colour tiles for every app on your TV.</td>
    <td valign="top"><h3>🌙 Calm screensaver</h3>After five idle minutes: the time, a quote of the day and the weather, gently drifting to protect the screen.</td>
    <td valign="top"><h3>↩️ Fully reversible</h3>The installer backs up your TV first. One command puts everything back the way it was.</td>
  </tr>
</table>

## 🔄 From cluttered to calm

<p align="center"><img src="docs/puretv/before-after.jpg" alt="Before and after Pure TV" width="560"></p>

## 🚀 Fast on an everyday TV

Measured on a real TV with 1.8 GB of RAM. The biggest win was a hidden one: every piece of text was rebuilding its own copy of the font, freezing the screen for 290 ms whenever the weather updated. Fixed-weight fonts brought that to 30 ms.

<p align="center"><img src="docs/puretv/numbers.jpg" alt="Cold start 0.75 s, app switch 0.2 s, weather update 30 ms, screen build 130 ms" width="560"></p>

## 🛡️ Ads, handled

The home screen is ad-free out of the box. The installer can also turn on ad blocking across your apps and install an ad-free YouTube app, if you want them. [What each option can and can't do](#optional-extras-and-what-they-can-and-cant-do).

<p align="center"><img src="docs/puretv/ads.jpg" alt="Built-in ad-free home, optional ad blocking, optional ad-free YouTube" width="560"></p>

<a id="screenshots"></a>
## 📸 Screenshots

**Home.** The clock mirrored by the weather, quick controls mirrored by the rain warning, and one glass strip with the next six hours, feels like, humidity, wind and air quality. The line under the weather shows when it was last updated.

<p align="center"><img src="docs/puretv/home.jpg" alt="Pure TV home screen" width="860"></p>

**Both dock rows.** Press Down to open the second row; the top of the screen fades away so the apps have the room.

<p align="center"><img src="docs/puretv/dock-open.jpg" alt="Dock with both rows open" width="860"></p>

**Dock editor.** Press and hold any tile to put any installed app in its place. Apps already in the dock are marked.

<p align="center"><img src="docs/puretv/dock-editor.jpg" alt="Choosing an app for a dock slot" width="860"></p>

**Screensaver.** After five minutes without a remote press (or press Back on Home): the time, a quote of the day, and the weather with the next hours and air quality.

<p align="center"><img src="docs/puretv/screensaver.jpg" alt="Pure TV screensaver" width="860"></p>

**Set-top box in one press.** The first press asks which HDMI input your box is on and remembers it.

## Install

The same 3 steps as the [quick start](#quick-start), with every detail.

Works on Xiaomi, TCL, Hisense, Sony, OnePlus, Realme and most other TVs running **Android TV or Google TV** (Android 8 or later). It does **not** work on Samsung (Tizen), LG (webOS) or Fire TV.

You need the TV, a computer (Mac, Windows or Linux) on the **same Wi-Fi**, and about 10 minutes. Nothing is deleted from your TV, and every change can be undone.

### Step 1 · On the TV: turn on debugging

1. Open the TV's **Settings** and find the build number:
   - **Xiaomi and other Google TV sets:** Settings → **System** → **About** → **Android TV OS build**
   - **Older Android TV sets:** Settings → **Device Preferences** → **About** → **Build**
2. Select it **7 times** with the OK button until the TV says *"You are now a developer"*.
3. Go back to Settings → **System** (or **Device Preferences**) → **Developer options** and switch on **USB debugging**, plus **Network debugging** or **ADB over network** if your TV shows it.

### Step 2 · On your computer: run one command

You need **Python 3** once. Get it from [python.org/downloads](https://www.python.org/downloads/); on Windows, tick **"Add python.exe to PATH"** during setup. Macs with Homebrew can run `brew install python` instead.

**Mac or Linux:** open **Terminal** and paste:

```bash
curl -fsSL https://raw.githubusercontent.com/Vardxn/pure-tv/main/install.sh | bash
```

**Windows:** open **PowerShell** and paste:

```powershell
irm https://raw.githubusercontent.com/Vardxn/pure-tv/main/install.ps1 | iex
```

The installer looks for your TV on the Wi-Fi and asks *"Found a TV at 192.168.1.25. Use it?"*. If it can't find it (some routers keep devices apart), it asks for the TV's IP address, which is under Settings → **Network & Internet** → your Wi-Fi network on the TV. You can also give the address up front: `… | bash -s -- 192.168.1.25`.

### Step 3 · On the TV: allow, answer, enjoy

1. The TV shows **"Allow USB debugging?"**. Tick **Always allow from this computer** and press **OK**.
2. The installer backs up your TV, installs Pure TV and makes it your home screen. Then it asks about a few optional extras. Our suggestions:

   | Question | Suggested answer |
   |---|---|
   | Remote's Home button opens Pure TV (Xiaomi) | **Yes** |
   | Debloat (only asked if your TV model has a tested list) | **Yes** |
   | AdGuard DNS | **Your choice.** Read the table below first |
   | SmartTube, YouTube without ads | **Yes**, if you watch a lot of YouTube |

3. Press **Home** on the remote. Then go back to **Developer options** and switch **USB debugging** off, so no other device on your Wi-Fi can connect to the TV.

**Prefer to have AI do it?** Open [Claude Code](https://claude.com/claude-code) (or another coding assistant that can run commands), paste the prompt from [PROMPT.md](PROMPT.md), and it will do steps 2 and 3 with you.

**Something not working?** The installer explains what to check, and [Troubleshooting](docs/TROUBLESHOOTING.md) covers the common snags (macOS blocking `adb`, TVs without a wireless-debugging switch, Windows quirks). Still stuck? [Open an issue](https://github.com/Vardxn/pure-tv/issues/new/choose) with your TV model and the message you saw.

### Optional extras, and what they can and can't do

| Extra | What it does | What it can't do |
|---|---|---|
| **Remote Home button** (Xiaomi) | Makes the remote's Home/PatchWall button open Pure TV, through a small accessibility service that only listens for that button. | Nothing else on the remote changes. |
| **Debloat** | Switches off preinstalled ad, tracking and promo apps, using a list tested on your TV model (from [`examples/`](examples/)). Switched off, not deleted: the TV's own Settings can turn them back on. | Only offered when there is a tested list for your model. |
| **AdGuard DNS** | Blocks known ad and tracking servers for the whole TV: banner and tracker ads in many apps, some ads in recorded shows. | **It cannot remove YouTube ads**, which come from the same servers as the videos, or ads stitched into live streams such as live cricket. Rarely, a streaming app may refuse to play or sign in; undo turns it off. |
| **SmartTube** | Installs [SmartTube](https://github.com/yuliskov/SmartTube), a free, open-source YouTube app for TVs with no ads and SponsorBlock. It sits next to the official YouTube app. | It is not made by Google; sign-in and features follow SmartTube's own releases. |

## Undo

Turn USB debugging back on, then run:

```bash
curl -fsSL https://raw.githubusercontent.com/Vardxn/pure-tv/main/install.sh | bash -s -- rollback
```

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Vardxn/pure-tv/main/install.ps1))) rollback
```

(Mac/Linux first, Windows second.) It finds the TV you installed on. Rollback reads the backup from your last install. It switches every app it turned off back on, restores your DNS and Home-button settings and your previous home screen, and offers to uninstall Pure TV and SmartTube.

When you're done, switch **USB debugging** off again on the TV.

## FAQ

**Will it work on my TV?** If your TV runs Android TV or Google TV on Android 8 or later (most Xiaomi, TCL, Hisense, Sony, OnePlus, Realme and Philips sets), yes. Samsung, LG and Fire TV use other systems and can't run it.

**Can I lose anything?** No. Nothing is deleted from your TV: apps the installer switches off can be switched back on from the TV's own Settings, and `rollback` undoes every change, including making your old home screen the default again.

**Does it block YouTube and Hotstar ads?** The home screen has no ads at all. Optional AdGuard DNS blocks ad and tracking servers in many apps, and optional SmartTube gives you ad-free YouTube. Ads stitched into live streams, like live cricket, can't be blocked by any app.

**Is it safe?** The code is open, there are no accounts, ads or analytics, and every release is signed and built by CI. The only network calls are listed below.

**Do I need to keep my computer connected?** Only during the install. Afterwards, switch USB debugging off on the TV.

## Network and privacy

Pure TV has no analytics, ads or accounts. It connects to:

- **Open-Meteo** (`api.open-meteo.com`, `air-quality-api.open-meteo.com`): the weather and air quality, each time you return to Home.
- **ipapi.co**: to find which city the TV is in, at most once a day. Not used when a location is pinned at build time.

Both over HTTPS. The installer also talks to GitHub to download releases.

## Tested on

- **Xiaomi MiTV-MOOR2** (Google TV, Android 11). Everything above, including the measurements.

It should work on most Android TV and Google TV sets running Android 8 or later (Xiaomi, TCL, Hisense, Sony, OnePlus and others), but those haven't been tested yet. If you try it on another TV, please open an issue with the model and what worked.

## Build from source

```bash
cd launcher
./gradlew assembleRelease     # JDK 17, Android SDK platform 34
```

To pin the weather to one place (a TV that never moves), add a line to `launcher/local.properties`, which is never committed:

```
weather.location=19.0760,72.8777,Mumbai
```

Release builds sign with the key configured in `~/.gradle/gradle.properties` (`PURETV_STORE_FILE`, `PURETV_STORE_PASSWORD`, `PURETV_KEY_ALIAS`, `PURETV_KEY_PASSWORD`); without it they use the debug key. Install a build with `./install.sh install --apk launcher/app/build/outputs/apk/release/app-release.apk`.

Screensaver quotes live in [`quotes.txt`](launcher/app/src/main/res/raw/quotes.txt).

## Support my work

Pure TV is free and open source, and I build and test it in my spare time. If it made your TV, or your evenings, a little better, you can buy me a coffee:

<a href="https://www.buymeacoffee.com/Vardxn"><img src="https://img.shields.io/badge/Buy_me_a_coffee-FFDD00?style=for-the-badge&logo=buymeacoffee&logoColor=black" alt="Buy me a coffee"></a>

**[buymeacoffee.com/Vardxn](https://www.buymeacoffee.com/Vardxn)**

In India, you can also pay by UPI: **`8279696707@yescred`** (any UPI app: Google Pay, PhonePe, Paytm, BHIM).

Not in a position to give? A ⭐ on this repo, a bug report, or trying Pure TV on a new TV model and [telling me how it went](https://github.com/Vardxn/pure-tv/issues) helps just as much.

And please consider supporting [cleanyourtv](https://github.com/Gathin23/cleanyourtv) too: Pure TV wouldn't exist without it.

## Credits

Pure TV is built on **[cleanyourtv](https://github.com/Gathin23/cleanyourtv)** by [Gathin23](https://github.com/Gathin23) and its contributors: the original launcher, the debloat lists in `examples/`, and the network ADB tools in `tools/`. If you want a small, offline, no-network launcher, use theirs. Pure TV is a restyle with weather, a screensaver and an installer on top.

Wallpaper photograph: river valley by [Karsten Würth](https://unsplash.com/photos/7BjhtdogU3A) on [Unsplash](https://unsplash.com/license).

Weather and air quality from [Open-Meteo](https://open-meteo.com/) (CC BY 4.0).

## License

[MIT](LICENSE), like the project it is built on.
