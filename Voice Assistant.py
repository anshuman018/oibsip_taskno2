import openai  # Import the OpenAI module
import pyttsx3
import speech_recognition as sr
import smtplib
import ssl
from email.message import EmailMessage

# Set your OpenAI API key
openai.api_key = 'YOUR_OPENAI_API_KEY'  # Replace with your actual OpenAI API key

# Set your email credentials
email_sender = 'YOUR_EMAIL@gmail.com'  # Replace with your email address
email_password = 'YOUR_EMAIL_PASSWORD'  # Replace with your email password
smtp_server = 'smtp.gmail.com'  # Change based on your email provider
smtp_port = 465  # Change based on your email provider

# Initialize the text-to-speech engine
def init_tts_engine():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    # Change the index to select a different voice (if available)
    engine.setProperty('voice', voices[0].id)
    new_rate = 180  # Adjust the rate as needed
    engine.setProperty('rate', new_rate)
    return engine

# Initialize the speech recognizer
def init_speech_recognizer():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
    return recognizer

# Function to send an email
def send_email(subject, body, recipient):
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(email_sender, email_password)
            message = EmailMessage()
            message.set_content(body)
            message['Subject'] = subject
            message['From'] = email_sender
            message['To'] = recipient
            server.send_message(message)
            print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {str(e)}")

if __name__ == '__main__':
    print('Chatbot')
    engine = init_tts_engine()
    recognizer = init_speech_recognizer()

    print("Hello, I am Chatbot. How can I assist you today?")
    engine.say("Hello, I am Chatbot. How can I assist you today?")
    engine.runAndWait()

    conversation_history = []  # Initialize conversation history

    voice_command_mode = False  # Initialize voice command mode

    while True:
        if not voice_command_mode:
            user_input_text = input("You (Text): ").strip().lower()

            if user_input_text == 'exit' or user_input_text == 'quit':
                # Send the conversation history via email
                subject = 'Chatbot Conversation Summary'
                body = '\n'.join(conversation_history)
                send_email(subject, body, email_sender)
                engine.say("Goodbye!")
                print("Chatbot: Goodbye!")
                engine.runAndWait()
                break

            # Check for other commands or handle user inputs
            if 'voice mode' in user_input_text:
                voice_command_mode = True
                print("Chatbot is now listening for voice commands...")
                engine.say("Chatbot is now listening for voice commands.")
                engine.runAndWait()
            elif 'send an email' in user_input_text:
                # Extract recipient, subject, and message from the text input
                recipient = "recipient@example.com"  # Replace with the recipient's email address
                subject = "Subject of the email"
                message = "This is the content of the email."

                # Send the email using the extracted information
                send_email(subject, message, recipient)
                engine.say("Email sent successfully!")
                print("Chatbot: Email sent successfully!")
                engine.runAndWait()
            else:
                # Use OpenAI to respond to the user's text command
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=user_input_text,
                    max_tokens=50
                )

                chatbot_response = response.choices[0].text.strip()
                print(f"Chatbot: {chatbot_response}")

                # Speak the chatbot response
                engine.say(chatbot_response)
                engine.runAndWait()

            # Store the conversation history
            conversation_history.append(f"You (Text): {user_input_text}")

        else:
            print("You can start speaking your command:")

            with sr.Microphone() as source:
                print("Listening...")
                engine.say("Listening...")
                engine.runAndWait()
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source)

            try:
                user_input_voice = recognizer.recognize_google(audio, language="en-in")
                print(f"You (Voice): {user_input_voice}")

                if 'email' in user_input_voice:
                    # Extract recipient, subject, and message from the voice command
                    recipient = "recipient@example.com"  # Replace with the recipient's email address
                    subject = "Subject of the email"
                    message = "This is the content of the email."

                    # Send the email using the extracted information
                    send_email(subject, message, recipient)
                    engine.say("Email sent successfully!")
                    print("Chatbot: Email sent successfully!")
                    engine.runAndWait()
                else:
                    # Use OpenAI to respond to the user's voice command
                    response = openai.Completion.create(
                        engine="text-davinci-003",
                        prompt=user_input_voice,
                        max_tokens=50
                    )

                    chatbot_response = response.choices[0].text.strip()
                    print(f"Chatbot: {chatbot_response}")

                    # Speak the chatbot response
                    engine.say(chatbot_response)
                    engine.runAndWait()

            except sr.UnknownValueError:
                print("You (Voice): (Silence)")
            except sr.RequestError:
                print("You (Voice): Sorry, there was an issue connecting to Google's servers.")
                engine.say("Sorry, there was an issue connecting to Google's servers.")
                engine.runAndWait()

            voice_command_mode = False  # Exit voice command mode after processing the command
