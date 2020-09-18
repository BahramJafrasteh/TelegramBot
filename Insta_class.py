#Author: Bahram Jafrasteh
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep, strftime
from random import randint
import time
import pandas as pd
import dateutil.parser
import urllib3

import socket
import mysql.connector as msql
import numpy as np
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import random
from pathlib import Path
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from nltk import *
from nltk.corpus import *

def remove_nan_from_list(y):
    y = [x for x in y if str(x) != 'nan']
    return y

comments_list_fa = pd.read_csv("Configs/Comments.csv")['comments_fa'].values.tolist()
comments_list_en = pd.read_csv("Configs/Comments.csv")['comments_en'].values.tolist()

comments_list_en = remove_nan_from_list(comments_list_en)
comments_list_fa = remove_nan_from_list(comments_list_fa)


with open('Configs/emojis.txt') as f:
    unicodes = f.readlines()
    emoji = []
    for line in unicodes:
        fo = line.strip('\n')
        emoji.append(fo)
def check_internet_connection0():
    try:
        http = urllib3.PoolManager()
        url = 'https://www.google.com'
        http.request('GET', url)
        return True
    except urllib3.exceptions.TimeoutError as err:
        return False

def check_internet_connection(hostname = "www.google.com"):
  try:
    # see if we can resolve the host name -- tells us if there is
    # a DNS listening
    host = socket.gethostbyname(hostname)
    # connect to the host -- tells us if the host is actually
    # reachable
    s = socket.create_connection((host, 80), 2)
    s.close()
    return True
  except:
     pass
  return False
def get_page(driver, url, css_val):

    while check_internet_connection():
        wait = WebDriverWait(driver, 20)
        driver.get(url)
        sleep(randint(5, 10))
        try:
            nopage = driver.find_element_by_css_selector('.error-container > h2:nth-child(1)').text
            error_text = driver.find_element_by_css_selector('.error-container > p:nth-child(2)').text
            if error_text == 'Please wait a few minutes before you try again.':
                sleep(randint(100, 200))
            elif nopage == "Sorry, this page isn't available.":
                comment = 'NoPage'
                return False, comment
        except:
            try:
                wait.until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR,
                        css_val
                    )))

                sleep(randint(5, 10))
                driver.execute_script("window.stop();")
                comment = ''
                return True, comment
            except:
                continue
    return False, 'NoInternet'

class Instagram_follow:
    def __init__(self, driver, myuser = '', mypass = '',
                 min_follow_ratio = 0.5,
                 max_follow_ratio = 4.0,
                 max_last_post_day = 30.0,
                 min_num_followers = 50,
                 max_num_followers = 200,
                 method = 'hashtag',
                 user_name = '',
                 check_previous_info = True,
                 min_post_num = 5,
                 max_post_num = 500,
                 max_follows = 3000,
                 num_post_hashtag = 200,
                 num_scroll = 50,
                 skip_post = 40,
                 max_likes = 100,
                 max_like_after_follow = 3
                 ):
        self.insta_database = msql.connect(
            host="localhost",
            user="root",
            passwd="se7en",
            database="Instagram",
        )
        self.cursor = self.insta_database.cursor(buffered=True)

        command_sql = """CREATE TABLE IF NOT EXISTS checked_user(id int PRIMARY KEY AUTO_INCREMENT,
        insta_username varchar(25) not null, num_followers int, num_followings int null, num_posts int null,
        follow BOOLEAN, follow_back BOOLEAN, date timestamp not null default CURRENT_TIMESTAMP, last_post_date timestamp null, PageExist BOOLEAN NULL);"""
        self.cursor.execute(command_sql)

        #cursor.execute("INSERT INTO table VALUES (%s, %s, %s)", (var1, var2, var3))
        self.minfr = min_follow_ratio
        self.maxfr = max_follow_ratio
        self.maxlpd = max_last_post_day
        self.mincfl = min_num_followers
        self.maxcfl = max_num_followers
        self.minpost = min_post_num
        self.maxpost = max_post_num
        self.method = method
        self.username = user_name
        self.driver = driver
        self.check_previous_info = check_previous_info
        self.xpath_insta_logo = '.oJZym > a:nth-child(1) > div:nth-child(1)'
        self.today = datetime.now()
        self.users_followed = []
        self.comments = 0
        self.likes = 0
        self.maxlikes = max_likes
        self.follows = 0
        self.maxlikes_follow = max_like_after_follow
        self.maxfollows =  max_follows
        self.num_post_hashtag = num_post_hashtag # number of hashtags post to check
        self.num_scroll = num_scroll
        self.skip_post = skip_post
        self.myuser = myuser
        self.mypass = mypass
        self.login = False
        self.Instagram_login()
        self.follows_til_now = pd.read_csv('Configs/myFollowingUsers.csv')['Following'].values.tolist()
        self.CheckedPages = pd.read_csv('Configs/CheckedPages.csv')['CheckedPages'].values.tolist()
        self.last_l = 0
        self.len_scroll = 0





    def extract_users(self, user, text):

        num_following = 0

        total_users = []

        filename = "Data/" + user + "_"+ text + ".csv"
        if self.check_previous_info and Path(filename).is_file():
                total_users = pd.read_csv(filename)[text]
        else:
            #url = 'https://www.instagram.com/' + user + '/?hl=en'
            #get_page(self.driver, url, self.xpath_insta_logo)

            sleep(2)
            try:

                #WebDriverWait(self.driver, 5).until(
                #    EC.visibility_of_element_located(
                #        (By.XPATH, xpath)))
                #followings = self.driver.find_element_by_xpath(xpath)
                #followings.click()
                xpath_element = "/html/body/div[4]/div/div[1]/div/h1"
                #WebDriverWait(self.driver, 10).until(
                #    EC.presence_of_all_elements_located(
                #        (By.XPATH, xpath_element)))
                element = self.driver.find_element_by_css_selector('.isgrP')
                last_height = self.driver.execute_script(
                    "return arguments[0].scrollHeight", element)
                self.driver.execute_script("arguments[0].scrollTop = 40000",
                                         element)
                sleep(randint(5, 10))
                r = 0
                while r < 5:
                    self.driver.execute_script(
                        "arguments[0].scrollTop = arguments[0].scrollHeight",
                        element)
                    sleep(2)
                    new_height = self.driver.execute_script(
                        "return arguments[0].scrollHeight", element)
                    if new_height == last_height:
                        r = r + 1
                    last_height = new_height

                nf = 1
                total_users = []
                while True:
                    text_foll = "li.wo9IH:nth-child({}) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > a:nth-child(1)".format(
                        nf)
                    nf = nf + 1
                    try:
                        WebDriverWait(self.driver, 5).until(
                            EC.visibility_of_element_located(
                                (By.CSS_SELECTOR, text_foll)))
                        name_following = self.driver.find_element_by_css_selector(
                            text_foll).text
                        total_users.append(name_following)
                        num_following = num_following + 1
                        print(
                            "follower number = {}, follower name = {}".format(
                                nf, name_following))
                    except:
                        break
            except:
                None

            followingFrame = pd.DataFrame(total_users,
                                          columns=[text])
            followingFrame.to_csv("Data/" + user + "_"+ text + ".csv", index=False)


        return total_users

    def get_user_info(self, user):
        xpath_num_post = '/html/body/span/section/main/div/header/section/ul/li[1]/span/span'

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, xpath_num_post)))

        # number of posts
        num_post_x = self.driver.find_element_by_css_selector(
            'span.-nal3 > span:nth-child(1)'
        ).text
        num_post = int(re.sub('[^0-9]', '', num_post_x))

        num_followers_x = self.driver.find_element_by_css_selector(
            'li.Y8-fY:nth-child(2) > a:nth-child(1) > span:nth-child(1)'
        ).get_attribute('title')
        num_followers = int(re.sub('[^0-9]', '', num_followers_x))


        num_followings_x = self.driver.find_element_by_css_selector(
            'li.Y8-fY:nth-child(3) > a:nth-child(1) > span:nth-child(1)'
        ).text
        num_followings = int(re.sub('[^0-9]', '', num_followings_x))

        if num_followings > 0:
            FollowRatio = num_followers / num_followings
        else:
            FollowRatio = 0

        num_likes = 1
        max_num_likes = 5
        if num_post > 0:
            css_post = 'div.Nnq7C:nth-child(1)> div:nth-child(1)'
            self.driver.find_element_by_css_selector(css_post).click()
            sleep(randint(2,5))
            like_stat = self.like_photo_from_page_initial()
            comment_stat = False
            if random.random() < 0.5:
                comment_stat = self.send_comment()

            self.comments += comment_stat
            self.likes += like_stat


            timestamp = self.driver.find_element_by_css_selector('._1o9PC').get_attribute('datetime')

            date_stamp = dateutil.parser.parse(timestamp).replace(tzinfo=None)
            difs = self.today - date_stamp
            dif_days = difs.total_seconds() / (3600 * 24)

            while True:
                status_post = self.driver.find_element_by_css_selector('._2dDPU').text.find('Next')
                if status_post >= 0:
                    self.driver.find_element_by_css_selector('.HBoOv').click()
                    sleep(randint(2, 5))
                    self.like_photo_from_page_initial()
                    if random.random() < 0.5:
                        comment_stat = self.send_comment()

                    self.comments += comment_stat
                    self.likes += like_stat
                    num_likes += 1
                else:
                    self.driver.find_element_by_css_selector('.ckWGn').click()
                    break
                if num_likes > max_num_likes:
                    self.driver.find_element_by_css_selector('.ckWGn').click()
                    break

        """        xpath_time = '/html/body/div[3]/div[2]/div/article/div[2]/div[2]/a/time'

                elems = self.driver.find_elements_by_xpath("//a[@href]")
                elem_ind = 0
                for elem in elems:
                    link = elem.get_attribute('href')
                    if link.find('/p/') > 0:
                            break
                    elem_ind = elem_ind + 1

                urllink = elems[elem_ind].get_attribute('href')
                get_page(self.driver, urllink, self.xpath_insta_logo)
                like_stat = self.like_photo(urllink)
                self.likes += like_stat
                self.driver.back()
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                self.xpath_insta_logo
            )))
        self.driver.execute_script("window.stop();")
           """


        sleep(randint(3, 5))

        command_sql_finduser = "SELECT IF(NOT EXISTS(SELECT insta_username FROM checked_user WHERE insta_username = '{}'), 1, 0);".format(user)
        self.cursor.execute(command_sql_finduser)
        if self.cursor.fetchone()[0] == 1:

            command_sql = "INSERT INTO checked_user (insta_username, num_followers, num_followings, num_posts, follow, follow_back, last_post_date, PageExist) " \
                      "VALUES ('{}', {} , {} , {}, False, False, TIMESTAMP('{}'), True);"\
            .format(user, num_followers, num_followings, num_post, date_stamp)
            self.cursor.execute(command_sql)
            self.insta_database.commit()


        if num_post > self.maxpost or num_post < self.minpost:
            return False
        if num_followers > self.maxcfl or num_followers < self.mincfl:
            return False
        if FollowRatio > self.maxfr or FollowRatio < self.minfr:
            return False
        if dif_days > self.maxlpd:
            return False

        return True

    def pages_to_follow(self,users_follow):
        count_follow = 0

        for user in users_follow:
            self.cursor.execute("SELECT insta_username FROM checked_user WHERE insta_username = '{}'".format(user))
            if user in self.follows_til_now or user in self.CheckedPages or self.cursor.fetchone() is not None:
                continue
            url = 'https://www.instagram.com/' + user + '/?hl=en'
            stat_page, comment = get_page(self.driver, url, self.xpath_insta_logo)

            if not stat_page:
                with open('Configs/CheckedPages.csv', "a") as myfile:
                    myfile.write(user + '\n')
                command_sql = "INSERT INTO checked_user (insta_username, num_followers, num_followings, num_posts, follow, follow_back, last_post_date, PageExist) " \
                              "VALUES ('{}', NULL , NULL , NULL, False, False, NULL, True);" \
                    .format(user)
                self.cursor.execute(command_sql)
                self.insta_database.commit()
                continue
            with open('Configs/CheckedPages.csv', "a") as myfile:
                myfile.write(user + '\n')

            try:
                self.driver.find_element_by_partial_link_text("follow")

                sleep(randint(5, 10))

                stat_follow = self.get_user_info(user)


                if stat_follow:

                    xpath_button = "/html/body/span/section/main/div/header/section/div[1]/div[1]/span/span[1]/button"
                    try:
                        WebDriverWait(self.driver, 5).until(
                            EC.visibility_of_element_located(
                                (By.XPATH, xpath_button)))

                        following_stat = self.driver.find_element_by_xpath(
                            xpath_button)

                        if following_stat.text == "Follow" and \
                            self.follows < self.maxfollows:

                            following_stat.click()
                            count_follow = count_follow + 1
                            self.users_followed.append(user)
                            self.follows_til_now.append(user)

                            with open('Configs/myFollowingUsers.csv', "a") as myfile:
                                myfile.write(user+'\n')
                            command_sql = "UPDATE checked_user SET follow = TRUE WHERE insta_username = '{}'" .format(user)
                            self.cursor.execute(command_sql)
                            self.insta_database.commit()
                            self.follows += 1
                            print("{} : {} has been followed ".format(
                                count_follow, user))
                            sleep(randint(5, 15))
                            """
                            elems = self.driver.find_elements_by_xpath("//a[@href]")
                            url_ads = []
                            elem_ind = 0
                            link_count = 0
                            for elem in elems:
                                url = elem.get_attribute('href')
                                if url.find('/p') > 0:
                                    link_count += 1
                                    if link_count > self.maxlikes_follow:
                                        break
                                    url_ads.append(url)
                                elem_ind = elem_ind + 1
                            for url in url_ads:
                                like_stat = self.like_photo(url)
                                comment_stat = False
                                if random.random() < 0.5:
                                    comment_stat = self.send_comment()

                                self.comments += comment_stat
                                self.likes += like_stat
                                """
                    except:
                        continue
            except:
                continue
            if self.follows > self.maxfollows:
                break

    def like_photo(self):
        #get_page(self.driver, url, self.xpath_insta_logo)
        string_s = '.fr66n > button:nth-child(1) > svg:nth-child(1)'

        like_status = self.driver.find_element_by_css_selector(string_s)
        string_like_stat = like_status.get_attribute('fill')
        if string_like_stat == '#262626':
            # already liked
            try:
                like_status.click()
            except:
                sleep(randint(5, 10))
            sleep(randint(5, 10))
            liked = True
        else:
            liked = False

        return liked

    def like_photo_from_page_initial(self):
        like_status = self.driver.find_element_by_css_selector('.fr66n > button:nth-child(1) > span:nth-child(1)')
        string_like_stat = like_status.get_attribute('class')
        if string_like_stat.find('filled') < 0:
            # already liked
            like_status.click()
            sleep(randint(5, 10))
            liked = True
        else:
            liked = False

        return liked

    def send_comment(self):

        text_post = self.driver.find_element_by_css_selector('.X7jCj')
        string_text_post = text_post.text
        string_text_post = string_text_post.replace('\n', ' ')
        string_text_post = string_text_post.replace('\u2060', ' ')
        string_text_post = string_text_post.replace(';', ' ')
        string_text_post = string_text_post.replace('.', ' ')

        lang_ratio = {}
        tokens = wordpunct_tokenize(string_text_post)
        words = [word.lower() for word in tokens]
        for language in stopwords.fileids():
            stopwords_set = set(stopwords.words(language))
            words_set = set(words)
            common_el = words_set.intersection(stopwords_set)
            lang_ratio[language] = len(common_el)
        lang = max(lang_ratio, key=lang_ratio.get)
        if lang == 'arabic':
            ind_sel = random.randint(0, len(comments_list_fa))
            comment_final = comments_list_fa[ind_sel]
        elif lang == 'spanish':
            ind_sel = random.randint(0, len(comments_list_en))
            comment_final = comments_list_en[ind_sel]
        else:
            ind_sel = random.randint(0, len(comments_list_en))
            comment_final = comments_list_en[ind_sel]

        try:
            css_selector = '.glyphsSpriteComment__outline__24__grey_9'
            self.driver.find_element_by_css_selector(css_selector).click()
            # sleep(1)
            xpath_text_area = "/html/body/div[3]/div[2]/div/article/div[2]/section[3]/div/form/textarea"
            #WebDriverWait(self.driver, 10).until(
            #   EC.presence_of_all_elements_located((By.XPATH, xpath_text_area)))
            # sleep(1)
            comment_box = self.driver.find_element_by_css_selector('.Ypffh')

            comment_box.send_keys(comment_final + emoji[randint(
                0, len(emoji) - 1)].encode('ASCII').decode('unicode-escape'))
            sleep(randint(2, 6))
            # Enter to post comment
            comment_box = self.driver.find_element_by_css_selector('.Ypffh')
            comment_box.send_keys(Keys.ENTER)
            sleep(randint(15, 20))
            comment_box.send_keys(Keys.ENTER)
            comment_sent = True
        except:
            comment_sent = False

        return comment_sent


    def get_account_type(self, user):
        try:
            self.driver.find_element_by_css_selector('.mrEK_')
            return ('Verified')
        except:
            None

        try:
            self.driver.find_element_by_css_selector('.rkEop')
            return ('Private')
        except:
            None

        return ('Public')



    def singluser(self):

        sleep(randint(1, 2))

        xpath_followers = '/html/body/span/section/main/div/header/section/ul/li[2]/a'
        xpath_followings = '/html/body/span/section/main/div/header/section/ul/li[3]/a'
        user = self.username

        account_type = self.get_account_type(user)

        if account_type == 'Public':
            total_followings = self.extract_users(user, xpath_followings, text = 'Following')
            total_followers = self.extract_users(user, xpath_followers, text= 'Followers')
            users = pd.concat([total_followers, total_followings]).values
            users = list(set(users))
            self.pages_to_follow(users)
        else:
            None

        followingFrame = pd.DataFrame(self.users_followed,
                                      columns=["Following"])
        filename = 'Following-' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '.csv'
        followingFrame.to_csv(filename, index=False)

    def my_followers(self):

        sleep(randint(1, 2))

        url = 'https://www.instagram.com/' + self.myuser + '/?hl=en'
        get_page(self.driver, url, self.xpath_insta_logo)


        xpath_followers = '/html/body/span/section/main/div/header/section/ul/li[2]/a'
        xpath_followings = '/html/body/span/section/main/div/header/section/ul/li[3]/a'

        #total_followings = self.extract_users(myuser, xpath_followings, text='Following')
        total_my_followers = self.extract_users(self.myuser, xpath_followers, text='Followers')

        total_follows = []
        for user in total_my_followers:
            total_followers = self.extract_users(user, xpath_followers, text='Followers')
            self.pages_to_follow(total_followers)
            total_follows.append(total_followers)
            if self.follows > self.maxfollows:
                break
        followingFrame = pd.DataFrame(total_follows,
                                      columns=["Following"])
        filename = 'Following-'+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+'.csv'
        followingFrame.to_csv(filename, index=False)


    def hashtag(self, hashtg):

        sleep(randint(1, 2))

        url = 'https://www.instagram.com/explore/tags/' + hashtg + '/'
        get_page(self.driver, url, self.xpath_insta_logo)

        Blacklists_frame = pd.read_csv("Configs/Blacklists.csv")["Blacklists"]
        BlackLists = Blacklists_frame.values.tolist()

        txt_num_follow_hastag = self.driver.find_element_by_css_selector('.g47SY').text
        num_follow_hastag = int(re.sub('[^0-9]', "", txt_num_follow_hastag))
        print("There are {} posts for hashtag : {}".format(num_follow_hastag,
                                                           hashtg))

        for ni in range(1, self.num_scroll):
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            sleep(randint(8,10))

        elems = self.driver.find_elements_by_xpath("//a[@href]")
        url_links = []
        for elem in elems:
            link = elem.get_attribute('href')
            if link.find('/p/')>0:
                url_links.append(link)
        post_check = 0
        for url in url_links:

            like_stat = self.like_photo(self.driver, url)
            comment_stat = False
            if random.random() < 0.5:
                comment_stat = self.send_comment()
            self.comments += comment_stat
            self.likes += like_stat
            username = self.driver.find_element_by_css_selector('.nJAzx').text
            url = 'https://www.instagram.com/' + username + '/?hl=en'
            get_page(self.driver, url, self.xpath_insta_logo)
            css_select = '._6VtSN'
            follow_stat = self.driver.find_element_by_css_selector(css_select)
            if follow_stat.text == 'Follow':
                follow_stat.click()
                self.users_followed.append(username)
                self.follows += 1
                print("{} : {} has been followed ".format(
                    self.follows, username))
                sleep(randint(5, 15))
            post_check += 1
            if post_check > self.num_post_hashtag:
                break

            self.today
            followingFrame = pd.DataFrame(self.users_followed,
                                          columns=["Following"])
            filename = 'Following-'+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+'.csv'
            followingFrame.to_csv(filename, index=False)




    def like_posts(self):
        def get_css_add():
            if l > 4:
                return 'article._8Rm4L:nth-child(1) > div:nth-child(3) > div:nth-child(4) > a:nth-child(1)'
            else:
                return 'article._8Rm4L:nth-child({}) > div:nth-child(3) > div:nth-child(4) > a:nth-child(1)'.format(l)
        def get_like_stat():
            if l > 4:
                return 'article._8Rm4L:nth-child(4) > div:nth-child(3) > section:nth-child(1) > span:nth-child(1) >' \
                       ' button:nth-child(1) > svg:nth-child(1)'
            else:
                return 'article._8Rm4L:nth-child({}) > div:nth-child(3) > section:nth-child(1) > span:nth-child(1) >' \
                       ' button:nth-child(1) > svg:nth-child(1)'.format(l)

        def like_post():
            like_status = self.driver.find_element_by_css_selector(get_like_stat())
            string_like_stat = like_status.get_attribute('fill')
            if string_like_stat == '#262626':
                # like post
                try:
                    like_status.click()
                    print('{} photos has been liked so far'.format(num_likes))
                    sleep(randint(50, 80))
                    return True
                except:
                    sleep(randint(5, 10))
                    return False
            sleep(randint(5, 10))
            return False
        if self.len_scroll == 0:
            url = 'https://www.instagram.com/'
            get_page(self.driver, url, self.xpath_insta_logo)
            len_scroll = 300
            start_time = time.time()
            while True:
                self.driver.execute_script("window.scrollTo(0,{});".format(len_scroll))
                len_scroll += 100
                if time.time() > start_time + 30:
                    break
            element = self.driver.find_element_by_css_selector('.SCxLW')
            max_height = self.driver.execute_script(
                "return arguments[0].scrollHeight", element)

            len_scroll = 300
            self.driver.execute_script("window.scrollTo(0,{});".format(len_scroll))
            l = 1
        else:
            len_scroll = self.len_scroll
            l = self.last_l
            max_height = self.max_height
        num_likes = 0
        like_stat = False

        sleep(randint(5, 10))

        css_add_like = get_css_add()
        newurl = self.driver.find_element_by_css_selector(css_add_like).get_property('href')
        prevurl = newurl
        while num_likes < self.maxlikes:

            try:
                like_stat = like_post()
                if l < 4:
                    l += 1
                while newurl == prevurl:
                    try:
                        css_add_like = get_css_add()
                        newurl = self.driver.find_element_by_css_selector(css_add_like).get_property('href')
                        #break
                    except:
                        None
                    self.driver.execute_script("window.scrollTo(0,{});".format(len_scroll))
                    len_scroll += 100
                    if len_scroll>= max_height:
                        break
                prevurl = newurl

                comment_stat = False
                if like_stat == False:
                    print("photo already have been liked")
                else:
                    num_likes = num_likes + 1
                    print("{} photos have been liked so far".format(num_likes))
                    if random.random() < -1:
                        comment_stat = self.send_comment()
            except:
                None


            sleep(randint(5, 7))
            self.driver.execute_script("window.stop();")

            sleep(4)
            #self.comments += comment_stat
            self.likes += like_stat
            if like_stat > 0:
                print('Number of post likes: {}'.format(self.likes))
            if self.likes > self.maxlikes:
                break
        self.len_scroll = len_scroll
        self.last_l = l
        self.max_height = max_height

    def unfollow(self):
        self.driver.find_element_by_css_selector('.gmFkV').click()

        sleep(randint(10,15))
        if self.check_previous_info:
            # total following
            total_name_following = pd.read_csv("Following.csv")["Following"]
            # total followers
            total_name_followers = pd.read_csv("Followers.csv")["Followers"]
        else:
            if prinf == 1:
                self.check_previous_info = True
            #url = 'https://www.instagram.com/' + self.myuser + '/?hl=en'
            #get_page(self.driver, url, self.xpath_insta_logo)

            sleep(2)

            xpath_followers = '/html/body/span/section/main/div/header/section/ul/li[2]/a'
            xpath_followings = '/html/body/span/section/main/div/header/section/ul/li[3]/a'

            self.driver.find_element_by_css_selector('li.Y8-fY:nth-child(3) > a:nth-child(1)').click()
            sleep(randint(5,10))
            total_name_following = self.extract_users(self.myuser, text = 'Following')
            close_windows_string = 'div.WaOAr:nth-child(3) > button:nth-child(1) > svg:nth-child(1)'
            self.driver.find_element_by_css_selector(close_windows_string).click()

            self.driver.find_element_by_css_selector('li.Y8-fY:nth-child(2) > a:nth-child(1)').click()
            total_name_followers = self.extract_users(self.myuser, text= 'Followers')
            self.driver.find_element_by_css_selector(close_windows_string).click()

            followersFrame = pd.DataFrame(total_name_followers,
                                          columns=["Followers"])
            followersFrame.to_csv("Followers.csv", index=False)
            followingFrame = pd.DataFrame(total_name_following,
                                          columns=["Following"])
            followingFrame.to_csv("Following.csv", index=False)
        Blacklists_frame = pd.read_csv("Configs/Blacklists.csv")["Blacklists"]

        #xpath_followings = '/html/body/span/section/main/div/header/section/ul/li[3]/a'

        #if self.check_previous_info == True:
         #   self.driver.find_element_by_css_selector('li.Y8-fY:nth-child(3) > a:nth-child(1)').click()
          #  sleep(randint(5, 10))
           # self.check_previous_info = False
            #self.extract_users(self.myuser, text='Following')
            #self.driver.find_element_by_css_selector('.wpO6b > svg:nth-child(1)').click()
            #self.check_previous_info = True



        sleep(randint(5,10))
        # difference between following and followers
        list_to_be_unfollowed = list(
            set(total_name_following[10:]) - set(total_name_followers))

        # exception list
        exception_list = pd.read_csv("Configs/Exception_list.csv")["exception"]

        FinalListUnf = list(set(list_to_be_unfollowed) - set(exception_list))
        list1 = Blacklists_frame.values.tolist()
        list2 = FinalListUnf
        list_fn = list1 + list2

        # unique black lists
        list_fn = list(set(list_fn))

        # save black lists
        Final_Blacklist = pd.DataFrame(list_fn, columns=["Blacklists"])
        Final_Blacklist.to_csv("Configs/Blacklists.csv", index=False)



        for user_un in FinalListUnf:
            sleep(randint(100, 150))

            gg = '''window.open("''' '''","_blank");'''
            self.driver.execute_script(gg)
            windowhandles = self.driver.window_handles
            self.driver.switch_to.window(windowhandles[1])
            ulr_add = 'https://www.instagram.com/' + user_un
            page_reachable, _ = get_page(self.driver, ulr_add, self.xpath_insta_logo)
            if page_reachable:
                print("Process Unfollowing {}".format(user_un))

                self.driver.execute_script("window.stop();")
                follow_sit_string = '.glyphsSpriteFriend_Follow'
                try:
                    if self.driver.find_element_by_css_selector(follow_sit_string).get_attribute(
                            'aria-label') == 'Following':
                        # unfollow button
                        self.driver.find_element_by_css_selector(follow_sit_string).click()
                        sleep(randint(5, 10))
                        # confirm it
                        unfollow_str = 'button.aOOlW:nth-child(1)'
                        self.driver.find_element_by_css_selector(unfollow_str).click()
                        sleep(randint(5, 10))
                        self.driver.close()
                        windowhandles = self.driver.window_handles
                        self.driver.switch_to.window(windowhandles[0])
                        sleep(randint(5, 10))
                    else:
                        sleep((randint(100,200)))
                        print('page {} does not exitst'.format(user_un))
                except:
                    print('{} has been unfollowed'.format(user_un))

        windowhandles = self.driver.window_handles
        self.driver.switch_to.window(windowhandles[0])
        return

    def Instagram_login(self):
        if not self.login:
            url = 'https://www.instagram.com/accounts/login/?source=auth_switcher'
            get_page(self.driver, url, '.NXVPg')


            sleep(randint(5,10))
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "[name=username]"))).send_keys(self.myuser)
            self.driver.find_element_by_css_selector('[name=password]').send_keys(self.mypass)
            sleep(randint(5,10))
            login = self.driver.find_element_by_xpath("//button[contains(.,'Log')]")
            login.click()
            sleep(randint(5,10))
            notnow = WebDriverWait(self.driver, 15).until(
                lambda d: d.find_element_by_xpath('//button[text()="Not Now"]'))
            notnow.click()
            sleep(randint(5,10))
            self.login = True
        else:
            url = 'https://www.instagram.com/accounts/login/?source=auth_switcher'
            get_page(self.driver, url, '.s4Iyt')

