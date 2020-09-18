#AUTHOR: Bahram Jafrasteh
from Insta_class import *
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import sleep
if __name__ == '__main__':
    user_name = '-'#input('please enter your instagram username: ')
    passwd = '-' #input('please enter your instagram password: ')

    #chromedriver_path = '/usr/bin/chromedriver'  # Change this to your own chromedriver path!
    gecko_path = '/usr/local/bin/geckodriver'
    capa = DesiredCapabilities.FIREFOX
    capa["pageLoadStrategy"] = "none"
    webdriver = webdriver.Firefox(executable_path=gecko_path,
                                  desired_capabilities=capa)
    firstent_like = True
    while True:
        sleep(2)
        read_arguments = True
        modes = ['unfollow', 'like', 'hashtag', 'search', 'none']
        option = input(
            "please choose a mode from 'like', 'unfollow', 'hashtag', 'search': "
        )
        while option not in modes:
            option = input(
                "please choose a mode from 'like', 'unfollow', 'hashtag', 'search': "
            )


        if option == 'like':
            if firstent_like:
                Instalike = Instagram_follow(
                    driver= webdriver,
                    myuser = user_name,
                    mypass = passwd,
                    method = 'like',
                    num_scroll = 50,
                    max_likes = 50
                     )
                firstent_like = False
            Instalike.like_posts()
        elif option == 'search':
            InstaSearch = Instagram_follow(
                driver=webdriver,
                myuser=user_name,
                mypass=passwd,
                min_follow_ratio=0.3,
                max_follow_ratio=2.0,
                max_last_post_day=60.0,
                min_num_followers=50,
                max_num_followers=10000,
                method='search',
                user_name='lorestantourism',
                check_previous_info=True,
                min_post_num=5,
                max_post_num=2000,
                max_follows=300,
                max_like_after_follow = 3
            )
            InstaSearch.singluser()
        elif option == 'unfollow':
            InstaSearch = Instagram_follow(driver=webdriver,
                myuser=user_name,
                mypass=passwd,
                method='unfollow',
                user_name='',
                check_previous_info=True,
            )
            InstaSearch.unfollow()
        elif option == 'hashtag':
            hashtagfilename = 'hashtags.txt'
            hashtag_list = pd.read_csv(hashtagfilename)['hashtags']

            print('You have chosen the following hashtags: \n')
            for hs in hashtag_list:
                print(hs)
                InstaSearch = Instagram_follow(
                driver=webdriver,
                myuser=user_name,
                mypass=passwd,
                min_follow_ratio=0.5,
                max_follow_ratio=4.0,
                max_last_post_day=30.0,
                min_num_followers=50,
                max_num_followers=200,
                method='hashtag',
                check_previous_info=True,
                min_post_num=5,
                max_post_num=500,
                max_follows=3000,
                num_post_hashtag=200,
                num_scroll=50,
                skip_post=40,
            )
        elif option == 'none':
            break
    webdriver.close()
