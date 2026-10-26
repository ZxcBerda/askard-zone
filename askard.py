# -*- coding: utf-8 -*-
# Askard Zone // OSINT Tool v13.0 (Fixed Layout)
import os, sys, subprocess, importlib.util, platform, time, random, socket, re, hashlib, threading, zipfile, sqlite3, datetime, json
from pathlib import Path

# --- АВТОУСТАНОВКА ЗАВИСИМОСТЕЙ ---
REQUIRED = {"requests": "requests", "bs4": "beautifulsoup4", "colorama": "colorama", "rarfile": "rarfile"}

def ensure_deps():
    missing = [pkg for mod, pkg in REQUIRED.items() if importlib.util.find_spec(mod) is None]
    if not missing: return
    for flags in ([], ["--break-system-packages"]):
        r = subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", *flags, *missing], capture_output=True)
        if r.returncode == 0: return

ensure_deps()

import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style, init as cinit
import rarfile
cinit(autoreset=True)

# --- ЦВЕТА ---
W = Fore.WHITE
GR = Fore.LIGHTBLACK_EX
LG = Fore.LIGHTWHITE_EX
G = Fore.GREEN
R = Fore.RED
BOLD, RESET = Style.BRIGHT, Style.RESET_ALL

def clear():
    os.system("cls" if platform.system() == "Windows" else "clear")

def pause():
    input(f"\n{GR}  Нажми Enter, чтобы вернуться...{RESET}")

# --- ЛОГОТИП ---
LOGO = [
    "  █████╗ ███████╗██╗  ██╗ █████╗ ██████╗ ██████╗ ",
    " ██╔══██╗██╔════╝██║ ██╔╝██╔══██╗██╔══██╗██╔══██╗",
    " ███████║███████╗█████╔╝ ███████║██████╔╝██║  ██║",
    " ██╔══██║╚════██║██╔═██╗ ██╔══██║██╔══██╗██║  ██║",
    " ██║  ██║███████║██║  ██╗██║  ██║██║  ██║██████╔╝",
    " ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ "
]

LOGO2 = [
    " ███████╗ ██████╗ ███╗   ██╗███████╗",
    " ╚══███╔╝██╔═══██╗████╗  ██║██╔════╝",
    "   ███╔╝ ██║   ██║██╔██╗ ██║█████╗  ",
    "  ███╔╝  ██║   ██║██║╚██╗██║██╔══╝  ",
    " ███████╗╚██████╔╝██║ ╚████║███████╗",
    " ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝"
]

def get_side_panel():
    user = os.getlogin() if hasattr(os, 'getlogin') else "User"
    os_name = platform.system()
    now = datetime.datetime.now().strftime("%H:%M:%S")
    
    return [
        f"{GR}┌──────────────────────────┐{RESET}",
        f"{GR}│{RESET} {LG}System:{RESET}  {W}{os_name:<14}{RESET} {GR}│{RESET}",
        f"{GR}│{RESET} {LG}User:{RESET}    {W}{user:<14}{RESET} {GR}│{RESET}",
        f"{GR}│{RESET} {LG}Time:{RESET}    {W}{now:<14}{RESET} {GR}│{RESET}",
        f"{GR}│{RESET} {LG}Status:{RESET}  {G}Active{RESET}          {GR}│{RESET}",
        f"{GR}└──────────────────────────┘{RESET}"
    ]

def show_banner():
    clear()
    print()
    panel = get_side_panel()
    
    # Выводим логотип и панель
    for i in range(len(LOGO)):
        c1 = LG if i % 2 == 0 else W
        c2 = W if i % 2 == 0 else LG
        line = f"{c1}{BOLD}{LOGO[i]}{RESET}   {c2}{BOLD}{LOGO2[i]}{RESET}"
        
        padding_len = 55 - (len(LOGO[i]) + len(LOGO2[i]) + 3)
        if padding_len < 0: padding_len = 0
        padding = " " * padding_len
        
        if i < len(panel):
            line += padding + panel[i]
        print(line)
        time.sleep(0.05)

    # --- СОВРЕМЕННОЕ МЕНЮ В ОДИН СТОЛБЕЦ ---
    print(f"\n  {GR}===================================================={RESET}")
    print(f"  {W}{BOLD}  ДОСТУПНЫЕ МОДУЛИ:{RESET}")
    print(f"  {GR}===================================================={RESET}")
    
    for k, (v, _) in MENU.items():
        # Красивое форматирование: [ 1 ] Название функции
        if k == "0":
            print(f"  {R}[ {k:>2} ]{RESET} {W}{v}{RESET}")
        else:
            print(f"  {GR}[{RESET} {G}{k:>2}{RESET} {GR}]{RESET} {W}{v}{RESET}")
            
    print(f"  {GR}===================================================={RESET}")
    
    print(f"\n{GR}  thx for using this tool | creator @slitev{RESET}\n")
# --- СПИННЕР ---
class Spinner:
    def __init__(self, msg="Загрузка"):
        self.msg = msg
        self.frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        self.running = False
        self.thread = None
    def _spin(self):
        i = 0
        while self.running:
            sys.stdout.write(f"\r  {GR}{self.frames[i % len(self.frames)]}{RESET} {LG}{self.msg}{RESET}   ")
            sys.stdout.flush()
            time.sleep(0.08)
            i += 1
    def __enter__(self):
        self.running = True
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()
        return self
    def __exit__(self, *args):
        self.running = False
        if self.thread: self.thread.join()
        sys.stdout.write("\r" + " " * (len(self.msg) + 8) + "\r")

# --- ФУНКЦИИ ---

def f_phone():
    clear(); print(f"{W}{BOLD}  [1] Поиск по номеру телефона{RESET}\n")
    ph = input(f"{GR}  Введите номер: {RESET}").strip()
    if not ph: return pause()
    digits = re.sub(r"\D", "", ph)
    print(f"\n  • Номер: {LG}+{digits}{RESET}")
    op = "Россия (МТС/Билайн/Мегафон)" if digits.startswith(("79", "89")) else "Другой регион"
    print(f"  • Оператор: {LG}{op}{RESET}")
    pause()

def f_telegram():
    clear(); print(f"{W}{BOLD}  [2] Поиск по Telegram ID{RESET}\n")
    un = input(f"{GR}  Введите юзернейм (без @): {RESET}").strip().replace("@", "")
    if not un: return pause()
    with Spinner(f"Сканирую t.me/{un}..."):
        try: r = requests.get(f"https://t.me/{un}", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        except: r = None
    if r and r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        t = soup.find("meta", property="og:title")
        d = soup.find("meta", property="og:description")
        print(f"  • Имя: {LG}{t['content'] if t else 'Скрыто'}{RESET}")
        print(f"  • Био: {GR}{d['content'] if d else 'Пусто'}{RESET}")
        print(f"  • Ссылка: {LG}https://t.me/{un}{RESET}")
    else: print(f"  {W}[-] Аккаунт не найден.{RESET}")
    pause()

def f_email():
    clear(); print(f"{W}{BOLD}  [3] Поиск по Email (Утечки){RESET}\n")
    em = input(f"{GR}  Введите Email: {RESET}").strip()
    if not em: return pause()
    with Spinner("Проверяю базы утечек..."):
        try:
            r = requests.get(f"https://api.xposedornot.com/v1/check-email/{em}", timeout=10)
            data = r.json()
        except: data = None
    if data and "breaches" in data and data["breaches"]:
        print(f"  {R}[!] EMAIL НАЙДЕН В УТЕЧКАХ:{RESET}")
        for b in data["breaches"][0]: print(f"    {GR}• {b}{RESET}")
    else: print(f"  {LG}[+] Утечек не найдено.{RESET}")
    pause()

def f_ip():
    clear(); print(f"{W}{BOLD}  [4] Поиск по IP{RESET}\n")
    ip = input(f"{GR}  IP (Enter - свой): {RESET}").strip()
    url = f"http://ip-api.com/json/{ip}" if ip else "http://ip-api.com/json/"
    with Spinner("Запрашиваю геолокацию..."):
        try: r = requests.get(url, timeout=10).json()
        except: r = {}
    if r.get("status") == "fail": print(f"  {W}Ошибка: {r.get('message')}{RESET}")
    elif r:
        print(f"    • IP: {LG}{r.get('query')}{RESET}")
        print(f"    • Страна: {LG}{r.get('country')}{RESET}")
        print(f"    • Город: {LG}{r.get('city')}{RESET}")
    pause()

def f_db():
    clear(); print(f"{W}{BOLD}  [5] Поиск по Локальным БД{RESET}\n")
    q = input(f"{GR}  Введите запрос: {RESET}").strip()
    if not q: return pause()
    db_dir = Path("db")
    if db_dir.exists():
        results = []
        for f in list(db_dir.rglob("*")):
            if f.is_file() and f.suffix in (".txt", ".csv", ".db"):
                try:
                    if f.suffix == ".db":
                        conn = sqlite3.connect(f); cur = conn.cursor()
                        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
                        for t in [x[0] for x in cur.fetchall()]:
                            cur.execute(f"SELECT * FROM {t}")
                            for row in cur.fetchall():
                                if q.lower() in str(row).lower(): results.append(f"[{f.name}] {row}")
                        conn.close()
                    else:
                        with open(f, "r", encoding="utf-8", errors="ignore") as file:
                            for line in file:
                                if q.lower() in line.lower(): results.append(f"[{f.name}] {line.strip()}")
                except: pass
        if results:
            print(f"  {W}[+] Найдено: {len(results)}{RESET}")
            for r in results[:10]: print(f"    {GR}{r}{RESET}")
        else: print(f"  {GR}[-] Ничего не найдено.{RESET}")
    else: print(f"  {GR}Папка db пуста.{RESET}")
    pause()

def f_fio():
    clear(); print(f"{W}{BOLD}  [6] Поиск по ФИО{RESET}\n")
    fio = input(f"{GR}  Введите ФИО: {RESET}").strip()
    if not fio: return pause()
    with Spinner("Ищу в поисковиках..."):
        try:
            r = requests.post("https://html.duckduckgo.com/html/", data={"q": f'"{fio}"'}, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "html.parser")
        except: soup = None
    if soup:
        links = soup.select(".result__a")[:5]
        for a in links: print(f"    {GR}- {a.get_text(strip=True)}{RESET}")
    else: print(f"  {W}Ошибка сети{RESET}")
    pause()

def f_dns():
    clear(); print(f"{W}{BOLD}  [7] DNS Lookup{RESET}\n")
    dom = input(f"{GR}  Домен: {RESET}").strip()
    if not dom: return pause()
    with Spinner("Разрешаю домен..."):
        try: ip = socket.gethostbyname(dom)
        except: ip = None
    if ip: print(f"    • IP: {LG}{ip}{RESET}")
    else: print(f"    {W}Не удалось разрешить домен{RESET}")
    pause()

def f_fake():
    clear(); print(f"{W}{BOLD}  [8] Генератор фейк-инфо{RESET}\n")
    with Spinner("Генерирую..."):
        time.sleep(0.5)
    n = random.choice(["Иван", "Алексей", "Дмитрий"])
    s = random.choice(["Иванов", "Смирнов", "Кузнецов"])
    print(f"    • ФИО: {LG}{s} {n}{RESET}")
    print(f"    • Тел: {LG}+79{random.randint(100000000, 999999999)}{RESET}")
    print(f"    • Email: {LG}{n.lower()}.{s.lower()}@mail.ru{RESET}")
    pause()

def f_pass():
    clear(); print(f"{W}{BOLD}  [9] Генератор паролей{RESET}\n")
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    print(f"    • Пароль: {LG}{''.join(random.choices(chars, k=16))}{RESET}")
    pause()

def f_fssp():
    clear(); print(f"{W}{BOLD}  [10] ФССП (Долги){RESET}\n")
    token = input(f"{GR}  Введите токен ФССП (Enter - инфо): {RESET}").strip()
    if not token:
        print(f"  {W}[!] Получи бесплатно: https://api-ip.fssprus.ru/register{RESET}")
        return pause()
    ln = input(f"{GR}  Фамилия: {RESET}").strip()
    fn = input(f"{GR}  Имя: {RESET}").strip()
    bd = input(f"{GR}  Дата рождения (ДД.ММ.ГГГГ): {RESET}").strip()
    if not ln or not fn or not bd: return pause()
    with Spinner("Ищу долги..."):
        try:
            r = requests.get("https://api-ip.fssprus.ru/api/v1.0/search/physical", params={"token": token, "lastname": ln, "firstname": fn, "birthdate": bd, "region": "0"}, timeout=15)
            data = r.json()
        except: data = None
    if data and data.get("status") == 0 and data.get("result"):
        print(f"  {R}[!] ДОЛГИ НАЙДЕНЫ:{RESET}")
        for t in data["result"]: print(f"    {GR}• {t.get('subject', 'Долг')}: {t.get('sum', 0)} руб.{RESET}")
    else: print(f"  {LG}[+] Долгов не найдено или ошибка.{RESET}")
    pause()

def f_sanctions():
    clear(); print(f"{W}{BOLD}  [11] Санкции (OpenSanctions){RESET}\n")
    key = input(f"{GR}  API-ключ (Enter - инфо): {RESET}").strip()
    if not key:
        print(f"  {W}[!] Получи: https://www.opensanctions.org/account/{RESET}")
        return pause()
    name = input(f"{GR}  Имя (на англ): {RESET}").strip()
    if not name: return pause()
    with Spinner("Проверяю..."):
        try:
            r = requests.post("https://api.opensanctions.org/match/default", json={"queries": {"q1": {"schema": "Person", "properties": {"name": [name]}}}}, headers={"Authorization": f"ApiKey {key}"}, timeout=15)
            data = r.json()
        except: data = None
    if data and "responses" in data:
        res = data["responses"].get("q1", {}).get("results", [])
        if res:
            print(f"  {R}[!] СОВПАДЕНИЯ:{RESET}")
            for i in res[:5]: print(f"    {GR}• {i.get('caption')} (Score: {i.get('score'):.2f}){RESET}")
        else: print(f"  {LG}[+] Совпадений нет.{RESET}")
    else: print(f"  {W}[-] Ошибка ключа.{RESET}")
    pause()

def f_kontragent():
    clear(); print(f"{W}{BOLD}  [12] Контрагенты (ЕГРЮЛ){RESET}\n")
    key = input(f"{GR}  API-ключ (Enter - анонимно): {RESET}").strip()
    inn = input(f"{GR}  ИНН компании: {RESET}").strip()
    if not inn: return pause()
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    with Spinner("Запрашиваю ЕГРЮЛ..."):
        try:
            r = requests.get(f"https://kontragentpro.ru/api/v2/company/{inn}", headers=headers, timeout=15)
            data = r.json()
        except: data = None
    if data and data.get("name"):
        print(f"  {G}[+] НАЙДЕНО:{RESET}")
        print(f"    • Название: {LG}{data.get('name')}{RESET}")
        print(f"    • ОГРН: {LG}{data.get('ogrn')}{RESET}")
    else: print(f"  {W}[-] Не найдено или ошибка.{RESET}")
    pause()

# --- МЕНЮ ---
MENU = {
    "1": ("Поиск по номеру", f_phone),
    "2": ("Поиск по Telegram", f_telegram),
    "3": ("Поиск по Email", f_email),
    "4": ("Поиск по IP", f_ip),
    "5": ("Поиск по БД", f_db),
    "6": ("Поиск по ФИО", f_fio),
    "7": ("DNS Lookup", f_dns),
    "8": ("Генератор фейков", f_fake),
    "9": ("Генератор паролей", f_pass),
    "10": ("ФССП (Долги)", f_fssp),
    "11": ("Санкции", f_sanctions), # Сокращено для ровности
    "12": ("Контрагенты", f_kontragent), # Сокращено для ровности
    "0": ("Выход", None),
}

def main_menu():
    while True:
        show_banner()
        choice = input(f"  {W}[*] Выбрать > {RESET}").strip()
        
        if choice == "0":
            print(f"\n{GR}  Выход...{RESET}")
            break
            
        if choice in MENU:
            name, func = MENU[choice]
            if func: func()
        else:
            print(f"\n{W}  Неверный выбор!{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{GR}Работа завершена.{RESET}")