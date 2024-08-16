# D&D bot
## Попробовать
Бот уже установлен здесь:
https://discord.gg/WYyeYE4W4v
Чтобы установить бота на свой Discord-сервер, перейдите по ссылке:<br>
https://discord.com/oauth2/authorize?client_id=1271129902246269030&permissions=8&integration_type=0&scope=bot
## Развёртывание на собственном сервере
Бот развёрнут на бесплатном хостинге с очень малым количеством памяти, поэтому настоятельно рекомендуется развернуть его самостоятельно на своём компьютере или сервере. Для этого:
1. Установите зависимости
```
pip install -r requirments.txt
```
2. Запустите бота
```
python -m main.py
```
## Музыка
На GitHub отсутствует музыка, разместите её в папке music. Названия должны быть вида "{category}{id}.mp3", где category - один из типов музыки:
```day, dungeon, city, tavern, combat, night, winter, death```; id - номер в списке от 1 до n, где n - количество файлов с музыкой данного типа. Все категории должны присутствовать.<br>
Структура может выглядеть вот так:
```
music
|-day1.mp3
|-day2.mp3
|-dungeon1.mp3
|-city1.mp3
|-city2.mp3
|...
|-tavern3.mp3
|-tavern4.mp3
cogs
|-dnd.py
audio.py
...
