#https://github.com/farhaanbukhsh/Telegram-Bots
import telegram
import json
import telepot
import time
from telegram.error import NetworkError, Unauthorized
from tinydb import TinyDB, Query
import xmltopnews
import caseydbhandler
import dbhandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

LAST_UPDATE_ID = None
error_counter=0
chat_id = 0
bot = None

db = TinyDB('/home/pi/Projects/db.json')
if(len(db)<1):#check if we got blank file
    db.insert({'content': 'running'})


news_id=0


def main():

    ''' This is the main function that has to be called '''

    global LAST_UPDATE_ID, error_counter,b
#        chat_id=200272963

    try:
        bot = telegram.Bot('445503486:AAGo9on5LZNgly5ca5UvkTHoi7h6ER5JYEI')
        b = telepot.Bot('445503486:AAGo9on5LZNgly5ca5UvkTHoi7h6ER5JYEI')

        b.setWebhook()
    except NetworkError as e: #if network hicks up
        print(e)
        log(e)
        error_counter +=1
        if error_counter>3:
           error_counter=0
           #restart()
        else:
           time.sleep(1)
           main()

    except Exception as e:
        print("got error",e)
        log(e)
        error_counter +=1
        if error_counter>3:
           error_counter=0
           #restart()
        else:
           time.sleep(1)
           main()

    # This will be our global variable to keep the latest update_id when requesting
    # for updates. It starts with the latest update_id if available.
    try:
        LAST_UPDATE_ID = bot.getUpdates()[-1].update_id
    except IndexError:
        LAST_UPDATE_ID = None

    while True:
        try:
           fetch_url(bot)
        except NetworkError as e: #if network hicks up
           print(e)
           log(e)
           time.sleep(1)
        except Exception as e:
           print("Error ",e, " rebooting now")
           db.purge()
           log(e)
           #restart()
           break

def restart():
    command = "/usr/bin/sudo /sbin/shutdown -r now"
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print (output)

def list_compare(first_list, second_list):

    ''' Function to compare two list and return the index of first matched index'''

    for word in first_list:
        if word in second_list:
            return second_list.index(word)
    return -1

def sendpic(bot,thepicfile):
    bot.sendPhoto(chat_id=chat_id, photo=open(thepicfile, 'rb'))

def log(err):
    with open("/home/pi/logs/exceptionlog", "a") as out_file:
       out_file.write(str(err)+"\n")


def fetch_url(bot):
    global LAST_UPDATE_ID, news_id,b, long, lat

    # Following is a dictionary of commands that the bot can use

    commands = {'/help':"You can add me in any group or text me!\nI don't have access to the group message so you need to call me by my name i.e @AskYourCouncilCaseyBot or start your senstence with '/' ,\nI listen to the keywords 'means', '/childcare', '/reboot', '/news' , '/trivia','/violence', 'emergency' or 'sos' followed by your problem like 'fire' or 'theft'  ", 
                '/start':'I am always listening to you. Just use magical words like "/childcare"',
                '/reboot':'You want me to restart...',
                '/childcare':'List of closest childcares from you',
                '/news':'Fetching top news...',
                '/trivia':'Random Trivia',
		'/childcare':'Getting the closest maternal child health care',
                '/callcouncil':'Get in touch with council member',
                '/violence':'Contact family violence hotline'
		}

    magic_words = ['sos','emergency']
    db_status = Query()
    b.setWebhook()

    message = ""
    fname = ""
    lname = ""
    message_list =""
    loc = False
    callbackmode = False
    pho = False
    phone = ""

    for update in bot.getUpdates(offset=LAST_UPDATE_ID, timeout=10):
        try:       
            chat_id = update.message.chat_id
            #if(update.callback_query==None or len(str(update.callback_query)==0)):
            callbackmode = False
            #else:
        except:
            print("callback!")
            callbackmode = True

        if(callbackmode == True):
            print("We are in callback mode")
            #print(update.callback_query)
            service = ""
            if(update.callback_query.data=="1"):
              print("sending police")
              service = "POLICE"
            elif(update.callback_query.data=="2"):
              print("sending ambulance")
              service = "AMBULANCE"
            elif(update.callback_query.data=="3"):
              print("sending fire brigades")
              service = "FIRE BRIGADES"
            else:
              chat_id = update.callback_query.message.chat.id
              #service = "Press to dial Call Safe Steps on [+611800015188](tel:+611800015188)."
              service = "Dialing 000 for you...." 
              print("dial 000")
              bot.sendMessage(chat_id=chat_id, text=service)
            if(update.callback_query.data!="4"):
              chat_id = update.callback_query.message.chat.id
              texttosend = "I am sending " + service + " to you now" + "\n"
              URL = "https://www.casey.vic.gov.au/health-safety/emergency/emergency-contact"
              texttosend = "".join([texttosend,URL])
              bot.sendMessage(chat_id=chat_id, text=texttosend)
        else:
            try:
              chat_id = update.message.chat_id
              fname = update.message.chat.first_name
              lname = update.message.chat.last_name
              message = update.message.text
              message = message.lower()

              message_list = message.split()
            except:
              print("keep going")


            try:
              long = float(update.message.location.longitude)
              lat = float(update.message.location.latitude)
              loc = True
              message = ""
            except:
              long = 0.0
              lat = 0.0
              loc = False

            try:
              phone = update.message.contact.phone_number
              message = ""
              pho = True
            except:
              pho = False


            if(message in commands):

              bot.sendMessage(chat_id=chat_id, text=commands[message])

              if(message=="/trivia"):
                trivia = dbhandler.retrieve_random_trivia()

                if(len(trivia)>0):
                  texttosend = "".join([trivia[0]," (",trivia[1],")"])

                  print("Random Trivia")
                  bot.sendMessage(chat_id=chat_id,text=texttosend)

                else:
                  bot.sendMessage(chat_id=chat_id,text="Sorry, but database not ready")

              elif(message=="/camera" or message=="/cam"):
                thepicfile = raspi_camera_oop3.shoothi()
                if(thepicfile):
                  print("sending pic:",thepicfile)
                  bot.sendMessage(chat_id=chat_id,text=thepicfile)
                  bot.sendPhoto(chat_id=chat_id, photo=open(thepicfile, 'rb'))
                else:
                  bot.sendMessage(chat_id=chat_id,text="Sorry, but camera is not ready :( Please wire connections")
              elif(message=="/reboot"):
                if(db.contains(db_status.content=='running')):
                  db.update({'content':'rebooted'},db_status.content=="running")
                #time.sleep(0.5) #takes time to update db
                  bot.sendMessage(chat_id=chat_id, text="Goodbye now")
                  restart()
                  break
                else:
                  bot.sendMessage(chat_id=chat_id, text="Old reboot command, not restarting")
              elif(message=="/callcouncil"):
                  print("You will be called")
                  texttosend = fname + ", please send your mobile number to contact you"
                  kb = [[telegram.KeyboardButton('Send my number', request_contact=True)],[telegram.KeyboardButton('No')]]
                  kb_markup = telegram.ReplyKeyboardMarkup(kb)             
                  bot.sendMessage(chat_id=chat_id, text=texttosend, reply_markup=kb_markup)
              elif(message=="/violence"):
                  service = "Press to dial Call Safe Steps on [+611800015188](tel:+611800015188)"
                  bot.sendMessage(chat_id=chat_id, text=service, parse_mode='Markdown')

              elif(message=="/childcare"): #feed the cat 192.168.1.122
                  print("ga")
                  texttosend = "Do you want to send your current location, " +fname+"?"
                  kb = [[telegram.KeyboardButton('Yes', request_location=True)],[telegram.KeyboardButton('No')]]
                  kb_markup = telegram.ReplyKeyboardMarkup(kb)             
                  bot.sendMessage(chat_id=chat_id, text=texttosend, reply_markup=kb_markup)
#                keyboard = [[telegram.InlineKeyboardButton("Option 
#                1",callback='1')], 
#                [telegram.InlineKeyboardButton("Option 
#                2",callback='2')], 
#                [telegram.InlineKeyboardButton("Option 
#                3",callback='3')]] 

#                kb_markup = telegram.InlineKeyboardMarkup(keyboard) 
#                bot.sendMessage(chat_id=chat_id, text=texttosend, 
#                reply_markup=kb_markup) bot.reply_text('Please 
#                choose:', reply_markup=kb_markup)

              elif(message=="/news"):
                  h = xmltopnews.getnews(news_id)
                  news_id +=1
                  text_to_send = "".join(["News Headline ",str(news_id) , ": ", h[2]])
                  bot.sendMessage(chat_id=chat_id, text=text_to_send)
                  bot.sendMessage(chat_id=chat_id, text=h[1])
                  if(news_id>20):
                    news_id=0
              else:
                  print("do nothing")
            elif (list_compare(magic_words, message_list)!= -1):
            #search = message_list[list_compare(magic_words, message_list)-1]
            #url='http://lmgtfy.com/?q='+search
            #bot.sendMessage(chat_id=chat_id,text=url)
              try:
                  print(message_list)         
              except:
                  message_list=""
   
              if("fire" in message_list or "burn" in message_list or "burning" in message_list):
                  print("Sending fireman!")
                  texttosend = "I am sending FIREMAN to your location now" + "\n"
                  URL = "https://www.casey.vic.gov.au/health-safety/emergency/emergency-contact"
                  texttosend = "".join([texttosend,URL])

                  bot.sendMessage(chat_id=chat_id, text=texttosend)

              elif("accident" in message_list or "sick" in message_list or "dying" in message_list or "died" in message_list):
                  print("Sending ambulance")
                  texttosend = "I am sending AMBULANCE to your location now" + "\n"
                  URL = "https://www.casey.vic.gov.au/health-safety/emergency/emergency-contact"
                  texttosend = "".join([texttosend,URL])

                  bot.sendMessage(chat_id=chat_id, text=texttosend)

              elif("violence" in message_list or "theft" in message_list or "thief" in message_list or "rape" in message_list or "kill" in message_list or "burglar" in message_list or "steal" in message_list):
                  print("Sending police")
                  texttosend = "I am sending POLICE to your location now"+ "\n"
                  URL = "https://www.casey.vic.gov.au/health-safety/emergency/emergency-contact"
                  texttosend = "".join([texttosend,URL])

                  bot.sendMessage(chat_id=chat_id, text=texttosend)

              else:
                  print("Please pick service to send")
                  keyboard = [[telegram.InlineKeyboardButton("Police",callback_data="1")], 
                  [telegram.InlineKeyboardButton("Ambulance",callback_data="2")], 
                  [telegram.InlineKeyboardButton("Fire Brigade",callback_data="3")], 
                  [telegram.InlineKeyboardButton("Dial 000",callback_data="4")]] 
                  texttosend = "Which service do you want us to send?"
                  kb_markup = telegram.InlineKeyboardMarkup(keyboard) 
                  bot.sendMessage(chat_id=chat_id, text=texttosend, reply_markup=kb_markup)
            elif(message=="no"):
              print("Do nothing")                
            elif(("hello" in message) or ("hi" in message) or ("good morning" in message) or ("good afternoon" in message) or ("good day" in message)):
              print("error here!")
              texttosend = "Hi " + fname + "! My name is Cassandra.\nI am your City of Casey virtual council assistant.\nHow can I help you? Type /help if you need anything."
              bot.sendMessage(chat_id=chat_id, text=texttosend)
            elif("bye" in message or "goodbye" in message or "see ya" in message or "see you" in message):
              texttosend = "Goodbye, " + fname +"! Have a good day!"
              bot.sendMessage(chat_id=chat_id, text=texttosend)
            elif("how are you" in message or "how is it going" in message or "how are you going" in message or "how do you do" in message):
              texttosend = "I am well, and so are members of the council\nHow can I help you? Type /help if you need anything."
              bot.sendMessage(chat_id=chat_id, text=texttosend)
            elif("name" in message):
              texttosend = "My name is Cassandra. I am a bot. I know your name is " + fname + " " + lname
              bot.sendMessage(chat_id=chat_id, text=texttosend)
            elif(pho):
                 print("Your phone number is " + phone)
                 texttosend = "Thank you " + fname + ". Our council member will contact you on " + phone
                 bot.sendMessage(chat_id=chat_id, text=texttosend)
            elif(loc):
              try:
                 print("gaga: ", lat, long)
                 t = caseydbhandler.closestChildCare(lat, long)
                 text1 = "".join([t[0]['name'],"\n",t[0]['address'],"\n",t[0]['telephone'],"\nDistance: ",t[0]['distance'], "km"])
                 text2 = "".join([t[1]['name'],"\n",t[1]['address'],"\n",t[1]['telephone'],"\nDistance: ",t[1]['distance'], "km"])
                 text3 = "".join([t[2]['name'],"\n",t[2]['address'],"\n",t[2]['telephone'],"\nDistance: ",t[2]['distance'],"km"])

                 texttosend = "".join(["1. ",text1,"\n2. ",text2,"\n3. ",text3])
                 bot.sendMessage(chat_id=chat_id, text=texttosend)
              except:
                  print("error!")
              loc = False
            else:
              bot.sendMessage(chat_id=chat_id, text="Sorry, I do not know the answer. Do you want talk to a real person? Type /help anytime")

        LAST_UPDATE_ID = update.update_id + 1
        db.update({'content':'running'},db_status.content=="rebooted")


if __name__ == '__main__':
    main()
