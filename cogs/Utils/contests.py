import requests
import discord
import json
import time
import datetime

TIME_LIMIT = 25000

id_to_platform= {
    2:'Codechef',
    1:'Codeforces',
    93:'Atcoder',
    102: 'Leetcode',
    35: 'Google',
    73: 'Hackerearth'
}



def get_formatted_contest_desc(id_str, start, duration, url, max_duration_len):
    em = '\N{EN SPACE}'
    sq = '\N{WHITE SQUARE WITH UPPER RIGHT QUADRANT}'
    desc = (f'`{em}{id_str}{em}| {em}{start}{em}| {em}{duration.rjust(max_duration_len, em)}{em}|' f'{em}`[`link {sq}`]({url} "Link to contest page")')
    return desc


def getFutureContest(res):
	desc = "**About to start in 1 hour**"
	embed = discord.Embed(description=desc, color=discord.Colour.gold())

	if len(res)==0:
		desc = "**No Recent Contest**"
		embed = discord.Embed(description=desc, color=discord.Colour.gold())
		return embed
	
	def convert(seconds): 
		seconds = seconds % (24 * 3600) 
		hour = seconds // 3600
		seconds %= 3600
		minutes = seconds // 60
		seconds %= 60
		return "%d:%02d" % (hour, minutes) 

	for i in range(len(res)):
		con = res[i]
		duration = convert(int(con[1]))
		name = con[0]
		url = con[3]
		start = con[2].replace("T"," ")
		em = '\N{EN SPACE}'
		sq = '\N{WHITE SQUARE WITH UPPER RIGHT QUADRANT}'
		desc = (f'`{em}{start}{em}| {em}{duration.rjust(5, em)}{em}| {em}`[`link {sq}`]({url} "Link to contest page")')
		embed.add_field(name=f"{name}", value= desc  ,inline=False)
	return embed



def getNextContest():
    current_time = time.strftime('%Y-%m-%dT%H:%M:%S')
    url = f"https://clist.by/api/v1/contest/?start__gt={current_time}&order_by=start&username=s5960r&api_key=2e6046e37a8c58f5f13464bea345d4ef5b17acbe"
    data = json.loads(requests.get(url).content)['objects']
    return data

def getRecentContests():
    all_contests = getNextContest()
    res = {}
    for data in all_contests:
        name = data['event']
        platform = data['resource']['id']
        start_time = data['start']
        link = data['href']
        dur = data['duration']
        time_left = int(datetime.datetime.timestamp(datetime.datetime.strptime(start_time,'%Y-%m-%dT%H:%M:%S')))
        time_left= int(time_left-time.time())
        if time_left <= TIME_LIMIT and platform in id_to_platform.keys():
        	if id_to_platform[platform] in res.keys():
        		res[id_to_platform[platform]].append([name,dur,start_time,link])
        	else:
        		res[id_to_platform[platform]]=list()
        		res[id_to_platform[platform]].append([name,dur,start_time,link])
    return res