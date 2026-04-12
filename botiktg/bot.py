import telebot
token = "8399418458:AAHmwgC4mmSjerfAC30kdJ19_w5AZ0G3KpE"
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def send_welcome(message):
        bot.reply_to(message, f'Привет, я помогу тебе сортировывать мусор, просто напиши /sorting и припиши цифру(1- пластик и металл 2- биоотходы 3- смешанные бытовые отходы 4- бумага и картон 5- опасные отходы)')

@bot.message_handler(commands=['sorting1'])
def send_welcome1(message):
        bot.reply_to(message, f'Пластик и металл (желтый контейнер): Пластиковые бутылки, банки, Tetra Pak упаковка (чистые). Крышки можно оставлять.')

@bot.message_handler(commands=['sorting2'])
def send_welcome2(message):
        bot.reply_to(message, f'Биоотходы (коричневый контейнер): Остатки еды, очистки, кофейная гуща, чайные пакетики, бумажные салфетки, цветы. НЕ класть: жидкости, жирные отходы, пластик, металл, стекло.')
        
@bot.message_handler(commands=['sorting3'])
def send_welcome3(message):
        bot.reply_to(message, f'Смешанные бытовые отходы (зеленый контейнер): Все остальное, что не поддается разделению (наполнители для лотков, грязные упаковки, подгузники), кроме опасных отходов.')
        
@bot.message_handler(commands=['sorting4'])
def send_welcome4(message):
        bot.reply_to(message, f'Бумага и картон (синий контейнер): Газеты, журналы, картонные коробки (смятые), бумажные пакеты. НЕ класть: грязную, мокрую бумагу, фольгу, пленку, бумажные стаканчики (с покрытием).jjn')
        
@bot.message_handler(commands=['sorting5'])
def send_welcome5(message):
        bot.reply_to(message, f'Опасные отходы (оранжевый контейнер): Батарейки, лампочки, ртутные градусники, химикаты. Сдавать в специальные пункты приема. ')


bot.polling()