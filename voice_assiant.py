import tkinter as tk
from tkinter import scrolledtext
import threading
import datetime
import time as time_module
import webbrowser
import smtplib
from email.message import EmailMessage
import speech_recognition as sr
import pyttsx3
from openai import OpenAI
import requests


api_key1 = "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"
weather_api_key = "736f83564bc11c24b17faf2b8f0845bd"
email_address = "valagondahanumesh3@gmail.com"
email_password = "hanu@143"


engine = pyttsx3.init()
listener = sr.Recognizer()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def log(message):
    output_box.insert(tk.END, message + "\n")
    output_box.see(tk.END)

def get_command():
    with sr.Microphone() as source:
        log("Listening...")
        try:
            voice = listener.listen(source, timeout=5)
            command = listener.recognize_google(voice)
            log(f"You said: {command}")
            return command.lower()
        except:
            log("Sorry, I didn't catch that.")
            return ""

# EMAIL FUNCTION
def send_email(to, subject, body):
    email = EmailMessage()
    email['From'] = email_address
    email['To'] = to
    email['Subject'] = subject
    email.set_content(body)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(email_address, email_password)
            smtp.send_message(email)
            speak("Email sent successfully.")
            log("Assistant: Email sent successfully.")
    except Exception as e:
        log(f"Error sending email: {e}")
        speak("Failed to send email.")

# REMINDER FUNCTION
def set_reminder(when, message):
    def reminder_thread():
        delay = (when - datetime.datetime.now()).total_seconds()
        if delay > 0:
            time_module.sleep(delay)
        speak(f"Reminder: {message}")
        log(f"Reminder: {message}")
    threading.Thread(target=reminder_thread).start()

# WEATHER FUNCTION
def get_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}"
        res = requests.get(url).json()
        if res["cod"] != "404":
            weather = res["weather"][0]["description"]
            temp = res["main"]["temp"]
            speak(f"The weather in {city} is {weather}, {temp}°C.")
            log(f"Weather: {weather}, {temp}°C in {city}")
        else:
            speak("City not found.")
    except:
        speak("Unable to get weather info.")
        log("Error fetching weather.")


def ask_gpt(prompt):
    try:
        client=OpenAI(api_key=f"{api_key1}")
        response = client.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print("GPT Error:", e)
        return "Sorry, I couldn't get a response."


def run_assistant():
    speak("Voice Assistant started.")
    while True:
        command = get_command()

        if 'hello' in command:
            speak("Hello there!")
            log("Assistant: Hello there!")

        elif 'time' in command:
            now = datetime.datetime.now().strftime('%I:%M %p')
            speak(f"The time is {now}")
            log(f"Time: {now}")

        elif 'date' in command:
            today = datetime.datetime.now().strftime('%A, %B %d, %Y')
            speak(f"Today is {today}")
            log(f"Date: {today}")

        elif 'search' in command:
            speak("What should I search for?")
            query = get_command()
            if query:
                url = f"https://www.google.com/search?q={query}"
                webbrowser.open(url)
                speak(f"Here are the results for {query}")
                log(f"Searched: {query}")

        elif 'send email' in command:
            speak("Who is the recipient?")
            recipient_name = get_command()
            contacts = {"john": "john@example.com", "alex": "alex@example.com"}
            to = contacts.get(recipient_name)
            if to:
                speak("What is the subject?")
                subject = get_command()
                speak("What should I say?")
                body = get_command()
                send_email(to, subject, body)
            else:
                speak("Recipient not found.")
                log("Recipient not found.")

        elif 'remind me' in command:
            speak("What is the reminder about?")
            message = get_command()
            speak("In how many seconds?")
            try:
                seconds = int(get_command())
                remind_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
                set_reminder(remind_time, message)
                speak(f"Reminder set for {seconds} seconds from now.")
            except:
                speak("Failed to set reminder.")
                log("Reminder error.")

        elif 'weather' in command:
            speak("Which city's weather?")
            city = get_command()
            get_weather(city)

        elif 'exit' in command or 'stop' in command:
            speak("Goodbye!")
            log("Assistant: Goodbye!")
            break

        else:
            reply = ask_gpt(command)
            speak(reply)
            log(f"GPT: {reply}")


def start_assistant_thread():
    assistant_thread = threading.Thread(target=run_assistant)
    assistant_thread.start()


window = tk.Tk()
window.title("Voice Assistant")
window.geometry("550x500")
window.config(bg="#1e1e1e")

title_label = tk.Label(window, text="Voice Assistant", font=("Helvetica", 20, "bold"), bg="#1e1e1e", fg="#00FFAB")
title_label.pack(pady=15)

output_box = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=65, height=20, font=("Courier", 10), bg="#333", fg="#fff")
output_box.pack(padx=10, pady=10)

start_button = tk.Button(window, text="🎤 Start Assistant", font=("Helvetica", 14), bg="#00FFAB", fg="black", command=start_assistant_thread)
start_button.pack(pady=15)

window.mainloop()
