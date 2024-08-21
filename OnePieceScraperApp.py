# import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import webbrowser

# Define the base URL for episode links
base_url = "https://tokyoinsider.com/anime/O/One_piece_(TV)/episode/"

def fetch_episode(episode_id):
    url = f"{base_url}{episode_id}"
    response = requests.get(url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    inner_page_div = soup.find('div', id='inner_page')
    if not inner_page_div:
        return None

    video_divs = inner_page_div.find_all('div', class_=['c_h2b', 'c_h2'])
    links_dict = {}
    count = 0
    for video_div in video_divs:
        a_tags = video_div.find_all('a', href=True)
        for i, a_tag in enumerate(a_tags):
            if i == 1:
                video_link = a_tag['href']
                links_dict[count] = {
                    'name': a_tag.text,
                    'link': video_link,
                    'size': video_div.find('div', class_='finfo').find('b').text
                }
                count += 1
    df = pd.DataFrame.from_dict(links_dict, orient='index')
    df['size_type'] = df['size'].apply(lambda x: 'MB' if 'MB' in x else 'GB')
    df['size'] = df['size'].str.replace('MB', '').str.replace('GB', '').str.strip()
    df['size'] = df['size'].astype(float)
    df.loc[df['size_type'] == 'GB', 'size'] = df.loc[df['size_type'] == 'GB', 'size'] * 1024
    df = df.sort_values('size', ascending=False)
    df.reset_index(drop=True, inplace=True)
    df['id'] = df.index
    df = df.set_index('id')
    result_dict = df.to_dict(orient='index')
    return result_dict

x = fetch_episode(512)


# Create UI with Streamlit
def main():
    st.title("One Piece Scraper")
    # Initialize session state variables
    if 'episode_id' not in st.session_state:
        st.session_state.episode_id = None
    if 'links_dict' not in st.session_state:
        st.session_state.links_dict = None
    if 'selected_link' not in st.session_state:
        st.session_state.selected_link = None

    episode_id = st.text_input("Enter episode number:")

    if st.button("Search"):
        if not episode_id.isdigit():
            st.error("Please enter a valid episode number.")
            return

        st.session_state.episode_id = int(episode_id)
        with st.spinner('Fetching episode link...'):
            st.session_state.links_dict = fetch_episode(st.session_state.episode_id)

    if st.session_state.links_dict:
        link_names = [f"{key}. {st.session_state.links_dict[key]['name']}........{st.session_state.links_dict[key]['size']} MB" for key in st.session_state.links_dict]
        st.session_state.selected_link = st.selectbox("Select a link:", link_names)

        if st.session_state.selected_link:
            video_link = st.session_state.links_dict[int(st.session_state.selected_link.split(".")[0])]["link"]
            st.video(video_link)
            st.write("Open in your preferred media player:")

            st.markdown(f'<a href="iina://open?url={video_link}" target="_blank">Open in IINA</a>', unsafe_allow_html=True)
            st.markdown(f'<a href="potplayer://{video_link}" target="_blank">Open in PotPlayer</a>', unsafe_allow_html=True)
            st.markdown(f'<a href="vlc://{video_link}" target="_blank">Open in VLC</a>', unsafe_allow_html=True)
    else:
        st.write("No episode found.")

if __name__ == "__main__":
    main()
