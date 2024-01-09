import json
import os
import re

from aiogram import types
from aiogram.dispatcher import FSMContext

from src.handlers.users.user_panel import cmd_start
from src.keyboards.inline.choice_buttons import admin_panel, keyboard
from src.loader import dp, bot
from src.states import NewItem, Get_Goods_Page, BankCardState, NewCategory
from src.utils.db_functions import add_good_to_db, remove_good_from_db, save_bank_card, get_bank_card, set_category, \
    generate_categories_keyboard, get_all_orders
from src.utils.inline_keyboards import get_all_goods_keyboard

ADMIN_ID = json.loads(os.getenv('ADMIN_ID'))


@dp.message_handler(text="Admin panel", state=Get_Goods_Page.page)
async def contacts(message: types.Message, state: FSMContext):
    print("Bot launched(Admin panel)")
    if message.from_user.id in ADMIN_ID:
        bot_message = await bot.send_message(message.from_user.id, f'You are logged in Admin panel', reply_markup=admin_panel)
        async with state.proxy() as data:
            data["key"] = bot_message.message_id

        await Get_Goods_Page.page.set()


@dp.message_handler(text="Add category", state=Get_Goods_Page.page)
async def add_category(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await bot.delete_message(message_id=data["key"], chat_id=message.from_user.id)
        await bot.send_message(message.from_user.id, "<b>Enter category name: </b>")

    await state.reset_state()
    await NewCategory.first()


@dp.message_handler(state=NewCategory.name)
async def get_category_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = message.text

    state_data = await state.get_data()
    name = state_data["name"]

    await message.answer("<b>Category added successfully!</b>", reply_markup=admin_panel)

    await set_category(name)
    await state.reset_state()

    await Get_Goods_Page.first()


@dp.message_handler(text="Add product", state=Get_Goods_Page.page)
async def add_good(message: types.Message, state: FSMContext):
    print('The "Add product" button is pressed. Categories')
    category_keyboard = await generate_categories_keyboard()

    await bot.send_message(message.from_user.id, "<b>Select a category:</b>", reply_markup=category_keyboard)

    await NewItem.category.set()


@dp.callback_query_handler(state=NewItem.category)
async def get_category(callback: types.CallbackQuery, state: FSMContext):
    print('Category selected')
    await callback.message.answer("<b>Enter product name:</b>")

    async with state.proxy() as data:
        print(callback.data)
        data["category_id"] = callback.data.split(':')[1]

    await NewItem.name.set()


@dp.message_handler(state=NewItem.name)
async def get_name(message: types.Message, state: FSMContext):
    await message.answer("<b>Enter product description:</b>")

    async with state.proxy() as data:
        data["name"] = message.text

    await NewItem.next()


@dp.message_handler(state=NewItem.description)
async def get_name(message: types.Message, state: FSMContext):
    await message.answer("<b>Enter the price of the product: </b>")

    async with state.proxy() as data:
        data["description"] = message.text

    await NewItem.next()


@dp.message_handler(state=NewItem.price)
async def get_name(message: types.Message, state: FSMContext):
    await message.answer("<b>Send the product photo link: </b>")
    async with state.proxy() as data:
        data["price"] = int(message.text)
    await NewItem.next()


@dp.message_handler(state=NewItem.photo)
async def get_photo(message: types.Message, state: FSMContext):
    await message.answer("<b>Enter the quantity of the product in stock: </b>")
    async with state.proxy() as data:
        data["photo"] = message.text
    await NewItem.next()


@dp.message_handler(state=NewItem.availability)
async def get_availability(message:types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["availability"] = int(message.text)

    state_data = await state.get_data()
    category_id = int(state_data["category_id"])
    name = state_data["name"]
    description = state_data["description"]
    price = state_data["price"]
    photo = state_data["photo"]
    availability = state_data["availability"]

    await message.answer("<b>Product added successfully!</b>", reply_markup=admin_panel)

    await add_good_to_db(name, description, price, photo, category_id, availability)

    await state.reset_state()
    await Get_Goods_Page.first()


@dp.message_handler(text="Remove product")
async def send_remove_goods(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        # print(type(data["key"]))
        await bot.delete_message(message_id=data["key"], chat_id=message.from_user.id)
        await bot.send_message(message.from_user.id, "<b>Click on a product to remove it:</b>", reply_markup=None)
        await bot.edit_reply_markup(reply_markup=await get_all_goods_keyboard("remove"))


@dp.message_handler(text="Remove product", state=Get_Goods_Page.page)
async def send_remove_goods(message: types.Message, state: FSMContext):
    keyboards = await get_all_goods_keyboard("remove")

    async with state.proxy() as data:
        await bot.delete_message(message_id=data["key"], chat_id=message.from_user.id)
        await bot.send_message(message.from_user.id, text="<b>Click on a product to remove it:</b>", reply_markup=None)
        await bot.send_message(chat_id=message.from_user.id,reply_markup=keyboards[1], text="All available products: ")
        data["keyboards"] = keyboards
        data["page"] = 1
    await Get_Goods_Page.first()


@dp.callback_query_handler(text_contains="remove_good", state=Get_Goods_Page.page)
async def remove_good(callback: types.CallbackQuery, state: FSMContext):
    callback_data = callback.data.strip().split(":")[1:]
    good_id = callback_data[0]

    await callback.message.edit_text("<b>The item was successfully removed!</b>")
    await remove_good_from_db(good_id)

    await state.reset_state()
    await Get_Goods_Page.first()
    await Get_Goods_Page.page.set()


@dp.message_handler(text='Bank card details', state=Get_Goods_Page.page)
async def bank_card_details(message: types.Message, state:FSMContext):
    await message.answer('You clicked on the "Bank card details" button".\nClick the button to enter your bank card number.', reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data == 'bank_card_number', state=Get_Goods_Page.page)
async def process_bank_card_button(callback_query: types.CallbackQuery, state:FSMContext):
    await bot.send_message(callback_query.from_user.id, 'Enter your bank card number:')


@dp.message_handler(regexp=r'^\d{4}\s\d{4}\s\d{4}\s\d{4}$', state=Get_Goods_Page.page)
async def process_bank_card_number(message: types.Message, state:FSMContext):
    card_number = message.text

    card_number = card_number.replace(' ','')

    await save_bank_card(user_id=message.from_user.id, card_number=card_number)

    await bot.send_message(message.chat.id, f'You have successfully entered your bank card number: {card_number}', reply_markup=admin_panel)


@dp.message_handler(text="Prepayment amount", state=Get_Goods_Page.page)
async def prepayment_amount(message: types.Message, state:FSMContext):
    user_id = message.from_user.id
    card_number = await get_bank_card(user_id)
    if card_number:
        await message.answer(f"Your bank card number: <b>{card_number[0]}</b>", reply_markup=admin_panel)
    else:
        await message.answer("Your bank card number was not found.", reply_markup=admin_panel)


@dp.message_handler(text="Go out", state=Get_Goods_Page.page)
async def return_to_lobby(message: types.Message, state: FSMContext):
    await cmd_start(message)



