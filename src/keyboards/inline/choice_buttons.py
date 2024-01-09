from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from src.keyboards.inline.callback_datas import buy_callback
from aiogram.utils.callback_data import CallbackData

import os


main = ReplyKeyboardMarkup(resize_keyboard=True)
main.add(KeyboardButton('Catalogue'))
main.add(KeyboardButton('Cart'))
main.add(KeyboardButton('Contacts'))

main_admin = ReplyKeyboardMarkup(resize_keyboard=True)
main_admin.add(KeyboardButton('Catalogue'))
main_admin.add(KeyboardButton('Cart'))
main_admin.add('Contacts')
main_admin.add('Admin panel')

admin_panel = ReplyKeyboardMarkup(resize_keyboard=True)
admin_panel.add(KeyboardButton('Add category'))
admin_panel.add(KeyboardButton('Add product'))
admin_panel.add(KeyboardButton('Remove product'))
admin_panel.add(KeyboardButton('Bank card details'))
admin_panel.add(KeyboardButton('Prepayment amount'))
admin_panel.add(KeyboardButton(text="Go out"))

button = InlineKeyboardButton('Enter card number: ', callback_data='bank_card_number')
keyboard = InlineKeyboardMarkup().add(button)


delivery_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
delivery_keyboard.add(KeyboardButton('SDEC'))
delivery_keyboard.add(KeyboardButton('Post office'))

payment_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
payment_keyboard.add(KeyboardButton('Full payment'))
payment_keyboard.add(KeyboardButton('Partial payment'))

cart_markup = ReplyKeyboardMarkup(resize_keyboard=True)
cart_markup.add(KeyboardButton(text='Empty trash'))
cart_markup.add(KeyboardButton('Order'))
cart_markup.add(KeyboardButton('Go out'))


def generate_cart_all(good_id: int) -> InlineKeyboardMarkup:
    cart_all = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text='➕', callback_data=f'good:plus:{good_id}')
    ).add(
        InlineKeyboardButton(text='➖', callback_data=f'good:minus:{good_id}')
    )

    return cart_all


return_to_new_state = ReplyKeyboardMarkup(resize_keyboard=True)
return_to_new_state.add(KeyboardButton(text="Exit to main menu"))



