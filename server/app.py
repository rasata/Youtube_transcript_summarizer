from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from flask import Flask
import datetime
from flask import request # used to parse payload
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from flask import render_template
from flask import abort
from flask_cors import CORS
import os

# define a variable to hold you app
app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/time', methods=['GET'])
def get_time():
    return str(datetime.datetime.now())

@app.route('/api/summarize', methods=['GET'])
def GetUrl():
    """
    Called as /api/summarize?youtube_url='url'
    """
    # if user sends payload to variable name, get it. Else empty string
    video_url = request.args.get('youtube_url', '') 
    # if(len(video_url) == 0) or (not '=' in video_url):
    #   print("f")
    #   abort(404)
    
    response = GetTranscript(video_url)
    return response

def SumySummarize(text):

    from sumy.parsers.html import HtmlParser
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.summarizers.lsa import LsaSummarizer as Summarizer
    from sumy.nlp.stemmers import Stemmer
    from sumy.utils import get_stop_words

    LANGUAGE = "english"
    SENTENCES_COUNT = 10
    import nltk;  
    nltk.download('punkt')

    # url = "https://en.wikipedia.org/wiki/Automatic_summarization"
    # parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
    # or for plain text files
    # parser = PlaintextParser.from_file("document.txt", Tokenizer(LANGUAGE))
    parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    s = ""
    for sentence in summarizer(parser.document, SENTENCES_COUNT):
      s += (str)(sentence)
      s += "\n"
    print('The summary is: ', s)
    return s

def GetTextFromAudio():
    import speech_recognition as sr
    from pydub import AudioSegment
    
    f = ""

    # convert mp3 file to wav           
    for file in os.listdir(os.getcwd()):
      if file.endswith(".mp3"):
          f = file      
                                          
    if(len(f) == 0):
      return f
    print('The file is: ', f)
    sound = AudioSegment.from_mp3(f)

    os.rename(os.path.join(os.getcwd(), f), os.path.join(os.getcwd(), "recordings", f))
    
    sound.export("transcript.wav", format="wav")
    
    # use the audio file as the audio source                                        
    AUDIO_FILE = "transcript.wav"

    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
      audio = r.record(source)  # read the entire audio file    
      print(audio)              
      return (r.recognize_google(audio))

def GetAudio(video_url):
    from youtube_dl import YoutubeDL
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3'
        }],
    }
    with YoutubeDL(ydl_opts) as ydl:
       ydl.download([video_url])
      

# video id are the last characters in the link of youtube video
def GetTranscript(video_url):
    text = ""
    try:
      video_id = video_url.split('=')[1]
      transcript = YouTubeTranscriptApi.get_transcript(video_id)
      formatter = TextFormatter()
      text = formatter.format_transcript(transcript)
      return SumySummarize(text)
    except:
      GetAudio(video_url)
      text = GetTextFromAudio()
      print('The text is: ', text)
      return SumySummarize(text)

# server the app when this file is run
if __name__ == '__main__': 
  app.run()