import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

# NOW you can do your other imports
import streamlit as st
from moviepy.editor import ...
import streamlit as st
import os
import tempfile
from io import BytesIO
from deep_translator import GoogleTranslator
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings

# ----------------------------
# 1. SYSTEM CONFIGURATION
# ----------------------------
# This must happen before any MoviePy objects are created.
# It tells the server where to find the "ImageMagick" tool to write text.
if os.name != 'nt':  # Linux / Streamlit Cloud logic
    change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})
else:
    # If you are on Windows, uncomment and point to your magick.exe if it fails
    # change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})
    pass

# ----------------------------
# 2. HELPER FUNCTIONS
# ----------------------------
def translate_text(text, target_code):
    if not text.strip():
        return ""
    return GoogleTranslator(source="auto", target=target_code).translate(text)

def generate_video(script_text, target_code, character_img_path):
    """
    Converts text to speech, merges it with a character image and subtitles.
    """
    # Create Audio (TTS)
    tts = gTTS(text=script_text, lang=target_code)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        tts.save(temp_audio.name)
        audio_path = temp_audio.name

    # Setup Audio Clip
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration

    # Setup Character Image Clip
    char_clip = ImageClip(character_img_path).set_duration(duration)
    char_clip = char_clip.resize(height=720) 

    # Add Subtitles
    try:
        txt_clip = TextClip(
            script_text, 
            fontsize=40, 
            color='white', 
            bg_color='black', 
            method='caption', 
            size=(char_clip.w, 100)
        )
        txt_clip = txt_clip.set_pos(('center', 'bottom')).set_duration(duration)
        video = CompositeVideoClip([char_clip, txt_clip])
    except Exception as e:
        st.error(f"Subtitle Error: {e}. Generating video without text.")
        video = char_clip

    # Final Assembly
    video = video.set_audio(audio_clip)
    output_path = tempfile.mktemp(suffix=".mp4")
    video.write_videofile(output_path, fps=24, codec="libx264")
    
    return output_path

# ----------------------------
# 3. MAIN APP
# ----------------------------
def main():
    st.set_page_config(page_title="PragyanAI Studio", layout="wide")
    st.title("🌐 PragyanAI Multi-Modal Studio")

    # Get supported languages
    langs_dict = GoogleTranslator().get_supported_languages(as_dict=True)
    
    target_lang = st.sidebar.selectbox("Target Language", list(langs_dict.keys()))
    target_code = langs_dict[target_lang]

    tabs = st.tabs(["📄 DOCX", "📸 Image/PDF", "🎤 Audio", "📝 Text", "🎬 Script-to-Video"])

    # ... (Tabs 0-3 would contain your existing file translation code) ...

    # ---------------- SCRIPT TO VIDEO TAB
    with tabs[4]:
        st.subheader("Generate AI Character Video")
        
        col1, col2 = st.columns(2)
        
        with col1:
            raw_script = st.text_area("Enter your script here...", height=200, placeholder="Hello, welcome to PragyanAI...")
            char_choice = st.selectbox(
                "Choose Character Avatar", 
                ["Male Professional", "Female Teacher", "Robot Helper"]
            )
            
            # Map choice to local image paths (Make sure these exist in your 'avatars' folder!)
            avatar_map = {
                "Male Professional": "avatars/male.png",
                "Female Teacher": "avatars/female.png",
                "Robot Helper": "avatars/robot.png"
            }

        with col2:
            st.info(f"The video will be generated in: **{target_lang}**")
            if st.button("Generate Video"):
                if not raw_script:
                    st.warning("Please enter a script first.")
                else:
                    with st.spinner("Processing... This may take a minute."):
                        # 1. Translate the script
                        translated_script = translate_text(raw_script, target_code)
                        
                        # 2. Check if avatar exists
                        path = avatar_map[char_choice]
                        if not os.path.exists(path):
                            st.error(f"File '{path}' not found. Please upload images to the 'avatars' folder.")
                        else:
                            # 3. Render video
                            video_file = generate_video(translated_script, target_code, path)
                            
                            # 4. Display & Download
                            st.video(video_file)
                            with open(video_file, "rb") as f:
                                st.download_button("Download Video", f, file_name="ai_video.mp4")

if __name__ == "__main__":
    main()
