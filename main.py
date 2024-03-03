import asyncio
import logging
import sys
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message, CallbackQuery
from aiogram.filters.command import Command
from redis.asyncio import Redis

from config import *
import kb
from states import *
from db import DB
db = DB()

redis = Redis(
    username=REDIS_USER,
    host=REDIS_HOST,
    port=REDIS_PORT,
    # db=REDIS_DB,
    password=REDIS_PASSWORD
)
storage = RedisStorage(redis)

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)

logging.basicConfig(filename="all.log", level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(filename)s function: %(funcName)s line: %(lineno)d - %(message)s')
errors = logging.getLogger("errors")
errors.setLevel(logging.ERROR)
fh = logging.FileHandler("errors.log")
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(filename)s function: %(funcName)s line: %(lineno)d - %(message)s')
fh.setFormatter(formatter)
errors.addHandler(fh)


def top(word: str, top_dict: dict) -> str:
    st = ''
    for i, j in top_dict.items():
        st += f'{i}) {j["name"]} — <b>{j["count"]}</b> <i>{word}</i>.\n'
    return st


# Главная ==============================================================================================================
@dp.message(Command('start'))
async def start(message: Message, state: FSMContext):
    try:
        await state.clear()
        if not await db.user_exists(str(message.from_user.id)):
            sp = message.text.split()
            if len(sp) > 1:
                user_id = sp[1]
                await db.update_refs(str(user_id))
                await db.update_points(str(user_id), 1)
                if bool(await db.select_notifications(user_id)):
                    await bot.send_message(user_id, 'Kimdir havolangiz orqali botga qo‘shildi!')
                    if await db.select_refs(user_id) % 10 == 0:
                        await bot.send_message(user_id, 'Sozlamalarda yangi murojaatlar haqidagi bildirishnomalarni o`chirib qo`yishingiz mumkin.')
            await message.answer(f'VibeLinega chatga xush kelibsiz!\n'
                                 f'Muloqotni boshlashdan oldin siz roʼyxatdan oʼtishingiz kerak.\n'
                                 f'Roʼyxatdan oʼtganingizdan soʼng siz bir hafta bepul <b>VIP taʼrifiga ega boʼlasiz!</b>\n'
                                 f'Botdan foydalanishni davom ettirish orqali siz qoidalarga rozilik bildirasiz.\n',
                                 reply_markup=kb.lobby_kb, parse_mode='HTML')
        else:
            await message.answer(f'Salom, {await db.select_name(str(message.from_user.id))}.', reply_markup=kb.main_kb)
    except Exception as e:
        errors.error(e)


@dp.callback_query(F.data == 'to_main')
async def call_start(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=f'Salom, {await db.select_name(str(call.from_user.id))}.',
                                    reply_markup=kb.main_kb)
    except Exception as e:
        errors.error(e)


# Лобби ================================================================================================================
@dp.callback_query(F.data == 'lobby')
async def lobby(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=f'VibeLinega xush kelibsiz!\n'
                                         f'Muloqotni boshlashdan oldin siz roʼyxatdan oʼtishingiz kerak.\n'
                                         f'Roʼyxatdan oʼtganingizdan soʼng siz bir hafta bepul <b>VIP taʼrifiga ega boʼlasiz!</b>\n'
                                         f'Botdan foydalanishni davom ettirish orqali siz qoidalarga rozilik bildirasiz.\n',
                                    reply_markup=kb.lobby_kb, parse_mode='HTML')
    except Exception as e:
        errors.error(e)


@dp.message(Command('help'))
async def help(message: Message):
    try:
        await message.answer(f'/start - Boshlash')
    except Exception as e:
        errors.error(e)


@dp.message(Command('bug'))
async def bug(message: Message, state: FSMContext):
    try:
        await message.answer('Siz duch kelgan xatoni tasvirlab bering.')
        await state.set_state(Bug.bug)
    except Exception as e:
        errors.error(e)


@dp.message(Bug.bug)
async def set_bug(message: Message, state: FSMContext):
    try:
        sender = message.from_user.id if message.from_user.username is None else f'@{message.from_user.username}'
        await bot.send_message(BUGS_GROUP_ID, f'Yuboruvchi: {sender}.\n'
                                              f'Xabar: {message.text}.')
        await message.answer('Dasturchi muammo haqida xabardor qilingan va tez orada uni tuzatadi..\n'
                             'Yordamingiz uchun rahmat!')
        await state.clear()
    except Exception as e:
        errors.error(e)


@dp.message(Command('idea'))
async def idea(message: Message, state: FSMContext):
    try:
        await message.answer('Nima taklif qilmoqchisiz?')
        await state.set_state(Idea.idea)
    except Exception as e:
        errors.error(e)


@dp.message(Idea.idea)
async def set_idea(message: Message, state: FSMContext):
    try:
        sender = message.from_user.id if message.from_user.username is None else f'@{message.from_user.username}'
        await bot.send_message(IDEAS_GROUP_ID, f'Yuboruvchi: {sender}.\n'
                                               f'Xabar: {message.text}.')
        await message.answer('Gʻoya dasturchiga yuborildi.\n'
                             'Yordamingiz uchun rahmat!')
        await state.clear()
    except Exception as e:
        errors.error(e)


# Правила ==============================================================================================================
@dp.callback_query(F.data == 'rules')
async def rules(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=f'<b>Taqiqlanadi!:</b>\n'
                                         f'1) Psixoaktiv moddalar (giyohvand moddalar) haqida har qanday eslatma.\n'
                                         f'2) Har qanday 18+ materiallarni almashish, tarqatish.\n'
                                         f'3) Har qanday reklama, spam, har qanday narsani sotish.\n'
                                         f'4) Yomon xatti-harakatlar.\n'
                                         f'5) Telegram qoidalarini buzadigan har qanday harakatlar.\n',
                                    reply_markup=kb.to_lobby_kb, parse_mode='HTML')
    except Exception as e:
        errors.error(e)


# Регистрация ==========================================================================================================
@dp.callback_query(F.data == 'registrate')
async def registrate(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Ismingizni kiriting.')
        await state.set_state(RegState.name)
    except Exception as e:
        errors.error(e)


@dp.message(RegState.name)
async def reg_name(message: Message, state: FSMContext):
    try:
        await state.update_data(name=message.text)
        await message.answer('Yoshingizni kiriting.')
        await state.set_state(RegState.age)
    except Exception as e:
        errors.error(e)


@dp.message(RegState.age)
async def reg_age(message: Message, state: FSMContext):
    try:
        await state.update_data(age=message.text)
        await message.answer('Jinsingizni tanlang.', reply_markup=kb.sex_kb)
        await state.set_state(RegState.sex)
    except Exception as e:
        errors.error(e)


@dp.callback_query(RegState.sex, F.data.endswith('male'))
async def reg_sex(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer()
        await state.update_data(sex=call.data)
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Roʻyxatdan oʻtish yakunlandi.\nSizga 7 kunlik VIP taʼrifi berildi!.', reply_markup=kb.main_kb)
        data = await state.get_data()
        await db.insert_in_users(str(call.from_user.id), data['name'], data['age'], data['sex'],
                                 (datetime.now() + timedelta(days=7)).strftime('%d.%m.%Y %H:%M'))
        await state.clear()
    except Exception as e:
        errors.error(e)


# Профиль ==============================================================================================================
@dp.callback_query(F.data == 'profile')
async def profile(call: CallbackQuery):
    try:
        await call.answer()
        sex = 'Nomaʼlum'
        if await db.select_sex(str(call.from_user.id)) == 'male':
            sex = 'Erkak'
        elif await db.select_sex(str(call.from_user.id)) == 'female':
            sex = 'Ayol'
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=f'🅰️ <b>Ism:</b> <i>{await db.select_name(str(call.from_user.id))}</i>\n'
                                         f'🔞 <b>Yosh:</b> <i>{await db.select_age(str(call.from_user.id))}</i>\n'
                                         f'👫 <b>Jins:</b> <i>{sex}</i>',
                                    reply_markup=kb.profile_kb, parse_mode='HTML')
    except Exception as e:
        errors.error(e)


# Настройки ============================================================================================================
@dp.callback_query(F.data == 'settings')
async def settings(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Nimani oʻzgartirmoqchisiz?', reply_markup=kb.settings_kb)
    except Exception as e:
        errors.error(e)


# Имя ==================================================================================================================
@dp.callback_query(F.data == 'name')
async def edit_name(call: CallbackQuery, state: FSMContext):
    try:
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Ismingizni kiriting.')
        await state.set_state(NameState.name)
    except Exception as e:
        errors.error(e)


@dp.message(NameState.name)
async def set_name(message: Message, state: FSMContext):
    try:
        await db.update_name(str(message.from_user.id), message.text)
        await message.answer(text='Ism saqlandi.', reply_markup=kb.to_settings_kb)
        await state.clear()
    except Exception as e:
        errors.error(e)


# Возраст ==============================================================================================================
@dp.callback_query(F.data == 'age')
async def edit_age(call: CallbackQuery, state: FSMContext):
    try:
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Yoshingizni kiriting.')
        await state.set_state(AgeState.age)
    except Exception as e:
        errors.error(e)


@dp.message(AgeState.age)
async def set_age(message: Message, state: FSMContext):
    try:
        await db.update_age(str(message.from_user.id), message.text)
        await message.answer('Yosh saqlandi.', reply_markup=kb.to_settings_kb)
        await state.clear()
    except Exception as e:
        errors.error(e)


# Пол ==================================================================================================================
@dp.callback_query(F.data == 'sex')
async def edit_sex(call: CallbackQuery, state: FSMContext):
    try:
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Jinsingizni tanlang.', reply_markup=kb.sex_kb)
        await state.set_state(SexState.sex)
    except Exception as e:
        errors.error(e)


@dp.callback_query(SexState.sex, F.data.endswith('male'))
async def set_sex(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer()
        await db.update_sex(str(call.from_user.id), call.data)
        await bot.send_message(call.from_user.id, 'Jins saqlandi.', reply_markup=kb.to_settings_kb)
        await state.clear()
    except Exception as e:
        errors.error(e)


# Статистика ===========================================================================================================
@dp.callback_query(F.data == 'stats')
async def stats(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=f'💬 Suhbatlar: {await db.select_chats(str(call.from_user.id))}\n'
                                         f'⌨️ Xabarlar: {await db.select_messages(str(call.from_user.id))}\n'
                                         f'👍 Layklar: {await db.select_likes(str(call.from_user.id))}\n'
                                         f'👎 Dislayklar: {await db.select_dislikes(str(call.from_user.id))}\n'
                                         f'👨‍💻 Foydalanuvchilar taklifi: {await db.select_refs(str(call.from_user.id))}',
                                    reply_markup=kb.statistic_kb)
    except Exception as e:
        errors.error(e)


# Рефералка ============================================================================================================
@dp.callback_query(F.data == 'ref')
async def ref(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=f'Ega boʼlish qilish uchun havolani ulashing 💎.\n'
                                         f'1ta referal = 1ta 💎.\n'
                                         f'5 💎 = 1 kunlik VIP statusi 👑.\n'
                                         f'Sizda {await db.select_points(str(call.from_user.id))} 💎.\n\n'
                                         f'🆔 Sizning havolangiz:\n'
                                         f'{f"{RETURN_URL}?start=" + str(str(call.from_user.id))}.',
                                    disable_web_page_preview=True,
                                    reply_markup=kb.ref_kb(await db.select_notifications(str(call.from_user.id))))
    except Exception as e:
        errors.error(e)


# Обмен 💎 =============================================================================================================
@dp.callback_query(F.data == 'trade')
async def trade(call: CallbackQuery):
    try:
        if await db.select_points(str(call.from_user.id)) >= 5:
            await db.update_points(str(call.from_user.id), -5)
            if await db.select_vip_ends(str(call.from_user.id)) is None:
                await db.update_vip_ends((datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y %H:%M'),
                                         str(call.from_user.id))
                await call.answer('Muvaffaqiyatli!')
            else:
                await db.update_vip_ends(
                    (datetime.strptime(await db.select_vip_ends(str(call.from_user.id)), '%d.%m.%Y %H:%M') +
                     timedelta(days=1)).strftime('%d.%m.%Y %H:%M'), str(call.from_user.id))
            await call.answer('Muvaffaqiyatli!')
        else:
            await call.answer('Ballaringiz yetarli emas.')
    except Exception as e:
        errors.error(e)


# Уведомления ==========================================================================================================
@dp.callback_query(F.data == 'on')
async def notifications_on(call: CallbackQuery):
    try:
        await call.answer()
        await db.update_notifications(str(call.from_user.id), 1)
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Bildirishnomalar yoqilgan.', reply_markup=kb.to_ref_kb)
    except Exception as e:
        errors.error(e)


@dp.callback_query(F.data == 'off')
async def notifications_off(call: CallbackQuery):
    try:
        await call.answer()
        await db.update_notifications(str(call.from_user.id), 0)
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Bildirishnomalar oʼchirilgan.', reply_markup=kb.to_ref_kb)
    except Exception as e:
        errors.error(e)


# Топы =================================================================================================================
@dp.callback_query(F.data == 'tops')
async def tops(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Quyida turli mezonlarga asoslangan reytinglar keltirilgan..', reply_markup=kb.top_kb)
    except Exception as e:
        errors.error(e)


@dp.callback_query(F.data == 'top_messages')
async def top_messages(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=top('xabarlar', await db.top_messages()), reply_markup=kb.to_tops_kb,
                                    parse_mode='HTML')
    except Exception as e:
        errors.error(e)


@dp.callback_query(F.data == 'top_likes')
async def top_likes(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=top('Layklar', await db.top_likes()), reply_markup=kb.to_tops_kb,
                                    parse_mode='HTML')
    except Exception as e:
        errors.error(e)


@dp.callback_query(F.data == 'top_refs')
async def top_refs(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=top('referallar', await db.top_refs()), reply_markup=kb.to_tops_kb,
                                    parse_mode='HTML')
    except Exception as e:
        errors.error(e)


# Вип ==================================================================================================================
@dp.callback_query(F.data == 'vip')
async def vip(call: CallbackQuery):
    try:
        await call.answer()
        if await db.select_vip_ends(str(call.from_user.id)) is not None:
            if datetime.strptime(await db.select_vip_ends(str(call.from_user.id)), '%d.%m.%Y %H:%M') > datetime.now():
                delta = datetime.strptime(await db.select_vip_ends(str(call.from_user.id)),
                                          '%d.%m.%Y %H:%M') - datetime.now()
                await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            text=f'VIP taʼrif tugashiga {delta.days} kun, {delta.seconds // 3600} soat, {delta.seconds // 60 % 60} daqiqa qoldi!.',
                                            reply_markup=kb.vip_kb)
            else:
                await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            text=f'VIP sizga quyidagi imkoniyatlarni beradi:\n'
                                                 f'1) Jins boʼyicha qidirish.\n'
                                                 f'2) Suhbatdosh haqida batafsil maʼlumot: sharhlar, ism, jins, yosh.\n'
                                                 f'<b>Hozir toʼlovlar test rejimida, yaʼni pul qabul qilinmaydi, lekin siz VIP ololasiz..</b>',
                                            reply_markup=kb.vip_kb, parse_mode='HTML')
        else:
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=f'VIP sizga quyidagi imkoniyatlarni beradi:\n'
                                             f'1) Jins boʼyicha qidirish.\n'
                                             f'2) Suhbatdosh haqida batafsil maʼlumot: sharhlar, ism, jins, yosh.\n'
                                             f'<b>Hozir toʼlovlar test rejimida, yaʼni pul qabul qilinmaydi, lekin siz VIP ololasiz..</b>',
                                        reply_markup=kb.vip_kb, parse_mode='HTML')
    except Exception as e:
        errors.error(e)



# Поиск ================================================================================================================
@dp.callback_query(F.data == 'search')
async def search(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer()
        await db.insert_in_queue(str(call.from_user.id), await db.select_sex(str(call.from_user.id)))
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Suhbatdosh qidirmoqdamiz... 🔍', reply_markup=kb.cancel_search_kb)
        while True:
            await asyncio.sleep(0.5)
            if await db.find_chat(str(call.from_user.id)) is not None:
                await db.update_connect_with(str(call.from_user.id), await db.find_chat(str(call.from_user.id)))
                break
        while True:
            await asyncio.sleep(0.5)
            if await db.select_connect_with(str(call.from_user.id)) is not None:
                await db.delete_from_queue(str(call.from_user.id))
                break
        await bot.send_message(call.from_user.id, 'Siz uchun suhbatdosh topdik 🥳\n'
                                                  '/stop - dialogni toʼxtatish')
        if datetime.strptime(await db.select_vip_ends(str(call.from_user.id)), '%d.%m.%Y %H:%M') > datetime.now():
            sex = 'Nomaʼlum'
            user_id = str(await db.select_connect_with(str(call.from_user.id)))
            if await db.select_sex(user_id) == 'male':
                sex = 'Erkak'
            elif await db.select_sex(user_id) == 'female':
                sex = 'Ayol'
            await bot.send_message(call.from_user.id,
                                   f'🅰️ Ism: {await db.select_name(user_id)}\n'
                                   f'🔞 Yosh: {await db.select_age(user_id)}\n'
                                   f'👫 Jins: {sex}\n'
                                   f'👍: {await db.select_likes(user_id)} 👎: {await db.select_dislikes(user_id)}\n', )
        await state.set_state(Chatting.msg)
    except Exception as e:
        errors.error(e)


# Поиск ♂️ =============================================================================================================
@dp.callback_query(F.data == 'search_man')
async def search_man(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer()
        if datetime.strptime(await db.select_vip_ends(str(call.from_user.id)), '%d.%m.%Y %H:%M') > datetime.now():
            await db.insert_in_queue_vip(str(call.from_user.id), await db.select_sex(str(call.from_user.id)), 'male')
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text='Suhbatdosh qidirmoqdamiz... 🔍', reply_markup=kb.cancel_search_kb)
            while True:
                await asyncio.sleep(0.5)
                if await db.find_chat_vip(str(call.from_user.id), await db.select_sex(str(call.from_user.id)),
                                          'male') is not None:
                    await db.update_connect_with(
                        str(call.from_user.id), await db.find_chat_vip(str(call.from_user.id),
                                                                       await db.select_sex(str(call.from_user.id)),
                                                                       'male'))
                    break
            while True:
                await asyncio.sleep(0.5)
                if await db.select_connect_with(str(call.from_user.id)) is not None:
                    await db.delete_from_queue(str(call.from_user.id))
                    break
            await bot.send_message(call.from_user.id, 'Siz uchun suhbatdosh topdik 🥳\n'
                                                      '/stop - dialogni toʼxtatish')
            sex = 'Nomaʼlum'
            user_id = str(await db.select_connect_with(str(call.from_user.id)))
            if await db.select_sex(user_id) == 'male':
                sex = 'Erkak'
            elif await db.select_sex(user_id) == 'female':
                sex = 'Ayol'
            await bot.send_message(call.from_user.id,
                                   f'🅰️ Ism: {await db.select_name(user_id)}\n'
                                   f'🔞 Yosh: {await db.select_age(user_id)}\n'
                                   f'👫 Jins: {sex}\n'
                                   f'👍: {await db.select_likes(user_id)} 👎: {await db.select_dislikes(user_id)}\n')
            await state.set_state(Chatting.msg)
        else:
            await call.answer()
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text='Jins boʼyihca qidirish faqat VIP foydalanuvchilar uchun mavjud',
                                        reply_markup=kb.sex_search_no_vip_kb)
    except Exception as e:
        errors.error(e)


# Поиск ♀️ =============================================================================================================
@dp.callback_query(F.data == 'search_woman')
async def search_woman(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer()
        if datetime.strptime(await db.select_vip_ends(str(call.from_user.id)), '%d.%m.%Y %H:%M') > datetime.now():
            await db.insert_in_queue_vip(str(call.from_user.id), await db.select_sex(str(call.from_user.id)), 'female')
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text='Suhbatdosh qidirmoqdamiz... 🔍', reply_markup=kb.cancel_search_kb)
            while True:
                await asyncio.sleep(0.5)
                if await db.find_chat_vip(str(call.from_user.id), await db.select_sex(str(call.from_user.id)),
                                          'female') is not None:
                    await db.update_connect_with(
                        str(call.from_user.id), await db.find_chat_vip(str(call.from_user.id),
                                                                       await db.select_sex(str(call.from_user.id)),
                                                                       'female'))
                    break
            while True:
                await asyncio.sleep(0.5)
                if await db.select_connect_with(str(call.from_user.id)) is not None:
                    await db.delete_from_queue(str(call.from_user.id))
                    break
            await bot.send_message(call.from_user.id, 'Siz uchun suhbatdosh topdik 🥳\n'
                                                      '/stop - dialogni toʼxtatish')
            sex = 'Nomaʼlum'
            user_id = str(await db.select_connect_with(str(call.from_user.id)))
            if await db.select_sex(user_id) == 'male':
                sex = 'Erkak'
            elif await db.select_sex(user_id) == 'female':
                sex = 'Ayol'
            await bot.send_message(call.from_user.id,
                                   f'🅰️ Ism: {await db.select_name(user_id)}\n'
                                   f'🔞 Yosh: {await db.select_age(user_id)}\n'
                                   f'👫 Jins: {sex}\n'
                                   f'👍: {await db.select_likes(user_id)} 👎: {await db.select_dislikes(user_id)}\n')
            await state.set_state(Chatting.msg)
        else:
            await call.answer()
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text='Jins orqali qidirish faqat VIP foydalanuvchilar uchun mavjud',
                                        reply_markup=kb.sex_search_no_vip_kb)
    except Exception as e:
        errors.error(e)


# Отменить поиск =======================================================================================================
@dp.callback_query(F.data == 'cancel_search')
async def cancel_search(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Qidiruv bekor qilindi 😥.',
                                    reply_markup=kb.main_kb)
        await db.delete_from_queue(str(call.from_user.id))
    except Exception as e:
        errors.error(e)


# Лайк =================================================================================================================
@dp.callback_query(F.data == 'like')
async def like(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Izohingiz uchun rahmat!', reply_markup=kb.review_kb)
        await db.update_likes(await db.select_last_connect(str(call.from_user.id)))
    except Exception as e:
        errors.error(e)


# Дизлайк ==============================================================================================================
@dp.callback_query(F.data == 'dislike')
async def dislike(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Izohingiz uchun rahmat!', reply_markup=kb.review_kb)
        await db.update_dislikes(await db.select_last_connect(str(call.from_user.id)))
    except Exception as e:
        errors.error(e)


# Ссылка ===============================================================================================================
@dp.message(Chatting.msg, Command('link'))
async def link(message: Message):
    try:
        if message.from_user.username is None:
            await message.answer('Telegram sozlamalaridagi foydalanuvchi nomingizni kiriting!')
        else:
            await bot.send_message(await db.select_connect_with(str(message.from_user.id)),
                                   f'Suhbatdosh foydalanuvchi nomini yubordi: @{message.from_user.username}.')
            await message.answer('Foydalanuvchi nomi yuborildi!')
    except Exception as e:
        errors.error(e)


# Остановить диалог ====================================================================================================
@dp.message(Chatting.msg, Command('stop'))
async def stop(message: Message, state: FSMContext):
    try:
        op_state = FSMContext(
            storage=storage,
            key=StorageKey(
                chat_id=int(await db.select_connect_with(str(message.from_user.id))),
                user_id=int(await db.select_connect_with(str(message.from_user.id))),
                bot_id=bot.id)
        )
        await bot.send_message(message.from_user.id,
                               'Dialog toʼxtatildi 😞\nSuhbatdoshga baho berishingiz mumkin.',
                               reply_markup=kb.search_kb)
        await bot.send_message(await db.select_connect_with(str(message.from_user.id)),
                               'Dialog toʼxtatildi 😞\nSuhbatdoshga baho berishingiz mumkin.',
                               reply_markup=kb.search_kb)
        await db.update_chats(await db.select_connect_with(str(message.from_user.id)))
        await db.update_chats(str(message.from_user.id))
        await db.update_last_connect(await db.select_connect_with(str(message.from_user.id)))
        await db.update_last_connect(str(message.from_user.id))
        await db.update_connect_with(await db.select_connect_with(str(message.from_user.id)), None)
        await db.update_connect_with(str(message.from_user.id), None)
        await state.clear()
        await op_state.clear()
    except Exception as e:
        errors.error(e)


# Общение ==============================================================================================================
@dp.message(Chatting.msg, F.text)
async def chatting_text(message: Message):
    try:
        await bot.send_message(await db.select_connect_with(str(message.from_user.id)), message.text)
        await db.insert_in_messages(str(message.from_user.id), message.from_user.username, message.text,
                                    datetime.now().strftime('%d.%m.%Y %H:%M:%S'))
        await db.update_messages(str(message.from_user.id))
    except Exception as e:
        errors.error(e)


# Фото =================================================================================================================
@dp.message(Chatting.msg, F.photo)
async def chatting_photo(message: Message):
    try:
        await bot.send_photo(await db.select_connect_with(str(message.from_user.id)), message.photo[-1].file_id)
    except Exception as e:
        errors.error(e)


# Видео ================================================================================================================
@dp.message(Chatting.msg, F.video)
async def chatting_video(message: Message):
    try:
        await bot.send_video(await db.select_connect_with(str(message.from_user.id)), message.video.file_id)
    except Exception as e:
        errors.error(e)


# Гиф ==================================================================================================================
@dp.message(Chatting.msg, F.animation)
async def chatting_animation(message: Message):
    try:
        await bot.send_animation(await db.select_connect_with(str(message.from_user.id)), message.animation.file_id)
    except Exception as e:
        errors.error(e)


# Стикер ===============================================================================================================
@dp.message(Chatting.msg, F.sticker)
async def chatting_sticker(message: Message):
    try:
        await bot.send_sticker(await db.select_connect_with(str(message.from_user.id)), message.sticker.file_id)
    except Exception as e:
        errors.error(e)


# Документ =============================================================================================================
@dp.message(Chatting.msg, F.document)
async def chatting_document(message: Message):
    try:
        await bot.send_document(await db.select_connect_with(str(message.from_user.id)), message.document.file_id)
    except Exception as e:
        errors.error(e)


# Аудио ================================================================================================================
@dp.message(Chatting.msg, F.audio)
async def chatting_audio(message: Message):
    try:
        await bot.send_audio(await db.select_connect_with(str(message.from_user.id)), message.audio.file_id)
    except Exception as e:
        errors.error(e)


# Гс ===================================================================================================================
@dp.message(Chatting.msg, F.voice)
async def chatting_voice(message: Message):
    try:
        await bot.send_voice(await db.select_connect_with(str(message.from_user.id)), message.voice.file_id)
    except Exception as e:
        errors.error(e)


# Кружок ===============================================================================================================
@dp.message(Chatting.msg, F.video_note)
async def chatting_video_note(message: Message):
    try:
        await bot.send_video_note(await db.select_connect_with(str(message.from_user.id)), message.video_note.file_id)
    except Exception as e:
        errors.error(e)


# Остальное ===============================================================================================================
@dp.message(Chatting.msg, F.unknown)
async def chatting_unknown(message):
    try:
        await message.answer('Ushbu turdagi kontent hali qoʼllab-quvvatlanmaydi😢.')
    except Exception as e:
        errors.error(e)


# id ===================================================================================================================
@dp.message(Command('id'))
async def ids(message: Message):
    try:
        await message.answer(str(message.from_user.id))
    except Exception as e:
        errors.error(e)


# group id =============================================================================================================
@dp.message(Command('gid'))
async def gids(message: Message):
    try:
        await message.answer(str(message.chat.id))
    except Exception as e:
        errors.error(e)


# all ==================================================================================================================
@dp.message()
async def all(message: Message):
    try:
        if str(message.chat.id) not in [BUGS_GROUP_ID, IDEAS_GROUP_ID]:
            await message.answer('Buyruq bajarilmadi. Asosiy menyuga chiqish uchun /start yuboring .')
    except Exception as e:
        errors.error(e)


async def main():
    await db.connect()
    await db.create_tables()
    await dp.start_polling(bot)


if __name__ == '__main__':
    print(f'Bot ishga tushirildi ({datetime.now().strftime("%H:%M:%S %d.%m.%Y")}).')
    asyncio.run(main())
