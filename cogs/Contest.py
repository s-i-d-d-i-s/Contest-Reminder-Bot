import discord
from discord.ext import commands,tasks
from .Utils import contests,constants, table
import asyncio
import random
from discord.utils import get
import os
import time
import pickle

def getCurrentTime():
	from datetime import datetime
	from pytz import timezone    

	india = timezone('Asia/Kolkata')
	in_time = datetime.now(india)
	return in_time.strftime('%H:%M %p %d-%m-%Y')

class Contests(commands.Cog):
	"""docstring for Contests"""
	def __init__(self, client):
		self.client = client
		self.channels = constants.REMINDER_CHANNELS
		self.printer.start()


	@commands.Cog.listener()
	async def on_ready(self):
		print("Contests is online")

	@tasks.loop(seconds=100)
	async def printer(self):
		await self.remind()


	@printer.before_loop
	async def before_printer(self):
		print('waiting...')
		await self.client.wait_until_ready()

	@commands.command(brief='Update Status')
	@commands.has_role('Admin')
	async def upd_status(self,ctx):
		cnt = 0
		for g in self.client.guilds:
			cnt += len(g.members)
		await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{cnt} members !"))

	@commands.command(brief='Show future contests')
	@commands.has_role('Admin')
	async def future(self,ctx):
		data = contests.getRecentContestsAll()
		contest_list = self.client.get_channel(self.channels['All-Contests'])
		style = table.Style('{:>}  {:<}  {:<}  {:<}  {:<}')
		t = table.Table(style)
		t += table.Header('#', 'Platform','Name', 'Dur', 'Countdown')
		t += table.Line()
		cnt=1

		def convert(seconds): 
			seconds = int(seconds)
			seconds = seconds % (24 * 3600) 
			hour = seconds // 3600
			seconds %= 3600
			minutes = seconds // 60
			seconds %= 60
			return "%d:%02d" % (hour, minutes) 

		def convert2(seconds): 
			seconds = int(seconds)
			h = seconds//60
			h = h//60
			seconds -= h*60*60
			m = seconds//60
			seconds -=m*60
			return "%d:%02d:%02d" % (h, m,seconds) 

		for x in data:
			if cnt>=10:
				break
			print(x[3],x[2])
			t += table.Data(cnt, x[3], x[0], convert(x[1]) , convert2(x[2]))
			cnt+=1
		clist = '```\n'+str(t)+'\n```'
		embed = discord.Embed(title='Upcoming Contests.',description=clist)

		await contest_list.send(embed=embed)


	async def future_update(self):
		print("Here")
		data = contests.getRecentContestsAll()
		contest_list = self.client.get_channel(self.channels['All-Contests'])
		msg = await contest_list.history(limit=1).flatten()
		msg = msg[0]
		style = table.Style('{:>}  {:<}  {:<}  {:<}  {:<}')
		t = table.Table(style)
		t += table.Header('#', 'Platform','Name', 'Dur', 'Countdown')
		t += table.Line()
		cnt=1

		def convert(seconds): 
			seconds = int(seconds)
			seconds = seconds % (24 * 3600) 
			hour = seconds // 3600
			seconds %= 3600
			minutes = seconds // 60
			seconds %= 60
			return "%d:%02d" % (hour, minutes) 

		def convert2(seconds): 
			seconds = int(seconds)
			h = seconds//60
			h = h//60
			seconds -= h*60*60
			m = seconds//60
			seconds -=m*60
			return "%d:%02d:%02d" % (h, m,seconds) 

		for x in data:
			if cnt>=10:
				break
			t += table.Data(cnt, x[3], x[0], convert(x[1]) , convert2(x[2]))
			cnt+=1
		clist = '```\n'+str(t)+'\n```'
		embed = discord.Embed(title='Upcoming Contests.',description=clist)
		embed.set_footer(text=f'Last Updated on {getCurrentTime()} IST')
		await msg.edit(embed=embed)

	async def clean_it(self,data):
		new_data = []
		logger = self.client.get_channel(self.channels["Logging"])
		hist_data = await self.getHistory()
		for x in data:
			if x[0] not in hist_data:
				# New Contest
				await logger.send(x[0])
				new_data.append(x)
		return new_data

	async def remind(self):
		print("Checking for New Contests...")
		try:
			data = contests.getRecentContests()
			all_reminders = self.client.get_channel(self.channels['All-Reminders'])
			for x in data.keys():
				channel = self.client.get_channel(self.channels[x])
				data_foo = await self.clean_it(data[x])
				emb = contests.getFutureContest(data_foo,x)
				if emb == None:
					continue
				role = self.client.get_guild(constants.SERVER_ID).get_role(self.channels[x+'_Role'])
				all_rem_msg =await channel.send(role.mention,embed=emb)
				try:
					# Publish_Msg
					await all_rem_msg.publish()
				except:
					pass
		except Exception as e:
			print(e)
		
		try:
			await self.future_update()
		except Exception as e:
			print(e)


	async def getHistory(self):
		channel = self.client.get_channel(self.channels["Logging"])
		data = await channel.history(limit=30).flatten()
		res = []
		for msg in data:
			res.append(msg.content)
		return res


def setup(client):
	client.add_cog(Contests(client))