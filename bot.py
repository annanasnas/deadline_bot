from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import logging, datetime, time, schedule
from pathlib import Path
from functools import partial

# see in real-time what is happening with the bot
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

updater = None
number = 1

def first_response(update, context):
  '''
    Функция получения ответа пользователя на вопрос:
    "Нужно сдать важную работу сегодня?"
  '''
  answer = update.message.text
  if answer == "Да, мне нужна помощь":
      update.message.reply_text("Отлично, я помогу тебе!")
      update.message.reply_text("Введи название дедлайна")
      return 2
  if answer == "Нет, отстань":
      update.message.reply_text("Ну как хочешь...")
      return ConversationHandler.END

def second_response(update, context):
  '''
    Функция сохранения названия дедлайна.
  '''
  DEADname = update.message.text
  context.user_data['DEADline'][number].append(DEADname)
  update.message.reply_text("На какое время ставим дедлайн?")
  return 3

def third_response(update, context):
  '''
    Функция сохранения времени дедлайна.
    Проверка дедлайна на валидность.
  '''
  try:
      DEADtime = update.message.text
      DEADtime = datetime.datetime.strptime(DEADtime, '%H:%M')
  except ValueError:
      update.message.reply_text('Введи в формате ЧЧ:ММ')
      return 3
  context.user_data['DEADline'][number].append(DEADtime)
  if DEADtime.hour < datetime.datetime.today().hour:
      update.message.reply_text("Мы не можем вернуться в прошлое :(")
      update.message.reply_text("Введи время еще раз")
      return 3
  if DEADtime.hour == datetime.datetime.today().hour and DEADtime.minute <= datetime.datetime.today().minute:
      update.message.reply_text("Этот дедлайн уже просрочен на несколько минут")
      update.message.reply_text("Введи время еще раз")
      return 3
  update.message.reply_text("Дедлайн установлен")
  keyboard = [
      [KeyboardButton("Да"), KeyboardButton("Нет")],
  ]
  reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
  update.message.reply_text("Хочешь установить еще один?", reply_markup=reply_markup)
  return 4

def forth_response(update, context):
  '''
    Функция добавления нового дедлайна.
  '''
  global number
  answer = update.message.text
  if answer == "Да":
      number += 1
      context.user_data['DEADline'][number] = []
      update.message.reply_text("Введи название дедлайна")
      return 2
  else:
      update.message.reply_text("Чтобы я начал следить за твоей работой, введи /follow")
      return ConversationHandler.END

def job(update, context):
  '''
    Функция напоминания пользователю о необходимости работы.
  '''
  update.message.reply_text("Ботай")

def job2(update, context):
  '''
    Функция напоминания пользователю о необходимости следить 
    за осанкой.
  '''
  update.message.reply_text("Выпрями спинку")

def show_deadlines(update, context):
  '''
    Функция вывода пользователю информации обо всех дедлайнах,
    учитывая их временные промежутки.
  '''
  global number
  for i in range(1, number+1):
      # 0: DEADname
      # 1: DEADtime
      name = context.user_data['DEADline'][i][0]
      hours = context.user_data['DEADline'][i][1].strftime('%H')
      mins = context.user_data['DEADline'][i][1].strftime('%M')
      current_hours = datetime.datetime.today().strftime('%H')
      current_min = datetime.datetime.today().strftime('%M')

      if int(current_hours) - int(hours) <= 1:
          if int(mins) >= int(current_min) and int(current_hours) == int(hours):
              update.message.reply_text(f"До дедлайна {name} осталось совсем немного. Успей до {hours}:{mins}")
          if int(mins) >= int(current_min) and int(current_hours) == int(hours) - 1:
              update.message.reply_text(f"До дедлайна {name} осталось совсем немного. Успей до {hours}:{mins}")
      elif int(current_hours) - int(hours) <= 3:
          update.message.reply_text(f"До дедлайна {name} осталось меньше 3 часов. Успей до {hours}:{mins}")

      if int(current_hours) == int(hours) and int(current_min) == int(mins):
          update.message.reply_text(f"Дедлайн {name} прошел")

def job5(update, context):
  '''
    Функция остановки бота по истечению суток.
  '''
  schedule.clear('deadlines')
  stop

def check_deadline(update, context):
  '''
    Функция проверки наступления дедлайна
  '''
  global number
  for i in range(1, number+1):
    # 0: DEADname
    # 1: DEADtime
    name = context.user_data['DEADline'][i][0]
    hours = context.user_data['DEADline'][i][1].strftime('%H')
    mins = context.user_data['DEADline'][i][1].strftime('%M')
    current_hours = datetime.datetime.today().strftime('%H')
    current_min = datetime.datetime.today().strftime('%M')
    
    if int(current_hours) == int(hours) and int(current_min) == int(mins):
        update.message.reply_text(f"Дедлайн {name} прошел")


# start watching
def follow(update, context):
  '''
    Функция, отображающая логику напоминаний о дедлайнах
  '''
  update.message.reply_text("Я слежу")
  schedule.every(60).minutes.do(partial(job, update, context)).tag('deadlines')
  schedule.every(90).minutes.do(partial(job2, update, context)).tag('deadlines')
  schedule.every(30).minutes.do(partial(show_deadlines, update, context)).tag('deadlines')
  schedule.every(1).minutes.do(partial(check_deadline, update, context)).tag('deadlines')
  schedule.every().day.at('23:59').do(job5)
  while True:
      schedule.run_pending()
      time.sleep(30)

def ask(update, context):
  '''
    Функция, которая подскажет пользователю о наличии команды help.
  '''
  update.message.reply_text("Пиши /help")

def help(update, context):
  '''
    Функци, отображающая для пользователя все возможные команды бота.
  '''
  update.message.reply_text("Напиши /stop, если хочешь выйти")

def start(update, context):
  '''
    Функция старта бота в общении с пользователем.
  '''
  context.user_data['DEADline'] = { number: []}
  name = update.message.chat.first_name
  keyboard = [
      [KeyboardButton("Да, мне нужна помощь")],
      [KeyboardButton("Нет, отстань")],
  ]
  reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
  update.message.reply_text(f"Привет, {name}! Нужно сдать важную работу сегодня?", reply_markup=reply_markup)
  return 1

def stop(update, context):
  '''
    Функция остановки бота. Прощание с пользователем.
  '''
  update.message.reply_text("Пока!")
  return ConversationHandler.END

def start_bot():
  '''
    Функция старта бота. Реализует Handler.
  '''
  global updater
  updater = Updater(token=Path('token.txt').read_text().strip(), use_context=True)
  dispatcher = updater.dispatcher 

  conv_handler = ConversationHandler(
      entry_points=[CommandHandler('start', start)],
      states={
          1: [MessageHandler(Filters.text, first_response)],
          2: [MessageHandler(Filters.text, second_response)],
          3: [MessageHandler(Filters.text, third_response)],
          4: [MessageHandler(Filters.text, forth_response)]
      },
      fallbacks=[CommandHandler('stop', stop)]
  )

  dispatcher.add_handler(conv_handler)
  dispatcher.add_handler(CommandHandler('start', start))
  dispatcher.add_handler(CommandHandler('stop', stop))
  dispatcher.add_handler(CommandHandler('help', help))
  dispatcher.add_handler(CommandHandler('follow', follow))
  dispatcher.add_handler(MessageHandler(Filters.text, ask))

  updater.start_polling() 
  updater.idle()

start_bot()