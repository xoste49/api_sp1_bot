# api_sp1_bot
Бот для Телеграмма работает с Домашкой Яндекс.Практикум, получает обновления проверки последней домашней работы.

## Установка Debian
```bash
$ cd /root/
$ mkdir python_projects
$ cd python_projects
$ git clone https://github.com/xoste49/api_sp1_bot.git
$ cd api_sp1_bot
$ python3 -m venv venv
$ source venv/bin/activate
(venv)$ pip install -r requirements.txt
$ nano /etc/environment
$ nano /lib/systemd/system/yaprbot.service
```

```
[Unit]
Description=Yandex.Praktikum Telegram Bot
After=network.target

[Service]
EnvironmentFile=/etc/environment
ExecStart=/root/python_projects/api_sp1_bot/venv/bin/python homework.py
ExecReload=/root/python_projects/api_sp1_bot/venv/bin/python homework.py
WorkingDirectory=/root/python_projects/api_sp1_bot/
KillMode=process
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
$ systemctl enable yaprbot
$ systemctl start yaprbot

$ systemctl status yaprbot  # статус
$ journalctl -u yaprbot.service  # логи
```
