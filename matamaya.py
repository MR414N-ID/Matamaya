#!/usr/bin/env python3
"""
OSINT Tools — Username Finder + Breach Check + Phone Lookup + Profile Scraper
             + Avatar pHash + Google Dorking + Wayback Check + Social Graph
             + NIK Search + BPJS Search + Full OSINT
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
    from stem import Signal
    from stem.control import Controller
    TOR_OK = True
except ImportError:
    TOR_OK = False

# ─────────────────────────────────────────────
# API KEYS
# ─────────────────────────────────────────────

RAPIDAPI_KEY  = "227f756b50mshbfbd6f18ab7cf41p17b064jsn0ade51590aae"
LEAKCHECK_KEY = "MASUKKAN_API_KEY_LEAKCHECK"

# ─────────────────────────────────────────────
# PROXY & HEADERS
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

proxy_pool  = []
proxy_index = 0

def load_proxies():
    global proxy_pool
    for src in FREE_PROXY_SOURCES:
        try:
            r = requests.get(src, timeout=10)
            proxy_pool.extend([p.strip() for p in r.text.strip().splitlines() if p.strip()])
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

def session_headers():
    return {"User-Agent": random.choice(UA_LIST), "Accept-Language": "en-US,en;q=0.9"}

def safe_get(url, timeout=12, use_proxy=True):
    proxies = None
    if use_proxy:
        if TOR_OK:
            proxies = {"http": "socks5://127.0.0.1:9050", "https": "socks5://127.0.0.1:9050"}
        elif proxy_pool:
            proxies = get_proxy()
    try:
        return requests.get(url, headers=session_headers(), timeout=timeout,
                            allow_redirects=True, proxies=proxies)
    except Exception:
        try:
            return requests.get(url, headers=session_headers(), timeout=timeout, allow_redirects=True)
        except Exception:
            return None

def safe_post(url, data=None, json=None, headers=None, timeout=12):
    h = session_headers()
    if headers:
        h.update(headers)
    try:
        return requests.post(url, data=data, json=json, headers=h, timeout=timeout)
    except Exception:
        return None

# ─────────────────────────────────────────────
# SITES — 500+ (LENGKAP DARI FILE ASLI)
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
observable https://observablehq.com/@{u}
huggingface https://huggingface.co/{u}
launchpad https://launchpad.net/~{u}
wikipedia https://en.wikipedia.org/wiki/User:{u}
roblox https://www.roblox.com/user.aspx?username={u}
steam https://steamcommunity.com/id/{u}
twitch https://www.twitch.tv/{u}
chesscom https://www.chess.com/member/{u}
lichess https://lichess.org/@/{u}
namemc https://namemc.com/profile/{u}
itchio https://{u}.itch.io
gamejolt https://gamejolt.com/@{u}
speedrun https://www.speedrun.com/users/{u}
osu https://osu.ppy.sh/users/{u}
newgrounds https://{u}.newgrounds.com
kongregate https://www.kongregate.com/accounts/{u}
trakt https://trakt.tv/users/{u}
myanimelist https://myanimelist.net/profile/{u}
anilist https://anilist.co/user/{u}
kitsu https://kitsu.io/users/{u}
gog https://www.gog.com/u/{u}
planetminecraft https://www.planetminecraft.com/member/{u}/
bandcamp https://{u}.bandcamp.com
soundcloud https://soundcloud.com/{u}
spotify https://open.spotify.com/user/{u}
lastfm https://www.last.fm/user/{u}
mixcloud https://www.mixcloud.com/{u}/
reverbnation https://www.reverbnation.com/{u}
audiomack https://audiomack.com/{u}
genius https://genius.com/{u}
discogs https://www.discogs.com/user/{u}
smule https://www.smule.com/{u}
youtube https://www.youtube.com/@{u}
vimeo https://vimeo.com/{u}
dailymotion https://www.dailymotion.com/{u}
rumble https://rumble.com/user/{u}
odysee https://odysee.com/@{u}
kick https://kick.com/{u}
deviantart https://www.deviantart.com/{u}
behance https://www.behance.net/{u}
dribbble https://dribbble.com/{u}
artstation https://www.artstation.com/{u}
500px https://500px.com/p/{u}
unsplash https://unsplash.com/@{u}
pexels https://www.pexels.com/@{u}
pixabay https://pixabay.com/users/{u}/
imgur https://imgur.com/user/{u}
giphy https://giphy.com/{u}
fiverr https://www.fiverr.com/{u}
freelancer https://www.freelancer.com/u/{u}
99designs https://99designs.com/profiles/{u}
wattpad https://www.wattpad.com/user/{u}
ao3 https://archiveofourown.org/users/{u}
fanfiction https://www.fanfiction.net/~{u}
letterboxd https://letterboxd.com/{u}/
ebay https://www.ebay.com/usr/{u}
etsy https://www.etsy.com/shop/{u}
poshmark https://poshmark.com/closet/{u}
depop https://www.depop.com/{u}/
tokopedia https://www.tokopedia.com/{u}
shopee https://shopee.co.id/{u}
bukalapak https://www.bukalapak.com/u/{u}
kaskus https://www.kaskus.co.id/@{u}
kompasiana https://www.kompasiana.com/{u}
trakteer https://trakteer.id/{u}
saweria https://saweria.co/{u}
sociabuzz https://sociabuzz.com/{u}
likee https://likee.video/@{u}
hackernews https://news.ycombinator.com/user?id={u}
producthunt https://www.producthunt.com/@{u}
disqus https://disqus.com/by/{u}/
gravatar https://gravatar.com/{u}
keybase https://keybase.io/{u}
pastebin https://pastebin.com/u/{u}
slideshare https://www.slideshare.net/{u}
scribd https://www.scribd.com/{u}
issuu https://issuu.com/{u}
instructables https://www.instructables.com/member/{u}/
hackaday https://hackaday.io/{u}
thingiverse https://www.thingiverse.com/{u}
sketchfab https://sketchfab.com/{u}
printables https://www.printables.com/@{u}
grailed https://www.grailed.com/{u}
steamgifts https://www.steamgifts.com/user/{u}
clubhouse https://www.clubhouse.com/@{u}
fandom https://community.fandom.com/wiki/User:{u}
foursquare https://foursquare.com/{u}
duolingo https://www.duolingo.com/profile/{u}
codecademy https://www.codecademy.com/profiles/{u}
freecodecamp https://www.freecodecamp.org/{u}
tryhackme https://tryhackme.com/p/{u}
rootme https://www.root-me.org/{u}
vsco https://vsco.co/{u}
ifunny https://ifunny.co/user/{u}
9gag https://9gag.com/u/{u}
wykop https://www.wykop.pl/ludzie/{u}
pikabu https://pikabu.ru/@{u}
habr https://habr.com/en/users/{u}/
nairaland https://www.nairaland.com/{u}
hubpages https://hubpages.com/@{u}
askfm https://ask.fm/{u}
curiouscat https://curiouscat.live/{u}
tellonym https://tellonym.me/{u}
stocktwits https://stocktwits.com/{u}
tradingview https://www.tradingview.com/u/{u}/
opensea https://opensea.io/{u}
hackerearth https://www.hackerearth.com/@{u}
topcoder https://www.topcoder.com/members/{u}
exercism https://exercism.org/profiles/{u}
codechef https://www.codechef.com/users/{u}
atcoder https://atcoder.jp/users/{u}
spoj https://www.spoj.com/users/{u}/
devpost https://devpost.com/{u}
figma https://www.figma.com/@{u}
indiehackers https://www.indiehackers.com/{u}
wellfound https://wellfound.com/u/{u}
flipboard https://flipboard.com/@{u}
scratch https://scratch.mit.edu/users/{u}/
trello https://trello.com/{u}
myfitnesspal https://www.myfitnesspal.com/profile/{u}
alltrails https://www.alltrails.com/members/{u}
tinder https://tinder.com/@{u}
smugmug https://{u}.smugmug.com
xing https://www.xing.com/profile/{u}
gettr https://gettr.com/user/{u}
truthsocial https://truthsocial.com/@{u}
minds https://www.minds.com/{u}
gab https://gab.com/{u}
mewe https://mewe.com/i/{u}
musescore https://musescore.com/{u}
bandlab https://www.bandlab.com/{u}
younow https://www.younow.com/{u}
ravelry https://www.ravelry.com/people/{u}
cults3d https://cults3d.com/en/users/{u}
myminifactory https://www.myminifactory.com/users/{u}
boardgamegeek https://boardgamegeek.com/user/{u}
geocaching https://www.geocaching.com/p/?u={u}
wordnik https://www.wordnik.com/users/{u}
coroflot https://www.coroflot.com/{u}
contently https://{u}.contently.com
muckrack https://muckrack.com/{u}
qiita https://qiita.com/{u}
zenn https://zenn.dev/{u}
note https://note.com/{u}
ameblo https://ameblo.jp/{u}
velog https://velog.io/@{u}
tistory https://{u}.tistory.com
csdn https://blog.csdn.net/{u}
lobsters https://lobste.rs/u/{u}
slashdot https://slashdot.org/~{u}
arduino https://forum.arduino.cc/u/{u}
fosstodon https://fosstodon.org/@{u}
mstdn https://mstdn.social/@{u}
mastodononline https://mastodon.online/@{u}
infosecexchange https://infosec.exchange/@{u}
hachyderm https://hachyderm.io/@{u}
techhub https://techhub.social/@{u}
mastoto https://mas.to/@{u}
mastodonworld https://mastodon.world/@{u}
universeodon https://universeodon.com/@{u}
sigmoid https://sigmoid.social/@{u}
pawoo https://pawoo.net/@{u}
misskeyio https://misskey.io/@{u}
chaossocial https://chaos.social/@{u}
tchncs https://social.tchncs.de/@{u}
floss https://floss.social/@{u}
techlgbt https://tech.lgbt/@{u}
vivaldisocial https://social.vivaldi.net/@{u}
octodon https://octodon.social/@{u}
mastodonart https://mastodon.art/@{u}
gamedevplace https://mastodon.gamedev.place/@{u}
rubysocial https://ruby.social/@{u}
phpcsocial https://phpc.social/@{u}
indieweb https://indieweb.social/@{u}
mathstodon https://mathstodon.xyz/@{u}
scholarsocial https://scholar.social/@{u}
journahost https://journa.host/@{u}
cim https://c.im/@{u}
tootcommunity https://toot.community/@{u}
nocsocial https://noc.social/@{u}
mastodoncloud https://mastodon.cloud/@{u}
socialcoop https://social.coop/@{u}
kolektiva https://kolektiva.social/@{u}
pixelfed https://pixelfed.social/{u}
lemmyworld https://lemmy.world/u/{u}
lemmyml https://lemmy.ml/u/{u}
beehaw https://beehaw.org/u/{u}
itjustworks https://sh.itjust.works/u/{u}
lemmee https://lemm.ee/u/{u}
programmingdev https://programming.dev/u/{u}
feddit https://feddit.de/u/{u}
lemmyca https://lemmy.ca/u/{u}
slrpnk https://slrpnk.net/u/{u}
tildes https://tildes.net/user/{u}
codeberg https://codeberg.org/{u}
gitea https://gitea.com/{u}
sourcehut https://sr.ht/~{u}/
cratesio https://crates.io/users/{u}
rubygems https://rubygems.org/profiles/{u}
packagist https://packagist.org/users/{u}/
nuget https://www.nuget.org/profiles/{u}
metacpan https://metacpan.org/author/{u}
jsfiddle https://jsfiddle.net/user/{u}/
stackblitz https://stackblitz.com/@{u}
codesandbox https://codesandbox.io/u/{u}
githubgist https://gist.github.com/{u}
anaconda https://anaconda.org/{u}
githubio https://{u}.github.io
gitlabio https://{u}.gitlab.io
netlify https://{u}.netlify.app
vercel https://{u}.vercel.app
cloudflarepages https://{u}.pages.dev
herokuapp https://{u}.herokuapp.com
surge https://{u}.surge.sh
webflow https://{u}.webflow.io
hackmd https://hackmd.io/@{u}
codeproject https://www.codeproject.com/Members/{u}
leanpub https://leanpub.com/u/{u}
hackster https://www.hackster.io/{u}
tinkercad https://www.tinkercad.com/users/{u}
gamedevnet https://www.gamedev.net/{u}/
hackernoon https://hackernoon.com/u/{u}
dicoding https://www.dicoding.com/users/{u}
datacamp https://www.datacamp.com/portfolio/{u}
geeksforgeeks https://auth.geeksforgeeks.org/user/{u}
leetcodecn https://leetcode.cn/u/{u}/
kattis https://open.kattis.com/users/{u}
dmoj https://dmoj.ca/user/{u}
toph https://toph.co/p/{u}
vjudge https://vjudge.net/user/{u}
bugcrowd https://bugcrowd.com/{u}
intigriti https://app.intigriti.com/profile/{u}
yeswehack https://yeswehack.com/hunters/{u}
v2ex https://www.v2ex.com/member/{u}
discoursemeta https://meta.discourse.org/u/{u}
discusspython https://discuss.python.org/u/{u}
cloudflarecommunity https://community.cloudflare.com/u/{u}
freecodecampforum https://forum.freecodecamp.org/u/{u}
mozillaforum https://discourse.mozilla.org/u/{u}
rustusers https://users.rust-lang.org/u/{u}
pytorchforum https://discuss.pytorch.org/u/{u}
openaicommunity https://community.openai.com/u/{u}
obsidianforum https://forum.obsidian.md/u/{u}
homeassistant https://community.home-assistant.io/u/{u}
kotlinforum https://discuss.kotlinlang.org/u/{u}
hashicorpforum https://discuss.hashicorp.com/u/{u}
gitlabforum https://forum.gitlab.com/u/{u}
letsencrypt https://community.letsencrypt.org/u/{u}
elasticforum https://discuss.elastic.co/u/{u}
manjaroforum https://forum.manjaro.org/u/{u}
nixosdiscourse https://discourse.nixos.org/u/{u}
snapcraftforum https://forum.snapcraft.io/u/{u}
flyiocommunity https://community.fly.io/u/{u}
ansibleforum https://forum.ansible.com/u/{u}
julialang https://discourse.julialang.org/u/{u}
godotforum https://forum.godotengine.org/u/{u}
ionicforum https://forum.ionicframework.com/u/{u}
bubbleforum https://forum.bubble.io/u/{u}
n8ncommunity https://community.n8n.io/u/{u}
huggingfaceforum https://discuss.huggingface.co/u/{u}
streamlitforum https://discuss.streamlit.io/u/{u}
rcloneforum https://forum.rclone.org/u/{u}
openwrtforum https://forum.openwrt.org/u/{u}
weheartit https://weheartit.com/{u}
ello https://ello.co/{u}
writeas https://write.as/{u}/
microblog https://micro.blog/{u}
beehiiv https://{u}.beehiiv.com
buttondown https://buttondown.email/{u}
tinyletter https://tinyletter.com/{u}
bearblog https://{u}.bearblog.dev
weebly https://{u}.weebly.com
jimdo https://{u}.jimdofree.com
neocities https://{u}.neocities.org
nekoweb https://{u}.nekoweb.org
tildeclub https://tilde.club/~{u}/
dreamwidth https://{u}.dreamwidth.org
insanejournal https://{u}.insanejournal.com
typepad https://{u}.typepad.com
overblog https://{u}.over-blog.com
skyrock https://{u}.skyrock.com
bloggse https://{u}.blogg.se
wikidot https://{u}.wikidot.com
livedoor https://blog.livedoor.jp/{u}/
hatena https://profile.hatena.ne.jp/{u}/
hatenablog https://{u}.hatenablog.com
fc2blog https://{u}.blog.fc2.com
lofter https://{u}.lofter.com
cnblogs https://www.cnblogs.com/{u}/
douban https://www.douban.com/people/{u}/
zhihu https://www.zhihu.com/people/{u}
naverblog https://blog.naver.com/{u}
booth https://{u}.booth.pm
fanbox https://{u}.fanbox.cc
skeb https://skeb.jp/@{u}
dzen https://dzen.ru/{u}
mailru https://my.mail.ru/mail/{u}/
drive2 https://www.drive2.ru/users/{u}/
flru https://www.fl.ru/users/{u}/
kwork https://kwork.ru/user/{u}
authortoday https://author.today/u/{u}
proza https://proza.ru/avtor/{u}
stihi https://stihi.ru/avtor/{u}
livelib https://www.livelib.ru/reader/{u}
bitchute https://www.bitchute.com/channel/{u}/
brighteon https://www.brighteon.com/channels/{u}
locals https://{u}.locals.com
kumparan https://kumparan.com/{u}
karyakarsa https://karyakarsa.com/{u}
bagibagi https://bagibagi.co/{u}
tako https://tako.id/{u}
goodreads https://www.goodreads.com/{u}
librarything https://www.librarything.com/profile/{u}
storygraph https://app.thestorygraph.com/profile/{u}
inkitt https://www.inkitt.com/{u}
tapas https://tapas.io/{u}
comicvine https://comicvine.gamespot.com/profile/{u}/
tmdb https://www.themoviedb.org/u/{u}
mydramalist https://mydramalist.com/profile/{u}
animeplanet https://www.anime-planet.com/users/{u}
shikimori https://shikimori.one/{u}
metacritic https://www.metacritic.com/user/{u}/
giantbomb https://www.giantbomb.com/profile/{u}/
gamefaqs https://gamefaqs.gamespot.com/community/{u}
backloggd https://www.backloggd.com/u/{u}/
exophase https://www.exophase.com/user/{u}/
psnprofiles https://psnprofiles.com/{u}
faceit https://www.faceit.com/en/players/{u}
rateyourmusic https://rateyourmusic.com/~{u}
modrinth https://modrinth.com/user/{u}
curseforge https://www.curseforge.com/members/{u}/projects
moddb https://www.moddb.com/members/{u}
indiedb https://www.indiedb.com/members/{u}
minecraftforum https://www.minecraftforum.net/members/{u}
moxfield https://www.moxfield.com/users/{u}
archidekt https://archidekt.com/u/{u}
deckbox https://deckbox.org/users/{u}
pokemonshowdown https://pokemonshowdown.com/users/{u}
humblebundle https://www.humblebundle.com/user/{u}
trovo https://trovo.live/s/{u}
dlive https://dlive.tv/{u}
bigo https://www.bigo.tv/user/{u}
picarto https://picarto.tv/{u}
audius https://audius.co/{u}
hearthis https://hearthis.at/{u}/
musicbrainz https://musicbrainz.org/user/{u}
setlistfm https://www.setlist.fm/user/{u}
listenbrainz https://listenbrainz.org/user/{u}/
ultimateguitar https://www.ultimate-guitar.com/u/{u}
8tracks https://8tracks.com/{u}
audiotool https://www.audiotool.com/user/{u}/
imgbb https://{u}.imgbb.com
tenor https://tenor.com/users/{u}
zenfolio https://{u}.zenfolio.com
viewbug https://www.viewbug.com/member/{u}
pixieset https://{u}.pixieset.com
exposure https://{u}.exposure.co
awwwards https://www.awwwards.com/{u}/
carbonmade https://{u}.carbonmade.com
cargo https://{u}.cargo.site
adobeportfolio https://{u}.myportfolio.com
tilda https://{u}.tilda.ws
strikingly https://{u}.mystrikingly.com
polycount https://polycount.com/profile/{u}
grabcad https://grabcad.com/{u}
cgtrader https://www.cgtrader.com/{u}
freepik https://www.freepik.com/author/{u}
flaticon https://www.flaticon.com/authors/{u}
iconfinder https://www.iconfinder.com/{u}
nounproject https://thenounproject.com/{u}/
canva https://www.canva.com/{u}
speakerdeck https://speakerdeck.com/{u}
yumpu https://www.yumpu.com/user/{u}
houzz https://www.houzz.com/user/{u}
envato https://themeforest.net/user/{u}
codecanyon https://codecanyon.net/user/{u}
audiojungle https://audiojungle.net/user/{u}
videohive https://videohive.net/user/{u}
graphicriver https://graphicriver.net/user/{u}
creativemarket https://creativemarket.com/{u}
redbubble https://www.redbubble.com/people/{u}
society6 https://society6.com/{u}
zazzle https://www.zazzle.com/mbr/{u}
teepublic https://www.teepublic.com/user/{u}
threadless https://{u}.threadless.com
dreamstime https://www.dreamstime.com/{u}_info
cameo https://www.cameo.com/{u}
throne https://throne.com/{u}
subscribestar https://www.subscribestar.com/{u}
liberapay https://liberapay.com/{u}
opencollective https://opencollective.com/{u}
githubsponsors https://github.com/sponsors/{u}
paypalme https://www.paypal.me/{u}
cashapp https://cash.app/${u}
venmo https://venmo.com/{u}
payhip https://payhip.com/{u}
sellfy https://sellfy.com/{u}
storenvy https://{u}.storenvy.com
bigcartel https://{u}.bigcartel.com
bonanza https://www.bonanza.com/booths/{u}
reverb https://reverb.com/shop/{u}
carousell https://id.carousell.com/u/{u}/
skillshare https://www.skillshare.com/en/profile/{u}
kickstarter https://www.kickstarter.com/profile/{u}
kiva https://www.kiva.org/lender/{u}
flavorsme https://flavors.me/{u}
lnkbio https://lnk.bio/{u}
campsitebio https://campsite.bio/{u}
soloto https://solo.to/{u}
allmylinks https://allmylinks.com/{u}
taplink https://taplink.cc/{u}
hoobe https://hoo.be/{u}
withkoji https://withkoji.com/@{u}
directme https://direct.me/{u}
tapbio https://tap.bio/@{u}
stanstore https://stan.store/{u}
linkpop https://linkpop.com/{u}
litlink https://lit.link/{u}
potofu https://potofu.me/{u}
crunchbase https://www.crunchbase.com/person/{u}
f6s https://www.f6s.com/{u}
steemit https://steemit.com/@{u}
peakd https://peakd.com/@{u}
warpcast https://warpcast.com/{u}
rarible https://rarible.com/{u}
foundation https://foundation.app/@{u}
superrare https://superrare.com/{u}
coinmarketcap https://coinmarketcap.com/community/profile/{u}/
etoro https://www.etoro.com/people/{u}
couchsurfing https://www.couchsurfing.com/people/{u}
memrise https://community.memrise.com/user/{u}/
quizlet https://quizlet.com/{u}
brilliant https://brilliant.org/profile/{u}/
tripadvisor https://www.tripadvisor.com/Profile/{u}
untappd https://untappd.com/user/{u}
beeradvocate https://www.beeradvocate.com/community/members/{u}
wikimediacommons https://commons.wikimedia.org/wiki/User:{u}
wikidata https://www.wikidata.org/wiki/User:{u}
archiveorg https://archive.org/details/@{u}
openstreetmap https://www.openstreetmap.org/user/{u}
mapillary https://www.mapillary.com/app/user/{u}
wikiloc https://www.wikiloc.com/wikiloc/user.do?name={u}
wikibooks https://en.wikibooks.org/wiki/User:{u}
wikiquote https://en.wikiquote.org/wiki/User:{u}
"""

NOT_FOUND = {
    "tiktok":    ["Couldn't find this account", "couldn\\u2019t find this account"],
    "instagram": ["Page Not Found", "isn't available"],
    "x":         ["This account doesn", "doesn\\u2019t exist"],
    "facebook":  ["This content isn't available", "Page Not Found"],
    "reddit":    ["Sorry, nobody on Reddit goes by that name", "page not found"],
    "twitch":    ["Sorry. Unless you've got a time machine"],
    "telegram":  ["tgme_page_extra\"></div>"],
    "roblox":    ["Page cannot be found", "Page not found"],
    "linktree":  ["The page you\u2019re looking for doesn", "doesn't exist"],
}
GENERIC_NOT_FOUND = [
    "page not found", "user not found", "profile not found", "account not found",
    "doesn't exist", "does not exist", "no such user", "couldn't find",
    "halaman tidak ditemukan", "pengguna tidak ditemukan",
]

PRIORITY_SITES   = ["instagram","facebook","tiktok","x","threads","telegram","github","linkedin"]
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

BREACH_LINKS = {
    "mangatoon":  "https://breachforums.st/Thread-Mangatoon",
    "senoai":     "https://breachforums.st/Thread-Seno-AI",
    "tokopedia":  "https://breachforums.st/Thread-Tokopedia",
    "adobe":      "https://breachforums.st/Thread-Adobe",
    "linkedin":   "https://breachforums.st/Thread-LinkedIn",
    "canva":      "https://breachforums.st/Thread-Canva",
    "bukalapak":  "https://breachforums.st/Thread-Bukalapak",
    "dukcapil":   "https://breachforums.st/Thread-Dukcapil",
}

def breach_check(email):
    print(f"\n{C['c']}[*] Breach Check: {email}{C['x']}")
    hasil = []

    # 1. HIBP scrape tanpa API key
    try:
        r = requests.get(
            f"https://haveibeenpwned.com/unifiedsearch/{email}",
            headers={**session_headers(), "Accept": "application/json"},
            timeout=12
        )
        if r.status_code == 200:
            data = r.json()
            for b in data.get("Breaches", []):
                nama      = b.get("Name", "")
                tahun     = b.get("BreachDate", "")[:4]
                data_bocor = ", ".join(b.get("DataClasses", []))
                link      = BREACH_LINKS.get(nama.lower().replace(" ",""), "https://haveibeenpwned.com")
                hasil.append({"nama": nama, "tahun": tahun, "data": data_bocor,
                               "link": link, "password": None})
                print(f"{C['r']}[BREACH]{C['x']} Email pernah tersebar di {C['y']}{nama}{C['x']}")
                print(f"  Tahun      : {tahun}")
                print(f"  Data bocor : {data_bocor}")
    except Exception as e:
        print(f"{C['y']}[!] HIBP: {e}{C['x']}")

    # 2. BreachDirectory via RapidAPI
    try:
        r = requests.get(
            "https://breachdirectory.p.rapidapi.com/",
            headers={
                "X-RapidAPI-Key":  RAPIDAPI_KEY,
                "X-RapidAPI-Host": "breachdirectory.p.rapidapi.com",
            },
            params={"func": "auto", "term": email},
            timeout=12
        )
        if r.status_code == 200:
            data = r.json()
            for item in data.get("result", []):
                src  = item.get("sources", ["Unknown"])[0]
                pw   = item.get("password", "")
                sha1 = item.get("sha1", "")
                # cari apakah breach ini sudah ada di list
                match = next((h for h in hasil if h["nama"].lower() == src.lower()), None)
                if match:
                    if pw:
                        match["password"] = pw
                else:
                    hasil.append({
                        "nama": src, "tahun": "", "data": "password",
                        "link": BREACH_LINKS.get(src.lower(), "https://breachdirectory.org"),
                        "password": pw or None
                    })
                    if pw:
                        print(f"{C['g']}[BD]{C['x']} {src} — password: {C['g']}{pw}{C['x']}")
    except Exception as e:
        print(f"{C['y']}[!] BreachDirectory: {e}{C['x']}")

    # 3. LeakCheck
    if LEAKCHECK_KEY and LEAKCHECK_KEY != "99aed655fc285391368f32a9d1bb6d67c01a0a18":
        try:
            r = requests.get(
                f"https://leakcheck.io/api/public?key={LEAKCHECK_KEY}&check={email}",
                timeout=12
            )
            if r.status_code == 200:
                data = r.json()
                for item in data.get("result", []):
                    pw  = item.get("password")
                    src = item.get("source", "")
                    match = next((h for h in hasil if h["nama"].lower() == src.lower()), None)
                    if match and pw:
                        match["password"] = pw
        except Exception:
            pass

    # output
    garis = "=" * 44
    print(f"\n{C['c']}{garis}{C['x']}")
    if not hasil:
        print(f"{C['r']}Tidak ada breach ditemukan.{C['x']}")
    for b in hasil:
        print(f"\n{C['y']}[{b['nama']}]{C['x']}" + (f" — {b['tahun']}" if b['tahun'] else ""))
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

def fmt_nomor(nomor):
    nomor = nomor.strip().replace(" ","").replace("-","")
    if nomor.startswith("08"):
        nomor = "+62" + nomor[1:]
    elif nomor.startswith("62"):
        nomor = "+" + nomor
    elif not nomor.startswith("+"):
        nomor = "+62" + nomor
    return nomor

def cek_wa(nomor):
    # WhatsApp: cek via klik.me wrapper
    no_bersih = nomor.replace("+","").replace(" ","")
    try:
        r = requests.get(
            f"https://api.whatsapp.com/send?phone={no_bersih}",
            headers=session_headers(), timeout=10, allow_redirects=True
        )
        if r and "invalid" not in r.text.lower() and "phone number" not in r.text.lower():
            return True
    except Exception:
        pass
    return False

def cek_telegram(nomor):
    try:
        r = safe_get(f"https://t.me/{nomor}", timeout=10)
        if r and r.status_code == 200 and "tgme_page_extra\"></div>" not in r.text:
            return True
    except Exception:
        pass
    return False

def cek_wa_link(nomor):
    no = nomor.replace("+","")
    try:
        r = requests.get(f"https://wa.me/{no}",
                         headers=session_headers(), timeout=10, allow_redirects=True)
        if r and r.status_code == 200 and "open.whatsapp.com" in r.url:
            return True
    except Exception:
        pass
    return False

def phone_lookup(nomor_raw):
    nomor = fmt_nomor(nomor_raw)
    no_bersih = nomor.replace("+","")
    print(f"\n{C['c']}[*] Phone Lookup: {nomor}{C['x']}")

    hasil = {"sosmed": [], "ecommerce": [], "fintech": [], "lain": []}

    checks = [
        # (kategori, nama, fungsi_cek)
        ("sosmed",    "WhatsApp",   lambda: cek_wa_link(nomor)),
        ("sosmed",    "Telegram",   lambda: cek_telegram(nomor)),
        ("sosmed",    "Line",       lambda: _http_ok(f"https://line.me/ti/p/~{no_bersih}", 200)),
        ("ecommerce", "Tokopedia",  lambda: _probe_json(
            "https://accounts.tokopedia.com/otp/c/page",
            json_data={"msisdn": nomor, "otpType": "116"},
            find="success")),
        ("ecommerce", "Shopee",     lambda: _probe_json(
            "https://shopee.co.id/api/v2/user/login",
            json_data={"phone": no_bersih},
            find="phone_used")),
        ("ecommerce", "Bukalapak",  lambda: _probe_json(
            "https://api.bukalapak.com/v2/users/check",
            json_data={"phone": nomor},
            find="available\":false")),
        ("ecommerce", "Lazada",     lambda: _probe_json(
            "https://member.lazada.co.id/user/api/checkPhoneNumber",
            json_data={"mobilePhone": nomor},
            find="exist")),
        ("fintech",   "GoPay/Gojek",lambda: _probe_json(
            f"https://goid.go-jek.com/v3/register/check",
            json_data={"phone_number": nomor},
            find="registered")),
        ("fintech",   "OVO",        lambda: _probe_json(
            "https://api.ovo.id/v2/user/check",
            json_data={"phone": nomor},
            find="registered")),
        ("fintech",   "Dana",       lambda: _probe_json(
            "https://m.dana.id/m/portal/v1/account/check",
            json_data={"phone": nomor},
            find="REGISTERED")),
        ("fintech",   "LinkAja",    lambda: _probe_json(
            "https://api.linkaja.id/v1/user/check",
            json_data={"msisdn": nomor},
            find="registered")),
        ("fintech",   "ShopeePay",  lambda: _probe_json(
            "https://shopee.co.id/api/v2/user/login",
            json_data={"phone": no_bersih},
            find="shopeepay")),
        ("lain",      "Grab",       lambda: _probe_json(
            f"https://p.grabtaxi.com/api/passenger/v2/profile/phone/{no_bersih}",
            find="user")),
        ("lain",      "Traveloka",  lambda: _probe_json(
            "https://www.traveloka.com/api/v2/account/checkIdentity",
            json_data={"type":"PHONE","identity": nomor},
            find="REGISTERED")),
    ]

    for kategori, nama, fn in checks:
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

def _http_ok(url, expected_status=200):
    try:
        r = safe_get(url, timeout=10)
        return r and r.status_code == expected_status
    except Exception:
        return False

def _probe_json(url, json_data=None, find=None):
    try:
        if json_data:
            r = safe_post(url, json=json_data, timeout=10)
        else:
            r = safe_get(url, timeout=10)
        if not r:
            return False
        if find and find.lower() in r.text.lower():
            return True
        return False
    except Exception:
        return False

# ─────────────────────────────────────────────
# PROFILE SCRAPER
# ─────────────────────────────────────────────

def scrape_github(username):
    try:
        r = safe_get(f"https://api.github.com/users/{username}")
        if r and r.status_code == 200:
            d = r.json()
            return {"nama": d.get("name"), "email": d.get("email"),
                    "lokasi": d.get("location"), "company": d.get("company"),
                    "bio": d.get("bio"), "avatar": d.get("avatar_url")}
    except Exception:
        pass
    return {}

def scrape_instagram(username):
    try:
        r = safe_get(f"https://www.instagram.com/{username}/?__a=1&__d=dis")
        if r and r.status_code == 200:
            d = r.json().get("graphql",{}).get("user",{})
            return {"nama": d.get("full_name"), "bio": d.get("biography"),
                    "follower": d.get("edge_followed_by",{}).get("count"),
                    "avatar": d.get("profile_pic_url_hd")}
    except Exception:
        pass
    return {}

def scrape_twitter(username):
    try:
        r = safe_get(f"https://api.twitter.com/2/users/by/username/{username}",
                     timeout=10)
        if r and r.status_code == 200:
            d = r.json().get("data",{})
            return {"nama": d.get("name"), "bio": d.get("description"),
                    "avatar": d.get("profile_image_url")}
    except Exception:
        pass
    return {}

def profile_scraper(username, found_sites):
    print(f"\n{C['c']}[*] Profile Scraper: {username}{C['x']}")
    profiles = {}
    scrapers = {"github": scrape_github, "instagram": scrape_instagram, "x": scrape_twitter}
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
        print(f"{C['y']}[!] pip install imagehash Pillow{C['x']}")
        return
    print(f"\n{C['c']}[*] Avatar pHash Analysis{C['x']}")
    hashes = {}
    for site, data in profiles.items():
        url = data.get("avatar")
        if url:
            h = get_phash(url)
            if h:
                hashes[site] = h
    sites = list(hashes.keys())
    for i in range(len(sites)):
        for j in range(i+1, len(sites)):
            jarak = hashes[sites[i]] - hashes[sites[j]]
            if jarak < 10:
                label = "identik" if jarak == 0 else "sangat mirip"
                print(f"{C['g']}[MATCH]{C['x']} {sites[i]} ↔ {sites[j]} — jarak {jarak} ({label})")

# ─────────────────────────────────────────────
# GOOGLE DORKING
# ─────────────────────────────────────────────

DORK_QUERIES = [
    '"{u}" site:pastebin.com',
    '"{u}" filetype:pdf',
    '"{u}" intext:password',
    '"{u}" site:github.com',
    '"{u}" site:linkedin.com',
    '"{u}" email',
    '"{u}" phone OR nomor',
    '"{u}" site:kaskus.co.id',
    '"@{u}"',
    '"{u}" -site:instagram.com -site:twitter.com',
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
            links = [l for l in links if "duckduckgo" not in l and "duckduck" not in l][:3]
            if links:
                print(f"\n  {C['y']}Query:{C['x']} {q}")
                for l in links:
                    print(f"    {C['g']}→{C['x']} {l}")
                    hasil_dork.append({"query": q, "link": l})
            time.sleep(1.5)
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
            r = safe_get(f"https://archive.org/wayback/available?url={url}",
                         timeout=12, use_proxy=False)
            if not r:
                continue
            snap = r.json().get("archived_snapshots",{}).get("closest",{})
            if snap.get("available"):
                ts    = snap.get("timestamp","")
                wb_url = snap.get("url","")
                print(f"{C['g']}  [ARCHIVED]{C['x']} {site} — {ts[:4]}")
                print(f"    {wb_url}")
                hasil_wb.append({"site": site, "tahun": ts[:4], "url": wb_url})
            else:
                print(f"{C['d']}  [no archive] {site}{C['x']}")
        except Exception:
            pass
    return hasil_wb

# ─────────────────────────────────────────────
# SOCIAL GRAPH
# ─────────────────────────────────────────────

def social_graph(username, found_sites):
    print(f"\n{C['c']}[*] Social Graph: {username}{C['x']}")
    koneksi = {}

    # GitHub followers/following
    if "github" in found_sites:
        try:
            r = safe_get(f"https://api.github.com/users/{username}/followers?per_page=10")
            if r and r.status_code == 200:
                for u in r.json():
                    login = u.get("login","")
                    koneksi[login] = koneksi.get(login, {"platform": [], "count": 0})
                    koneksi[login]["platform"].append("github-follower")
                    koneksi[login]["count"] += 1
            r2 = safe_get(f"https://api.github.com/users/{username}/following?per_page=10")
            if r2 and r2.status_code == 200:
                for u in r2.json():
                    login = u.get("login","")
                    koneksi[login] = koneksi.get(login, {"platform": [], "count": 0})
                    koneksi[login]["platform"].append("github-following")
                    koneksi[login]["count"] += 1
        except Exception:
            pass

    # tampilkan
    if koneksi:
        garis = "=" * 44
        print(f"\n{C['c']}{garis}{C['x']}")
        print(f"{C['g']}{C['B']}KONEKSI DITEMUKAN [{len(koneksi)}]{C['x']}")
        print(f"{C['c']}{garis}{C['x']}")
        for nama_k, info in sorted(koneksi.items(), key=lambda x: -x[1]["count"])[:20]:
            platform_str = ", ".join(set(info["platform"]))
            print(f"  {C['y']}{nama_k:<20}{C['x']} — {platform_str}")
    else:
        print(f"{C['d']}  Tidak ada koneksi publik ditemukan.{C['x']}")

    return koneksi

# ─────────────────────────────────────────────
# NIK SEARCH
# ─────────────────────────────────────────────

def nik_search():
    print(f"\n{C['c']}{C['B']}NIK SEARCH — dari nama{C['x']}")
    try:
        nama  = input(f"{C['g']}[?] Nama lengkap  >> {C['x']}").strip()
        kota  = input(f"{C['g']}[?] Kota (Enter skip) >> {C['x']}").strip()
    except (EOFError, KeyboardInterrupt):
        return []

    if not nama:
        return []

    print(f"\n{C['y']}[*] Mencari NIK untuk: {nama}{C['x']}")
    kandidat = []

    # BreachDirectory by nama
    try:
        r = requests.get(
            "https://breachdirectory.p.rapidapi.com/",
            headers={
                "X-RapidAPI-Key":  RAPIDAPI_KEY,
                "X-RapidAPI-Host": "breachdirectory.p.rapidapi.com",
            },
            params={"func": "auto", "term": nama},
            timeout=12
        )
        if r.status_code == 200:
            data = r.json()
            for item in data.get("result", []):
                # filter field yang relevan
                nik     = item.get("nik") or item.get("id_number","")
                tgl     = item.get("tanggal_lahir") or item.get("dob","")
                alamat  = item.get("alamat") or item.get("address","")
                jk      = item.get("jenis_kelamin") or item.get("gender","")
                nama_db = item.get("nama") or item.get("name","")
                if not nik:
                    continue
                if kota and kota.lower() not in alamat.lower():
                    continue
                kandidat.append({
                    "nik": nik, "nama": nama_db, "tgl": tgl,
                    "alamat": alamat, "jk": jk
                })
    except Exception as e:
        print(f"{C['y']}[!] BreachDirectory: {e}{C['x']}")

    # LeakCheck fallback
    if not kandidat and LEAKCHECK_KEY != "MASUKKAN_API_KEY_LEAKCHECK":
        try:
            r = requests.get(
                f"https://leakcheck.io/api/public?key={LEAKCHECK_KEY}&check={nama}&type=name",
                timeout=12
            )
            if r.status_code == 200:
                for item in r.json().get("result", []):
                    nik = item.get("nik","")
                    if not nik:
                        continue
                    kandidat.append({
                        "nik": nik,
                        "nama": item.get("name",""),
                        "tgl": item.get("dob",""),
                        "alamat": item.get("address",""),
                        "jk": item.get("gender","")
                    })
        except Exception:
            pass

    # output
    garis = "=" * 44
    print(f"\n{C['c']}{garis}{C['x']}")
    if not kandidat:
        print(f"{C['r']}Tidak ada NIK ditemukan untuk nama '{nama}'.{C['x']}")
        print(f"{C['d']}(Data mungkin tidak ter-index di breach database){C['x']}")
        print(f"{C['c']}{garis}{C['x']}")
        return []

    print(f"{C['g']}{C['B']}HASIL NIK SEARCH — {len(kandidat)} kandidat{C['x']}")
    print(f"{C['c']}{garis}{C['x']}")
    for i, k in enumerate(kandidat, 1):
        print(f"\n{C['y']}[{i}]{C['x']} NIK    : {C['w']}{k['nik']}{C['x']}")
        print(f"     Nama   : {k['nama']}")
        print(f"     TTL    : {k['tgl']}")
        print(f"     Alamat : {k['alamat']}")
        print(f"     JK     : {k['jk']}")
    print(f"\n{C['c']}{garis}{C['x']}")

    # tawaran chain ke BPJS
    try:
        chain = input(f"{C['y']}Chain ke BPJS Search? (nomor / skip) >> {C['x']}").strip()
        if chain.isdigit():
            idx = int(chain) - 1
            if 0 <= idx < len(kandidat):
                k = kandidat[idx]
                bpjs_search(k["nik"], k["tgl"])
    except (EOFError, KeyboardInterrupt):
        pass

    return kandidat

# ─────────────────────────────────────────────
# BPJS SEARCH
# ─────────────────────────────────────────────

def bpjs_search(nik=None, tgl_lahir=None):
    print(f"\n{C['c']}{C['B']}BPJS SEARCH{C['x']}")
    try:
        if not nik:
            nik      = input(f"{C['g']}[?] NIK          >> {C['x']}").strip()
        if not tgl_lahir:
            tgl_lahir = input(f"{C['g']}[?] Tgl lahir (YYYY-MM-DD) >> {C['x']}").strip()
    except (EOFError, KeyboardInterrupt):
        return

    if not nik or not tgl_lahir:
        print(f"{C['r']}NIK dan tanggal lahir wajib diisi.{C['x']}")
        return

    print(f"\n{C['y']}[*] Query BPJS via CHIKA untuk NIK: {nik}{C['x']}")

    # Simulasi CHIKA WhatsApp via request ke endpoint publik
    hasil_bpjs = {}
    try:
        # endpoint publik PASTI BPJS
        r = requests.post(
            "https://pasti.bpjs-kesehatan.go.id/cek/",
            data={"nik": nik, "tanggal_lahir": tgl_lahir},
            headers={**session_headers(), "Content-Type": "application/x-www-form-urlencoded"},
            timeout=15
        )
        if r and r.status_code == 200:
            body = r.text
            # parse nama
            nama_match = re.search(r'Nama[^:]*:\s*([^\n<]+)', body)
            status_match = re.search(r'Status[^:]*:\s*([^\n<]+)', body)
            kelas_match = re.search(r'Kelas[^:]*:\s*([^\n<]+)', body)
            fktp_match = re.search(r'FKTP[^:]*:\s*([^\n<]+)', body)
            no_bpjs_match = re.search(r'No[^:]*BPJS[^:]*:\s*([^\n<]+)', body)

            if nama_match:
                hasil_bpjs["nama"]     = nama_match.group(1).strip()
            if status_match:
                hasil_bpjs["status"]   = status_match.group(1).strip()
            if kelas_match:
                hasil_bpjs["kelas"]    = kelas_match.group(1).strip()
            if fktp_match:
                hasil_bpjs["fktp"]     = fktp_match.group(1).strip()
            if no_bpjs_match:
                hasil_bpjs["no_bpjs"]  = no_bpjs_match.group(1).strip()
    except Exception as e:
        print(f"{C['y']}[!] PASTI endpoint: {e}{C['x']}")

    garis = "=" * 44
    print(f"\n{C['c']}{garis}{C['x']}")
    print(f"{C['g']}{C['B']}HASIL BPJS SEARCH{C['x']}")
    print(f"{C['c']}{garis}{C['x']}")

    if hasil_bpjs:
        for k, v in hasil_bpjs.items():
            print(f"  {k:<10}: {C['w']}{v}{C['x']}")
    else:
        print(f"{C['r']}Data tidak ditemukan atau endpoint terblokir captcha.{C['x']}")
        print(f"{C['d']}Coba manual: https://pasti.bpjs-kesehatan.go.id/cek/{C['x']}")

    print(f"{C['c']}{garis}{C['x']}")

# ─────────────────────────────────────────────
# FULL OSINT
# ─────────────────────────────────────────────

def full_osint():
    print(f"\n{C['c']}{C['B']}FULL OSINT{C['x']}")
    print(f"{C['d']}(Enter untuk skip){C['x']}\n")
    try:
        username = input(f"{C['g']}[?] Username  >> {C['x']}").strip().lstrip("@")
        email    = input(f"{C['g']}[?] Email     >> {C['x']}").strip()
        nomor    = input(f"{C['g']}[?] Nomor HP  >> {C['x']}").strip()
    except (EOFError, KeyboardInterrupt):
        return

    laporan = {}

    if username:
        print(f"\n{C['y']}{C['B']}[1/7] USERNAME FINDER{C['x']}")
        koleksi = {}
        cari(username, simpan=False, koleksi=koleksi)
        found_sites = [s for s, _ in koleksi.get(username, [])]
        laporan["found_sites"] = found_sites

        print(f"\n{C['y']}{C['B']}[2/7] PROFILE SCRAPER{C['x']}")
        profiles = profile_scraper(username, found_sites)
        laporan["profiles"] = profiles

        print(f"\n{C['y']}{C['B']}[3/7] AVATAR pHASH{C['x']}")
        avatar_phash(profiles)

        print(f"\n{C['y']}{C['B']}[4/7] GOOGLE DORKING{C['x']}")
        laporan["dorks"] = google_dork(username)

        print(f"\n{C['y']}{C['B']}[5/7] WAYBACK CHECK{C['x']}")
        laporan["wayback"] = wayback_check(username, found_sites)

        print(f"\n{C['y']}{C['B']}[6/7] SOCIAL GRAPH{C['x']}")
        laporan["social"] = social_graph(username, found_sites)

    if email:
        print(f"\n{C['y']}{C['B']}[7a/7] BREACH CHECK{C['x']}")
        laporan["breach"] = breach_check(email)

    if nomor:
        print(f"\n{C['y']}{C['B']}[7b/7] PHONE LOOKUP{C['x']}")
        laporan["phone"], _ = phone_lookup(nomor)

    # laporan final
    garis = "=" * 44
    print(f"\n{C['c']}{C['B']}{garis}{C['x']}")
    print(f"{C['g']}{C['B']}LAPORAN OSINT LENGKAP{C['x']}")
    print(f"{C['c']}{garis}{C['x']}")
    if username:
        print(f"{C['y']}Target     :{C['x']} {username}")
        print(f"{C['y']}Platform   :{C['x']} {len(laporan.get('found_sites',[]))} ditemukan")
    if email:
        print(f"{C['y']}Email      :{C['x']} {email}")
        print(f"{C['y']}Breach     :{C['x']} {len(laporan.get('breach',[]))} breach")
    if nomor:
        print(f"{C['y']}Nomor HP   :{C['x']} {fmt_nomor(nomor)}")

    # simpan
    try:
        nama_file = f"osint_{username or email or nomor}.txt"
        with open(nama_file, "w", encoding="utf-8") as fh:
            fh.write(f"LAPORAN OSINT — BY. MR414N-ID\n")
            fh.write(f"Target: {username or email or nomor}\n\n")
            if laporan.get("found_sites"):
                fh.write("=== PLATFORM ===\n")
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
                fh.write("\n=== DORK ===\n")
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
# CORE — fitur lama tidak diubah
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
        username = username.replace("_","-")
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
    for teks in NOT_FOUND.get(nama,[]) + GENERIC_NOT_FOUND:
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
    "r":"\033[91m","g":"\033[92m","y":"\033[93m","b":"\033[94m",
    "m":"\033[95m","c":"\033[96m","w":"\033[97m","d":"\033[90m",
    "x":"\033[0m", "B":"\033[1m",
}

FONT = {
    "M":["#   #","## ##","# # #","#   #","#   #"],
    "R":["#### ","#   #","#### ","#  # ","#   #"],
    "4":["#  # ","#  # ","#####","   # ","   # "],
    "1":["  #  "," ##  ","  #  ","  #  "," ### "],
    "N":["#   #","##  #","# # #","#  ##","#   #"],
    "-":["     ","     "," ### ","     ","     "],
    "I":["###"," # "," # "," # ","###"],
    "D":["#### ","#   #","#   #","#   #","#### "],
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
    return any(a in username.lower() for a in aliases)

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
        if j in ("y","ya"): return True
        if j in ("n","t","tidak"): return False
        print(f"{C['r']}Ketik y atau n.{C['x']}")

def baca_file_username(path):
    path = os.path.expanduser(path.strip().strip("\"'"))
    if not os.path.isfile(path) and os.path.isfile(path+".txt"):
        path += ".txt"
    if not os.path.isfile(path):
        return None
    daftar, dilewati, lihat = [], 0, set()
    with open(path, encoding="utf-8", errors="ignore") as fh:
        for baris in fh:
            u = baris.strip().lstrip("@")
            if not u: continue
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
            print(f"{C['r']}Username tidak valid.{C['x']}")
        elif u.lower() in [x.lower() for x in daftar]:
            print(f"{C['y']}'{u}' sudah ada.{C['x']}")
        else:
            daftar.append(u)
            print(f"{C['g']}[+] Ditambahkan: {u} (total {len(daftar)}){C['x']}")
        while True:
            lanjut = input(f"{C['y']}[1]{C['x']} Tambah  {C['y']}[2]{C['x']} Selesai >> ").strip()
            if lanjut in ("1","2"): break
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
    print(f"{C['g']}{C['B']}KANDIDAT [{len(sorted_found)} username]{C['x']}")
    print(f"{C['c']}{garis}{C['x']}")
    for i, (cand, info) in enumerate(sorted_found, 1):
        tags = []
        if info["region_match"]: tags.append(f"{C['g']}[daerah✓]{C['x']}")
        if info["indonesian"]: tags.append(f"{C['c']}[indo✓]{C['x']}")
        sites_str = ", ".join(s[0] for s in info["sites"][:4])
        print(f"{C['y']}{i:2}.{C['x']} {C['w']}{cand:<22}{C['x']} {C['d']}({sites_str}){C['x']} {' '.join(tags)}")
    print(f"{C['c']}{garis}{C['x']}")
    try:
        choice = input(f"\n{C['y']}Pilih nomor cek 500 situs (1,2,3 / all / skip) >> {C['x']}").strip().lower()
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
            daftar, _ = data
        elif pilih == "2":
            daftar = input_manual()
        else:
            return
        if not daftar:
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
        print(f"{C['d']}Total: {len(hasil)} username, {total_jejak} jejak{C['x']}")
        if tanya_yn("Simpan hasil?"):
            with open("hasil_massal.txt","w",encoding="utf-8") as fh:
                fh.write("Pencarian massal - BY. MR414N-ID\n")
                for u, v in urut:
                    fh.write(f"\n=== {u} ({len(v)} situs) ===\n")
                    for ns, lk in sorted(v):
                        fh.write(f"{ns} : {lk}\n")
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
    print(f"{C['y']}[4]{C['x']}  Cari Massal           {C['d']}(file / manual){C['x']}")
    print(f"{C['y']}[5]{C['x']}  Breach Check          {C['d']}(HIBP + BD + LC){C['x']}")
    print(f"{C['y']}[6]{C['x']}  Phone Lookup          {C['d']}(40+ platform){C['x']}")
    print(f"{C['y']}[7]{C['x']}  Profile Scraper       {C['d']}(dari username){C['x']}")
    print(f"{C['y']}[8]{C['x']}  Avatar pHash          {C['d']}(korelasi foto){C['x']}")
    print(f"{C['y']}[9]{C['x']}  Google Dorking        {C['d']}(auto query){C['x']}")
    print(f"{C['y']}[10]{C['x']} Wayback Check         {C['d']}(lacak akun lama){C['x']}")
    print(f"{C['y']}[11]{C['x']} Social Graph          {C['d']}(peta koneksi){C['x']}")
    print(f"{C['y']}[12]{C['x']} NIK Search            {C['d']}(nama → NIK){C['x']}")
    print(f"{C['y']}[13]{C['x']} BPJS Search           {C['d']}(NIK → status BPJS){C['x']}")
    print(f"{C['y']}[14]{C['x']} Full OSINT            {C['d']}(gabungan semua){C['x']}")
    print(f"{C['y']}[q]{C['x']}  Keluar")

def main():
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
                u = input(f"\n{C['g']}[?] Username >> {C['x']}").strip().lstrip("@")
            except (EOFError, KeyboardInterrupt):
                break
            if u: cari(u)
        elif pilih == "2":
            try:
                nama = input(f"\n{C['g']}[?] Nama lengkap >> {C['x']}").strip()
                if not nama: continue
                region = input(f"{C['g']}[?] Daerah >> {C['x']}").strip()
            except (EOFError, KeyboardInterrupt):
                break
            cari_dari_nama(nama, region)
        elif pilih == "3":
            try:
                nama = input(f"\n{C['g']}[?] Nama lengkap >> {C['x']}").strip()
                if not nama: continue
                region = input(f"{C['g']}[?] Daerah >> {C['x']}").strip()
            except (EOFError, KeyboardInterrupt):
                break
            cari_gabungan(nama, region)
        elif pilih == "4":
            cari_massal()
        elif pilih == "5":
            try:
                email = input(f"\n{C['g']}[?] Email >> {C['x']}").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if email: breach_check(email)
        elif pilih == "6":
            try:
                nomor = input(f"\n{C['g']}[?] Nomor HP >> {C['x']}").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if nomor: phone_lookup(nomor)
        elif pilih == "7":
            try:
                u = input(f"\n{C['g']}[?] Username >> {C['x']}").strip().lstrip("@")
            except (EOFError, KeyboardInterrupt):
                break
            if u:
                koleksi = {}
                cari(u, simpan=False, koleksi=koleksi)
                found = [s for s, _ in koleksi.get(u, [])]
                profile_scraper(u, found)
        elif pilih == "8":
            try:
                u = input(f"\n{C['g']}[?] Username >> {C['x']}").strip().lstrip("@")
            except (EOFError, KeyboardInterrupt):
                break
            if u:
                koleksi = {}
                cari(u, simpan=False, koleksi=koleksi)
                found = [s for s, _ in koleksi.get(u, [])]
                profiles = profile_scraper(u, found)
                avatar_phash(profiles)
        elif pilih == "9":
            try:
                u = input(f"\n{C['g']}[?] Username >> {C['x']}").strip().lstrip("@")
            except (EOFError, KeyboardInterrupt):
                break
            if u: google_dork(u)
        elif pilih == "10":
            try:
                u = input(f"\n{C['g']}[?] Username >> {C['x']}").strip().lstrip("@")
            except (EOFError, KeyboardInterrupt):
                break
            if u:
                koleksi = {}
                cari(u, simpan=False, koleksi=koleksi)
                found = [s for s, _ in koleksi.get(u, [])]
                wayback_check(u, found)
        elif pilih == "11":
            try:
                u = input(f"\n{C['g']}[?] Username >> {C['x']}").strip().lstrip("@")
            except (EOFError, KeyboardInterrupt):
                break
            if u:
                koleksi = {}
                cari(u, simpan=False, koleksi=koleksi)
                found = [s for s, _ in koleksi.get(u, [])]
                social_graph(u, found)
        elif pilih == "12":
            nik_search()
        elif pilih == "13":
            bpjs_search()
        elif pilih == "14":
            full_osint()
        else:
            print(f"{C['r']}Pilihan tidak valid.{C['x']}")

    print(C["c"] + "\nTerima kasih!  —  BY. MR414N-ID" + C["x"])

if __name__ == "__main__":
    main()
