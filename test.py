import unittest
from unittest.mock import MagicMock
import bot

class BotCase(unittest.TestCase):
  def test_first_response_no(self):
    chat = "Нет, отстань"
    message = MagicMock(chat=chat)
    update = MagicMock(message=message)
    context = MagicMock(user_data=dict())
    bot.first_response(update, context)
    message.reply_text.assert_called_with("Ну как хочешь...")
  def test_first_response_yes(self):
    chat = "Да, мне нужна помощь"
    message = MagicMock(chat=chat)
    update = MagicMock(message=message)
    context = MagicMock(user_data=dict())
    bot.first_response(update, context)
    message.reply_text.assert_called_with("Отлично, я помогу тебе!")
    message.reply_text.assert_called_with("Введи название дедлайна")

if __name__ == '__main__':
  unittest.main()