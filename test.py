import unittest
from unittest.mock import MagicMock, call
import bot

class BotCase(unittest.TestCase):
  def test_first_response_no(self):
    message = "Нет, отстань"
    update = MagicMock(text=message)
    context = MagicMock()
    bot.first_response(update, context)
    message.reply_text.assert_called_with("Ну как хочешь...")
  def test_first_response_yes(self):
    message = "Да, мне нужна помощь"
    update = MagicMock(text=message)
    context = MagicMock()
    bot.first_response(update, context)
    calls = [call("Отлично, я помогу тебе!"), call("Введи название дедлайна")]
    message.reply_text.assert_has_calls(calls)

if __name__ == '__main__':
  unittest.main()