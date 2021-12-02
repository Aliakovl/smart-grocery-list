# smart-grocery-list


Creating a virtual environment:
``python3 -m venv env``

Activating a virtual environment:
``source env/bin/activate``

Using requirements files:
``python3 -m pip install -r requirements.txt``

*nix:
``export PYTHONPATH="${PYTHONPATH}:/path/to/smart-grocery-list/"``

Windows:
``set PYTHONPATH="${PYTHONPATH}:/path/to/smart-grocery-list/"``

``export TELEGRAM_TOKEN=telegram-bot-api-token``

Install __mongoDB__ (don't forget to active it: ``systemctl start mongodb``)

Run:
``python3 src/main/tgbot/tgbot.py``
