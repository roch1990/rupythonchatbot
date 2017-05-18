# -*- coding: utf-8 -*-
# external python library
try:
    import sys
    import datetime
    import telebot
    import random
    import requests
    from bs4 import BeautifulSoup
# internal bot library
    import config
except ImportError as e:
    raise e


# Логи в stdout гарантировано, чтобы docker logs их видел
sys.stdout.write('Bot starting\n'.format())


bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=[u'помоги'])
def user_help(message):
    sys.stdout.write('{0}\tHelp method call\n'.format(message.chat.id))
    # Кортеж вывода
    help_text = ('Решу за вас вопросы:',
                 '1) Загуглить - /гугл тут_текст',
                 '2) Спутник - /спутник тут_текст')
    
    for item in help_text:
        bot.send_message(message.chat.id, item)


@bot.message_handler(commands=['ping'])
def user_help(message):
    sys.stdout.write('{0}\tPing method call\n'.format(message.chat.id))
    # Дерзим в ответ
    help_text = ('Че надо?')
    bot.send_message(message.chat.id, help_text)


@bot.message_handler(commands=[u'гугл'], content_types=["text"])
def user_help(message):
    sys.stdout.write('{0}\tGDD method call\n'.format(message.chat.id))
    # Режем запрос на кортеж слов
    keywords_list = tuple(message.text.split(' '))
    google_querry = config.google_string
    
    # Составляем запрос гуглу и убираем команду /гугл
    for item in keywords_list:
        if item != u'/гугл':
            google_querry += '+' + item

    help_text = ('Тут глянь:', google_querry)
    for item in help_text:
        bot.send_message(message.chat.id, item)
        

@bot.message_handler(commands=[u'спутник'], content_types=["text"])
def user_help(message):
    sys.stdout.write('{0}\tSputnik method call\n'.format(message.chat.id))
    # Режем запрос на кортеж слов
    keywords_list = tuple(message.text.split(' '))
    sputnik_querry = config.sputnik_string
    
    # Составляем запрос спутнику и убираем команду /спутник
    for item in keywords_list:
        if item != u'/спутник':
            sputnik_querry += '+' + item
            
    help_text = ('Конечно можно, но...', 'Вообщем я предупреждал:', sputnik_querry)
    for item in help_text:
        bot.send_message(message.chat.id, item)


@bot.message_handler(content_types=["text"])
def user_help(message):
    weather_flag = False
    news_flag = False
    sys.stdout.write('{0}\tText method call\n'.format(message.chat.id))
    # Режем список  слов
    keywords_list = tuple(message.text.split(' '))
    
    if message.chat.id == config.ighar_chat_id :
        bot.send_message(config.python_ru_chat_id, message.text)
    
    # Пробегаемся по всем значениям в словаре хештегов и подбираем релевантный хэштег
    for key in config.hashtag:
        for item in config.hashtag[key]:
            for word in keywords_list:
                # Не забываем занизить все как ладу приору
                if word.lower() == item:
                    bot.send_message(message.chat.id, key)

    # Парсим сообщение в чате по словам
    for word in keywords_list:
        
        # Если есть чето по погоде - ставим флаг готовности ее выдать
        if word.lower() in config.weather_key:
            weather_flag = True
        
        elif word.lower() in config.news_key:
            news_flag = True
        
        # Если есть флаг погоды и выставлен город - парсим погоду с Рамблера и выдаем   
        elif (weather_flag == True) and (word.lower() in config.weather_hash):
            help_text = __weather_parser(message.chat.id, word.lower())
            for item in help_text:
                bot.send_message(message.chat.id, item)
            # Щелкаем флаг обратно
            weather_flag = False
            key = 'weather'
            break
        
        # Если пошел мат в чате, то работаем по принципу:
        # "Кто обзывается - тот сам так называется"
        elif word.lower() in config.bad_word_key:
            key = 'сам ' + word.lower()
            bot.send_message(message.chat.id, key)
        
        # Выдаем время
        # Таймзоны лень чинить, поэтому серверное пулит
        elif word.lower() in config.time_key:
            key = word.lower()
            bot.send_message(message.chat.id,
                             'На райончике: ' +
                             str(datetime.datetime.now()))
        
        # Новости с хабра питоновские
        elif (news_flag == True):
            # Для каждого ключа из хэша конфиговского
            for key in config.habrahabr_rubik:
                # Если слово из сообщения есть в значениях ключа хэша из конфига
                if word.lower() in config.habrahabr_rubik[key]:
                    # Берем релевантный url
                    habr_url = config.habrahabr_url[key]
                    # Парсим страничку на первые попавшиеся 3 новости
                    news_hash = __news_parser(message.chat.id, word.lower(), habr_url)
                    help_text = ''
                    # Приветсвенное сообщение
                    bot.send_message(message.chat.id,
                                     'Во че на районе болтают: ')
                    # Передаем каждую новость в отдельном сообщении
                    for item in news_hash:
                        bot.send_message(message.chat.id,
                                         item + '\n'+
                                         news_hash[item])
                    # Щелкаем флаг
                    news_flag = False
                
        else:
            key = 'nothing'
            
    # Каждое сообщение парсит на запрос погоды
    # Так как дебилы могут абстрактуню погоду запросить
    # И выдает им ответ по принципу "Невнятное ТЗ - результат ХЗ"
    if (weather_flag == True):
            bot.send_message(message.chat.id, config.weather[
                random.randint(0,
                              len(config.weather)-1)])
    
    # По аналогии с предыдущим
    if (news_flag == True):
        bot.send_message(message.chat.id, 'Да за такое в южном бутово по щам дают.')
            
    sys.stdout.write('{0}\tKey:\t{1}\n'.format(message.chat.id, key))


# Парсим погоду на рамблере
def __weather_parser(chat_id, city='москве'):
    sys.stdout.write('{0}\tCity:\t{1}\n'.format(chat_id, city))
    
    # Составляем урл
    rambler_url = config.weather_rambler + config.weather_hash[city.lower()]
    # Получаем html'ку
    html_doc = (requests.get(rambler_url)).text
    # Парсим
    soup_fd = BeautifulSoup(html_doc, 'html.parser')
    temperature = (soup_fd.find('span', class_='weather-now__value').text)
    description = (soup_fd.find('div', class_=
                                'weather-today__explanation weather-today__grid-explanation').text)
    
    # Выдаем кортеж с распарсенными значениями и удаленными переводами строки
    return ('Ну че\nВ ' + city.replace('\n', '') +
            ':\n' +
            temperature.replace('\n', '') +
            ' градусов\n' +
            description,
            'Инфа предоставлена: ' + rambler_url)


def __news_parser(chat_id, message, url):
    sys.stdout.write('{0}\tNews url:\t{1}\n'.format(chat_id, url))
    counter = 0
    news_hash = {}
    
    # Получаем html'ку
    html_doc = (requests.get(url)).text
    # Парсим
    soup_fd = BeautifulSoup(html_doc, 'html.parser')
    # Ищем все контейнеры с постами на странице
    post_div = soup_fd.find_all('h2', class_='post__title')
    
    # Находим первые 3 поста
    for counter in range(0,3):
        post_a_href = post_div[counter].find('a')
        post_link = post_a_href.get('href')
        post_title = post_a_href.text
        news_hash[post_title] = post_link

    # возвращаем словарь с новостями
    return news_hash
    

# Все поллим, веб-хуки втопку
if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        sys.stdout.write('{0}\tSomething went wrong with connection:\n{1}\n'.
                         format('WARNING', e))
