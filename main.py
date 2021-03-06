# IMPORTS
from datetime import datetime
import csv
import tweepy
import time

# PROPERTIES
data = []
apiSwitchCount = 0

# INPUTs
usernames = []
number_of_tweets = 30

# JSON INIT
import json
file = open("input.json","r")
inputs = json.loads(file.read())

# API CREDS 1
consumer_key=inputs["api_key"]
consumer_secret=inputs["api_key_secret"]
access_key=inputs["access_token"]
access_secret=inputs["access_secret"]
bearer_token=inputs["bearer_token"]
currentAPI = 1

# API INIT
auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_key,access_secret)
api = tweepy.API(auth)
client = tweepy.Client(bearer_token)

def main():

  global auth
  global api
  global client

  readCSV()
  
  for username in usernames:
    
    print("🔍 Evaluating ", username)
    getData(username)
    # Convert the "Data" list to a spreadsheet
    toCsv(data, username)

def readCSV():

  global usernames
    
  # Using readlines()
  file1 = open('players.txt', 'r')
  Lines = file1.readlines()

  # Strips the newline character
  for line in Lines:
    line = line.replace("@","")
    line = line.replace('\n', '')
    usernames.append(line)

def init(consumer_key, consumer_secret, access_key,access_secret,bearer_token):

  global auth
  global api
  global client
  
  # API INIT
  auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
  auth.set_access_token(access_key,access_secret)
  api = tweepy.API(auth)
  client = tweepy.Client(bearer_token)

  print("        - Api + Client initialized with new credentials")
  

def switchAPI():

  time.sleep(15)

  global apiSwitchCount
  global file
  global inputs
  global currentAPI

  if apiSwitchCount==0:
    
    # API CREDS 2
    consumer_key=inputs["api_key"]
    consumer_secret=inputs["api_key_secret"]
    access_key=inputs["access_token"]
    access_secret=inputs["access_secret"]
    bearer_token=inputs["bearer_token"]
    
    init(consumer_key, consumer_secret, access_key,access_secret,bearer_token)

    print("                - API Creds 1")
    currentAPI = 1
    apiSwitchCount +=1
    
  elif apiSwitchCount == 1:
    
    # API CREDS 2
    consumer_key=inputs["api_key_2"]
    consumer_secret=inputs["api_key_secret_2"]
    access_key=inputs["access_token_2"]
    access_secret=inputs["access_secret_2"]
    bearer_token=inputs["bearer_token_2"]
    
    init(consumer_key, consumer_secret, access_key,access_secret,bearer_token)
    
    print("                - API Creds 2")
    currentAPI = 2
    apiSwitchCount += 1
    
  elif apiSwitchCount == 2:

    # API CREDS 2
    consumer_key=inputs["api_key_3"]
    consumer_secret=inputs["api_key_secret_3"]
    access_key=inputs["access_token_3"]
    access_secret=inputs["access_secret_3"]
    bearer_token=inputs["bearer_token_3"]
    
    init(consumer_key, consumer_secret, access_key,access_secret,bearer_token)
    
    print("                - API Creds 3")
    currentAPI = 3
    apiSwitchCount = 0

def getData(username):

  # START Time
  start = datetime.now().time()

  credentialsUsed = []
    
  # Get a X amount of Tweets from the specified user
  tweet_IDs = getPaginatedTweets(username, number_of_tweets)
  credentialsUsed.append(currentAPI)
  
  statusMetrics = getStatusMetrics(tweet_IDs)
  credentialsUsed.append(currentAPI)
  
  followerCount = getFollowerCount(username)
  credentialsUsed.append(currentAPI)
  
  replyCount = getReplies(tweet_IDs)
  credentialsUsed.append(currentAPI)

  userMetrics = [username,
                 followerCount,
                 statusMetrics[0],
                 statusMetrics[1],
                 replyCount,
                 start,
                 datetime.now().time(),
                 number_of_tweets,
                 credentialsUsed]

  # Add this fan and their data to the "Data" list
  data.append(userMetrics)
  
def toCsv(data, username):

  # Open or create a CSV file, with "w" or write permission
  f = open("data.csv", "w")

  # initialize the writer
  writer = csv.writer(f)

  # write the header
  writer.writerow(["User",
                   "Follower Count",
                   "Total Likes",
                   "Total Retweets",
                   "Total Replies",
                   "Start Time",
                   "End Time",
                   "Number of Tweets Evaluated",
                  "API Credentials Set"])

  # write a new row for each fan and their data
  for fan in data:
    writer.writerow(fan)
  f.close()

  print("    - ✅ Data written to csv file ")
  
def getPaginatedTweets(username, number_of_tweets):

  tweetIdList = []
  
  print("    - Gathering Tweet IDs...")

  while True:
    try:
      
      for tweet in tweepy.Cursor(api.user_timeline,
                                 screen_name=username,
                                 include_rts='false',
                                 count=200).items(number_of_tweets):
        tweetIdList.append(tweet.id)
      break
    except tweepy.errors.Unauthorized as e:
      print("        - Unauthorized")
      print("        - Current API Creds: ", currentAPI)
      print("        - Error: ", e)
      break
    except tweepy.errors.TooManyRequests as e:
      print(("        - Too many requests... switching creds"))
      print("        - Current API Creds: ", currentAPI)
      print("        - Error: ", e)
      switchAPI()
      continue
    except tweepy.errors.NotFound as e:
      print("        - Current API Creds: ", currentAPI)
      print("        - Error: ", e)
      break
    except tweepy.errors.Forbidden as e:
      print("        - Current API Creds: ", currentAPI)
      print("        - Error: ", e)
      print("        - Forbidden")
      break
    except:
      time.sleep(900)
      switchAPI()

  # return the entire list of Tweet IDs
  return(tweetIdList)

def getRetweets(tweetIdList):
  
  retweets = 0

  print("    - Counting retweets...")
  for tweet in tweetIdList:
    while True:
      try:
        tweet = api.get_status(tweet)
        retweets += tweet.retweet_count
        break
      except tweepy.errors.Unauthorized as e:
        print("        - Unauthorized")
        print("        - Current API Creds: ", currentAPI)
        print("        - Error: ", e)
        switchAPI()
        break
      except tweepy.errors.TooManyRequests as e:
        print(("        - Too many requests... switching creds"))
        print("        - Current API Creds: ", currentAPI)
        print("        - Error: ", e)
        switchAPI()
        continue
      except tweepy.errors.NotFound as e:
        print("        - Current API Creds: ", currentAPI)
        print("        - Error: ", e)
        break
      except:
        time.sleep(900)
        switchAPI()

  print("        - ", retweets, " Retweets")
  return(retweets)

def getLikes(tweetIdList):

  likes = 0
  
  print("    - Counting favorites...")
  for tweet in tweetIdList:
    
    while True:
      try:
        tweet = api.get_status(tweet)
        likes += tweet.favorite_count
        break
      except tweepy.errors.Unauthorized as e:
        print("        - Unauthorized")
        print("        - Current API Creds: ", currentAPI)
        print("        - Error: ", e)
        switchAPI()
        break
      except tweepy.errors.TooManyRequests as e:
        print(("        - Too many requests... switching creds"))
        print("        - Current API Creds: ", currentAPI)
        print("        - Error: ", e)
        switchAPI()
        continue
      except tweepy.errors.NotFound as e:
        print("        - Current API Creds: ", currentAPI)
        print("        - Error: ", e)
        break
      except:
        time.sleep(900)
        switchAPI()
  
  print("        - ", likes, " Likes")
  return(likes)

def getStatusMetrics(tweetIdList):

  likes = 0
  retweets = 0
  
  print("    - Counting favorites and retweets...")
  for tweet in tweetIdList:
    
    while True:
      try:
        tweet = api.get_status(tweet)
        likes += tweet.favorite_count
        retweets += tweet.retweet_count
        break
      except tweepy.errors.Unauthorized as e:
        print("        - Unauthorized")
        print("        - Current API Creds: ", currentAPI)
        print("        - Error: ", e)
        switchAPI()
        break
      except tweepy.errors.TooManyRequests as e:
        print(("        - Too many requests... switching creds"))
        print("        - Current API Creds: ", currentAPI)
        print("        - Error: ", e)
        switchAPI()
        continue
      except tweepy.errors.NotFound as e:
        print("        - Current API Creds: ", currentAPI)
        print("        - Error: ", e)
        break
      except:
        time.sleep(900)
        switchAPI()
        
  print("        - ", likes, " Likes")
  print("        - ", retweets, " Retweets")
  return([likes,retweets])

def getReplies(tweetIDList):

  replies = 0

  print("    - Counting replies...")
  for tweet in tweetIDList:

    while True:
      try:
        client_result = client.get_tweet(tweet, \
            tweet_fields=["public_metrics"])
        tweet = client_result.data
        replies += tweet.public_metrics["reply_count"]
        break
      except tweepy.errors.Unauthorized as e:
        print("        - Unauthorized")
        print("        - Current API Creds: ", currentAPI)
        print("        - Error: ", e)
        switchAPI()
        break
      except tweepy.errors.TooManyRequests as e:
        print(("        - Too many requests... switching creds"))
        print("        - Current API Creds: ", currentAPI)
        print("        - Error: ", e)
        switchAPI()
        continue
      except tweepy.errors.NotFound as e:
        print("        - Error: ", e)
        break
      except:
        time.sleep(900)
        switchAPI()

  print("        - ", replies, " Replies")
  return(replies)

def getFollowerCount(fan):

  followers = 0

  print("    - Counting followers...")

  while True:
    try:
      user = api.get_user(screen_name=fan)
      followers = user.followers_count
      break
    except tweepy.errors.Unauthorized as e:
      print("        - Unauthorized")
      print("        - Current API Creds: ", currentAPI)
      print("        - Error: ", e)
      break
    except tweepy.errors.TooManyRequests as e:
      print(("        - Too many requests... switching creds"))
      print("        - Current API Creds: ", currentAPI)
      print("        - Error: ", e)
      switchAPI()
      continue
    except tweepy.errors.Forbidden as e:
      print("        - Forbidden")
      print("        - Current API Creds: ", currentAPI)
      print("        - Error: ", e)
      break
    except tweepy.errors.NotFound as e:
      print("        - Current API Creds: ", currentAPI)
      print("        - Error: ", e)
      break
    except:
      time.sleep(900)
      switchAPI()

  print("        - ", followers, " Followers")

  return(followers)

main()
