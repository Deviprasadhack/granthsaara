import telebot
import internetarchive
from telebot import types
import requests
import os
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))
@bot.message_handler(commands=['start'])
def start(message):
    try:
        bot.send_message(message.chat.id, '''Welcome to GranthSaara! I'm a bot 🤖 created by @redmoon0x that can help you find and download free PDF books 📚 right in our chat.

To get started, simply type in the title, author name, or keyword 🔍 of the book you are looking for and I will send you results. Select the book you want and I'll send the PDF your way! 📩 

I have access to thousands of free books 📚 from sources like Project Gutenberg, Open Library, and more. Let me know if you are looking for a specific book or topic and I'll do my best to track it down 🔎.

Reading and learning 📖 should be easy. That's why I'm here! Message me anytime 💬 to start finding and downloading PDF books without any hassle.

Let's get searching! 🕵️‍♂️ What book are you looking to read next? 🤔

Hope you enjoy using this bot created by @redmoon0x! Let them know if you have any feedback or suggestions.''')
    except Exception as e:
        bot.send_message(message.chat.id, f"Error sending start message: {e}")

def search_results(search_object):
    for result in search_object:
        yield result

@bot.message_handler(func=lambda msg: True)
def search(message):
    query = message.text
    results = internetarchive.search_items(query)
    results_list = list(search_results(results))

    if len(results_list) == 0:
        bot.send_message(message.chat.id, "No results found.🔍🔍")
        return

    results_list = results_list[:20]  # Limit to the first 20 results

    buttons = []

    for r in results_list:
        title = r.get('identifier', 'Unknown Title')
        book_id = r.get('identifier', '')[:64]
        callback = book_id

        button = types.InlineKeyboardButton(title, callback_data=callback)
        buttons.append(button)

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(*buttons)

    try:
        bot.send_message(message.chat.id, f"Here are the results for {query}❤🐈", reply_markup=markup)
    except Exception as e:
        bot.send_message(message.chat.id, f"Error sending search results: {e}")

@bot.callback_query_handler(func=lambda call: True)

def send_pdf(call):

    try:
        book_id = call.data
        
        # Get PDF info
        item = internetarchive.get_item(book_id)
        pdf_files = [f for f in item.files if f['name'].endswith('.pdf')]
        
        if not pdf_files:
            bot.send_message(call.message.chat.id, f"Sorry Thats not PDF 🤦‍♂️🤦‍♂️")
            return 
            
        file = pdf_files[0]
        pdf_url = f"https://archive.org/download/{book_id}/{file['name']}"
        
        # Notify sending
        bot.send_message(call.message.chat.id, "Sending PDF...")
        
        # Download PDF data
        
        
        # Send PDF 
        bot.send_document(call.message.chat.id, pdf_url)
        
        # Notify success
        bot.send_message(call.message.chat.id, "PDF sent!")
        
    except requests.exceptions.RequestException as e:
        bot.send_message(call.message.chat.id, f"Error downloading PDF: {e}")
        
    except telebot.apihelper.ApiTelegramException as e:
        bot.send_message(call.message.chat.id, f"PDF NOT AVAILABLE SORRY 🫡🫡: {e}")
        
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Unknown error: {e}")
        raise e # re-raise after handling
        
    finally:
        bot.answer_callback_query(call.id)
if __name__ == '__main__':
    bot.polling()
