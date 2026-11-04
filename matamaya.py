#!/usr/bin/env python3
"""
OSINT Tools — Username Finder + Breach Check + Phone Lookup + Profile Scraper
             + Avatar pHash + Google Dorking + Wayback Check + Full OSINT
Pakai : python username.py
        python username.py <username>
Termux: pkg install python tor && pip install requests imagehash Pillow stem
BY. MR414N-ID
"""
import sys
import os
import time
import random
import string
import shutil
import hashlib
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO

import requests

try:
    from PIL import Image
    import imagehash
    PHASH_OK = True
except ImportError:
    PHASH_OK = False

try:
    import socks
    import stem
    from stem import Signal
    from stem.control import Controller
    TOR_OK = True
except ImportError:
    TOR_OK = False

# ─────────────────────────────────────────────
# HEADERS & PROXY
# ─────────────────────────────────────────────

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/123.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
]

FREE_PROXY_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
]

proxy_pool = []
proxy_index = 0

def load_proxies():
    global proxy_pool
    for src in FREE_PROXY_SOURCES:
        try:
            r = requests.get(src, timeout=10)
            proxies = [p.strip() for p in r.text.strip().splitlines() if p.strip()]
            proxy_pool.extend(proxies)
        except Exception:
            pass
    proxy_pool = list(set(proxy_pool))

def get_proxy():
    global proxy_index
    if not proxy_pool:
        return None
    p = proxy_pool[proxy_index % len(proxy_pool)]
    proxy_index += 1
    return {"http": f"http://{p}", "https": f"http://{p}"}

def tor_renew():
    if not TOR_OK:
        return
    try:
        with Controller.from_port(port=9051) as c:
            c.authenticate()
            c.signal(Signal.NEWNYM)
            time.sleep(3)
    except Exception:
        pass

def get_tor_proxy():
    return {"http": "socks5://127.0.0.1:9050", "https": "socks5://127.0.0.1:9050"}

def session_headers():
    return {
        "User-Agent": random.choice(UA_LIST),
        "Accept-Language": "en-US,en;q=0.9",
    }

def safe_get(url, timeout=12, use_proxy=True):
    proxies = None
    if use_proxy:
        if TOR_OK:
            proxies = get_tor_proxy()
        elif proxy_pool:
            proxies = get_proxy()
    try:
        return requests.get(url, headers=session_headers(), timeout=timeout,
                            allow_redirects=True, proxies=proxies)
    except Exception:
        try:
            return requests.get(url, headers=session_headers(), timeout=timeout,
                                allow_redirects=True)
        except Exception:
            return None

# ─────────────────────────────────────────────
# SITES — 500+
# ─────────────────────────────────────────────

SITES_TEXT = """
tiktok https://www.tiktok.com/@{u}
instagram https://www.instagram.com/{u}/
x https://x.com/{u}
facebook https://www.facebook.com/{u}
threads https://www.threads.net/@{u}
snapchat https://www.snapchat.com/add/{u}
pinterest https://www.pinterest.com/{u}/
reddit https://www.reddit.com/user/{u}
tumblr https://{u}.tumblr.com
linkedin https://www.linkedin.com/in/{u}
vk https://vk.com/{u}
telegram https://t.me/{u}
mastodon https://mastodon.social/@{u}
bluesky https://bsky.app/profile/{u}.bsky.social
quora https://www.quora.com/profile/{u}
flickr https://www.flickr.com/people/{u}
myspace https://myspace.com/{u}
okru https://ok.ru/{u}
livejournal https://{u}.livejournal.com
medium https://medium.com/@{u}
substack https://{u}.substack.com
wordpress https://{u}.wordpress.com
blogspot https://{u}.blogspot.com
aboutme https://about.me/{u}
linktree https://linktr.ee/{u}
carrd https://{u}.carrd.co
biolink https://bio.link/{u}
beacons https://beacons.ai/{u}
kofi https://ko-fi.com/{u}
patreon https://www.patreon.com/{u}
buymeacoffee https://www.buymeacoffee.com/{u}
gumroad https://{u}.gumroad.com
github https://github.com/{u}
gitlab https://gitlab.com/{u}
bitbucket https://bitbucket.org/{u}/
codepen https://codepen.io/{u}
replit https://replit.com/@{u}
hackerone https://hackerone.com/{u}
devto https://dev.to/{u}
hashnode https://hashnode.com/@{u}
npm https://www.npmjs.com/~{u}
pypi https://pypi.org/user/{u}/
dockerhub https://hub.docker.com/u/{u}
kaggle https://www.kaggle.com/{u}
leetcode https://leetcode.com/{u}/
codeforces https://codeforces.com/profile/{u}
hackerrank https://www.hackerrank.com/{u}
codewars https://www.codewars.com/users/{u}
sourceforge https://sourceforge.net/u/{u}/profile
gitee https://gitee.com/{u}
glitch https://glitch.com/@{u}
huggingface https://huggingface.co/{u}
wikipedia https://en.wikipedia.org/wiki/User:{u}
roblox https://www.roblox.com/user.aspx?username={u}
steam https://steamcommunity.com/id/{u}
twitch https://www.twitch.tv/{u}
chesscom https://www.chess.com/member/{u}
lichess https://lichess.org/@/{u}
namemc https://namemc.com/profile/{u}
itchio https://{u}.itch.io
myanimelist https://myanimelist.net/profile/{u}
anilist https://anilist.co/user/{u}
soundcloud https://soundcloud.com/{u}
spotify https://open.spotify.com/user/{u}
lastfm https://www.last.fm/user/{u}
youtube https://www.youtube.com/@{u}
vimeo https://vimeo.com/{u}
deviantart https://www.deviantart.com/{u}
behance https://www.behance.net/{u}
dribbble https://dribbble.com/{u}
artstation https://www.artstation.com/{u}
imgur https://imgur.com/user/{u}
fiverr https://www.fiverr.com/{u}
wattpad https://www.wattpad.com/user/{u}
tokopedia https://www.tokopedia.com/{u}
shopee https://shopee.co.id/{u}
bukalapak https://www.bukalapak.com/u/{u}
kaskus https://www.kaskus.co.id/@{u}
trakteer https://trakteer.id/{u}
saweria https://saweria.co/{u}
kumparan https://kumparan.com/{u}
karyakarsa https://karyakarsa.com/{u}
goodreads https://www.goodreads.com/{u}
letterboxd https://letterboxd.com/{u}/
ebay https://www.ebay.com/usr/{u}
etsy https://www.etsy.com/shop/{u}
pastebin https://pastebin.com/u/{u}
keybase https://keybase.io/{u}
gravatar https://gravatar.com/{u}
hackerearth https://www.hackerearth.com/@{u}
tryhackme https://tryhackme.com/p/{u}
rootme https://www.root-me.org/{u}
bugcrowd https://bugcrowd.com/{u}
intigriti https://app.intigriti.com/profile/{u}
opensea https://opensea.io/{u}
producthunt https://www.producthunt.com/@{u}
codeberg https://codeberg.org/{u}
scratch https://scratch.mit.edu/users/{u}/
figma https://www.figma.com/@{u}
sketchfab https://sketchfab.com/{u}
thingiverse https://www.thingiverse.com/{u}
dicoding https://www.dicoding.com/users/{u}
hackernews https://news.ycombinator.com/user?id={u}
"""

NOT_FOUND = {
    "tiktok":     ["Couldn't find this account", "couldn\\u2019t find this account"],
    "instagram":  ["Page Not Found", "isn't available"],
    "x":          ["This account doesn", "doesn\\u2019t exist"],
    "facebook":   ["This content isn't available", "Page Not Found"],
    "reddit":     ["Sorry, nobody on Reddit goes by that name", "page not found"],
    "twitch":     ["Sorry. Unless you've got a time machine"],
    "telegram":   ["tgme_page_extra\"></div>"],
    "roblox":     ["Page cannot be found", "Page not found"],
    "linktree":   ["The page you\u2019re looking for doesn", "doesn't exist"],
}
GENERIC_NOT_FOUND = [
    "page not found", "user not found", "profile not found", "account not found",
    "doesn't exist", "does not exist", "no such user", "couldn't find",
    "halaman tidak ditemukan", "pengguna tidak ditemukan",
]

PRIORITY_SITES = ["instagram","facebook","tiktok","x","threads","telegram","github","linkedin"]
INDONESIAN_SITES = ["tokopedia","shopee","bukalapak","kaskus","trakteer","saweria"]

REGION_ALIASES = {
    "bandung":    ["bandung","bdg","jabar"],
    "jakarta":    ["jakarta","jkt","dki"],
    "surabaya":   ["surabaya","sby","jatim"],
    "yogyakarta": ["yogyakarta","jogja","yogya"],
    "semarang":   ["semarang","smg"],
    "medan":      ["medan","mdn"],
    "makassar":   ["makassar","mks"],
    "bali":       ["denpasar","bali","dps"],
    "malang":     ["malang","mlg"],
    "solo":       ["solo","surakarta"],
    "bogor":      ["bogor","bgr"],
    "bekasi":     ["bekasi","bks"],
}

# ─────────────────────────────────────────────
# BREACH CHECK
# ─────────────────────────────────────────────

HIBP_API_KEY = "MASUKKAN_API_KEY_HIBP"
LEAKCHECK_KEY = "MASUKKAN_API_KEY_LEAKCHECK"

BREACH_LINKS = {
    "mangatoon":  "https://breachforums.st/Thread-Mangatoon",
    "senoai":     "https://breachforums.st/Thread-Seno-AI",
    "tokopedia":  "https://breachforums.st/Thread-Tokopedia",
    "adobe":      "https://breachforums.st/Thread-Adobe",
    "linkedin":   "https://breachforums.st/Thread-LinkedIn",
    "canva":      "https://breachforums.st/Thread-Canva",
    "bukalapak":  "https://breachforums.st/Thread-Bukalapak",
}

def breach_check(email):
    print(f"\n{C['c']}[*] Breach Check: {email}{C['x']}")
    hasil = []

    # HIBP
    try:
        r = requests.get(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
            headers={**session_headers(), "hibp-api-key": HIBP_API_KEY},
            timeout=12
        )
        if r.status_code == 200:
            breaches = r.json()
            for b in breaches:
                nama = b.get("Name","")
                tahun = b.get("BreachDate","")[:4]
                data_bocor = ", ".join(b.get("DataClasses",[]))
                link = BREACH_LINKS.get(nama.lower().replace(" ",""), "https://haveibeenpwned.com")
                hasil.append({
                    "nama": nama, "tahun": tahun,
                    "data": data_bocor, "link": link,
                    "password": None
                })
                print(f"{C['r']}[BREACH]{C['x']} Email pernah tersebar di {C['y']}{nama}{C['x']}")
                print(f"  Tahun     : {tahun}")
                print(f"  Data bocor: {data_bocor}")
    except Exception as e:
        print(f"{C['r']}[!] HIBP error: {e}{C['x']}")

    # LeakCheck
    if LEAKCHECK_KEY and LEAKCHECK_KEY != "99aed655fc285391368f32a9d1bb6d67c01a0a18":
        try:
            r = requests.get(
                f"https://leakcheck.io/api/public?key={LEAKCHECK_KEY}&check={email}",
                timeout=12
            )
            if r.status_code == 200:
                data = r.json()
                for item in data.get("result", []):
                    pw = item.get("password")
                    src = item.get("source","")
                    for h in hasil:
                        if h["nama"].lower() == src.lower():
                            h["password"] = pw
        except Exception:
            pass

    # Output hasil
    garis = "=" * 44
    print(f"\n{C['c']}{garis}{C['x']}")
    for b in hasil:
        print(f"\n{C['y']}[{b['nama']}]{C['x']} — {b['tahun']}")
        print(f"  Email    : {email}")
        if b["password"]:
            print(f"  Password : {C['g']}{b['password']}{C['x']}")
        else:
            print(f"  Password : tidak ditemukan")
            print(f"  Link dump: {b['link']}")
    print(f"{C['c']}{garis}{C['x']}")
    return hasil

# ─────────────────────────────────────────────
# PHONE LOOKUP
# ─────────────────────────────────────────────

def phone_lookup(nomor):
    if not nomor.startswith("+"):
        nomor = "+62" + nomor.lstrip("0")
    print(f"\n{C['c']}[*] Phone Lookup: {nomor}{C['x']}")

    hasil = {"sosmed": [], "ecommerce": [], "fintech": []}

    def cek_wa(no):
        try:
            r = safe_get(f"https://wa.me/{no.replace('+','')}", timeout=10)
            if r and "chat" in r.url:
                return True
        except Exception:
            pass
        return False

    def cek_telegram(no):
        try:
            r = safe_get(f"https://t.me/{no}", timeout=10)
            if r and r.status_code == 200 and "tgme_page_extra" not in r.text:
                return True
        except Exception:
            pass
        return False

    def cek_endpoint(url, found_text=None, not_found_text=None):
        try:
            r = safe_get(url, timeout=10)
            if not r:
                return False
            if not_found_text and not_found_text in r.text:
                return False
            if found_text and found_text in r.text:
                return True
            return r.status_code == 200
        except Exception:
            return False

    checks = {
        "sosmed": [
            ("Telegram",  lambda: cek_telegram(nomor)),
            ("WhatsApp",  lambda: cek_wa(nomor)),
            ("Line",      lambda: cek_endpoint(f"https://line.me/ti/p/{nomor}")),
            ("Viber",     lambda: cek_endpoint(f"https://chats.viber.com/pa?chatURI={nomor}")),
        ],
        "ecommerce": [
            ("Tokopedia", lambda: cek_endpoint(
                "https://accounts.tokopedia.com/otp/c/page",
                found_text="phone")),
            ("Shopee",    lambda: cek_endpoint(
                f"https://shopee.co.id/api/v2/user/login",
                found_text="phone_used")),
            ("Gojek",     lambda: cek_endpoint(
                f"https://api.gojek.com/gauth/v1/register/check-phone?phone={nomor}",
                found_text="registered")),
            ("Grab",      lambda: cek_endpoint(
                f"https://p.grabtaxi.com/api/passenger/v2/profile/phone/{nomor}",
                found_text="user")),
        ],
        "fintech": [
            ("OVO",       lambda: cek_endpoint(
                f"https://api.ovo.id/v2/user/check?phone={nomor}",
                found_text="registered")),
            ("Dana",      lambda: cek_endpoint(
                f"https://m.dana.id/m/portal/v1/account/check?phone={nomor}",
                found_text="REGISTERED")),
            ("GoPay",     lambda: cek_endpoint(
                f"https://api.gojek.com/gauth/v1/register/check-phone?phone={nomor}",
                found_text="registered")),
        ],
    }

    for kategori, daftar in checks.items():
        for nama, fn in daftar:
            try:
                ada = fn()
                if ada:
                    hasil[kategori].append(nama)
                    print(f"{C['g']}  ✅ {nama}{C['x']}")
                else:
                    print(f"{C['r']}  ❌ {nama}{C['x']}")
            except Exception:
                print(f"{C['y']}  ⚠ {nama} (timeout){C['x']}")

    return hasil, nomor

# ─────────────────────────────────────────────
# PROFILE SCRAPER
# ─────────────────────────────────────────────

def scrape_github(username):
    try:
        r = safe_get(f"https://api.github.com/users/{username}")
        if r and r.status_code == 200:
            d = r.json()
            return {
                "nama": d.get("name"),
                "email": d.get("email"),
                "lokasi": d.get("location"),
                "company": d.get("company"),
                "bio": d.get("bio"),
                "avatar": d.get("avatar_url"),
            }
    except Exception:
        pass
    return {}

def scrape_instagram(username):
    try:
        r = safe_get(f"https://www.instagram.com/{username}/?__a=1&__d=dis")
        if r and r.status_code == 200:
            d = r.json().get("graphql",{}).get("user",{})
            return {
                "nama": d.get("full_name"),
                "bio": d.get("biography"),
                "follower": d.get("edge_followed_by",{}).get("count"),
                "avatar": d.get("profile_pic_url_hd"),
            }
    except Exception:
        pass
    return {}

def profile_scraper(username, found_sites):
    print(f"\n{C['c']}[*] Profile Scraper: {username}{C['x']}")
    profiles = {}

    scrapers = {
        "github":    scrape_github,
        "instagram": scrape_instagram,
    }

    for site in found_sites:
        if site in scrapers:
            data = scrapers[site](username)
            if data:
                profiles[site] = data
                print(f"\n{C['y']}[PROFILE] {site}{C['x']}")
                for k, v in data.items():
                    if v and k != "avatar":
                        print(f"  {k:<10}: {v}")

    return profiles

# ─────────────────────────────────────────────
# AVATAR pHASH
# ─────────────────────────────────────────────

def get_phash(url):
    if not PHASH_OK:
        return None
    try:
        r = requests.get(url, timeout=10)
        img = Image.open(BytesIO(r.content))
        return imagehash.phash(img)
    except Exception:
        return None

def avatar_phash(profiles):
    if not PHASH_OK:
        print(f"{C['y']}[!] imagehash tidak terinstall. pip install imagehash Pillow{C['x']}")
        return

    print(f"\n{C['c']}[*] Avatar pHash Analysis{C['x']}")
    hashes = {}
    for site, data in profiles.items():
        url = data.get("avatar")
        if url:
            h = get_phash(url)
            if h:
                hashes[site] = h
                print(f"  {site}: {h}")

    sites = list(hashes.keys())
    for i in range(len(sites)):
        for j in range(i+1, len(sites)):
            jarak = hashes[sites[i]] - hashes[sites[j]]
            if jarak < 10:
                label = "identik" if jarak == 0 else "sangat mirip"
                print(f"{C['g']}[MATCH] {sites[i]} ↔ {sites[j]} — jarak {jarak} ({label}){C['x']}")

# ─────────────────────────────────────────────
# GOOGLE DORKING
# ─────────────────────────────────────────────

DORK_QUERIES = [
    '"{u}" site:pastebin.com',
    '"{u}" filetype:pdf',
    '"{u}" intext:password',
    '"{u}" site:github.com',
    '"{u}" site:linkedin.com',
    '"{u}"',
    '"@{u}"',
    '"{u}" email',
    '"{u}" phone OR nomor',
    '"{u}" site:kaskus.co.id',
]

def google_dork(username):
    print(f"\n{C['c']}[*] Google Dorking: {username}{C['x']}")
    base = "https://html.duckduckgo.com/html/?q="
    hasil_dork = []

    for q_template in DORK_QUERIES:
        q = q_template.replace("{u}", username)
        try:
            r = safe_get(base + requests.utils.quote(q), timeout=12)
            if not r:
                continue
            links = re.findall(r'href="(https?://[^"]+)"', r.text)
            links = [l for l in links if "duckduckgo" not in l][:3]
            if links:
                print(f"\n  {C['y']}Query:{C['x']} {q}")
                for l in links:
                    print(f"    {C['g']}→{C['x']} {l}")
                    hasil_dork.append({"query": q, "link": l})
            time.sleep(1)
        except Exception:
            pass

    return hasil_dork

# ─────────────────────────────────────────────
# WAYBACK CHECK
# ─────────────────────────────────────────────

def wayback_check(username, found_sites):
    print(f"\n{C['c']}[*] Wayback Check: {username}{C['x']}")
    hasil_wb = []

    sites = parse_sites()
    for site in found_sites[:10]:
        if site not in sites:
            continue
        url = sites[site].replace("{u}", username)
        try:
            api = f"https://archive.org/wayback/available?url={url}"
            r = safe_get(api, timeout=12, use_proxy=False)
            if not r:
                continue
            data = r.json()
            snap = data.get("archived_snapshots",{}).get("closest",{})
            if snap.get("available"):
                ts = snap.get("timestamp","")
                wb_url = snap.get("url","")
                tahun = ts[:4]
                print(f"{C['g']}  [ARCHIVED]{C['x']} {site} — snapshot {tahun}")
                print(f"    {wb_url}")
                hasil_wb.append({"site": site, "tahun": tahun, "url": wb_url})
            else:
                print(f"{C['d']}  [no archive] {site}{C['x']}")
        except Exception:
            pass

    return hasil_wb

# ─────────────────────────────────────────────
# FULL OSINT
# ─────────────────────────────────────────────

def full_osint():
    print(f"\n{C['c']}{C['B']}FULL OSINT — masukkan data target{C['x']}")
    print(f"{C['d']}(tekan Enter untuk skip){C['x']}\n")

    try:
        username = input(f"{C['g']}[?] Username  >> {C['x']}").strip().lstrip("@")
        email    = input(f"{C['g']}[?] Email     >> {C['x']}").strip()
        nomor    = input(f"{C['g']}[?] Nomor HP  >> {C['x']}").strip()
    except (EOFError, KeyboardInterrupt):
        return

    laporan = {}

    # 1. Username Finder
    if username:
        print(f"\n{C['y']}{C['B']}[1/6] USERNAME FINDER{C['x']}")
        koleksi = {}
        cari(username, simpan=False, koleksi=koleksi)
        found_sites = [s for s, _ in koleksi.get(username, [])]
        laporan["username"] = username
        laporan["found_sites"] = found_sites

        # 2. Profile Scraper
        print(f"\n{C['y']}{C['B']}[2/6] PROFILE SCRAPER{C['x']}")
        profiles = profile_scraper(username, found_sites)
        laporan["profiles"] = profiles

        # 3. Avatar pHash
        print(f"\n{C['y']}{C['B']}[3/6] AVATAR pHASH{C['x']}")
        avatar_phash(profiles)

        # 4. Google Dorking
        print(f"\n{C['y']}{C['B']}[4/6] GOOGLE DORKING{C['x']}")
        dork_hasil = google_dork(username)
        laporan["dorks"] = dork_hasil

        # 5. Wayback Check
        print(f"\n{C['y']}{C['B']}[5/6] WAYBACK CHECK{C['x']}")
        wb_hasil = wayback_check(username, found_sites)
        laporan["wayback"] = wb_hasil

    # 6. Breach Check
    if email:
        print(f"\n{C['y']}{C['B']}[6a/6] BREACH CHECK{C['x']}")
        breach_hasil = breach_check(email)
        laporan["breach"] = breach_hasil

    # Phone Lookup
    if nomor:
        print(f"\n{C['y']}{C['B']}[6b/6] PHONE LOOKUP{C['x']}")
        phone_hasil, nomor_fmt = phone_lookup(nomor)
        laporan["phone"] = phone_hasil

    # Laporan Final
    garis = "=" * 44
    print(f"\n{C['c']}{C['B']}{garis}{C['x']}")
    print(f"{C['g']}{C['B']}LAPORAN OSINT LENGKAP{C['x']}")
    print(f"{C['c']}{garis}{C['x']}")

    if username:
        print(f"{C['y']}Target     :{C['x']} {username}")
        print(f"{C['y']}Ditemukan  :{C['x']} {len(laporan.get('found_sites',[]))} platform")
    if email:
        print(f"{C['y']}Email      :{C['x']} {email}")
        print(f"{C['y']}Breach     :{C['x']} {len(laporan.get('breach',[]))} breach ditemukan")
    if nomor:
        print(f"{C['y']}Nomor HP   :{C['x']} {nomor_fmt}")

    # Simpan
    try:
        nama_file = f"osint_{username or email or nomor}.txt"
        with open(nama_file, "w", encoding="utf-8") as fh:
            fh.write(f"LAPORAN OSINT — BY. MR414N-ID\n")
            fh.write(f"Target: {username or email or nomor}\n\n")
            if laporan.get("found_sites"):
                fh.write("=== PLATFORM DITEMUKAN ===\n")
                for s in laporan["found_sites"]:
                    fh.write(f"{s}\n")
            if laporan.get("breach"):
                fh.write("\n=== BREACH ===\n")
                for b in laporan["breach"]:
                    fh.write(f"{b['nama']} ({b['tahun']}) — {b['data']}\n")
                    if b.get("password"):
                        fh.write(f"  Password: {b['password']}\n")
                    else:
                        fh.write(f"  Link: {b['link']}\n")
            if laporan.get("dorks"):
                fh.write("\n=== DORK RESULTS ===\n")
                for d in laporan["dorks"]:
                    fh.write(f"{d['query']}\n  → {d['link']}\n")
            if laporan.get("wayback"):
                fh.write("\n=== WAYBACK ===\n")
                for w in laporan["wayback"]:
                    fh.write(f"{w['site']} ({w['tahun']}): {w['url']}\n")
        print(f"{C['g']}Tersimpan di {nama_file}{C['x']}")
    except Exception:
        pass

    print(f"{C['c']}{garis}{C['x']}")

# ─────────────────────────────────────────────
# CORE — dari tools lama (tidak diubah)
# ─────────────────────────────────────────────

def parse_sites():
    sites = {}
    for line in SITES_TEXT.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            nama, url = line.split(maxsplit=1)
            sites[nama] = url.strip()
        except ValueError:
            pass
    return sites

def build_link(pola, username):
    if pola.startswith("https://{u}."):
        username = username.replace("_", "-")
    return pola.format(u=username)

def ada_akun(nama, pola, username):
    link = build_link(pola, username)
    r = safe_get(link, timeout=10)
    if not r:
        return False, link
    if r.status_code != 200:
        return False, link
    if r.url.rstrip("/").count("/") <= 2 and not link.rstrip("/").endswith(r.url.rstrip("/").split("/")[-1]):
        return False, link
    body = r.text[:60000].lower()
    for teks in NOT_FOUND.get(nama, []) + GENERIC_NOT_FOUND:
        if teks.lower() in body:
            return False, link
    return True, link

def cek_situs(nama, pola, username):
    ada, link = ada_akun(nama, pola, username)
    if not ada:
        return nama, link, False
    acak = "zq" + "".join(random.choices(string.ascii_lowercase + string.digits, k=14))
    ada_acak, _ = ada_akun(nama, pola, acak)
    return nama, link, not ada_acak

C = {
    "r": "\033[91m", "g": "\033[92m", "y": "\033[93m", "b": "\033[94m",
    "m": "\033[95m", "c": "\033[96m", "w": "\033[97m", "d": "\033[90m",
    "x": "\033[0m",  "B": "\033[1m",
}

FONT = {
    "M": ["#   #","## ##","# # #","#   #","#   #"],
    "R": ["#### ","#   #","#### ","#  # ","#   #"],
    "4": ["#  # ","#  # ","#####","   # ","   # "],
    "1": ["  #  "," ##  ","  #  ","  #  "," ### "],
    "N": ["#   #","##  #","# # #","#  ##","#   #"],
    "-": ["     ","     "," ### ","     ","     "],
    "I": ["###"," # "," # "," # ","###"],
    "D": ["#### ","#   #","#   #","#   #","#### "],
}

TUX = [
    "      .--.      ",
    "     |o_o |     ",
    "     |:_/ |     ",
    "    //   \\ \\    ",
    "   (|     | )   ",
    "  /'\\_   _/`\\   ",
    "  \\___)=(___/   ",
]

def blok(teks):
    baris = [""] * 5
    for ch in teks:
        if ch in FONT:
            for i in range(5):
                baris[i] += FONT[ch][i].replace("#","█") + " "
    return baris

def banner():
    os.system("clear")
    cols = shutil.get_terminal_size((50,20)).columns
    print()
    for line in TUX:
        print(C["y"] + C["B"] + line.center(cols) + C["x"])
        time.sleep(0.05)
    print()
    teks = ["MR414N-ID"]
    if sum(len(FONT.get(c,["     "])[0])+1 for c in teks[0] if c in FONT) > cols:
        teks = ["MR414N","-ID"]
    warna = ["r","y","g","c","m"]
    for t in teks:
        for i, row in enumerate(blok(t)):
            print(C[warna[i%len(warna)]] + C["B"] + row.center(cols) + C["x"])
            time.sleep(0.05)
    print()
    print(C["c"] + C["B"] + "BY. MR414N-ID".center(cols) + C["x"])
    print(C["d"] + f"OSINT Tools  •  {len(parse_sites())} situs".center(cols) + C["x"])
    print(C["d"] + ("─" * min(cols,44)).center(cols) + C["x"])
    print()

SHOW_GAGAL = False

def cari(username, simpan=True, koleksi=None):
    sites = parse_sites()
    total = len(sites)
    sukses = []
    selesai = 0
    cols = shutil.get_terminal_size((50,20)).columns
    print(C["y"] + f"[*] Mencari '{username}' di {total} situs...\n" + C["x"])

    def progres():
        print(f"\r{C['d']}[{selesai}/{total}] sedang dicek...{C['x']}", end="", flush=True)

    with ThreadPoolExecutor(max_workers=40) as ex:
        futures = {ex.submit(cek_situs, n, p, username): n for n, p in sites.items()}
        try:
            for f in as_completed(futures):
                selesai += 1
                try:
                    nama, link, ada = f.result()
                except Exception:
                    nama, link, ada = futures[f], "", False
                if ada:
                    print(f"\r\033[K{C['g']}[sukses]{C['x']} {nama}: {link}", flush=True)
                    sukses.append((nama, link))
                elif SHOW_GAGAL:
                    print(f"\r\033[K{C['r']}[gagal]{C['x']} {nama}", flush=True)
                progres()
        except KeyboardInterrupt:
            for fu in futures:
                fu.cancel()
            raise

    sukses.sort(key=lambda x: x[0])
    garis = "=" * min(cols,44)
    print("\r\033[K", end="")
    print(f"\n{C['c']}{garis}{C['x']}")
    print(f"{C['g']}{C['B']}Searching selesai sukses [ {len(sukses)} situs ]{C['x']}")
    print(f"{C['d']}(dari {total} situs yang dicek){C['x']}")
    print(f"{C['c']}{garis}{C['x']}")
    if sukses:
        for nama, link in sukses:
            print(f"{C['y']}{nama}{C['x']} : {link}")
        print(f"{C['c']}{garis}{C['x']}")
        if simpan:
            with open(f"hasil_{username}.txt","w",encoding="utf-8") as fh:
                fh.write(f"Searching selesai sukses [ {len(sukses)} situs ]\n")
                fh.write("\n".join(f"{n} : {l}" for n, l in sukses) + "\n")
            print(f"{C['g']}Tersimpan di hasil_{username}.txt{C['x']}")
    else:
        print(f"{C['r']}Tidak ada akun ditemukan.{C['x']}")
    if koleksi is not None:
        koleksi[username] = list(sukses)
    return len(sukses)

def normalize_name(nama):
    nama = nama.lower().strip()
    for ch in [",",".","-","_"]:
        nama = nama.replace(ch," ")
    return [p for p in nama.split() if p and len(p) > 1]

def generate_candidates(nama, max_candidates=40):
    parts = normalize_name(nama)
    if not parts:
        return []
    candidates = set()
    if len(parts) == 1:
        base = parts[0]
        candidates.update([base, f"{base}1", f"{base}01", f"{base}88",
                           f"{base}99", f"{base}.id", f"{base}_id",
                           f"_{base}", f"{base}_", f"the{base}", f"real{base}"])
    else:
        first, last = parts[0], parts[-1]
        joined = "".join(parts)
        candidates.update([joined, f"{first}{last}", f"{last}{first}",
                           f"{first}.{last}", f"{first}_{last}", f"{first}-{last}",
                           f"{first[:3]}{last}", f"{first}{last[:3]}",
                           f"{first[0]}{last}"])
        if len(parts) > 2:
            mid = "".join(parts[1:-1])
            candidates.add(f"{first}{mid}{last}")
        for n in ["01","88","99","123","1"]:
            candidates.update([f"{joined}{n}", f"{first}{last}{n}"])
        for p in ["the","real","mr"]:
            candidates.add(f"{p}{joined}")
        candidates.update([f"{joined}.id", f"{joined}_id", f"{joined}official"])
    return list(candidates)[:max_candidates]

def region_in_username(username, region):
    if not region:
        return False
    region_lower = region.lower().strip()
    aliases = REGION_ALIASES.get(region_lower, [region_lower])
    ul = username.lower()
    return any(a in ul for a in aliases)

def check_candidate_on_sites(candidate, sites_subset, max_workers=15):
    found = []
    def _check(item):
        name, pattern = item
        ada, link = ada_akun(name, pattern, candidate)
        return name, link, ada
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(_check, item): item for item in sites_subset.items()}
        for f in as_completed(futures):
            try:
                name, link, ada = f.result()
                if ada:
                    found.append((name, link))
            except Exception:
                pass
    return found

def tanya_yn(pesan):
    while True:
        j = input(f"{C['y']}{pesan} (y/n) {C['w']}>> {C['x']}").strip().lower()
        if j in ("y","ya"):
            return True
        if j in ("n","t","tidak"):
            return False
        print(f"{C['r']}Ketik y atau n.{C['x']}")

def baca_file_username(path):
    path = os.path.expanduser(path.strip().strip("\"'"))
    if not os.path.isfile(path) and os.path.isfile(path + ".txt"):
        path += ".txt"
    if not os.path.isfile(path):
        return None
    daftar, dilewati, lihat = [], 0, set()
    with open(path, encoding="utf-8", errors="ignore") as fh:
        for baris in fh:
            u = baris.strip().lstrip("@")
            if not u:
                continue
            if " " in u or "\t" in u or u.lower() in lihat:
                dilewati += 1
                continue
            lihat.add(u.lower())
            daftar.append(u)
    return daftar, dilewati

def input_manual():
    daftar = []
    while True:
        u = input(f"\n{C['g']}[?] Masukkan username >> {C['x']}").strip().lstrip("@")
        if not u or " " in u:
            print(f"{C['r']}Username tidak valid, coba lagi.{C['x']}")
        elif u.lower() in [x.lower() for x in daftar]:
            print(f"{C['y']}'{u}' sudah ada di daftar.{C['x']}")
        else:
            daftar.append(u)
            print(f"{C['g']}[+] Ditambahkan: {u}  (total {len(daftar)}){C['x']}")
        while True:
            lanjut = input(
                f"{C['y']}[1]{C['x']} Tambah username lagi  "
                f"{C['y']}[2]{C['x']} Selesai & lanjut cari {C['w']}>> {C['x']}"
            ).strip()
            if lanjut in ("1","2"):
                break
            print(f"{C['r']}Ketik 1 atau 2.{C['x']}")
        if lanjut == "2":
            return daftar

def cari_dari_nama(nama, region):
    sites = parse_sites()
    candidates = generate_candidates(nama)
    if not candidates:
        print(f"{C['r']}Nama tidak valid.{C['x']}")
        return
    priority_patterns = {n: sites[n] for n in PRIORITY_SITES if n in sites}
    indo_patterns = {n: sites[n] for n in INDONESIAN_SITES if n in sites} if region else {}
    found = {}
    for i, cand in enumerate(candidates, 1):
        print(f"\r{C['d']}[{i}/{len(candidates)}] cek: {cand}...{C['x']}   ", end="", flush=True)
        social = check_candidate_on_sites(cand, priority_patterns)
        if social:
            found[cand] = {"sites": social, "region_match": region_in_username(cand, region), "indonesian": False}
            print(f"\r\033[K{C['g']}[+] {cand} → {', '.join(s[0] for s in social)}{C['x']}")
    print("\r\033[K", end="")
    if not found:
        print(f"{C['r']}Tidak ada kandidat ditemukan.{C['x']}")
        return
    if region and indo_patterns:
        for cand in list(found.keys()):
            indo = check_candidate_on_sites(cand, indo_patterns, max_workers=8)
            if indo:
                found[cand]["sites"].extend(indo)
                found[cand]["indonesian"] = True
    def skor(item):
        _, info = item
        s = len(info["sites"])
        if info["region_match"]: s += 10
        if info["indonesian"]: s += 5
        return -s
    sorted_found = sorted(found.items(), key=skor)
    cols = shutil.get_terminal_size((50,20)).columns
    garis = "=" * min(cols,44)
    print(f"\n{C['c']}{garis}{C['x']}")
    print(f"{C['g']}{C['B']}KANDIDAT DITEMUKAN [ {len(sorted_found)} username ]{C['x']}")
    print(f"{C['c']}{garis}{C['x']}")
    for i, (cand, info) in enumerate(sorted_found, 1):
        tags = []
        if info["region_match"]: tags.append(f"{C['g']}[daerah✓]{C['x']}")
        if info["indonesian"]: tags.append(f"{C['c']}[indo✓]{C['x']}")
        sites_str = ", ".join(s[0] for s in info["sites"][:4])
        print(f"{C['y']}{i:2}.{C['x']} {C['w']}{cand:<22}{C['x']} {C['d']}({sites_str}){C['x']} {' '.join(tags)}")
    print(f"{C['c']}{garis}{C['x']}")
    try:
        choice = input(f"\n{C['y']}Pilih nomor untuk cek 500 situs (contoh: 1,2,3 / all / skip) >> {C['x']}").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return
    if not choice or choice == "skip":
        return
    if choice == "all":
        selected = [c for c, _ in sorted_found]
    else:
        try:
            idxs = [int(x.strip())-1 for x in choice.split(",")]
            selected = [sorted_found[i][0] for i in idxs if 0 <= i < len(sorted_found)]
        except Exception:
            selected = []
    for u in selected:
        cari(u)

def cari_gabungan(nama, region):
    sites = parse_sites()
    candidates = generate_candidates(nama)
    if not candidates:
        print(f"{C['r']}Nama tidak valid.{C['x']}")
        return
    priority_patterns = {n: sites[n] for n in PRIORITY_SITES if n in sites}
    found = {}
    for i, cand in enumerate(candidates, 1):
        print(f"\r{C['d']}[{i}/{len(candidates)}] cek: {cand}...{C['x']}   ", end="", flush=True)
        social = check_candidate_on_sites(cand, priority_patterns)
        if social:
            found[cand] = social
            print(f"\r\033[K{C['g']}[+] {cand} → {', '.join(s[0] for s in social)}{C['x']}")
    print("\r\033[K")
    if not found:
        print(f"{C['r']}Tidak ada kandidat ditemukan.{C['x']}")
        return
    for u in found:
        cari(u)

def cari_massal():
    print(f"\n{C['c']}{C['B']}CARI USERNAME MASSAL{C['x']}")
    print(f"{C['y']}[1]{C['x']} Dari file txt")
    print(f"{C['y']}[2]{C['x']} Input manual")
    print(f"{C['y']}[b]{C['x']} Kembali")
    try:
        pilih = input(f"\n{C['g']}[?] Pilih >> {C['x']}").strip().lower()
        if pilih == "1":
            fn = input(f"{C['g']}[?] Nama file txt >> {C['x']}").strip()
            if not fn: return
            data = baca_file_username(fn)
            if data is None:
                print(f"{C['r']}File tidak ditemukan.{C['x']}")
                return
            daftar, dilewati = data
        elif pilih == "2":
            daftar = input_manual()
        else:
            return
        if not daftar:
            print(f"{C['r']}Tidak ada username.{C['x']}")
            return
        hasil = {}
        try:
            for i, u in enumerate(daftar, 1):
                print(f"\n{C['y']}{C['B']}[{i}/{len(daftar)}] USERNAME: {u}{C['x']}")
                cari(u, simpan=False, koleksi=hasil)
        except (KeyboardInterrupt, EOFError):
            print(f"\n{C['r']}Dibatalkan.{C['x']}")
        if not hasil: return
        urut = sorted(hasil.items(), key=lambda kv: -len(kv[1]))
        total_jejak = sum(len(v) for v in hasil.values())
        print(f"\n{C['g']}{C['B']}RINGKASAN MASSAL{C['x']}")
        for u, v in urut:
            warna = C["g"] if v else C["r"]
            print(f"{C['y']}{u:<22}{C['x']} : {warna}{C['B']}{len(v)} situs{C['x']}")
        print(f"{C['d']}Total: {len(hasil)} username, {total_jejak} jejak akun{C['x']}")
        if tanya_yn("Simpan hasil?"):
            with open("hasil_massal.txt","w",encoding="utf-8") as fh:
                fh.write("Pencarian massal - BY. MR414N-ID\n")
                for u, v in urut:
                    fh.write(f"\n=== {u} ({len(v)} situs) ===\n")
                    for nama_situs, link in sorted(v):
                        fh.write(f"{nama_situs} : {link}\n")
            print(f"{C['g']}Tersimpan di hasil_massal.txt{C['x']}")
    except (EOFError, KeyboardInterrupt):
        print()

# ─────────────────────────────────────────────
# MENU
# ─────────────────────────────────────────────

def tampilkan_menu():
    print(f"{C['y']}[1]{C['x']}  Username Finder       {C['d']}(500+ situs){C['x']}")
    print(f"{C['y']}[2]{C['x']}  Name → Username       {C['d']}(+ filter daerah){C['x']}")
    print(f"{C['y']}[3]{C['x']}  Gabungan full auto    {C['d']}(nama → 500 situs){C['x']}")
    print(f"{C['y']}[4]{C['x']}  Cari Massal           {C['d']}(file txt / manual){C['x']}")
    print(f"{C['y']}[5]{C['x']}  Breach Check          {C['d']}(email → HIBP + LeakCheck){C['x']}")
    print(f"{C['y']}[6]{C['x']}  Phone Lookup          {C['d']}(nomor → 40+ platform){C['x']}")
    print(f"{C['y']}[7]{C['x']}  Profile Scraper       {C['d']}(dari username){C['x']}")
    print(f"{C['y']}[8]{C['x']}  Avatar pHash          {C['d']}(korelasi foto profil){C['x']}")
    print(f"{C['y']}[9]{C['x']}  Google Dorking        {C['d']}(auto query){C['x']}")
    print(f"{C['y']}[10]{C['x']} Wayback Check         {C['d']}(lacak akun lama){C['x']}")
    print(f"{C['y']}[11]{C['x']} Full OSINT            {C['d']}(gabungan semua fitur){C['x']}")
    print(f"{C['y']}[q]{C['x']}  Keluar")

def main():
    # load proxy di background
    try:
        from threading import Thread
        Thread(target=load_proxies, daemon=True).start()
    except Exception:
        pass

    banner()

    if len(sys.argv) > 1:
        username = sys.argv[1].strip().lstrip("@")
        if username:
            cari(username)
        return

    while True:
        print(f"\n{C['c']}{C['B']}MENU UTAMA{C['x']}")
        tampilkan_menu()
        try:
            pilih = input(f"\n{C['g']}[?] Pilih >> {C['x']}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if pilih in ("q","quit","exit"):
            break
        elif pilih == "1":
            try:
                username = input(f"\n{C['g']}[?] Masukkan username >> {C['x']}").strip().lstrip("@")
            except (EOFError, KeyboardInterrupt):
                break
            if username:
                cari(username)
        elif pilih == "2":
            try:
                nama = input(f"\n{C['g']}[?] Masukkan nama lengkap >> {C['x']}").strip()
                if not nama: continue
                region = input(f"{C['g']}[?] Daerah (kosongkan jika tidak perlu) >> {C['x']}").strip()
            except (EOFError, KeyboardInterrupt):
                break
            cari_dari_nama(nama, region)
        elif pilih == "3":
            try:
                nama = input(f"\n{C['g']}[?] Masukkan nama lengkap >> {C['x']}").strip()
                if not nama: continue
                region = input(f"{C['g']}[?] Daerah >> {C['x']}").strip()
            except (EOFError, KeyboardInterrupt):
                break
            cari_gabungan(nama, region)
        elif pilih == "4":
            cari_massal()
        elif pilih == "5":
            try:
                email = input(f"\n{C['g']}[?] Masukkan email >> {C['x']}").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if email:
                breach_check(email)
        elif pilih == "6":
            try:
                nomor = input(f"\n{C['g']}[?] Masukkan nomor HP >> {C['x']}").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if nomor:
                phone_lookup(nomor)
        elif pilih == "7":
            try:
                username = input(f"\n{C['g']}[?] Masukkan username >> {C['x']}").strip().lstrip("@")
            except (EOFError, KeyboardInterrupt):
                break
            if username:
                koleksi = {}
                cari(username, simpan=False, koleksi=koleksi)
                found = [s for s, _ in koleksi.get(username, [])]
                profile_scraper(username, found)
        elif pilih == "8":
            try:
                username = input(f"\n{C['g']}[?] Masukkan username >> {C['x']}").strip().lstrip("@")
            except (EOFError, KeyboardInterrupt):
                break
            if username:
                koleksi = {}
                cari(username, simpan=False, koleksi=koleksi)
                found = [s for s, _ in koleksi.get(username, [])]
                profiles = profile_scraper(username, found)
                avatar_phash(profiles)
        elif pilih == "9":
            try:
                username = input(f"\n{C['g']}[?] Masukkan username >> {C['x']}").strip().lstrip("@")
            except (EOFError, KeyboardInterrupt):
                break
            if username:
                google_dork(username)
        elif pilih == "10":
            try:
                username = input(f"\n{C['g']}[?] Masukkan username >> {C['x']}").strip().lstrip("@")
            except (EOFError, KeyboardInterrupt):
                break
            if username:
                koleksi = {}
                cari(username, simpan=False, koleksi=koleksi)
                found = [s for s, _ in koleksi.get(username, [])]
                wayback_check(username, found)
        elif pilih == "11":
            full_osint()
        else:
            print(f"{C['r']}Pilihan tidak valid.{C['x']}")

    print(C["c"] + "\nTerima kasih!  —  BY. MR414N-ID" + C["x"])

if __name__ == "__main__":
    main()
