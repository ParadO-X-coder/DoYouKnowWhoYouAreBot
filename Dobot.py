import telebot
import numpy
import neural_network
import config
import dbworker
from telebot import types
bot = telebot.TeleBot(config.token)

neural_network.retrain(neural_network.data,neural_network.all_y_trues)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, я - искуственный интеллект, и ты написал мне. Я могу предсказать '
                                      'твой пол, давай проверим! Отправь сообщение перве число - вес(в кг),'
                                      'второе число - рост(в см) через пробел, и получишь ответ')
    dbworker.set_state(message.chat.id, config.States.S_MAIN.value)


@bot.message_handler(commands=['edit'])
def settings_message(message):
    if message.from_user.id == 460800754:
        bot.send_message(message.chat.id, "Вес Рост Пол")
        dbworker.set_state("460800754", config.States.S_EDIT.value)
        print("-1")
    else:
        bot.send_message(message.chat.id, "Нет ноступа!")



@bot.message_handler(func=lambda message: dbworker.get_current_state("460800754") == config.States.S_EDIT.value)
def edit(message):
    try:
        print("1")
        u = message.text.split()
        human = [int(u[0]) - 65, int(u[1]) - 170]
        neural_network.data.append(human)
        neural_network.all_y_trues.append(int(u[2]))
        neural_network.retrain(neural_network.data, neural_network.all_y_trues)
        dbworker.set_state(460800754, config.States.S_MAIN.value)
    except:
        bot.send_message(message.chat.id,
                            text="Не верный тип исходных данных!!!")

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_MAIN.value)
def test(message):
    #print(dbworker.get_current_state(message.chat.id))
    keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')  # кнопка «Да»
    keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    keyboard1 = types.InlineKeyboardMarkup()
    key_yes1 = types.InlineKeyboardButton(text='Помогите нам улучшить результат', callback_data='imp')
    keyboard1.add(key_yes1)
    global flag
    try:
        global a
        a = message.text.split()
        human = [int(a[0]) - 65, int(a[1]) - 170]
        result = neural_network.network.feedforward(human)
        print(result)
        if result < 0.45:
            bot.send_message(message.chat.id, "Вы - Мужчина",reply_markup=keyboard)
            bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAA'
                                              'IM1F52O0_2RTlm4SUoP_ZAkmtNdOiKAALYAwACnNbnCiOdOMOyRdRSGAQ')
            flag=0
        elif result > 0.55:
            bot.send_message(message.chat.id, "Вы - Женщина",reply_markup=keyboard)
            bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAA'
                                              'IM2l52PMreDeKhXF0WWRM0aeS-7C3mAAKqxgACY4tGDEqajcnbw6o3GAQ')
            flag = 1
        else:
            bot.send_message(message.chat.id, "Невозможно определить(",reply_markup=keyboard1)
            bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIM0l52Oyfd'
                                              'MaAw1gHavVhPs3dX83jwAAJ60wACY4tGDAe5s2rCFpMTGAQ')
            flag = -1
        # user_id = message.from_user.id
    except:
        bot.send_message(message.chat.id,
                            text="Не верный тип исходных данных!!!")



@bot.message_handler(content_types=['sticker'])
def sticker_id(message):
    print(message)


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_PREEDIT.value)
def change(message):

    try:
        dbworker.set_state(message.chat.id, config.States.S_MAIN.value)
        if int(message.text)==0:
            flag = 0
        elif int(message.text)==1:
            flag = 1
        question = 'Пользователь ' + str(message.chat.id) + " Имя:\t" + str(message.from_user.first_name) \
                   + " Фамилия:\t" + str(message.from_user.last_name) + ' исходные данные ' + str(
            a) + ", результат\t" + str(flag)
        bot.send_message(460800754, question)
    except:
        bot.send_message(message.chat.id,
                            text="Не верный тип исходных данных")

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes": #call.data это callback_data, которую мы указали при объявлении кнопки
        bot.send_message(call.message.chat.id, 'Спасибо за помощь)')
    elif call.data == "no":
        bot.send_message(call.message.chat.id, 'Запомню : )')
        question = 'Пользователь ' + str(call.from_user.id) + " Имя:\t" +str(call.from_user.first_name)\
                   +" Фамилия:\t"+str(call.from_user.last_name) +' исходные данные '+str(a)+", результат\t"+str(flag)
        bot.send_message(460800754,question)
    elif call.data == "imp":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
            text="Извените за неудобства! Введите ваш пол(0-мужчина 1-женщина)", reply_markup=None)
        dbworker.set_state(call.message.chat.id, config.States.S_PREEDIT.value)
    if flag==0:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Вы - Мужчина",
                reply_markup=None)
    elif flag == 1:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Вы - Женщина",
                          reply_markup=None)




bot.polling()
