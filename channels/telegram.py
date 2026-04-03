# channels/telegram.py
# Bot Telegram (phase 3)

import os
from typing import Optional


class TelegramBot:
    """
    Bot Telegram pour interagir avec l'agent.
    Phase 3 : implémentation complète.
    """
    
    def __init__(self, token: str = None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.api_url = f"https://api.telegram.org/bot{self.token}"
    
    def send_message(self, chat_id: str, text: str) -> dict:
        """Envoie un message à un utilisateur."""
        if not self.token:
            return {"ok": False, "error": "Token non configuré"}
        
        import requests
        try:
            response = requests.post(
                f"{self.api_url}/sendMessage",
                json={"chat_id": chat_id, "text": text}
            )
            return response.json()
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def set_webhook(self, webhook_url: str) -> dict:
        """Configure le webhook pour les mises à jour."""
        if not self.token:
            return {"ok": False, "error": "Token non configuré"}
        
        import requests
        try:
            response = requests.post(
                f"{self.api_url}/setWebhook",
                json={"url": webhook_url}
            )
            return response.json()
        except Exception as e:
            return {"ok": False, "error": str(e)}


def start_bot():
    """Point d'entrée pour démarrer le bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("ERREUR : TELEGRAM_BOT_TOKEN non configuré")
        return
    
    bot = TelegramBot(token)
    print(f"Bot Telegram初始isé (token: ...{token[-4:]})")
    print("Phase 3 : implémentation du webhook à compléter")


if __name__ == "__main__":
    start_bot()