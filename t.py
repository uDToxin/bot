import requests
import telebot
from telebot import types
from random import randint
try:
    import telebot
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
except ModuleNotFoundError:
    input("There is no necessary library. Complete the command line command: PIP Install Pytelegrambotapi")

url = "https://leakosintapi.com/"
bot_token = "7891280232:AAEQR4JeKStkMzHKvr_cYt6aIZHvtsxdnLQ" #Insert here the token received from @botfather
api_token = "5759541541:ZMmr0slR"  #Insert here the token received from Leakosint
lang = "en"
limit = 300

#In this function, you can check whether the user has access to
def user_access_test(user_id):
    return(True)

#Function for generating reports
cash_reports = {}
def generate_report(query, query_id):
    global cash_reports, url, bot_token, api_token, limit, lang
    data =  {"token":api_token, "request":query.split("\n")[0], "limit": limit, "lang":lang}
    response = requests.post(url, json=data).json()
    print(response)
    if "Error code" in response:
        print("Error:"+response["Error code"])
        return(None)
    cash_reports[str(query_id)] = []
    for database_name in response["List"].keys():
        text = [f"<b>{database_name}</b>",""]
        text.append(response["List"][database_name]["InfoLeak"]+"\n")
        if database_name!="No results found Toxic Baby":
            for report_data in response["List"][database_name]["Data"]:
                for column_name in report_data.keys():
                    text.append(f"<b>{column_name}</b>:  {report_data[column_name]}")
                text.append("")
        text = "\n".join(text)
        if len(text)>3500:
            text = text[:3500]+text[3500:].split("\n")[0]+"\n\nSome data did not fit this message"
        cash_reports[str(query_id)].append(text)
    return(cash_reports[str(query_id)])

#Function for creating an inline keyboard
def create_inline_keyboard(query_id, page_id, count_page):
    markup = InlineKeyboardMarkup()
    if page_id<0:
        page_id=count_page
    elif page_id>count_page-1:
        page_id=page_id%count_page
    if count_page==1:
        return markup
    markup.row_width = 3
    markup.add(InlineKeyboardButton(text = "<<", callback_data=f"/page {query_id} {page_id-1}"),
               InlineKeyboardButton(text = f"{page_id+1}/{count_page}", callback_data="page_list"),
               InlineKeyboardButton(text = ">>", callback_data=f"/page {query_id} {page_id+1}"))
    return markup

bot = telebot.TeleBot(bot_token)

@bot.message_handler(commands=["start"])
def send_welcome(message):
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    btn_search = types.InlineKeyboardButton("📱 Search Data", callback_data="search_data")
    btn_support_chat = types.InlineKeyboardButton("💬 Support Chat", url="https://t.me/YourSupportChat")
    btn_support_channel = types.InlineKeyboardButton("📢 Support Channel", url="https://t.me/YourChannel")
    btn_owner = types.InlineKeyboardButton("👑 Owner", url="tg://user?id=8233966309")

    keyboard.add(btn_search)
    keyboard.add(btn_support_chat, btn_support_channel, btn_owner)

    photo_url = "https://ar-hosting.pages.dev/1759776521409.jpg"  # apna photo link daalna
    bot.send_photo(message.chat.id, photo_url,
                   caption="Hello! I am a telegram-bot that can search for databases.",
                   reply_markup=keyboard, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "search_data":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id,
                         "You can look for the following data:\n\n"
                         "📱Search by phone number\n"
                         "├ +79002206090\n"
                         "├ +17900220609\n"
                         "└ +911234567890")
        
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    user_id = message.from_user.id
    if not(user_access_test(user_id)):
        bot.send_message(message.chat.id, "You have no access to the bot")
        return()
    if message.content_type == "text":
        query_id = randint(0,9999999)
        report = generate_report(message.text,query_id)
        markup = create_inline_keyboard(query_id,0,len(report))
        if report==None:
            bot.reply_to(message, "The bot does not work at the moment.", parse_mode="Markdown")
        try:
            bot.send_message(message.chat.id, report[0], parse_mode="html", reply_markup=markup) #, reply_markup=markup
        except telebot.apihelper.ApiTelegramException:
            bot.send_message(message.chat.id, text = report[0].replace("<b>","").replace("</b>",""), reply_markup=markup)
        
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery):
    global cash_reports
    if call.data.startswith("/page "):
        query_id, page_id = call.data.split(" ")[1:]
        if not(query_id in cash_reports):
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="The results of the request have already been deleted")
        else:
            report = cash_reports[query_id]
            markup = create_inline_keyboard(query_id,int(page_id),len(report))
            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=report[int(page_id)], parse_mode="html", reply_markup=markup)
            except telebot.apihelper.ApiTelegramException:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=report[int(page_id)].replace("<b>","").replace("</b>",""), reply_markup=markup)
while True:
    try:
        bot.polling()
    except:
        pass
