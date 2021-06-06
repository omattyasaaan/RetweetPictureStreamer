import asyncio
import json
import threading
import discord

# import twitter_rt_watcher

class DiscordApiKyes():
    def __init__(self):
        with open('properties.json') as f:
            properties = json.load(f)
            discord_api_properties = properties['discord_api']
            f.close()
        self.token = discord_api_properties['token']
        self.channel_id = discord_api_properties['channel_id']

discord_api_keys = DiscordApiKyes()
client = discord.Client()
is_update_user = False


@client.event
async def on_ready():
    print('準備ok')

#メッセージ受信時イベント
@client.event
async def on_message(message):
    if message.author.bot:
        return

    split_message = message.content.split()
    if split_message[0] == '!add':
        if add_user(split_message[1]):
            await message.channel.send(split_message[1] + 'さんを追加しました')
        else:
            await message.channel.send('すでに追加されているユーザです')
    elif split_message[0] == '!rm':
        if delete_user(split_message[1]):
            await message.channel.send(split_message[1] + 'さんを削除しました')
        else:
            await message.channel.send('存在しないユーザです')
    elif split_message[0] == '!list':
        user_list = read_user()
        display_massage = '登録ユーザ一覧'
        for user in user_list:
            display_massage = display_massage + '\n' + user
        await message.channel.send(display_massage)


#user追加コマンド
def add_user(twitter_id):
    global is_update_user
    with open('user_list.json') as f:
        user_list = json.load(f)
        users = user_list['user_list']
        if any(twitter_id == user for user in users):
            return False
        users.append(twitter_id)
        user_list['user_list'] = users
        f.close() 

    with open('user_list.json', mode='wt', encoding='utf-8') as f:    
        json.dump(user_list, f, indent=4)
        f.close()
    is_update_user = True
    return True


#user削除コマンド
def delete_user(twitter_id):
    global is_update_user
    with open('user_list.json') as f:
        user_list = json.load(f)
        users = user_list['user_list']
        if all(twitter_id != user for user in users):
            return False
        users.remove(twitter_id)
        user_list['user_list'] = users
        f.close() 

    with open('user_list.json', mode='wt', encoding='utf-8') as f:    
        json.dump(user_list, f, indent=4)
        f.close()
    is_update_user = True
    return True


#userリスト取得
def read_user():
    with open('user_list.json') as f:
        user_list = json.load(f)
        users = user_list['user_list']
        f.close() 
    return users


def main():
    client.run(discord_bot.discord_api_keys.token)


if __name__ == '__main__':
    main()
