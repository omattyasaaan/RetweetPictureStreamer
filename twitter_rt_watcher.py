import threading
from datetime import timedelta
import json
import time
import tweepy

# import discord_epr_streamer

class TwitterApiKyes():
    def __init__(self):
        with open('properties.json') as f:
            properties = json.load(f)
            twitter_properties = properties['twitter_api']
            f.close()
        self.consumer_key = twitter_properties['consumer_key']
        self.consumer_secret = twitter_properties['consumer_secret']
        self.access_token = twitter_properties['access_token']
        self.access_token_seret = twitter_properties['access_token_seret']

is_rt = False
url = ''
is_update_user = False
twitter_properties = TwitterApiKyes()

class MyStreamListener(tweepy.StreamListener):
    def __init__(self, observing_list):
        super(MyStreamListener, self).__init__()
        self.counter = 0
        self.observing_list = observing_list
        # self.sync_q = sync_q

    def on_status(self, status):
        global is_rt
        global url
        global is_update_user
        # 画像つきツイート, RTされたorRTしたツイート, 登録ユーザのリツイート
        if 'media' in status.entities:
            if status.text[:2]=='RT' :
                if any(status.author.id_str == user for user in self.observing_list):
                    url = 'https://twitter.com/'+status.retweeted_status.user.screen_name + '/status/' +status.retweeted_status.id_str
                    is_rt = True
                    print(url)
        print(status.text)
        if is_update_user:
            return False

    def on_error(self, status_code):
        print('エラー発生: '+ str(status_code))
        return True

    def on_timeout(self):
        print('タイムアウト')
        return True
    
    def on_exception(self, exception):
        print('例外エラー:' + str(exception))
        return

    def on_limit(self, track):
        print('受信リミットが発生しました:' + str(track))
        return
    
    def discord_epr_report(url):
        discord_epr_streamer.notify_from_twitter(url)


def get_targets(api):
    with open('user_list.json') as f:
        user_list = json.load(f)
        users = user_list['user_list']
        user_id_list = list()
        for user in users:
            user_info = api.get_user(user)
            user_id_list.append(user_info.id_str)
        f.close()
    return user_id_list
    
    
def start_discord_bot():
    discord_epr_streamer.bot_start()


def authenticate_twitter():
    auth = tweepy.OAuthHandler(twitter_properties.consumer_key, twitter_properties.consumer_secret)
    auth.set_access_token(twitter_properties.access_token, twitter_properties.access_token_seret)
    api = tweepy.API(auth)
    return api


def observe_rt():
    global is_update_user
    twitter_api = authenticate_twitter()
    target_list = get_targets(twitter_api)

    auth = tweepy.OAuthHandler(twitter_properties.consumer_key, twitter_properties.consumer_secret)
    auth.set_access_token(twitter_properties.access_token, twitter_properties.access_token_seret)

    my_stream_listener = MyStreamListener(target_list)
    my_stream = tweepy.Stream(auth, my_stream_listener)
    
    while not is_update_user:
        try:
            my_stream.filter(follow=target_list, is_async=False)
        except:
            pass
    print('end')


def main():
    auth = tweepy.OAuthHandler(twitter_properties.consumer_key, twitter_properties.consumer_secret)
    auth.set_access_token(twitter_properties.access_token, twitter_properties.access_token_seret)
    api = tweepy.API(auth)
    target_list = get_targets(api)
    print(target_list)
    # user_info = api.get_user('omattyasaaan')
    # print(user_info.id_str)
    
    my_stream_listener = MyStreamListener(target_list)
    my_stream = tweepy.Stream(auth, my_stream_listener)
    my_stream.filter(follow=target_list, is_async=False)
    #fllowで指定したユーザの「リツイートされたツイート」も対象になっている
    # while True:
    #     try:
    #         my_stream.filter(follow=target_list, is_async=False)
    #     except:
    #         pass



if __name__ == '__main__':
    main()