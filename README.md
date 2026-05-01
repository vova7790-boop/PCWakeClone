# PCWake

Telegram-бот для удалённого включения домашнего ПК через Wake-on-LAN.
Запускается в Termux на Android-телефоне, который находится в той же локальной сети, что и ПК.

## Как это работает

```
Рабочий телефон → Telegram → Домашний телефон (Termux) → WoL пакет (UDP) → ПК
```

## Команды бота

| Команда | Действие |
|---------|----------|
| `/wake` | Отправить Wake-on-LAN пакет — ПК включится |

---

## Установка

### Шаг 1 — Включить Wake-on-LAN на ПК (Windows)

1. Зайти в BIOS/UEFI при загрузке (Del / F2) → найти **Wake on LAN** → включить
2. В Windows: `Диспетчер устройств` → `Сетевые адаптеры` → двойной клик на Ethernet-адаптере
   → вкладка `Управление электропитанием` → поставить галочку **"Разрешить этому устройству выводить компьютер из режима ожидания"**
3. Узнать MAC-адрес ПК: открыть `cmd` → выполнить `ipconfig /all` → найти строку `Физический адрес` для Ethernet-адаптера

### Шаг 2 — Создать Telegram-бота

1. Написать [@BotFather](https://t.me/BotFather) → `/newbot` → придумать имя и username
2. Сохранить выданный **токен**
3. Узнать свой Telegram user_id: написать [@userinfobot](https://t.me/userinfobot) → сохранить `Id`

### Шаг 3 — Установить Termux на домашний телефон

> Устанавливать только из **[F-Droid](https://f-droid.org/)** — версия в Google Play устарела.

Установить два приложения:
- **Termux**
- **Termux:Boot** (для автозапуска при перезагрузке телефона)

### Шаг 4 — Настроить бота в Termux

```bash
# Обновить пакеты
pkg update && pkg upgrade -y

# Установить Python и git
pkg install python git -y

# Установить Termux API (для wake-lock)
pkg install termux-api -y

# Клонировать репозиторий
git clone https://github.com/vova7790-boop/pcwake ~/PCWake
cd ~/PCWake

# Установить зависимости
pip install -r requirements.txt

# Создать файл конфигурации
cp .env.example .env
```

Заполнить `.env`:

```bash
cat > ~/PCWake/.env << 'EOF'
BOT_TOKEN=токен_от_BotFather
ALLOWED_USER_ID=твой_user_id
PC_MAC=хх-хх-хх-хх-хх-хх
PC_IP=192.ххх.х.ххх
EOF
```

### Шаг 5 — Настроить автозапуск (Termux:Boot)

```bash
mkdir -p ~/.termux/boot
cp ~/PCWake/termux-boot/start_bot.sh ~/.termux/boot/start_bot.sh
chmod +x ~/.termux/boot/start_bot.sh
chmod +x ~/PCWake/start.sh
```

Открыть приложение **Termux:Boot** хотя бы один раз, чтобы оно зарегистрировалось в системе.

---

## Запуск

### Для тестирования (бот останавливается при закрытии Termux)

```bash
python ~/PCWake/bot.py
```

### Для постоянной работы с заблокированным экраном

```bash
bash ~/PCWake/start.sh
```

### Обновить бота до последней версии

```bash
cd ~/PCWake && git pull origin Main
```

### Перезапустить бота

```bash
# Остановить: Ctrl+C (кнопка CTRL в строке над клавиатурой, затем C)
# Запустить снова:
bash ~/PCWake/start.sh
```

### Проверить что бот запущен

```bash
ps aux | grep bot.py
```

---

## Настройка фона (важно)

Чтобы Android не убивал Termux при заблокированном экране:

`Настройки` → `Приложения` → `Termux` → `Батарея` → **"Без ограничений"**

---

## Если Telegram заблокирован провайдером

Добавить в `.env` прокси:

```
PROXY=socks5://user:pass@host:port
```

Или включить VPN системно на телефоне — тогда строка `PROXY` не нужна.

---

## Устранение проблем

**Бот не отвечает** — проверить процесс:
```bash
ps aux | grep bot.py
```

**ПК не включается** — убедиться что:
- WoL включён в BIOS и в настройках сетевой карты Windows
- ПК подключён по Ethernet (не WiFi)
- MAC-адрес в `.env` указан верно (взят из `ipconfig /all`, адаптер Ethernet)

**Бот не запускается после перезагрузки телефона** — открыть Termux:Boot и убедиться что приложение активно. Также убедиться что VPN включён до запуска бота.
