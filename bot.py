import logging
from datetime import datetime
from typing import Union, List
import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
import requests

SUBJECT, AMOUNT1, AMOUNT2, TIME= range(4)

subjectv = None
amount1v = None
amount2v = None
timev = None
datev = None
datef = None


  
def callback_timer(update, context):
    timev = update.message.text.upper()
    
    context.bot.send_message(chat_id=update.message.chat_id,
                     text='🤖 <code> En sus marcas, listo, fuera ...! </code> 🤖', parse_mode=telegram.ParseMode.HTML)
    context.job_queue.run_repeating(callback_alarm, int(timev), context=update.message.chat_id, name="revolico")
    return ConversationHandler.END

def stop_timer(update, context):
    job = context.job  
    global datef
    global datev
    datef = None
    datev = None    
    context.bot.send_message(chat_id=update.message.chat_id,
                      text='🤖 <code>Hemos parado de buscar Usa la opción reiniciar para comenzar otra busqueda 🤖</code>', parse_mode=telegram.ParseMode.HTML)                      
    restart_msg_job(context)
    


def get_msg_job(context):    
    jobs = context.job_queue.get_jobs_by_name('revolico')
    return jobs[0] if len(jobs) else None



def clean_msg_job(context):
    msg_job = get_msg_job(context)
    if msg_job:
        msg_job.schedule_removal()
        

def restart_msg_job(context):
    clean_msg_job(context)     
    user_data = context.user_data
    user_data.clear()
    return ConversationHandler.END

def start(update, context):
    """Send a message when the command /start is issued."""    
    context.bot.send_message(chat_id=update.message.chat_id,
                      text='🤖 <code>Hola!, bienvenidos. Soy un Robot caza ofertas y estoy a tu disposición para ayudarte 🤖</code> \n\n''<i>👉 Introduzca que desea buscar</i>', parse_mode=telegram.ParseMode.HTML)
    # update.message.reply_text('👉 *bold* Hola, bienvenidos a este super buscador.\n\n''Introduzca que desea buscar', parse_mode=telegram.ParseMode.MARKDOWN_V2)
    
    return SUBJECT

def subject(update, context):
    global subjectv
    subjectv = update.message.text
    update.message.reply_text('🤖 <code>Perfecto!, Vas a buscar '+subjectv+'🤖 </code> \n\n''<i>👉 Introduce el precio mínimo por el que deseas buscar </i>', parse_mode=telegram.ParseMode.HTML)
    
    return AMOUNT1

def amount1(update, context):
    global amount1v
    amount1v = update.message.text
    update.message.reply_text('🤖 <code>Muy bien!, Has fijado un precio mínimo de '+amount1v+'🤖 </code> \n\n''<i>👉 Introduce ahora el precio máximo por el que deseas buscar </i>', parse_mode=telegram.ParseMode.HTML)
    
    return AMOUNT2

def amount2(update, context):
    global amount2v 
    amount2v = update.message.text
    update.message.reply_text('🤖 <code>Correcto!, Has fijado un precio máximo de '+amount2v+' Ya estamos por terminar! 🤖 </code> \n\n''<i>👉 Introduce cada cuanto tiempo quieres que revise por una nueva oferta (en segundos) </i>', parse_mode=telegram.ParseMode.HTML)
    
    return TIME

def callback_alarm(context):
    job = context.job    
    newHeaders = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    print(subjectv)
    data = [{
		"operationName": "AdsSearch",
		"query": "query AdsSearch($category: ID, $subcategory: ID, $contains: String, $priceGte: Float, $priceLte: Float, $sort: [adsPerPageSort], $hasImage: Boolean, $categorySlug: String, $subcategorySlug: String, $page: Int, $provinceSlug: String, $municipalitySlug: String, $pageLength: Int) {\n  adsPerPage(category: $category, subcategory: $subcategory, contains: $contains, priceGte: $priceGte, priceLte: $priceLte, hasImage: $hasImage, sort: $sort, categorySlug: $categorySlug, subcategorySlug: $subcategorySlug, page: $page, provinceSlug: $provinceSlug, municipalitySlug: $municipalitySlug, pageLength: $pageLength) {\n    pageInfo {\n      ...PaginatorPageInfo\n      __typename\n    }\n    edges {\n      node {\n        id\n        title\n        price\n        currency\n        shortDescription\n        permalink\n        imagesCount\n        updatedOnToOrder\n        isAuto\n        province {\n          id\n          name\n          slug\n          __typename\n        }\n        municipality {\n          id\n          name\n          slug\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    meta {\n      total\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment PaginatorPageInfo on CustomPageInfo {\n  startCursor\n  endCursor\n  hasNextPage\n  hasPreviousPage\n  pageCount\n  __typename\n}\n",
		"variables": {
			"contains": subjectv,
			"page": 1,
			"pageLength": "10",
			"priceGte": amount1v,
			"priceLte": amount2v,			
            "sort": [
                {
                    "field": "relevance",
                    "order": "desc"
                }
            ]
		}
	}]
   

   
    response = requests.post('https://api.revolico.app/graphql/', json=data, headers=newHeaders)
    print("Status code: ", response.status_code)
    response_Json = response.json()
    
    query = response_Json[0]['data']['adsPerPage']['edges']
    min = 60
    # max = input("Entra la cantidad maxima: ")
    
    global datev
    global datef
    datef = datetime.strptime(query[0]["node"]["updatedOnToOrder"], '%Y-%m-%dT%H:%M:%S.%f%z')
    if datev == None or datef > datev:
        datev =  datetime.strptime(query[0]["node"]["updatedOnToOrder"], '%Y-%m-%dT%H:%M:%S.%f%z')
        for s in query:
            # print(s['node'])    
            # if int(s["node"]["price"] or 0) <= int(min) and currency in str(s["node"]["title"]): 
                print("Date :"+str(datev)) 
                print(s["node"]["updatedOnToOrder"]+'-'+ s["node"]["title"])
                
                context.bot.send_message(job.context, text="Precio: {} {} \n\n {} \n\n URL: https://www.revolico.com{} \n\n {} \n\n Fecha y Hora : {}.".format(s["node"]["price"], s["node"]["currency"], s["node"]["title"], s["node"]["permalink"], s["node"]["shortDescription"], s["node"]["updatedOnToOrder"]))           
                # client.send_message(541437201, "ID {} Title {}.".format(s["node"]["id"], s["node"]["title"]))




def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)   


    return ConversationHandler.END


def main() -> None:

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={           
            SUBJECT: [MessageHandler(Filters.text & ~Filters.command, subject)],
            AMOUNT1: [MessageHandler(Filters.text & ~Filters.command, amount1)],
            AMOUNT2: [MessageHandler(Filters.text & ~Filters.command, amount2)],
            TIME: [MessageHandler(Filters.text & ~Filters.command, callback_timer, pass_job_queue=True)],
        },
        fallbacks=[CommandHandler('stop', stop_timer)],
    )

    updater = Updater("1887661416:AAEquuuDDHEnDAwKapOQrmpDBGsvqMrboV0")
    updater.dispatcher.add_handler(conv_handler)
    # updater.dispatcher.add_handler(CommandHandler('stop', unset)) 
    # updater.dispatcher.add_handler(CommandHandler('call', callback_timer, pass_job_queue=True))    
   
    updater.dispatcher.add_handler(CommandHandler('stop', stop_timer, pass_job_queue=True))   
    updater.dispatcher.add_handler(CommandHandler('start', start))  
    updater.start_polling()
    updater.idle()




if __name__ == '__main__':
    main()