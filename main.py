import os
import parser
import sqlite3
from aiogram import Bot,Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Dispatcher, Bot, executor, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import InputFile, ParseMode

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,Message, ReplyKeyboardRemove,InlineKeyboardMarkup,InlineKeyboardButton,CallbackQuery
import captcha_func
TOKEN = "5098506729:AAEOPBp7RWfNWw9-R1iaI4OHH-_WFg6e2d8"
conn = sqlite3.Connection("shop_originals.db", check_same_thread=False)

# DB connection
cursor = conn.cursor()
#
# Bot connection
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class Captchas(StatesGroup):
    start = State()
    cc = State()

class Submit(StatesGroup):
    teleg = State()
    twitter =State()
    tiktok = State()
    cyc = State()

cursor.execute("CREATE TABLE IF NOT EXISTS users(id integer primary key,username varchar,user_id integer)")
cursor.execute("CREATE TABLE IF NOT EXISTS user_data(id integer primary key,user_id integer,telegram varchar,twitter varchar,wallet varchar)")
conn.commit()


@dp.message_handler(commands=["start", "menu"], state='*')
async def start(message: types.Message, state: FSMContext):
    uid = message.from_user.id
    print(message)
    cursor.execute("SELECT * from users where user_id = ?",(uid,))
    results = cursor.fetchall()
    ref_uids = 0

    if results:
        await state.finish()
        await message.answer("""Hello, {}! I am your friendly CYC airdrop bot

           Please complete the required tasks to qualify for the airdrop tokens.

           Value: $200000CYCOIN (1 CYCOIN=0.62$)
           👥 For every referral - get - 5 CYCOIN (limit is 100 CYCOIN)
           💸 For joining - get - 20 CYCOIN
           📅 Distribution dates: January 17, 2022 to January 25, 2022
           Official website: http://www.cyshushi.com
           White Paper: https://urlzs.com/4yFjJ

           📃 Information
             CYCLEBASE is focused on building a decentralized platform for global energy mining, running decentralized energy trading and carbon indexed emissions, and global carbon coordination, using fairer and market friendly prices for mining and delivery of carbon energy markets.

           Its mission is to provide a more efficient application scenario and equal environment for global carbon emission schemes through the popularization of blockchain applications.

           Click "Join Airdrop" to continue""".format(message.from_user.username),reply_markup=await join_key())
    else:
        if len(message.text) > 8:
            print(message)
            ref_uid = message.text.split(" ")
            ref_uids = int(ref_uid[1])
            await state.update_data( ref_uid=ref_uids)
        captcha_text = captcha_func.create_random_captcha_text(4)
        captcha_func.generate_image(captcha_text)
        img_dir = InputFile("{}.png".format(captcha_text))
        await bot.send_photo(message.from_user.id, photo=img_dir, caption="❇️ Enter the captcha:")
        await state.update_data(captcha_txt=captcha_text)
        await Captchas.cc.set()

@dp.message_handler(commands=["excel_file_get"], state='*')
async def start(message: types.Message, state: FSMContext):
    name = captcha_func.generate_excel()
    await message.answer_document(open(name,'rb'))

@dp.message_handler(lambda message:message.text == "🚫 Cancel",state='*')
async def join_airdrop(message:types.Message,state:FSMContext):
    await message.answer("""📢 Airdrop rules

 ✏️ Missions that must be completed.
        🔹Join our Telegraph Channel (https://t.me/+PQ7l37XRczM1ZDVh)
        🔹Join our Telegraph group (https://t.me/+i976_ZdIZZxhNDhh)
        🔹Follow our Twitter (https://twitter.com/dougnewell2) page and retweet nailed posts and @threepeople
        🔹Follow our Tiktok(XXXX)duet with our pin videos

Complete all tasks, then click "Submit Details" to verify you've completed your task.""",disable_web_page_preview=True,parse_mode=ParseMode.HTML,
                         reply_markup=await menu_key())
    await state.finish()

@dp.message_handler(state=Captchas.start,content_types=types.ContentTypes.TEXT)
async def check_captcha(message:types.Message,state:FSMContext):
    captcha_text = captcha_func.create_random_captcha_text(4)
    captcha_func.generate_image(captcha_text)
    img_dir = InputFile("{}.png".format(captcha_text))
    await bot.send_photo(message.from_user.id, photo=img_dir, caption="❇️ Enter the captcha:")
    await state.update_data(captcha_txt=captcha_text)
    await Captchas.cc.set()




@dp.message_handler(state=Captchas.cc,content_types=types.ContentTypes.TEXT)
async def check_captcha(message:types.Message,state:FSMContext):
    txt = await state.get_data()

    txts = txt['captcha_txt']
    print(txt)
    if message.text == txts:
        if len(txt)>1:
            cursor.execute("Update user_data set total_ref = total_ref+1, ref_balance = ref_balance + 5 where user_id = ?",(txt['ref_uid'],))
            conn.commit()
            cursor.execute("INSERT INTO users(username,user_id,ref_user_id) values (?,?,?)",(message.from_user.username,message.from_user.id,txt['ref_uid'],))
            conn.commit()
        else:
            cursor.execute("INSERT INTO users(username,user_id) values (?,?)",
                           (message.from_user.username, message.from_user.id,))
            conn.commit()
        os.remove('{}.png'.format(txts))
        await message.answer("""Hello, {}! I am your friendly CYC airdrop bot

           Please complete the required tasks to qualify for the airdrop tokens.

           Value: $200000CYCOIN (1 CYCOIN=0.62$)
           👥 For every referral - get - 5 CYCOIN (limit is 100 CYCOIN)
           💸 For joining - get - 20 CYCOIN
           📅 Distribution dates: January 17, 2022 to January 25, 2022
           Official website: http://www.cyshushi.com
           White Paper: https://urlzs.com/4yFjJ

           📃 Information
             CYCLEBASE is focused on building a decentralized platform for global energy mining, running decentralized energy trading and carbon indexed emissions, and global carbon coordination, using fairer and market friendly prices for mining and delivery of carbon energy markets.

           Its mission is to provide a more efficient application scenario and equal environment for global carbon emission schemes through the popularization of blockchain applications.

           Click "Join Airdrop" to continue""".format(message.from_user.username), reply_markup=await join_key())
        await state.finish()
    else:
        await message.answer("Wrong captcha try again")
        captcha_text = captcha_func.create_random_captcha_text(4)
        captcha_func.generate_image(captcha_text)
        img_dir = InputFile("{}.png".format(captcha_text))
        await bot.send_photo(message.from_user.id, photo=img_dir, caption="❇️ Enter the captcha:")
        await state.update_data(captcha_txt=captcha_text)
        await Captchas.cc.set()


@dp.message_handler(lambda message:message.text == "🔝 Main Menu")
async def join_airdrop(message:types.Message):
    uid = message.from_user.id
    cursor.execute("SELECT * from users where user_id = ?", (uid,))
    results = cursor.fetchall()
    if uid in results[0]:
        await message.answer("""Hello, {}! I am your friendly CYC airdrop bot

           Please complete the required tasks to qualify for the airdrop tokens.

           Value: $200000CYCOIN (1 CYCOIN=0.62$)
           👥 For every referral - get - 5 CYCOIN (limit is 100 CYCOIN)
           💸 For joining - get - 20 CYCOIN
           📅 Distribution dates: January 17, 2022 to January 25, 2022
           Official website: http://www.cyshushi.com
           White Paper: https://urlzs.com/4yFjJ

           📃 Information
             CYCLEBASE is focused on building a decentralized platform for global energy mining, running decentralized energy trading and carbon indexed emissions, and global carbon coordination, using fairer and market friendly prices for mining and delivery of carbon energy markets.

           Its mission is to provide a more efficient application scenario and equal environment for global carbon emission schemes through the popularization of blockchain applications.

           Click "Join Airdrop" to continue""".format(message.from_user.username), reply_markup=await join_key())



@dp.message_handler(lambda message:message.text == "✅ Join Airdrop")
async def join_airdrop(message:types.Message):
    await message.answer("""📢 Airdrop rules

 ✏️ Missions that must be completed.
        🔹Join our Telegraph Channel (https://t.me/+PQ7l37XRczM1ZDVh)
        🔹Join our Telegraph group (https://t.me/+i976_ZdIZZxhNDhh)
        🔹Follow our Twitter (https://twitter.com/dougnewell2) page and retweet nailed posts and @threepeople
        🔹Follow our Tiktok(XXXX)duet with our pin videos

Complete all tasks, then click "Submit Details" to verify you've completed your task.""",disable_web_page_preview=True,parse_mode=ParseMode.HTML,reply_markup=await menu_key())




@dp.message_handler(lambda message:message.text == "✍️Submit Details")
async def join_airdrop(message:types.Message):
    await message.answer("""🔹 Join our Telegram <a href = 'https://t.me/Cyclebas_CYC'><b>Channel</b></a> & <a href = 'https://t.me/Cyclebas_cyc01'><b>Group</b></a>

Submit your Telegram username, with (@)""",parse_mode=ParseMode.HTML,disable_web_page_preview=True, reply_markup=await cancel_key())
    await Submit.teleg.set()


@dp.message_handler(lambda message:message.text == "🔙 Back⠀")
async def check_captcha(message:types.Message,state:FSMContext):
    await message.answer("""📢 Airdrop rules

 ✏️ Missions that must be completed.
        🔹Join our Telegraph Channel (https://t.me/+PQ7l37XRczM1ZDVh)
        🔹Join our Telegraph group (https://t.me/+i976_ZdIZZxhNDhh)
        🔹Follow our Twitter (https://twitter.com/dougnewell2) page and retweet nailed posts and @threepeople
        🔹Follow our Tiktok(XXXX)duet with our pin videos

Complete all tasks, then click "Submit Details" to verify you've completed your task.""",
                         parse_mode=ParseMode.HTML,disable_web_page_preview=True,
                         reply_markup=await menu_key())

@dp.message_handler(lambda message:message.text == "🔙 Back⠀⠀")
async def check_captcha(message:types.Message,state:FSMContext):
    await message.answer("""Hello, {}! I am your friendly CYC airdrop bot

           Please complete the required tasks to qualify for the airdrop tokens.

           Value: $200000CYCOIN (1 CYCOIN=0.62$)
           👥 For every referral - get - 5 CYCOIN (limit is 100 CYCOIN)
           💸 For joining - get - 20 CYCOIN
           📅 Distribution dates: January 17, 2022 to January 25, 2022
           Official website: http://www.cyshushi.com
           White Paper: https://urlzs.com/4yFjJ

           📃 Information
             CYCLEBASE is focused on building a decentralized platform for global energy mining, running decentralized energy trading and carbon indexed emissions, and global carbon coordination, using fairer and market friendly prices for mining and delivery of carbon energy markets.

           Its mission is to provide a more efficient application scenario and equal environment for global carbon emission schemes through the popularization of blockchain applications.

           Click "Join Airdrop" to continue""".format(message.from_user.username), reply_markup=await join_key())


@dp.message_handler(state=Submit.teleg,content_types=types.ContentTypes.TEXT)
async def check_captcha(message:types.Message,state:FSMContext):
    await state.update_data(teleg = message.text)
    await message.answer("""🔹️ Follow our Twitter page and retweet pinned posts and @three people

Submit your Twitter profile link (Example: https://www.twitter.com/yourusername)""",disable_web_page_preview=True,reply_markup=await cancel_key())
    await Submit.twitter.set()


@dp.message_handler(state=Submit.twitter,content_types=types.ContentTypes.TEXT)
async def check_captcha(message:types.Message,state:FSMContext):
    await state.update_data(twitter = message.text)
    await message.answer("""🔹 Follow our official Tiktok account and post duet videos

Submit a link to the Tiktok duet video you posted (e.g. https://vm.tiktok.com/TTPdrPBJGJ/)""")
    await Submit.tiktok.set()


@dp.message_handler(state=Submit.tiktok,content_types=types.ContentTypes.TEXT)
async def check_captcha(message:types.Message,state:FSMContext):
    await state.update_data(tiktok = message.text)

    await message.answer("""Select BSC main chain in TP wallet, add CYC token contract address, then add CYC to the wallet and send CYC receipt address to the airdrop bot. 

    ✅ Video Guideline: https://youtu.be/eSFmA48UJow

    CYC Contract Address：0x909aa6E4C6f8bc49263321092Ba41c6Ea3F8a9a4""", disable_web_page_preview=True,
                         reply_markup=await cancel_key())

    await Submit.cyc.set()
@dp.message_handler(state=Submit.cyc,content_types=types.ContentTypes.TEXT)
async def check_captcha(message:types.Message,state:FSMContext):
    await state.update_data(cyc = message.text)
    await message.answer("""🌟 Congratulations, {}- 🌟

🎉 You've received 50 CYC for completing airdrop tasks

💳 CYC tokens will be distributed uniformly at the end of the event, please pay attention to the telegraph group announcement information

⚠️ Note: If you submitted any wrong information please click /start to resubmit correctly.""".format(message.from_user.username),reply_markup=await menu_balance())
    res = await state.get_data()
    cursor.execute("SELECT * from user_data where user_id = ?",(message.from_user.id,))
    have_no = cursor.fetchall()
    if have_no:
        cursor.execute("Update user_data set telegram = ? , twitter = ?,tiktok =?, wallet=? where user_id = ?",(res['teleg'],res['twitter'],res['tiktok'],res['cyc'],message.from_user.id,))
        conn.commit()
    else:
        cursor.execute("INSERT INTO user_data(user_id,telegram,twitter,tiktok,wallet) values (?,?,?,?,?)",(message.from_user.id,res['teleg'],res['twitter'],res['tiktok'],res['cyc'],))
        conn.commit()
    cursor.execute("SELECT ref_user_id from users where user_id = ?",(message.from_user.id,))
    ref_user_id = cursor.fetchall()
    if int(ref_user_id[0][0])>1:
        ref_user_id = ref_user_id[0][0]
        await bot.send_message(chat_id=ref_user_id,text="{} user has finished all tasks".format(message.from_user.id))
    await state.finish()



@dp.message_handler(lambda message:message.text == '🔝 Main Menu')
async def check_captcha(message:types.Message,state:FSMContext):
    await message.answer("""Hello, {}! I am your friendly CYC airdrop bot

           Please complete the required tasks to qualify for the airdrop tokens.

           Value: $200000CYCOIN (1 CYCOIN=0.62$)
           👥 For every referral - get - 5 CYCOIN (limit is 100 CYCOIN)
           💸 For joining - get - 20 CYCOIN
           📅 Distribution dates: January 17, 2022 to January 25, 2022
           Official website: http://www.cyshushi.com
           White Paper: https://urlzs.com/4yFjJ

           📃 Information
             CYCLEBASE is focused on building a decentralized platform for global energy mining, running decentralized energy trading and carbon indexed emissions, and global carbon coordination, using fairer and market friendly prices for mining and delivery of carbon energy markets.

           Its mission is to provide a more efficient application scenario and equal environment for global carbon emission schemes through the popularization of blockchain applications.

           Click "Join Airdrop" to continue""".format(message.from_user.username), reply_markup=await join_key())

@dp.message_handler(lambda message:message.text == "🔗Referral Link")
async def check_captcha(message:types.Message,state:FSMContext):
    ref_link = 'https://t.me/RTB_airdrop_bot?start={}'.format(message.from_user.id)
    await message.answer("""💥 Congratulations, {}

🎉 Share this link with your friends and earn 5 CYC for each referral!

👥 Your Referral Link is: {}

❗️IMPORTANT: You get a reward only if your referrals have completed mandatory tasks.""".format(message.from_user.username,ref_link),reply_markup=await menu_balance())
    await state.finish()


@dp.message_handler(lambda message:message.text == "💰Balance")
async def check_captcha(message:types.Message,state:FSMContext):
    cursor.execute("SELECT * FROM user_data where user_id = ?",(message.from_user.id,))
    res = cursor.fetchall()
    cursor.execute("SELECT balance from users where user_id = ?",(message.from_user.id,))
    balance = cursor.fetchone()
    await message.answer("""💰Airdrop Reward Bonus Balance: <b>{}</b> CYC

📊 Referral Balance: <b>{}</b> CYC for referrals will be manually verified by the airdrop manager at the end of the airdrop.


 👥 People invited: {}

Your Submitted details:
-------------------
👨‍✈️ Telegram: {}
💬 Twitter: {}
✨ TikTok: {}
🏦 Wallet: {}

✍️If your submitted data is incorrect then please restart the bot and resubmit the data again by clicking /start before airdrop end date.""".format(balance[0],res[0][7],res[0][6],res[0][2],res[0][3],res[0][4],res[0][5]),parse_mode=ParseMode.HTML)


@dp.message_handler()
async def trash(message:types.Message):
    await message.answer("""❌ Unknown Command!

You have send a Message directly into the Bot's chat or
Menu structure has been modified by Admin.

ℹ️ Do not send Messages directly to the Bot or
reload the Menu by pressing /start""")
async def join_key():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('✅ Join Airdrop')
    return  markup

async def menu_key():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('✍️Submit Details')
    markup.add('🔙 Back⠀⠀','🔝 Main Menu')
    return markup

async def menu_balance():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('💰Balance','🔗Referral Link')
    markup.add('🔙 Back⠀','🔝 Main Menu')
    return  markup

async def cancel_key():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('🚫 Cancel')
    return markup

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)