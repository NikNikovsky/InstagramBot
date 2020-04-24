from InstagramAPI import InstagramAPI
from database import db
from imgur import im
import asyncio
import codecs
import constants

#this class makes communicating with instagram api straightforward
class InstaAPI:
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.iGram = InstagramAPI(self.username, self.password)
        self.iGram.login()

    #this function takes a username and returns a pk, AKA user id
    def returnId(self, targetUsername):

        self.iGram.searchUsername(targetUsername)
        self.response = self.iGram.LastJson

        if 'message' in self.response and self.response['satus'] == 'fail':
            print(f"[INSTAGRAM] Warning! No Instagram account found with username: {targetUsername}!")
            return False

        if self.response['status'] == 'ok':
            return self.response['user']['pk']


    def getRecentImages(self, targetUsername):
        self.instaId = returnId(targetUsername)
        if self.instaId == False:
            return False

        #getting the user id, getting the feed, formatting, and returning the most recent pk
        self.userId = returnId(targetUsername)

        if self.userId == False:
            print(f"[INSTAGRAM] Warning! Unable to get feed of user {targetUsername} due to above error!")
            return False

        self.iGram.getUserFeed(userId)
        self.userFeed = self.iGram.LastJson
        if self.userFeed['num_results'] == 0:
            print(f"[INSTAGRAM] Warning! Feed of user {targetUsername} is empty!)
            return False

        if 'message' in self.userFeed and self.userFeed['status'] == 'fail':
            print(f"[INSTAGRAM] Warning! Unknown Instaram API error: \"{message}\"!")
            return False

        return self.userFeed


    #this function checks if there are any new images from a given account
    #and if so, uploads that image and returns the imgur URL
    async def getAndUpload(self, conn_id):
        #blank list that will eventually hold our url[s]
        self.urlOut = []

        #getting the pk of the most recent post checked
        self.connection = db.returnConnection(conn_id)
        if self.connection != False:
            self.recentPost = self.connection['previousPost']
            self.targetPk = self.connection['instagramAccount']

        if self.connection == False:
            print("[INSTAGRAM] Warning! Failed due to above error!")
            return False

        #getting the account's most recent post (from instagram)
        self.accountFeed = getRecentImages(self.targetUsername)
        self.accountRecentPost = self.accountFeed['items'][0]['pk']
        if self.accountRecentPost == False:
            print("[INSTAGRAM] Warning! Returning recent image failed due to above error!")
            return False

        if self.recentPost == self.accountRecentPost:
            print(f"[INSTAGRAM] Message! No new posts were found for user {targetUsername}")
            return self.urlOut

        if 'carousel_media' in self.accountFeed['items'][0]:
            for slide in self.accountFeed['items'][0]['carousel_media']:
                if slide['media_type'] == 1:
                    self.urlOut.append(slide['image_versions2']['candidates'][0]['url'])

        if 'carousel_media' not in self.accountFeed['items'][0]:
            if slide['media_type'] == 1:
                self.urlOut.append(self.accountFeed['items'][0]['image_versions2']['candidates'][0]['url'])

        """Now, we do something with our data"""
        #making a title
        self.postTitle = f"New post from Instagram user @{self.connection['instagramAccountUsername']} for r/{self.connection['subreddit']}"
        #getting the caption
        if 'caption' in self.accountFeed['items'][0]:
            if self.accountFeed['items'][0]['caption'] != '':
                self.postCaption = f"Caption from post: \"{self.accountFeed['items'][0]['caption'].encode("utf-8").decode("utf-8")}\""

        if len(self.urlOut) == 0:
            print("[INSTAGRAM] Warning! Program recevied empty out list! Quitting!")
            return 0

        if len(self.urlOut) == 1:
            image = im.uploadImage(self.urlOut[0], self.postTitle, self.postCaption)

        if len(self.urlOut) >=2 :
            image = im.uploadAlbum(self.urlOut, self.postTitle, self.postCaption)

        #updating the database with some info
        db.updateTable(self.connection['id'], self.accountRecentPost, 1)

        #formatting and returning a link
        if 'link' in image:
            return image['link']

        if 'id' in image:
            return f"https://imgur.com/a/{image['id']}"




ig = InstaAPI(constants.INSTAGRAM_USERNAME, constants.INSTAGRAM_PASSWORD)
