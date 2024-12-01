import streamlit as st
import yt_dlp
import os
from time import sleep

# Page Configuration
st.set_page_config(page_title="NeoSound", page_icon="🎷", layout="centered")

# CSS Styling
# CSS Styling
st.markdown(
    """
    <style>
    body {
        background-color: #000000; /* Black background */
        color: #00FF00; /* Neon green */
        font-family: 'Bahnschrift Condensed', monospace; /* Hacker-style font */
    }

    /* Title Styling */
    .title {
        color: #00FF00; /* Neon green */
        text-align: center;
        font-size: 3em;
        animation: fade-brighten 2s infinite; /* Fading and Brightening Effect */
        margin-bottom: 20px;
    }

    @keyframes fade-brighten {
        0%, 100% {
            opacity: 1; /* Fully visible */
        }
        50% {
            opacity: 0.5; /* Faded */
        }
    }

    /* Input Fields with Green Borders */
    .stTextInput, .stSelectbox {
        border-radius: 8px;
        font-size: 1.2em;
        font-family: 'Bahnschrift Condensed', monospace; /* Consistent font */
        border: 2px solid #00FF00; /* Neon green border */
        background-color: #101010; /* Dark black */
        color: #00FF00; /* Neon green text */
        padding: 10px;
        margin-bottom: 15px;
    }

    .stTextInput:focus, .stSelectbox:focus {
        border-color: #33FF33; /* Lighter green on focus */
        box-shadow: 0 0 10px #33FF33; /* Neon glow on focus */
    }

    /* Buttons */
    .stButton>button {
        background-color: #00FF00;
        color: #000000;
        border-radius: 8px;
        font-size: 1.2em;
        padding: 10px 20px;
        text-shadow: 0 0 5px #00FF00;
        transition: background-color 0.3s, transform 0.2s;
    }

    .stButton>button:hover {
        background-color: #33FF33;
        transform: scale(1.05);
        cursor: pointer;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title
st.markdown("<div class='title'>🎷NeoSound🎷</div>", unsafe_allow_html=True)


# Initialize Session State
if 'video_list' not in st.session_state:
    st.session_state.video_list = []
if 'selected_video' not in st.session_state:
    st.session_state.selected_video = None

# User Input
song_name = st.text_input("Enter Song Name:", placeholder="E.g., Blinding Lights")
artist_name = st.text_input("Enter Artist Name:", placeholder="E.g., The Weeknd")
content_type = st.selectbox("Select Type:", ["Song", "Movie", "Lyrics"], key="content_type", help="Select the type of content.")

# Enhanced Helper Function for Searching Videos
def search_videos(query, content_type):
    # Append type-specific keywords to the query
    if content_type == "Song":
        query += " song"
    elif content_type == "Movie":
        query += " movie"
    elif content_type == "Lyrics":
        query += " lyrics"

    options = {'format': "best[height<=720]"}
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            search_results = ydl.extract_info(f"ytsearch5:{query}", download=False)  # Fetch top 5 results
            return [
                {
                    "title": video["title"],
                    "url": video["webpage_url"],
                    "thumbnail": video["thumbnail"],
                    "preview": video["url"],
                }
                for video in search_results["entries"]
            ]
    except Exception as e:
        st.error(f"Error while fetching videos: {e}")
        return []

# Create a sanitized filename
def sanitize_filename(filename):
    return "".join(c if c.isalnum() or c in (' ', '.', '_', '-') else "_" for c in filename)

# Create Folder for Storing Videos or Movies
def create_download_folder(folder_name="Songs_From_YT", content_type="Song"):
    if content_type == "Movie":
        folder_name = "Movies_From_YT"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

# Video Search Trigger
if st.button("Search"):
    if song_name and artist_name:
        query = f"{song_name} {artist_name}"
        videos = search_videos(query, content_type)
        if videos:
            st.session_state.video_list = videos
            st.success("Videos fetched successfully! Please select one below.")
        else:
            st.warning("No videos found for your query.")
    else:
        st.warning("Please provide both song and artist names.")

# Display Video Options
if st.session_state.video_list:
    video_titles = [video["title"] for video in st.session_state.video_list]
    selected_title = st.selectbox("Choose a Video:", video_titles)
    st.session_state.selected_video = next(
        video for video in st.session_state.video_list if video["title"] == selected_title
    )

    # Preview Selected Video
    if st.session_state.selected_video:
        video = st.session_state.selected_video
        st.image(video["thumbnail"], caption=video["title"], use_column_width=True)
        st.video(video["preview"], format="video/mp4", start_time=0)

# Download Video with Snowflake Progress Bar
if st.session_state.selected_video and st.button("Download"):
    video = st.session_state.selected_video
    download_folder = create_download_folder(content_type=content_type)  # Ensure folder exists
    raw_filename = f"{video['title'].replace('/', '-')}.mp4"
    filename = os.path.join(download_folder, sanitize_filename(raw_filename))  # Sanitize filename
    options = {"format": "best[height<=720]", "outtmpl": filename}

    try:
        with st.spinner("Preparing download..."):
            progress_placeholder = st.empty()
            for i in range(100):
                sleep(0.05)  # Simulate download progress
                progress_placeholder.progress(i + 1, text="⛄ Downloading... ⛄")

            # Perform the actual download
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([video["url"]])

            progress_placeholder.empty()  # Remove progress bar after download
            st.success(f"Download complete! File: {filename}")

            # Direct download button
            with open(filename, "rb") as file:
                st.download_button(
                    label="Download File",
                    data=file,
                    file_name=os.path.basename(filename),
                    mime="video/mp4",
                )
    except Exception as e:
        st.error(f"Error during download: {e}")

# Footer
st.markdown("<footer>DISCLAIMER-<br><br>This software is provided on an 'as is' and 'as available' basis for experimental purposes only. It may contain errors or inaccuracies, and its outputs are not guaranteed to be correct or reliable. Users should not rely solely on this software for critical decisions or applications. The developer disclaims all warranties, express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, and non-infringement. In no event shall the developer be liable for any claim, damages, or other liability arising from the use of this software. By using this software, you acknowledge and accept these terms.<br><br></footer>", unsafe_allow_html=True)
st.markdown("<footer>© NeoSound</footer>", unsafe_allow_html=True)


