import speech_recognition as sr
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import webbrowser
import pyttsx3
import os
import datetime
import requests
import json

nltk.download('punkt')
nltk.download('stopwords')

def process_text(text):
    # Tokenizing the text
    tokens = word_tokenize(text)
    print(f"Tokens: {tokens}")

    #Removing stop words
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token not in stop_words]
    print(f"Tokens after stop word removal: {filtered_tokens}")

    # Stemming the tokens
    stemmer = PorterStemmer()
    stems = [stemmer.stem(token) for token in tokens]
    print(f"Stemmed tokens: {stems}")

    # Joining the stemmed tokens back into string
    stemmed_text = ''.join(stems)
    return stemmed_text

def say(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    rate = engine.getProperty('rate')
    print(rate)
    engine.setProperty('rate', 150)

    sentences = text.split('. ')
    for i in range(len(sentences)):
        sentences[i] += '.'
    text_with_pauses = ', '.join(sentences)
    engine.say(text_with_pauses)
    engine.runAndWait()


def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 1
        audio = r.listen(source)
        try:
            print("Recognizing")
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")

            #processing the user's input
            processed_query = process_text(query)

            return query, processed_query
        except Exception as e:
            print(f"Error: {str(e)}")
            say("“I’m sorry, I’m having trouble understanding your request. Could you please repeat?")
            return "", ""


def get_weather(city_name, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}appid={api_key}&q={city_name}"
    try:
        response = requests.get(complete_url)
        response.raise_for_status()  # it raises a http error if the response status is 404, 503
    except requests.exceptions.RequestException as e:
        print(f"Error:{str(e)}")
        return "Weather data not found"
    weather_data = response.json()

    if weather_data["cod"] != "404":
        main_data = weather_data["main"]
        temperature = main_data["temp"] - 273.15  # Converting temperature from kelvin to celsius
        pressure = main_data["pressure"]
        humidity = main_data["humidity"]
        wind_speed = weather_data["wind"]["speed"] if "wind" in weather_data and "speed" in weather_data["wind"] else "Wind speed data not available"
        weather_desc = weather_data["weather"][0]["description"]
        return (temperature, pressure, humidity, wind_speed, weather_desc)
    else:
        return "Weather data not found."

def get_news(api_key, query):
    url = f"https://newsapi.org/v2/everything?q={query}&apikey={api_key}"
    response = requests.get(url)
    news_data = response.json()
    if news_data["status"] != "ok":
        return "News data not found"
    else:
        articles = news_data["articles"]
        news = []
        for article in articles:
            news.append({
                "title": article["title"],
                "description": article["description"],
                "content": article["content"] if "content" in article else "Content not available",
                "url": article["url"],
            })
        return news

if __name__ == '__main__':
    print("PyCharm")
    greetings = ['hey', 'hi', 'hello', 'good morning', 'good evening', 'sam', 'hey sam']
    farewells = ['thank you', 'thanks', 'ok thank you', 'okay thanks', 'that\'s all', 'bye']
    while True:
        print("Listening...")
        query, processed_query = takecommand()
        query = query.lower()
        processed_query = processed_query.lower()
        if query == "":
            continue
        if any(greeting in query for greeting in greetings):
            say("Hello, I'm here to assist you. What can I do for you today?")
        elif any(farewell in query for farewell in farewells):
            say("Great! if you need anything else in the future, feel free to reach out. Have a wonderful day!")
            break
        elif "weather" in query:
            api_key = "91029bee01cd2f649f78078554268fa8"
            city_name = query.split("in ")[1]  # Extracting the city name from the user's query
            weather_info = get_weather(city_name, api_key)
            if isinstance(weather_info, tuple):
                say(f"Right now in {city_name}, it's "
                    f"{weather_info[0]:.2f} degrees Celsius, with a wind speed of "
                    f"{weather_info[3]} km/h. The humidity is at {weather_info[2]}%, It's {weather_info[4]} outside."
                    )
            else:
                say("I'm sorry, I couldn't fetch the weather data right now.")
        elif "news" in query:
            api_key = "78741a5134de4b28887d8531ef312fb5"
            if "about" in query:
                topic = query.split("about ")[1]
            else:
                topic = 'latest'
            news = get_news(api_key, topic)
            for article in news:
                say(f"Sure. Here's an interesting news story titled. {article['title']}. "
                    f"Here's what it's about. {article['content']}. "
                    f"If you're interested in exploring this further, you can read the complete article at the given URL."
                )
                break
        else:
            processed_query = process_text(query)
            sites = [["youtube", "https://youtube.com"], ["google", "https://google.com"], ["wikipedia", "https://wikipedia.com"]]
            for site in sites:

                if f"open {site[0]}".lower() in query.lower():
                    say(f"Sure, I'm navigating to {site[0]} for you.")
                    webbrowser.open(site[1])
                    break
            if "time" in query:
                current_time = datetime.datetime.now().strftime("%I:%M %p")
                say(f"Currently, it's {current_time}.")
