import discord
from discord.ext import commands
from .Utils import contests,constants
import asyncio
import random
from discord.utils import get
import os
import pickle



class Contests(commands.Cog):
	"""docstring for Contests"""
	def __init__(self, client):
		self.client = client
		self.channels = constants.REMINDER_CHANNELS
		


	@commands.Cog.listener()
	async def on_ready(self):
		print("Contests is online")


	@commands.command(brief='Send Reminders')
	async def remind(self,ctx):
		data = contests.getRecentContests()
		for x in data.keys():
			channel = self.client.get_channel(self.channels[x])
			emb = contests.getFutureContest(data[x])
			await channel.send(embed=emb)
		


def setup(client):
	client.add_cog(Contests(client))