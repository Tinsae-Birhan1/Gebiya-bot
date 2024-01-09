from aiogram.dispatcher import FSMContext
from aiogram.types import (LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram import types
from src.loader import bot

from src.loader import  bot
from src.keyboards.inline.choice_buttons import main, main_admin, cart_markup, delivery_keyboard, \
    payment_keyboard, generate_cart_all
from src.loader import dp
import os
import datetime
import json

from src.states import Get_Goods_Page, YourForm
from src.utils.db_functions import get_good_from_db, delete_cart, save_order, generate_order_number, \
    get_category_id_by_name, get_cart_items_count, get_cart_items, update_good_quantity, save_cart
from src.utils.inline_keyboards import get_all_goods_keyboard, get_all_categories_keyboard, update_good_card, \
    subtract_good_from_cart, get_username
from src.utils.db_functions import get_cart, add_good_to_cart


ADMIN_ID = json.loads(os.getenv('ADMIN_ID'))


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(f'Welcome to the store!', reply_markup=main)

    if message.from_user.id in ADMIN_ID:
        await message.answer(f'You are logged in as an administrator', reply_markup=main_admin)

    await Get_Goods_Page.first()

# @dp.message_handler()
# async def ggggg(message: types.Message):
#     print(message.text)
#
# @dp.message_handler(state='*')
# async def ggggg_state(message: types.Message, state: FSMContext):
#     print(message.text, await state.get_state())


@dp.message_handler(text='Catalogue', state=Get_Goods_Page.page)
async def send_catalog_start(message: types.Message, state: FSMContext):
    keyboards_category = await get_all_categories_keyboard("get")
    print(keyboards_category.keys())

    await bot.send_message(text="<b>🎉 Welcome to the product catalog!</b>", chat_id=message.from_user.id)
    await bot.send_message(text="Product categories", reply_markup=keyboards_category[1], chat_id=message.from_user.id)

    async with state.proxy() as data:
        data["keyboards"] = keyboards_category
        data["page"] = 1


@dp.message_handler(text="next_page", state=Get_Goods_Page.page)
async def send_next_page(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["page"] += 1

    state_data = await state.get_data()
    keyboards = state_data["keyboards"]
    page = state_data["page"]

    await message.edit_text(text="<b>Catalog:</b>")
    await message.edit_reply_markup(reply_markup=keyboards[page])


@dp.callback_query_handler(text="previous_page", state=Get_Goods_Page.page)
async def send_previous_page(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["page"] -= 1

    state_data = await state.get_data()
    keyboards = state_data["keyboards"]
    page = state_data["page"]

    await bot.message.edit_text("<b>Catalog:</b>")
    await bot.message.edit_reply_markup(reply_markup=keyboards[page])


@dp.callback_query_handler(text_contains="get_category", state=Get_Goods_Page.page)
async def send_cart_good(callback: types.CallbackQuery, state: FSMContext):
    category_id = callback.data.split(":")[1] 
    keyboards_goods = await get_all_goods_keyboard("get", category_id=category_id)
    print('We receive the key to the goods')
    print(keyboards_goods.keys())

    await bot.send_message(text="<b>Products in category </b>", chat_id=callback.message.chat.id)
    if len(keyboards_goods) > 0:
        await bot.send_message(text="Select product", reply_markup=keyboards_goods[list(keyboards_goods.keys())[0]],
                               chat_id=callback.message.chat.id)

        async with state.proxy() as data:
            data["keyboards"] = keyboards_goods
            data["page"] = 1
    else:
        await bot.send_message(text="There are no products in this category.", chat_id=callback.message.chat.id)
        await state.reset_state()


@dp.callback_query_handler(text_contains="get_good", state=Get_Goods_Page.page)
async def send_good(callback: types.CallbackQuery, state: FSMContext):
    callback_data = callback.data.strip().split(":")[1:]
    good_id = int(callback_data[0])
    good_information = await get_good_from_db(good_id)

    if good_information is None:
        await callback.answer(text="Sorry, the requested product is currently unavailable.",) 
        return

    good_name, good_description, good_price, good_image, good_quantity = good_information
    price = [LabeledPrice(label=f"{good_name} | {good_description}", amount=good_price)]

    add_to_cart = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text='Add to Cart', callback_data=f'add_to_cart:{good_id}'))
    add_to_cart.add(InlineKeyboardButton(text='Return to menu', callback_data='return_to_menu'))

    await bot.send_photo(callback.message.chat.id, photo=good_image,caption=f"Product name - {good_name}\n"
                                                          f"Description - {good_description}\n"
                                                          f"Price - {good_price}\n"
                                                                            f"Quantity of goods - {good_quantity}", reply_markup=add_to_cart)

    await callback.message.delete()
    await state.reset_state()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('add_to_cart'))
async def process_add_to_cart(callback_query: types.CallbackQuery, state: FSMContext):
    good_id = int(callback_query.data.split(':')[1])
    user_id = callback_query.from_user.id

    good_information = await get_good_from_db(good_id)

    if good_information is None:
        await callback_query.answer(text="Sorry, the requested product is currently unavailable.")
        return

    good_name, good_description, good_price, good_image, good_quantity = good_information
    print(good_quantity)
    if good_quantity == 0:
        await callback_query.answer(text="Sorry, this product is out of stock.")
        return send_good
    else:
        await add_good_to_cart(user_id, good_id, good_name, good_description, good_price, good_quantity)

        await bot.send_message(
            callback_query.from_user.id,
            text=f'🎉Goods {good_name} added to cart.\nAdd another copy of the product or remove it',
            reply_markup=generate_cart_all(good_id)
        )
        print(good_name, good_description)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith(f'good:plus:'), state="*")
async def add_item_to_cart(callback_query: types.CallbackQuery, state: FSMContext):
    print('I am in the plus')
    print(await state.get_state())
    good_id = int(callback_query.data.split(":")[2])
    print(callback_query.data)
    good_information = await get_good_from_db(good_id)
    good_name, good_description, good_price, good_image, good_quantity = good_information

    await add_good_to_cart(callback_query.from_user.id, good_id, good_name, good_description, good_price, good_quantity)

    cart_items_count = await get_cart_items_count(callback_query.from_user.id, good_id)
    await update_good_card(callback_query.message, good_name, good_description, good_price, good_image,
                           cart_items_count, good_id)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith(f'good:minus:'), state="*")
async def remove_item_from_cart(callback_query: types.CallbackQuery):
    good_id = int(callback_query.data.split(":")[2])
    good_information = await get_good_from_db(good_id)
    good_name, good_description, good_price, good_image, good_quantity = good_information
    user_id = callback_query.from_user.id

    await subtract_good_from_cart(
        message=callback_query.message,
        user_id=callback_query.from_user.id,
        good_id=good_id,
        good_name=good_name,
        good_description=good_description,
        good_quantity=good_quantity
    )
    await subtract_good_from_cart(callback_query.message, user_id, good_id, good_name, good_description, good_quantity)


@dp.message_handler(text="Exit to main menu")
async def return_to_menu_new_state(message: types.Message):
    await cmd_start(message)


@dp.message_handler(text="Go to cart")
async def go_to_cart(message: types.Message, state: FSMContext):
    await show_cart(message, state)


@dp.message_handler(text='Cart', state=Get_Goods_Page.page)
async def show_cart(message: types.Message, state: FSMContext):
   
    print("I'm in the caer")
    user_id = message.from_user.id
    cart = await get_cart(user_id)

    if not cart:
        await message.answer("Cart is empty!")
    else:
        total_price = 0
        cart_text = "<b>Items in cart:</b>\n\n"
        for good_information in cart:
            good_name, good_description, good_price, good_image = good_information
            cart_text += f"{good_name} | {good_description}\nPrice - {good_price}\n\n"
            total_price += good_price

        cart_text += f"<b>Total: {total_price}</b>"

        await bot.send_message(message.chat.id, text=cart_text, reply_markup=cart_markup, parse_mode="HTML")


@dp.message_handler(text="Empty trash", state=Get_Goods_Page.page)
async def process_clear_cart(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await delete_cart(user_id)
    await bot.send_message(message.chat.id, text='Cart is empty!')
    await return_to_main_menu(message, state)


@dp.message_handler(text='Order', state=Get_Goods_Page.page)
async def order_start(message: types.Message, state: FSMContext):
    await message.answer('Enter your full name:')
    await YourForm.name.set()


@dp.message_handler(text='Go out', state=Get_Goods_Page.page)
async def quit_carts(message: types.Message, state: FSMContext):
    await cmd_start(message)


@dp.message_handler(state=YourForm.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['fio'] = message.text
    await message.answer('Enter your phone number:')
    await YourForm.next()


@dp.message_handler(state=YourForm.phone)
async def process_phone(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = message.text
    await message.answer('Select delivery method:', reply_markup=delivery_keyboard)
    await YourForm.next()


@dp.message_handler(state=YourForm.delivery)
async def process_delivery(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['delivery_method'] = message.text
    await message.answer('Choose your payment method:', reply_markup=payment_keyboard)
    await YourForm.next()


# @dp.message_handler(lambda message: message.text == 'Full payment', state=YourForm.payment)
# async def process_full_payment(message: types.Message, state: FSMContext):
#     await message.answer("<b>Оплатите на карту: </b>")


@dp.message_handler(state=YourForm.payment)
async def process_payment(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['payment_method'] = message.text
    await message.answer('Enter delivery address: ')
    await YourForm.next()


@dp.message_handler(state=YourForm.address)
async def get_address(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['address'] = message.text

    state_data = await state.get_data()
    order_number = generate_order_number()
    fio = state_data['fio']
    phone_number = state_data['phone_number']
    delivery_method = state_data['delivery_method']
    payment_method = state_data['payment_method']
    address = state_data['address']
    user_id = message.from_user.id
    username = await get_username(user_id)
    day = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Get cart items
    cart_items = await get_cart_items(user_id)
    goods_amount = {}
    goods_quantity = {}
    for good in cart_items:
        good_id = good[0]
        goods_quantity[good_id] = good[4]
        if good_id not in goods_amount.keys():
            goods_amount[good_id] = 0
        goods_amount[good_id] += 1

    for good_id, quantity in goods_quantity.items():
        amount = goods_amount[good_id]
        new_quantity = quantity - amount
        await update_good_quantity(good_id, new_quantity)

    orders = ''
    for good in cart_items:
        good_id = good[0]
        goods_quantity[good_id] = 4
        if good_id not in goods_amount.keys():
            goods_amount[good_id] = 0
        goods_amount[good_id] += 1
        orders += f'{good[2]} ({good[4]}шт.), '

    await save_order(message.from_user.id, fio, username, phone_number, day, orders, delivery_method, address, payment_method, order_number, goods_quantity)
    await delete_cart(user_id)
    await message.answer("<b>Order created successfully!</b>")
    admin_id = os.getenv('ADMIN_ID')
    order_info = f"Order №{order_number}\n\n"
    order_info += f"Date: {day}\n"
    order_info += f"The contact person: {fio} - {username}\n"
    order_info += f"Telephone: {phone_number}\n"
    order_info += f"Address: {address}\n"
    order_info += f"Delivery method: {delivery_method}\n"
    order_info += f"Payment method: {payment_method}\n"
    order_info += f"Goods:\n{orders}"
    await bot.send_message(chat_id=admin_id, text=order_info)
    
    await state.finish()
    await return_to_main_menu(message, state)


@dp.message_handler(text='Contacts', state=Get_Goods_Page.page)
async def contacts(message: types.Message, state: FSMContext):
    await message.answer('Contact [Tinsae Birhan](https://t.me/Birhanne)', parse_mode='Markdown')


@dp.message_handler(text='Exit to main menu', state=Get_Goods_Page.page)
async def return_to_main_menu(message: types.Message, state: FSMContext):
    await cmd_start(message)


@dp.message_handler()
async def answer(message: types.Message):
    await message.reply('I do not understand you')



