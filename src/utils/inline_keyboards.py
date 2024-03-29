from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, inline_keyboard
from aiogram.utils.callback_data import CallbackData
from aiogram.types import Message

from src.keyboards.inline.choice_buttons import return_to_new_state
from src.loader import bot

from src.loader import dp
from src.states import BankCardState
from src.utils.db_functions import get_all_goods, get_categories_from_db, get_goods_by_category_from_db, \
    get_cart_items_count, get_cart, update_good_quantity, save_cart, get_goods_my_db

get_category_callback = CallbackData("get_category", "category_id")
remove_category_callback = CallbackData("remove_category", "category_id")
get_good_callback = CallbackData("get_good", "id")
remove_good_callback = CallbackData("remove_good", "id")


async def get_all_categories_keyboard(mode):
    all_categories_keyboards = {}
    all_buttons = []
    categories = await get_categories_from_db()

    page = 1

    if mode == "get":
        callback = get_category_callback

    elif mode == "remove":
        callback = remove_category_callback

    for category_name, category_id in categories:
        print(all_categories_keyboards)
        all_buttons.append(InlineKeyboardButton(text=f"{category_name}", callback_data=callback.new(category_id)))

    while len(all_buttons) > 0:
        keyboard = InlineKeyboardMarkup()
        counter = 1

        try:
            while counter < 5:
                keyboard.add(all_buttons[0])
                all_buttons.remove(all_buttons[0])
                counter += 1

        except:
            if page != 1:
                keyboard.add(InlineKeyboardButton(text="Back", callback_data="previous_page"))

            else:
                keyboard.add(InlineKeyboardButton(text="Back", callback_data="back_to_shop_menu"))

            break

        else:
            if page == 1:
                keyboard.add(InlineKeyboardButton(text="Back", callback_data="back_to_shop_menu"))

            else:
                keyboard.add(InlineKeyboardButton(text="Back", callback_data="previous_page"))

            if len(all_buttons) > 0:
                keyboard.insert(InlineKeyboardButton(text="Next", callback_data="next_page"))

        finally:
            all_categories_keyboards[page] = keyboard
            page += 1

    return all_categories_keyboards


async def get_all_goods_keyboard(mode, category_id):
    all_goods_keyboards = {}
    all_buttons = []
    goods = await get_goods_by_category_from_db(category_id)
    callback = None
    page = 1

    if mode == "get":
        callback = get_good_callback

    elif mode == "remove":
        callback = remove_good_callback

    for name, description, id in goods:
        print(f'Goods: {all_goods_keyboards}')
        all_buttons.append(InlineKeyboardButton(text=f"{name} | {description}", callback_data=callback.new(id)))

    while len(all_buttons) > 0:
        keyboard = InlineKeyboardMarkup()
        counter = 1

        try:
            while counter < 5 and all_buttons:
                keyboard.add(all_buttons[0])
                all_buttons.remove(all_buttons[0])
                counter += 1

        except:
            if page != 1:
                keyboard.add(InlineKeyboardButton(text="Back", callback_data="previous_page"))

            else:
                keyboard.add(InlineKeyboardButton(text="Back", callback_data="back_to_shop_menu"))

            break

        else:
            if page == 1:
                keyboard.add(InlineKeyboardButton(text="Back", callback_data="back_to_shop_menu"))

            else:
                keyboard.add(InlineKeyboardButton(text="Back", callback_data="previous_page"))

            if len(all_buttons) > 0:
                keyboard.insert(InlineKeyboardButton(text="Next", callback_data="next_page"))

        finally:
            all_goods_keyboards[page] = keyboard
            page += 1

    return all_goods_keyboards


async def update_good_card(message, good_name, good_description, good_price, good_image, user_id, good_id):
    cart_count = await get_cart_items_count(user_id, good_id)

    await bot.send_message(chat_id=message.chat.id, text=f'<b>You have added another item: </b>\n{good_name} | {good_description}', reply_markup=return_to_new_state) #\nТаких товаров в корзине: {cart_count}',


async def subtract_good_from_cart(message, user_id: int, good_id: int, good_name, good_description, good_quantity):
    cart_item_count = await get_cart_items_count(user_id, good_id)

    if cart_item_count > 0:
        await update_cart_item_count(user_id, good_id, cart_item_count - 1)

    await bot.send_message(chat_id=message.chat.id,
                           text=f'<b>You have removed one item: </b>\n{good_name} | {good_description}',
                           reply_markup=return_to_new_state)
    await save_cart(good_id, good_quantity)


async def update_cart_item_count(user_id: int, good_id: int, count: int):
    cart = await get_cart(user_id)

    for item in cart:
        if item["good_id"] == good_id:
            item["count"] = count
            break

async def get_username(id):
    chat_member = await bot.get_chat_member(chat_id=id, user_id=id)
    return chat_member.user.username



    # await save_cart(user_id, cart)


# async def add_good_to_cart(message: Message):
#     if not message.get_args():
#         await message.answer("")
#         return
#
#     args = message.get_args().split()
#     good_id = int(args[0])
#     quantity = int(args[1])
#
#     cart = await dp.current_state(user=message.from_user.id).get_data()
#
#     if good_id in cart:
#         cart[good_id] += quantity
#     else:
#         cart[good_id] = quantity
#
#     await dp.current_state(user=message.from_user.id).set_data(cart)
#
#     await message.answer(f".")


