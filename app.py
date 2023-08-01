import os
import json
import requests
import streamlit as st
from utils import write_audio_file, generate_speech_11lab
from recommendation import *

ELEVEN_LAB_URL = "https://api.elevenlabs.io/v1/text-to-speech/"
LEVEL_RULE = 2

# importing required modules
def read_text_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content

def get_metadata(input):
    #  metadata:{genre, title, author, description/summary} 
    #  user_data:{nationality, gender, age, voice favor in history, accent}
    st.title("Book's metadata")
    option = st.selectbox(
            'Select the example:',
            ('<select>', 'book1', 'book2', 'book3'))
    
    if option == 'book1':
        input['genre'] = 'Adventure'
        input['title'] = 'The Adventures of Tom Sawyer'
        input['author']= 'Mark Twain'
        input['description'] = 'A classic tale of a young boy named Tom Sawyer and his adventures along the Mississippi River.'

    elif option == 'book2':
        input['genre'] = 'Adventure'
        input['title'] = 'The Adventures of Tom Sawyer'
        input['author'] = 'Mark Twain'
        input['description'] = 'A classic tale of a young boy named Tom Sawyer and his adventures along the Mississippi River.'
        
    elif option == 'book3':
        input['genre'] = 'Adventure'
        input['title'] = 'The Adventures of Tom Sawyer'
        input['author'] = 'Mark Twain'
        input['description'] = 'A classic tale of a young boy named Tom Sawyer and his adventures along the Mississippi River.'
    return input

def get_user(input):
    # user_data:{nationality, gender, age, voice favor in history, accent}

    st.title("User's metadata")
    option = st.selectbox(
            'Select the example:',
            ('<select>', 'user1', 'user2', 'user3'))
    if option == 'user1':
        input['nationality'] = 'Bristish'
        input['gender'] = 'male'
        input['age'] = '25'
        input['voice favor in history'] = 'male'
        input['accent'] = 'Bristish'
        
    elif option == 'user2':
        input['nationality'] = 'American'
        input['gender'] = 'female'
        input['age'] = '50'
        input['voice favor in history'] =  'female'
        input['accent']= 'Bristish'

    elif option == 'user3':
        input['nationality'] = 'Indian'
        input['gender'] = 'female'
        input['age'] = '15'
        input['voice favor in history'] = 'female'
        input['accent'] = 'American'
    return input

    
def select_settings_by_rulebase(level_rule, data):
    """
        This is a baseline version for voice-settings recommendation to generate audiobooks
    """
    # Level1: Rulebase
    if level_rule == 1:
        suggetor = RuleBase()
        rem_voice = suggetor.pairse_rule(data)
    # Level2: Semantic Similarity
    elif level_rule == 2:
        rem_voice = {}
        suggetor = SemanticCompare()
        voice_ids = suggetor.get_all_voices_embedding()

        book_info = [data[k] for k in data.keys()]
        ids, list_voices = suggetor.compare(suggetor.get_embedding(' '.join(book_info)), voice_ids)
        num_voice_settings = len(list_voices)
        index_voice_settings = random.randint(0, num_voice_settings - 1) 
        
        for id in voice_ids.keys(): 
            if id == list_voices[index_voice_settings]:
                rem_voice["voice_id"] = list_voices[index_voice_settings]
                rem_voice["metadata"] = voice_ids[id]["metadata"]
                break
    # Level3: Recommendation system
    elif level_rule == 3:
        st.write(
            "under construction"
        )

    return rem_voice

def main():
    try:
        st.title("Voice Settings Recommendation for generating audio")
        st.markdown('we recommend the voice settings which is suitable for audio book based on its genre, title, etc and listerner favorite voice, gender, accent, etc')
        st.header(" Book Information")
        title = st.text_input('Book title', 'Life of Pi')
        genere = st.text_input('Book genre', 'Adventure')
        
        st.header(" User favorite Information")
        favor_gender  = st.selectbox('Favorite gender', ('male', 'female'))
        favor_age = st.selectbox('Favorite age', ('young', 'middle age', 'old', 'child'))
        favor_accent = st.text_input('Favorite accent', 'Bristish')

        text_book = st.text_area('Text to speak', "")
        
        if text_book == "":
            st.warning("Please put text sample in the text area!")
        
        input = {
                "title": title,
                "genere": genere,
                "favor_gender": favor_gender,
                "favor_age": favor_age,
                "favor_accent": favor_accent,
            }
            
        button_generate = st.button("generate voice settings")
        if button_generate and input != None:
            rem_voice = select_settings_by_rulebase(LEVEL_RULE, input)
            st.title('recommend voice setting: ')
            st.write(rem_voice)
            
            voice_id = None
            if rem_voice != None:
                voice_id = rem_voice['voice_id']
            
            with st.expander("the sample of the book"):
                st.write(text_book)
            voice_settings = {
                "text": text_book,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5,
                    "style": 0.5,
                    "use_speaker_boost": True
                }
            }
            
            save_path = 'test_audio.wav'
            with st.spinner("Waiting for the audio book"):
                ret = generate_speech_11lab(voice_settings, voice_id, save_path)
                if 'successful' in ret:
                    st.write("The audio generating after suggestion")
                    st.audio(save_path)
    except Exception as e:
        st.error(e)
            
if __name__ == '__main__':
    main()
