from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
import os 
from pytube import YouTube
import glob
import requests
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import moviepy.editor as mp
import shutil
from pytube.cli import on_progress
import asyncio

app = Client(
    "API_TOKEN",
    api_id=API_ID,
    api_hash=API_HASH
)

global loo
loo=[]
print('Success!')
async def progress(current, total,ids,message,ans):
	prog = f"{current * 100 / total:.1f}"
	count=int(prog[:prog.index('.')])
	padjn = (count//5)*'█'
	proga = f'|{padjn}| {count}%'
	if count not in loo:
		loo.append(count)
		try:
			await app.edit_message_caption(ids,message,f'🔉{ans.title}<a href = "{link}"> → </a>\n👤<a href = "{ans.channel_url}">#{ans.author}</a>\n\nSending...\n{proga}\n\n@YouTube_Mp4_bot', parse_mode = "HTML")
		except:
			pass
		if count==100:
			loo.clear()

@app.on_message()
async def start(client, message):
	if message.text=='/start' or message.text=='/start@MisterAbu_bot':
		await app.send_message(message.chat.id,'👋 This is youtube shorts and short videoes downloader bot.')
	elif message.text=='/help' or message.text=='/help@MisterAbu_bot':
		await app.send_photo(message.chat.id,open('example.jpg', "rb"),caption='👋 This bot for download videos from YouTube.\nSand me link like this.')
	else:
		try:
			global ans
			global link
			link = message.text
			ans=YouTube(message.text,on_progress_callback=on_progress)
			yt=ans.streams.filter(progressive=True,file_extension='mp4').all()
			ls=[]
			size=[]
			for i in range(len(yt)):
				size.append(yt[i].filesize)
				ls.append(int(yt[i].resolution.replace('p','')))
			ls=list(set(ls))
			markup_ls=[]
			test=[]
			for i in range(len(ls)):
				sizes = f"{size[i] / 1048000:.1f}"
				test.append(InlineKeyboardButton(f'📹{ls[i]}p ({sizes}mb)',callback_data=f'{ls[i]}'))
				if i%3==0 and i!=0:
					markup_ls.append(test)
					test=[]
			markup_ls.append(test) 
			sizes = f"{ans.streams.filter(only_audio=True,file_extension='mp4').first().filesize / 1048000:.1f}"
			test=[InlineKeyboardButton(f'🔊MP3 ({sizes}mb)',callback_data=f'audio'),InlineKeyboardButton('🖼',callback_data='img')]
			markup_ls.append(test)
			markup=InlineKeyboardMarkup(markup_ls)

			send_type = 'IMG ✅\nMP3 ✅\n360p ✅\n720p ✅'
			def words(fileobj):
				for line in fileobj:
					for word in line.split():
						yield word
			with open("db.txt") as wordfile:
				wordgen = words(wordfile)
				for word in wordgen:
					if word in f'{link}img':
						send_type=send_type.replace('IMG ✅','IMG 🚀')
					else:
						pass
					if word in f'{link}audio':
						send_type=send_type.replace('MP3 ✅','MP3 🚀')
					else:
						pass
					if word in f'{link}360':
						send_type=send_type.replace('360p ✅','360p 🚀')
					else:
						pass
					if word in f'{link}720':
						send_type=send_type.replace('720p ✅','720p 🚀')
					else:
						pass
			await app.send_photo(message.chat.id,ans.thumbnail_url,reply_markup=markup, caption=f'📹{ans.title}<a href = "{message.text}"> → </a>\n👤<a href = "{ans.channel_url}">#{ans.author}</a>\n\n{send_type}\n\nResolution for download. ↓', parse_mode = "HTML")
		except:
			await app.send_message(message.chat.id,'Please send YouTube link. /help')
		await app.delete_messages(message.chat.id,message.message_id)
	
@app.on_callback_query()
async def answer(client, callback_query):
	await app.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.message_id)
	
	def words(fileobj):
		for line in fileobj:
			for word in line.split():
				yield word
	with open("db.txt") as wordfile:
		wordgen = words(wordfile)
		for word in wordgen:
			if word in f'{link}{callback_query.data}':
				break
			else:
				word = None
		foundwords = next(wordgen, None)
	try:
		if foundwords!=None:
			await app.delete_messages(callback_query.message.chat.id,callback_query.message.message_id)
			await app.copy_message(callback_query.message.chat.id,-1001551364203,int(foundwords))
		else:
			await app.edit_message_caption(callback_query.message.chat.id, callback_query.message.message_id,f'{ans.title}<a href = "{link}"> → </a>\n👤<a href = "{ans.channel_url}">#{ans.author}</a>\n\nDownloading...\n\n@YouTube_Mp4_bot', parse_mode = "HTML")
			if callback_query.data == 'img':
				with open('files/pic.jpg', 'wb') as handle:
					response = requests.get(ans.thumbnail_url, stream=True)
					for block in response.iter_content(1024):
						if not block:
							break
						handle.write(block)
				os.rename('files/pic.jpg',f'files/{ans.title}.jpg')
				await callback_query.message.reply_document(open(f'files/{ans.title}.jpg', "rb"),progress=progress,progress_args=(callback_query.message.chat.id,callback_query.message.message_id,ans), caption=f'🖼{ans.title}<a href = "{link}"> → </a>\n\n@YouTube_Mp4_bot', parse_mode = "HTML")
				os.rename(f'files/{ans.title}.jpg','files/pic.jpg')
			
			elif callback_query.data == 'audio':
				try:		
					ans.streams.filter(only_audio=True,file_extension='mp4').first().download(f'{callback_query.message.chat.id}mp3')
					await callback_query.message.reply_audio(open(min(glob.glob(f'{callback_query.message.chat.id}mp3//*'), key=os.path.getctime),'rb').name,progress=progress,progress_args=(callback_query.message.chat.id,callback_query.message.message_id,ans), caption=f'🔉{ans.title}<a href = "{link}"> → </a>\n👤<a href = "{ans.channel_url}">#{ans.author}</a>\n\n@YouTube_Mp4_bot:🔉 MP3', parse_mode = "HTML")		
				except:
					await callback_query.message.reply_text('Something went wrong. Try again.')
				try:
					shutil.rmtree((f'{callback_query.message.chat.id}mp3//'))
				except:
					pass
			else:
				try:
					ans.streams.filter(progressive=True,res=f'{callback_query.data}p',file_extension='mp4').first().download(f'{callback_query.message.chat.id}')
					await callback_query.message.reply_video(open(min(glob.glob(f'{callback_query.message.chat.id}//*'), key=os.path.getctime),'rb').name,progress=progress,progress_args=(callback_query.message.chat.id,callback_query.message.message_id,ans), caption=f'📹{ans.title}<a href = "{link}"> → </a>\n👤<a href = "{ans.channel_url}">#{ans.author}</a>\n\n@YouTube_Mp4_bot:📹{callback_query.data}p', parse_mode = "HTML")	
				except:
					await callback_query.message.reply_text('Something went wrong. Try again.')
				try:
					shutil.rmtree(f'{callback_query.message.chat.id}//')
				except:
					pass
			try:
				await app.copy_message(-1001551364203,callback_query.message.chat.id,callback_query.message.message_id+1)	
				with open("id.txt",'rb') as idd:
					yess = str(idd.read())
					yess = yess.replace("'",'')
					yess = int(yess.replace("b",''))
				with open("id.txt",'w+') as wordfile:
					wordfile.write(f'{yess+1}')
				file_object = open('db.txt', 'a')
				file_object.write(f'{link}{callback_query.data} {yess} ')
				file_object.close()
			except:
				pass
			await app.delete_messages(callback_query.message.chat.id,callback_query.message.message_id)
	except:
		app.send_message(callback_query.message.chat.id,'Something went wrong. Try again.')
app.run()
