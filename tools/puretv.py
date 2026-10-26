#!/usr/bin/env python3
"""Pure TV installer: puts Pure TV on an Android TV / Google TV over the network, and undoes it.

    puretv.py install  [tv-ip] [--apk FILE] [--yes] [--home-key] [--debloat] [--dns] [--smarttube]
    puretv.py rollback [tv-ip]
    puretv.py probe    [tv-ip]
    puretv.py find

Leave out the IP and the installer finds the TV itself: it looks for network ADB (port 5555) on
this computer's local network, and remembers the TV it used so rollback can find it again.

Talks to the TV with the pure-Python adb-shell client, so it works where the adb binary is blocked
(macOS Local Network privacy). Every change is recorded in ~/PureTV-backups/<model>-<time>/state.json
before it is made; `rollback` reads the newest one and reverses it. Nothing is uninstalled from the
TV: debloat uses `pm disable-user`, which the TV's own Settings can also undo.
"""
import argparse
import base64
import datetime
import glob
import hashlib
import ipaddress
import json
import os
import socket
import sys
import tempfile
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.keygen import keygen
from adb_shell.auth.sign_pythonrsa import PythonRSASigner

REPO = "Vardxn/pure-tv"
PKG = "dev.vardxn.puretv"
HOME_ACTIVITY = PKG + "/com.gathin.tvhome.MainActivity"
HOME_KEY_SERVICE = PKG + "/com.gathin.tvhome.HomeKeyService"
UPSTREAM_PKG = "com.gathin.tvhome"
STOCK_LAUNCHERS = [
    "com.google.android.apps.tv.launcherx",   # Google TV
    "com.google.android.tvlauncher",          # Android TV
    "com.google.android.leanbacklauncher",    # older Android TV
    "com.mitv.tvhome",                         # Xiaomi PatchWall
]
ADGUARD_DNS = "dns.adguard-dns.com"
SMARTTUBE_REPO = "yuliskov/SmartTube"
SMARTTUBE_PKG = "com.liskovsoft.smarttubetv.beta"

STATE_HOME = os.path.expanduser("~/.puretv")
LAST_TV = os.path.join(STATE_HOME, "last-tv")
BACKUPS = os.path.expanduser("~/PureTV-backups")
HERE = os.path.dirname(os.path.abspath(__file__))
EXAMPLES = os.path.join(os.path.dirname(HERE), "examples")


# ---------------------------------------------------------------- connection

def signer():
    """Reuse the stock adb key when there is one (the TV may already trust it), else our own."""
    key = os.path.expanduser("~/.android/adbkey")
    if not (os.path.exists(key) and os.path.exists(key + ".pub")):
        os.makedirs(STATE_HOME, exist_ok=True)
        key = os.path.join(STATE_HOME, "adbkey")
        if not os.path.exists(key):
            keygen(key)
    with open(key) as f:
        priv = f.read()
    with open(key + ".pub") as f:
        pub = f.read()
    return PythonRSASigner(pub, priv)


class TV:
    def __init__(self, host, port=5555):
        say(f"Connecting to {host}:{port}. If the TV asks \"Allow USB debugging?\", tick "
            "\"Always allow\" and press OK.")
        self.dev = AdbDeviceTcp(host, port, default_transport_timeout_s=120.0)
        try:
            self.dev.connect(rsa_keys=[signer()], transport_timeout_s=120.0, auth_timeout_s=120.0)
        except OSError as e:
            sys.exit(f"\nCould not reach the TV at {host}:{port} ({e}).\n"
                     "Check: the TV is on, on the same Wi-Fi, and Developer options > USB debugging\n"
                     "(and Network debugging, if your TV has it) is on. See README > Install, step 1.")
        try:
            os.makedirs(STATE_HOME, exist_ok=True)
            with open(LAST_TV, "w") as f:
                f.write(host)
        except OSError:
            pass

    def sh(self, cmd, timeout=120.0):
        return self.dev.shell(cmd, read_timeout_s=timeout).strip()

    def prop(self, name):
        return self.sh(f"getprop {name}")

    def packages(self, flag=""):
        out = self.sh(f"pm list packages {flag}")
        return {line.split(":", 1)[1].strip() for line in out.splitlines() if line.startswith("package:")}

    def push(self, local, remote):
        """Send a file as base64 chunks through the shell: slower than sync push, but works everywhere."""
        data = open(local, "rb").read()
        tmp = remote + ".b64"
        self.sh(f"rm -f {remote} {tmp}")
        chunk = 48 * 1024
        total = (len(data) + chunk - 1) // chunk
        for i in range(total):
            part = base64.b64encode(data[i * chunk:(i + 1) * chunk]).decode()
            if f"ok{i}" not in self.sh(f"echo '{part}' >> {tmp} && echo ok{i}", 60.0):
                sys.exit("File transfer to the TV failed; please run the installer again.")
            print(f"\r  sending {100 * (i + 1) // total}%", end="", flush=True)
        print()
        self.sh(f"base64 -d {tmp} > {remote} && rm {tmp}")
        if self.sh(f"md5sum {remote}").split()[0] != hashlib.md5(data).hexdigest():
            sys.exit("The file arrived damaged; please run the installer again.")

    def install(self, apk):
        remote = "/data/local/tmp/puretv-install.apk"
        self.push(apk, remote)
        out = self.sh(f"pm install -r {remote}; rm -f {remote}", 300.0)
        if "Success" not in out:
            sys.exit(f"Android refused the install:\n{out}")

    def home_package(self):
        out = self.sh("cmd package resolve-activity --brief -a android.intent.action.MAIN "
                      "-c android.intent.category.HOME")
        last = out.splitlines()[-1] if out else ""
        return last.split("/")[0].strip() if "/" in last else last.strip()


# ---------------------------------------------------------------- finding the TV

def local_ipv4():
    """This computer's address on the LAN. A UDP connect picks the outgoing interface; nothing is sent."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("192.0.2.1", 9))   # TEST-NET-1, never routed
        return s.getsockname()[0]
    except OSError:
        return None
    finally:
        s.close()


def adb_open(ip, port=5555, timeout=0.6):
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except OSError:
        return False


def hostname(ip):
    try:
        name = socket.gethostbyaddr(ip)[0]
    except OSError:
        return ""
    name = name.split(".")[0]
    # Routers answer "unknown_<mac>" or the address itself for devices without a name.
    return "" if name == ip.split(".")[0] or name.lower().startswith("unknown") else name


def find_tvs():
    """Every address on this computer's /24 that answers on the network ADB port, with its name."""
    me = local_ipv4()
    if not me or ipaddress.ip_address(me).is_loopback:
        return []
    net = ipaddress.ip_network(f"{me}/24", strict=False)
    hosts = [str(h) for h in net.hosts() if str(h) != me]
    say(f"Looking for your TV on {net} ...")
    with ThreadPoolExecutor(max_workers=64) as pool:
        found = [ip for ip, ok in zip(hosts, pool.map(adb_open, hosts)) if ok]
        names = list(pool.map(hostname, found))
    return list(zip(found, names))


def pick_tv(assume_yes=False):
    """Find the TV on the network, or ask for its address when that doesn't work."""
    tvs = find_tvs()
    if len(tvs) == 1:
        ip, name = tvs[0]
        if ask(f"Found a TV at {ip}{f' ({name})' if name else ''}. Use it?", True, assume_yes):
            return ip
    elif tvs:
        say("Found these devices with debugging on:")
        for n, (ip, name) in enumerate(tvs, 1):
            say(f"  {n}. {ip}  {name}")
        while True:
            a = prompt(f"Which one is your TV? [1-{len(tvs)}, or type an IP address] ")
            if a.isdigit() and 1 <= int(a) <= len(tvs):
                return tvs[int(a) - 1][0]
            if valid_ip(a):
                return a
    else:
        say("No TV answered on this network. Check that the TV is on, on the same Wi-Fi as this\n"
            "computer, and that Developer options > USB debugging (and Network debugging, if your TV\n"
            "has it) is on. Or type the TV's IP address: Settings > Network & Internet > your Wi-Fi.")
    while True:
        a = prompt("TV's IP address: ")
        if valid_ip(a):
            return a
        say("That doesn't look like an IP address; it looks like 192.168.1.25.")


def remembered_tv():
    try:
        with open(LAST_TV) as f:
            ip = f.read().strip()
    except OSError:
        return None
    return ip if valid_ip(ip) else None


def valid_ip(s):
    try:
        return ipaddress.ip_address(s).version == 4
    except ValueError:
        return False


def resolve_host(args, use_last=False):
    """The TV to talk to: given on the command line, remembered from last time, or found now."""
    if args.host:
        return args.host
    if use_last:
        last = remembered_tv()
        if last and adb_open(last):
            say(f"Using the TV from last time, {last}.")
            return last
    return pick_tv(getattr(args, "yes", False))


# ---------------------------------------------------------------- helpers

def prompt(question):
    try:
        return input(question).strip()
    except EOFError:
        sys.exit("\nNo answer; run the installer again with the TV's IP address.")


def say(msg=""):
    print(msg, flush=True)


def ask(question, default, assume_yes):
    if assume_yes:
        return True
    hint = "Y/n" if default else "y/N"
    while True:
        try:
            a = input(f"{question} [{hint}] ").strip().lower()
        except EOFError:
            return default
        if not a:
            return default
        if a in ("y", "yes"):
            return True
        if a in ("n", "no"):
            return False


def github_latest_asset(repo, pick):
    """Download the release asset `pick(names)` chooses from the repo's latest GitHub release."""
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/releases/latest",
                                 headers={"Accept": "application/vnd.github+json", "User-Agent": "puretv"})
    with urllib.request.urlopen(req, timeout=30) as r:
        release = json.load(r)
    assets = {a["name"]: a["browser_download_url"] for a in release.get("assets", [])}
    name = pick(sorted(assets))
    if not name:
        sys.exit(f"No suitable file in the latest {repo} release.")
    path = os.path.join(tempfile.mkdtemp(prefix="puretv-"), name)
    say(f"  downloading {name} ({release.get('tag_name', '')})")
    urllib.request.urlretrieve(assets[name], path)
    return path


def model_slug(tv):
    brand = tv.prop("ro.product.brand").lower() or tv.prop("ro.product.manufacturer").lower()
    model = tv.prop("ro.product.model").lower().replace(" ", "-")
    return f"{brand}-{model}"


def debloat_list(slug):
    """Packages from examples/<brand>-<model>/debloat.txt, when the repo has a list for this TV."""
    path = os.path.join(EXAMPLES, slug, "debloat.txt")
    if not os.path.exists(path):
        return None, path
    pkgs = []
    for line in open(path, encoding="utf-8"):
        line = line.split("#", 1)[0].strip()
        if line:
            pkgs.append(line.split()[0])
    return pkgs, path


def save_state(state):
    with open(os.path.join(state["dir"], "state.json"), "w") as f:
        json.dump(state, f, indent=2)


# ---------------------------------------------------------------- commands

def cmd_find(args):
    tvs = find_tvs()
    if not tvs:
        sys.exit("No device with network debugging on was found on this network.")
    for ip, name in tvs:
        say(f"  {ip}  {name}")


def cmd_probe(args):
    args.host = resolve_host(args, use_last=True)
    tv = TV(args.host)
    for p in ("ro.product.manufacturer", "ro.product.model", "ro.build.version.release",
              "ro.product.cpu.abi", "ro.build.display.id"):
        say(f"{p} = {tv.prop(p)}")
    say(f"home screen = {tv.home_package()}")


def cmd_install(args):
    args.host = resolve_host(args)
    tv = TV(args.host)
    model = tv.prop("ro.product.model")
    android = tv.prop("ro.build.version.release")
    say(f"\nConnected: {tv.prop('ro.product.manufacturer')} {model}, Android {android}\n")

    # 1. Back up everything we might change, before changing anything
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    folder = os.path.join(BACKUPS, f"{model.replace(' ', '_')}-{stamp}")
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "packages.txt"), "w") as f:
        f.write("\n".join(sorted(tv.packages())))
    with open(os.path.join(folder, "disabled-before.txt"), "w") as f:
        f.write("\n".join(sorted(tv.packages("-d"))))
    with open(os.path.join(folder, "getprop.txt"), "w") as f:
        f.write(tv.sh("getprop"))
    state = {
        "dir": folder, "model": model, "host": args.host,
        "previous_home": tv.home_package(),
        "dns_mode": tv.sh("settings get global private_dns_mode"),
        "dns_host": tv.sh("settings get global private_dns_specifier"),
        "a11y": tv.sh("settings get secure enabled_accessibility_services"),
        "disabled": [], "installed": [], "dns_changed": False,
    }
    save_state(state)
    say(f"Backup saved in {folder}")

    # 2. Pure TV itself
    say("\nInstalling Pure TV...")
    apk = args.apk or github_latest_asset(REPO, lambda names: next((n for n in names if n.endswith(".apk")), None))
    tv.install(apk)
    state["installed"].append(PKG)
    save_state(state)
    # Android counts the Wi-Fi network name as location, so this is what lets the Wi-Fi pill show it.
    # (TVs have no GPS; the weather's place comes from the internet connection, not from this.)
    for perm in ("ACCESS_FINE_LOCATION", "ACCESS_COARSE_LOCATION"):
        tv.sh(f"pm grant {PKG} android.permission.{perm}")
    # Compile ahead of time: the launcher starts and scrolls at full speed from the first run.
    say("Optimising for speed...")
    tv.sh(f"cmd package compile -m speed -f {PKG}", 300.0)

    # 3. Make it the home screen
    say("Making Pure TV the home screen...")
    tv.sh(f"cmd package set-home-activity {HOME_ACTIVITY}")
    prev = state["previous_home"]
    if prev in STOCK_LAUNCHERS:
        # Stock launchers grab Home back after updates and reboots unless they are switched off.
        tv.sh(f"pm disable-user --user 0 {prev}")
        state["disabled"].append(prev)
        say(f"  switched off the stock launcher ({prev}); rollback switches it back on")
    elif prev == UPSTREAM_PKG:
        say("  the cleanyourtv launcher was your home screen; it stays installed (remove it in Settings if you like)")
    save_state(state)

    # 4. Optional extras, each explained before asking
    say("\nOptional extras (each can be undone with rollback):\n")

    if args.home_key or ask("Xiaomi remotes: make the remote's Home/PatchWall button open Pure TV?\n"
                            "  (turns on Pure TV's accessibility service, which only listens for that button)",
                            "xiaomi" in model.lower() or "mitv" in model.lower(), args.yes):
        current = state["a11y"] if state["a11y"] not in ("", "null") else ""
        # Drop the upstream launcher's key service: two services would both answer the Home button.
        keep = [s for s in current.split(":") if s and not s.startswith(UPSTREAM_PKG + "/") and s != HOME_KEY_SERVICE]
        services = ":".join(keep + [HOME_KEY_SERVICE])
        tv.sh(f"settings put secure enabled_accessibility_services {services}")
        tv.sh("settings put secure accessibility_enabled 1")
        # Lets Pure TV switch its button service back on by itself if an update turns it off.
        # Only granted when the viewer said yes here, so it never enables the service on its own otherwise.
        tv.sh(f"pm grant {PKG} android.permission.WRITE_SECURE_SETTINGS")
        state["a11y_changed"] = True
        save_state(state)
        say("  done\n")

    pkgs, path = debloat_list(model_slug(tv))
    if pkgs is None:
        say(f"Debloat: no tested list for this TV yet ({os.path.relpath(path, os.path.dirname(HERE))}).\n"
            "  Skipping. If you make one, please share it with the cleanyourtv project.\n")
    else:
        installed = tv.packages()
        disabled = tv.packages("-d")
        todo = [p for p in pkgs if p in installed and p not in disabled and p != PKG]
        if todo and (args.debloat or ask(f"Debloat: switch off {len(todo)} preinstalled ad, tracking and promo apps\n"
                                         f"  tested on this model ({os.path.basename(os.path.dirname(path))})?",
                                         True, args.yes)):
            for p in todo:
                tv.sh(f"pm disable-user --user 0 {p}")
                state["disabled"].append(p)
                save_state(state)
            say(f"  switched off {len(todo)} apps\n")

    if args.dns or ask("AdGuard DNS: block ad and tracking servers for the whole TV?\n"
                       "  Removes banner/tracker ads in many apps and some ads in recorded shows.\n"
                       "  It CANNOT remove YouTube ads, or ads stitched into live streams (live cricket).\n"
                       "  Rarely a streaming app may fail to play or sign in; rollback turns it off.",
                       False, args.yes):
        tv.sh("settings put global private_dns_mode hostname")
        tv.sh(f"settings put global private_dns_specifier {ADGUARD_DNS}")
        state["dns_changed"] = True
        save_state(state)
        say("  done\n")

    if args.smarttube or ask("SmartTube: install the free, open-source YouTube app for TVs with no ads and\n"
                             "  SponsorBlock? It sits next to the official YouTube app; nothing is modified.",
                             False, args.yes):
        abi = tv.prop("ro.product.cpu.abi")
        want = "arm64" if "arm64" in abi else "armeabi"

        def pick(names):
            apks = [n for n in names if n.endswith(".apk") and "stable" in n.lower()] or \
                   [n for n in names if n.endswith(".apk")]
            return next((n for n in apks if want in n), apks[0] if apks else None)

        tv.install(github_latest_asset(SMARTTUBE_REPO, pick))
        state["installed"].append(SMARTTUBE_PKG)
        save_state(state)
        say("  done\n")

    say("All set. Press Home on the remote to see Pure TV.\n")
    say("For safety, switch debugging off again on the TV when you're happy:")
    say("  Settings > Device Preferences > Developer options > USB debugging: off")
    say("To undo everything later: run the installer with  rollback")


def cmd_rollback(args):
    states = sorted(glob.glob(os.path.join(BACKUPS, "*", "state.json")), key=os.path.getmtime)
    if not states:
        sys.exit(f"No Pure TV install recorded in {BACKUPS}.")
    state = json.load(open(states[-1]))
    if not args.host and state.get("host") and adb_open(state["host"]):
        args.host = state["host"]
        say(f"Using the TV from the install, {args.host}.")
    args.host = resolve_host(args, use_last=True)
    tv = TV(args.host)
    say(f"Undoing the install recorded in {state['dir']}")

    for p in reversed(state.get("disabled", [])):
        tv.sh(f"pm enable {p}")
    say(f"  switched {len(state.get('disabled', []))} apps back on")

    if state.get("dns_changed"):
        mode = state.get("dns_mode") or "off"
        tv.sh(f"settings put global private_dns_mode {mode if mode != 'null' else 'off'}")
        host = state.get("dns_host")
        if host and host != "null":
            tv.sh(f"settings put global private_dns_specifier {host}")
        else:
            tv.sh("settings delete global private_dns_specifier")
        say("  restored the DNS setting")

    if state.get("a11y_changed"):
        before = state.get("a11y")
        if before and before != "null":
            tv.sh(f"settings put secure enabled_accessibility_services {before}")
        else:
            tv.sh("settings delete secure enabled_accessibility_services")
        tv.sh(f"pm revoke {PKG} android.permission.WRITE_SECURE_SETTINGS")
        say("  removed the remote Home-button service")

    prev = state.get("previous_home")
    # "android" is the system's "choose a home app" screen: nothing to restore, the TV will ask.
    if prev and prev not in (PKG, "android"):
        tv.sh(f"cmd package set-home-activity $(cmd package resolve-activity --brief "
              f"-a android.intent.action.MAIN -c android.intent.category.HOME {prev} | tail -n 1)")
        say(f"  home screen set back to {prev}")

    for p in state.get("installed", []):
        if ask(f"Uninstall {p}?", True, False):
            tv.sh(f"pm uninstall {p}")
    say("Done. Your TV is back the way it was before Pure TV.")


def main():
    ap = argparse.ArgumentParser(description="Install Pure TV on an Android TV, or undo it.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("install", help="install Pure TV and make it the home screen")
    i.add_argument("host", nargs="?", help="the TV's IP address; leave out to find the TV")
    i.add_argument("--apk", help="install this APK instead of downloading the latest release")
    i.add_argument("--yes", action="store_true", help="answer yes to every question")
    i.add_argument("--home-key", action="store_true", help="Xiaomi remote Home button opens Pure TV")
    i.add_argument("--debloat", action="store_true", help="switch off the tested bloat list for this TV")
    i.add_argument("--dns", action="store_true", help="turn on AdGuard DNS")
    i.add_argument("--smarttube", action="store_true", help="install SmartTube")
    r = sub.add_parser("rollback", help="undo the last install")
    r.add_argument("host", nargs="?")
    p = sub.add_parser("probe", help="show the TV's model and home screen")
    p.add_argument("host", nargs="?")
    sub.add_parser("find", help="list the TVs on this network with debugging on")
    args = ap.parse_args()
    {"install": cmd_install, "rollback": cmd_rollback, "probe": cmd_probe,
     "find": cmd_find}[args.cmd](args)


if __name__ == "__main__":
    main()
