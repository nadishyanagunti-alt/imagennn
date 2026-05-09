import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip, TextClip, CompositeVideoClip
import tempfile
import os
from io import BytesIO

# ... (Keep your existing imports and helper functions) ...

def generate_video(script_text, target_code, character_img_path):
    """
    Converts text to speech, then merges it with a character image 
    and subtitles to create a video.
    """
    # 1. Create Audio from translated script
    tts = gTTS(text=script_text, lang=target_code)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        tts.save(temp_audio.name)
        audio_path = temp_audio.name

    # 2. Setup Audio Clip
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration

    # 3. Setup Character Image Clip
    # If no image provided, we'll use a placeholder color or default avatar
    char_clip = ImageClip(character_img_path).set_duration(duration)
    char_clip = char_clip.resize(height=720) # Standard HD height

    # 4. Add Subtitles (TextClip)
    # Note: TextClip requires ImageMagick installed on the system. 
    # If not available, we skip this part.
    try:
        txt_clip = TextClip(script_text, fontsize=40, color='white', 
                            bg_color='black', method='caption', size=(char_clip.w, 100))
        txt_clip = txt_clip.set_pos(('center', 'bottom')).set_duration(duration)
        video = CompositeVideoClip([char_clip, txt_clip])
    except:
        video = char_clip

    # 5. Combine and Write
    video = video.set_audio(audio_clip)
    output_path = tempfile.mktemp(suffix=".mp4")
    video.write_videofile(output_path, fps=24, codec="libx264")
    
    return output_path

# Update your main() function tabs
def main():
    st.title("🌐 PragyanAI Multi-Modal Studio")
    
    # ... (Keep your existing sidebar and language logic) ...

    tabs = st.tabs([
        "📄 DOCX", "📸 Image/PDF", "🎤 Audio", "📝 Text", "🎬 Script-to-Video"
    ])

    # ... (Keep existing tabs 0-3) ...

    # ---------------- SCRIPT TO VIDEO
    with tabs[4]:
        st.subheader("Generate AI Character Video from Script")
        
        col1, col2 = st.columns(2)
        
        with col1:
            raw_script = st.text_area("Enter your script here...", height=200)
            char_choice = st.selectbox("Choose Character Avatar", 
                                     ["Male Professional", "Female Teacher", "Robot Helper"])
            
            # Map choice to local image paths
            avatar_map = {
                "Male Professional": "avatars/male.png",
                "Female Teacher": "avatars/female.png",
                "Robot Helper": "avatars/robot.png"
            }

        with col2:
            st.info(f"Target Language: **{target_lang}**")
            if st.button("Generate Video"):
                if not raw_script:
                    st.warning("Please enter a script.")
                else:
                    with st.spinner("Translating and Rendering Video..."):
                        # Translate
                        translated_script = translate_text(raw_script, target_code)
                        
                        # Use a default path if file doesn't exist
                        path = avatar_map[char_choice]
                        if not os.path.exists(path):
                            # Fallback: Just use a solid color if image missing
                            st.error("Avatar image not found. Ensure 'avatars/' folder exists.")
                        else:
                            video_file = generate_video(translated_script, target_code, path)
                            
                            st.video(video_file)
                            
                            with open(video_file, "rb") as f:
                                st.download_button("Download Video", f, file_name="ai_script_video.mp4")

if __name__ == "__main__":
    main()
