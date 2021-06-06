import asyncio
import threading

import discord_epr_streamer
import twitter_rt_watcher

#DiscordClientを止めないためにスレッドの停止、起動をスレッド化するためのターゲット
def generate_thread(thread):
    discord_epr_streamer.is_update_user = False
    twitter_rt_watcher.is_update_user = True
    thread.join()
    twitter_rt_watcher.is_update_user = False
    thread = threading.Thread(target=twitter_rt_watcher.observe_rt)
    thread.start()


# rt,ユーザの変更フラグ監視
# twitter discird側から通知を受けとって発火するように作り変えたい
async def observe_flag(thread):
    url = ''
    while True:
        # print('test')
        await asyncio.sleep(1)
        if twitter_rt_watcher.is_rt and url != twitter_rt_watcher.url:
            print('rt_ok')
            url = twitter_rt_watcher.url
            channel = discord_epr_streamer.client.get_channel(int(discord_epr_streamer.discord_api_keys.channel_id))
            await channel.send(twitter_rt_watcher.url)
            twitter_rt_watcher.is_rt = False

        if discord_epr_streamer.is_update_user:
            t = threading.Thread(target=generate_thread, args=(thread,))
            t.start()
        
        
def main():
    twitter_api = twitter_rt_watcher.authenticate_twitter()
    target_list = twitter_rt_watcher.get_targets(twitter_api)
    print(target_list)

    thread = threading.Thread(target=twitter_rt_watcher.observe_rt)
    thread.start()

    discord_epr_streamer.client.loop.create_task(observe_flag(thread))
    discord_epr_streamer.client.run(discord_epr_streamer.discord_api_keys.token)


if __name__ == '__main__':
    main()
