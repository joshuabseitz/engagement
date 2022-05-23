import csv
import tweepy

# Read inputs.json file
import json
file = open("input.json","r")
inputs = json.loads(file.read())

# Pulling search criteria from input.json
number_of_tweets = 0

# Pulling Twitter API information from input.json
consumer_key=inputs["api_key"]
consumer_secret=inputs["api_key_secret"]
access_key=inputs["access_token"]
access_secret=inputs["access_secret"]
bearer_token=inputs["bearer_token"]
username = ""

# API Construction
auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_key,access_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)
client = tweepy.Client(bearer_token,wait_on_rate_limit=True)

def main():

  # usernames =  ["DianaTaurasi","s10bird","jewellloyd","breannastewart","skydigg4", "brittneygriner","de11edonne","_AJAWILSON22","nnekaogwumike","kaymac_2123","chelsea_dungee","dijonaivictoria","deauzya","breezyyy14","eweezy_for3eezy","T_Cloud4","kelseyplum10","bigmamastef","slletget","werofierro","calvo05oficial","quiotosamir","hopesolo","sydneyleroux","sincy12","julieertz","mpinoe","alexmorgan13","carlilloyd","christenpress","lindseyhoran","amyrodriguez8","sarah_luebbe","sebastianaho","jhugh86"]

  usernames =  ["DianaTaurasi","s10bird"]
  number_of_tweets = 5

  for uname in usernames:

    username = uname
    
    # Get a X amount of Tweets from the specified user
    tweet_IDs = getPaginatedTweets(username, number_of_tweets)

    # get last Tweet for reference in replies request (i.e. get repliese since this last Tweet)
    lastTweetId = tweet_IDs[len(tweet_IDs)-1]
    print("Last Tweet ID: ", lastTweetId)

    # get replies
    repliers = getPaginatedReplies(lastTweetId)
  
    replierCount = 0
    
    for fan in repliers:
      replierCount += 1
  
    print("Reply Count ", replierCount)
  
    # Get all retweeters of each Tweet
    retweeters = getPaginatedRts(tweet_IDs)
  
    retweetersCount = 0
    
    for fan in retweeters:
      retweetersCount += 1
  
    print("Retweet Count ", retweetersCount)
  
    # Get all likers of each Tweet
    likers = getPaginatedLikes(tweet_IDs)
  
    likersCount = 0
    
    for fan in likers:
      likersCount += 1
  
    print("Liker Count ", likersCount)
  
    print("----- STORING FAN DATA -----")
    data = []
  
    # Add this fan and their data to the "Data" list
    data.append([username, likersCount, retweetersCount, replierCount])
      
  # Convert the "Data" list to a spreadsheet
  toCsv(data)
  
def toCsv(data):

  # Open or create a CSV file, with "w" or write permission
  f = open("data.csv", "w")

  # initialize the writer
  writer = csv.writer(f)

  # write the header
  writer.writerow(["User","Total Likes", "Total Retweets", "Total Replies"])

  # write a new row for each fan and their data
  for fan in data:
    writer.writerow(fan)
  f.close()

  print("----- Data written to 'data.csv' file -----")

def getPaginatedReplies(lastTweetID):

  repliers = []

  print("----- GET REPLIES -----")

  # Get replies
  responsePages = tweepy.Cursor(api.search_tweets, q='to:{}'.format(username),
                          since_id=lastTweetID,count=100).pages(number_of_tweets*10)

  # for every reply, append their username
  for response in responsePages:

    print("fetching new response...")
    
    for reply in response:
      
      # print("Reply from:  ", reply.user.screen_name, " appended.")
      repliers.append(reply.user.screen_name)
  
  return repliers
  
def getPaginatedTweets(username, number_of_tweets):
  
  tweetIdList = []

  print("----- RETRIEVING TWEET IDs -----")

  # Captures all specified Tweets, paginates through multiple pages as needed
  for tweet in tweepy.Cursor(api.user_timeline,screen_name=username,include_rts='false',count=200).items(number_of_tweets):

    # appends the ID of each Tweet
    tweetIdList.append(tweet.id)
    
    print(tweet.id)

  # return the entire list of Tweet IDs
  return(tweetIdList)

def getPaginatedRts(tweetIdList):
  
  print("----- RETRIEVING PAGINATED RETWEETERS -----")

  retweetersList = []

  # for every Tweet
  for tweet in tweetIdList:

    print("Evaluating: ", tweet, " for retweets.")

    # get the retweeters and paginate as needed
    for response in tweepy.Paginator(client.get_retweeters,
                                     tweet):
      # if the response from Twitter's API is not empty
      if(response.meta['result_count']!=0):

        # append each retweeter to an array
        for retweeter in response.data:
          retweetersList.append(retweeter.username)

  # reutrn the list of retweeters
  return(retweetersList)

def getPaginatedLikes(tweetIdList):

  print("----- RETRIEVING PAGINATED LIKERS -----")
  
  userLikeList = []

  # for every Tweet captured
  for tweet in tweetIdList:
    
    print("Evaluating: ", tweet, " for favorites.")

    # get the likers of the Tweet, paginate as needed
    for response in tweepy.Paginator(client.get_liking_users,tweet):

      # if there are likers
      if(response.meta['result_count']!=0):

        # append them
        for like in response.data:
          userLikeList.append(like.username)

  # return the list of likers
  return(userLikeList)

main()
