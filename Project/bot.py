import sqlite3
import random
import string
import itertools

import re
import telebot
from telebot import types

bot = telebot.TeleBot('5432824872:AAHgqoCGrKd7Cqg0775HiYuP8n1NuiT4SAU')

@bot.message_handler(commands=['start'])
def start(message):
	board = types.ReplyKeyboardMarkup() 
	random = types.KeyboardButton(text='/Случайный_рецепт')
	like = types.KeyboardButton(text='/Понравившееся')
	board.add(random)
	board.add(like)
	bot.send_message(message.chat.id, 'Бот включен', reply_markup = board)

@bot.message_handler(commands=['Случайный_рецепт'])
def send_welcome(message):
	with sqlite3.connect('eat.db') as connect:
		cur = connect.cursor()
		cur.execute(''' SELECT * FROM eat''')
		result = cur.fetchall()
		global recipe
		recipe = result[random.randint(3,len(result))]
		#print(recipe)
		image = recipe[1]
		name = recipe[2]
		if image == 'Нет изображения':
			image = 'https://sun6-21.userapi.com/s/v1/if2/lVrMt9iCQThqVaGXtYylXEx9ZrzKSqefSCkRSI10I6AQ5gbE4oTh8LR21HJrkFx8D8PaY8C7nLxnarvVHufSkFCa.jpg?size=100x100&quality=95&crop=231,123,471,471&blur=7,3&ava=1'
		#cur.execute(f'''DELETE FROM eat WHERE id={recipe[0]}''')

	keyboard = types.InlineKeyboardMarkup() # объект клавиатуры, прикрепленной к сообщению бота
	key_yes = types.InlineKeyboardButton(text='Подробнее', callback_data ='yes') # создание кнопки "Да" (есть именованый параметр 'url')
	keyboard.add(key_yes)

	bot.send_photo(message.chat.id, photo=image, caption=name, reply_markup = keyboard)

@bot.message_handler(commands=['Понравившееся'])
def like(message):
	lst = []
	button = types.InlineKeyboardMarkup()
	key_ = types.InlineKeyboardButton(text='Подробнее', callback_data ='maybe')
	button.add(key_)

	with sqlite3.connect('eat.db') as connect:
		cur = connect.cursor()
		cur.execute(''' SELECT * FROM good_food''')
		result = cur.fetchall()

	for i in result:
		name = i[2]
		bot.send_message(message.chat.id, f'{name}', reply_markup = button)

@bot.callback_query_handler(func =lambda call: True) # Принимает все данные полученные от клавиатуры(путем тоо что пользователь на нёё нажал)
def callback_worker(call):
	if call.data == 'yes':
		conditions = recipe[3]
		instruction_image = recipe[4].strip('[] \ r n')
		instruction_image = re.sub(r'["\']', '', instruction_image)
		ins_im = instruction_image.split(',')
		instruction = recipe[5].strip('[]')
		instruction = re.sub(r'["\']', '', instruction).split('Шаг')
		conditions = conditions.translate(str.maketrans('', '', string.punctuation))
		
		#print(instruction)
		bot.send_message(call.message.chat.id, f'Рецепт: {conditions}')
		
		for z,i in itertools.zip_longest(instruction, ins_im):
			#print(z)
			if i == 'Нет изображения для инструкции':
				bot.send_message(call.message.chat.id, 'Нет фото инструкции')
				break
			elif i == None:
				bot.send_message(call.message.chat.id, z)
			else:
				try:
					bot.send_photo(call.message.chat.id, photo = i.strip(), caption = z)
				except AttributeError:
					pass

		button = types.InlineKeyboardMarkup() # объект клавиатуры, прикрепленной к сообщению бота
		key_no = types.InlineKeyboardButton(text='Да', callback_data ='no') # создание кнопки "Да" (есть именованый параметр 'url')
		button.add(key_no)
		bot.send_message(call.message.chat.id, 'Добавить в понравившееся?', reply_markup = button) 

	elif call.data == 'no':
		with sqlite3.connect('eat.db') as connect:
			cur = connect.cursor()
			cur.execute(''' INSERT INTO good_food (image, name, compositions, instruction_image, instruction) 
							VALUES (?,?,?,?,?)''', (recipe[1], recipe[2], str((recipe[3])), str(recipe[4]), str((recipe[5]))))

	elif call.data == 'maybe':
		#print(call.message.text)
		rep = str(call.message.text)
		with sqlite3.connect('eat.db') as connect:
			cur = connect.cursor()
			cur.execute(f''' SELECT * FROM good_food WHERE name = '{rep}' ''')
			result = cur.fetchone()
			image = result[1]
			name = result[2]
			conditions = result[3]
			instruction_image = result[4].strip('[] r n')
			instruction_image = re.sub(r'["\']', '', instruction_image)
			ins_im = instruction_image.split(',')
			instruction = result[5].strip('[]')
			instruction = re.sub(r'["\']', '', instruction).split('Шаг')
		conditions = conditions.translate(str.maketrans('', '', string.punctuation))
		if image == 'Нет изображения':
			image = 'https://sun6-21.userapi.com/s/v1/if2/lVrMt9iCQThqVaGXtYylXEx9ZrzKSqefSCkRSI10I6AQ5gbE4oTh8LR21HJrkFx8D8PaY8C7nLxnarvVHufSkFCa.jpg?size=100x100&quality=95&crop=231,123,471,471&blur=7,3&ava=1'
		

		bot.send_photo(call.message.chat.id, photo=image, caption=name)
		bot.send_message(call.message.chat.id, f'Рецепт: {conditions}')
		for z,i in itertools.zip_longest(instruction, ins_im):
			#print(z)
			if i == 'Нет изображения для инструкции':
				bot.send_message(call.message.chat.id, 'Нет фото инструкции')
				break
			elif i == None:
				bot.send_message(call.message.chat.id, z)
			else:
				try:
					bot.send_photo(call.message.chat.id, photo = i.strip(), caption = z)
				except AttributeError:
					pass


if __name__ == '__main__':
	bot.polling() # запуск бота
