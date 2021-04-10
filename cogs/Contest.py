import discord
from discord.ext import commands,tasks
from .Utils import contests,constants
import asyncio
import random
from discord.utils import get
import os
import time
import pickle



class Contests(commands.Cog):
	"""docstring for Contests"""
	def __init__(self, client):
		self.client = client
		self.channels = constants.REMINDER_CHANNELS
		self.printer.start()


	@commands.Cog.listener()
	async def on_ready(self):
		print("Contests is online")

	@tasks.loop(seconds=65)
	async def printer(self):
		await self.remind()


	@printer.before_loop
	async def before_printer(self):
		print('waiting...')
		await self.client.wait_until_ready()


	@commands.has_role('Admin')
	async def upd_status(self,ctx):
		cnt = 0
		for g in self.client.guilds:
			cnt += len(g.members)
		await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{cnt} members !"))

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
				emb = contests.getFutureContest(data_foo)
				if emb == None:
					continue
				role = self.client.get_guild(constants.SERVER_ID).get_role(constants.ROLE_ID)
				await channel.send(role.mention,embed=emb)
				all_rem_msg = await all_reminders.send(f"Reminder for {x}",embed=emb)
				try:
					# Publish_Msg
					await all_rem_msg.publish()
				except:
					pass
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