
import requests
from youtube_transcript_api import YouTubeTranscriptApi
import pandas as pd
#youtube_api_key = "AIzaSyBHEAurZG_mPwMO8Qde6Av19v_SPZP6qYc"
youtube_api_key = "AIzaSyCbn2IWXVEn0vuFZdNzK5U8V1Cjv_JEp-s"


def get_badwords(filename):
    f = open(filename,"r")
    lines = f.readlines()
    return [line.strip() for line in lines]

def multiword_explicit(multiplewordlst):

    for i in range(len(multiplewordlst)):
        multiplewordlst[i] = multiplewordlst[i].split(" ")

    dct = {}
    for blurb in multiplewordlst:
        if blurb[0] in dct:
            dct[blurb[0]].append(blurb[1:])
        elif blurb[0] not in dct:
            dct[blurb[0]] = [blurb[1:]]

    return dct

def clean_badwords(lst1, lst2):

    biglst = list(set(lst1 + lst2))
    multiplewordlst = []
    for word in biglst:
        if " " in word:
            multiplewordlst.append(word)

    multiplewordlst = multiword_explicit(multiplewordlst)

    return biglst, multiplewordlst

def get_transcript(video_id):
    transcript_lst = YouTubeTranscriptApi.get_transcript(video_id)

    transcript = []
    for blurb in transcript_lst:
        words = blurb["text"]
        wordlst = words.split(" ")
        for word in wordlst:
            transcript.append(word)

    return transcript

def transcript_analyze(transcript,biglst, multiplewordlst ):
    badlst = []
    for i in range(len(transcript)):
        if transcript[i] in biglst:
            badlst.append(transcript[i])

        # first word of multiple word explicit phrase is there
        if transcript[i] in multiplewordlst:

            # for each path of explicit phrase from starting word
            for x in range(len(multiplewordlst[transcript[i]])):

                path = multiplewordlst[transcript[i]][x]

                # first word in phrase
                idx = i + 1

                # start assuming phrase is equal to path
                equals = True

                # for each word in path
                for y in range(len(path)):
                    # if word in phrase isnt equal to word in path
                    if transcript[idx] != path[y]:

                        # phrases arent equal, move on
                        equals = False
                        break
                    idx += 1

                if equals == True:
                    phrase = transcript[i]
                    for word in path:
                        phrase += " " + word
                    badlst.append(phrase)

    return badlst

def get_stats(badlst, transcript):
    proportion_explicit = len(badlst) / len(transcript)
    num_explicit = len(badlst)
    num_unique_explicit = len(set(badlst))

    #print("Proportion Explicit",proportion_explicit)
    #print("Number of Explicit Words/Phrases", num_explicit)
    #print("Number of Unique Explicit Words/Phrases", num_unique_explicit)
    return proportion_explicit, num_explicit, num_unique_explicit


def get_channelid_options(user):
    # listed under "id" in items
    # UCgoFStVyEsm8tBZP5NC-aBQ
    id = None
    url = f"https://www.googleapis.com/youtube/v3/channels?key={youtube_api_key}&forUsername={user}&part=id"

    dct = requests.get(url).json()

    if "items" in dct:
        id = dct["items"][0]["id"]

    url1 = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&maxResults=5&q={user}&key={youtube_api_key}"

    r = requests.get(url1).json()
    biglst = []
    for item in r["items"]:
        lst = []
        channel_id = item["id"]["channelId"]
        if len(item["snippet"]["title"][:25]) > 25:
            name = item["snippet"]["title"][:25] + "..."
        else:
            name = item["snippet"]["title"][:25]
        if len(item["snippet"]["description"][:50]) > 50:
            desc = item["snippet"]["description"][:50] + " ..."
        else:
            desc = item["snippet"]["description"][:50]

        lst.append(name)
        lst.append(desc)
        lst.append(channel_id)

        biglst.append(lst)

    df = pd.DataFrame(biglst, columns=['Name', "Description", 'ID'])

    return df

def get_channel_stats(channel_id):

    endpoint = "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=" + channel_id + "&maxResults=15&order=date&type=video&key=" + youtube_api_key
    request = requests.get(endpoint)
    videos = request.json()[u"items"]

    lst1 = get_badwords("en.txt")
    lst2 = get_badwords("badwords.txt")

    print("Loaded Negative Words")
    biglst, multiplewordlst = clean_badwords(lst1, lst2)
    print("Cleaned Negative Words")

    all_vidstats = []
    for i in range(len(videos)):
        videoId = videos[i]["id"]["videoId"]
        try:
            transcript = get_transcript(videoId)
            badlst = transcript_analyze(transcript, biglst, multiplewordlst)
            proportion_explicit, num_explicit, num_unique_explicit = get_stats(badlst, transcript)
            video_stats = [len(transcript), proportion_explicit, num_explicit, num_unique_explicit]
            all_vidstats.append(video_stats)
        except:
            continue
        print("loaded video #"+str(i+1))

    df = pd.DataFrame(all_vidstats, columns=['Transcript Length', 'Explicit Prop.', "Num. Explicit Words/Phrases", "Num. Unique Explicit Words/Phrases"])
    return int(df["Num. Explicit Words/Phrases"].mean()), float(df["Explicit Prop."].mean())

def main():

    # Use a breakpoint in the code line below to debug your script.
    transcript = get_transcript("xD9RpU7ZRuk")



    #print(get_channelid_options("Emergency Intercom")["ID"])
    # UCgCvOM4cMI2mW622ZRkZFnA

main()
