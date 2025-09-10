# -*- coding: utf-8 -*-
import os
import subprocess
import sys

# Путь к корню проекта (где находится scr/)
project_root = os.path.dirname(os.path.abspath(__file__))

# Команды с указанием PYTHONPATH
commands = [
    [sys.executable, "bot.py"],  # запускает бота
    [sys.executable, "parser/parser.py"],  # запускает парсер и сервера
]

# Установить PYTHONPATH на корень проекта
env = os.environ.copy()
env["PYTHONPATH"] = project_root

processes = [subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for cmd in commands]

for p in processes:
    out, err = p.communicate()
    if out:
        print(out.decode())
    if err:
        print("Ошибка:", err.decode())
