import streamlit as st
from streamlit_autorefresh import st_autorefresh
import requests
from datetime import datetime
from database import get_recent_detections

st.set_page_config(
    page_title="🐦 Bird Detections (Last 24 Hours)",
    layout="wide",
    initial_sidebar_state="auto",
)

count = st_autorefresh(interval=2000)

@st.cache_data(ttl=86400)  # Cache for 24 hours
def get_wikipedia_data(common_name, scientific_name):
    """Fetches bird data from Wikipedia and retrieves its Wikidata item."""
    def fetch_summary(search_term):
        """Fetch summary, image, and Wikidata item from Wikipedia."""
        search_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{search_term.replace(' ', '_')}"
        response = requests.get(search_url)
        if response.status_code == 200:
            return response.json()
        return None

    # Try searching with common name first, then scientific name
    data = fetch_summary(common_name) or fetch_summary(scientific_name)
    
    if data:
        # Extract only the first two sentences of the summary
        full_summary = data.get("extract", "No description available.")
        sentences = full_summary.split(". ")
        short_summary = ". ".join(sentences[:1]) + "." if len(sentences) > 1 else full_summary

        return {
            "summary": short_summary,
            "image_url": data["thumbnail"]["source"] if "thumbnail" in data else None,
            "page_url": data.get("content_urls", {}).get("desktop", {}).get("page", None),
            "wikidata_id": data.get("wikibase_item")  # Wikidata ID
        }
    return None

@st.cache_data(ttl=86400)  # Cache for 24 hours
def get_wikidata_info(wikidata_id):
    """Fetches additional bird information from Wikidata."""
    if not wikidata_id:
        return None

    wikidata_url = f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id}.json"
    response = requests.get(wikidata_url)

    if response.status_code == 200:
        data = response.json()
        entity_data = data.get("entities", {}).get(wikidata_id, {}).get("claims", {})

        # Extract taxon range map image
        taxon_range_map = None
        if "P181" in entity_data:  # Property P181 = taxon range map
            taxon_range_map = entity_data["P181"][0]["mainsnak"]["datavalue"]["value"]
            taxon_range_map = f"https://commons.wikimedia.org/wiki/Special:FilePath/{taxon_range_map.replace(' ', '_')}"

        # Extract IUCN conservation status
        iucn_status = None
        if "P141" in entity_data:  # Property P141 = IUCN conservation status
            status_id = entity_data["P141"][0]["mainsnak"]["datavalue"]["value"]["id"]
            iucn_status = f"https://www.wikidata.org/wiki/{status_id}"  # Link to the conservation status

        return {"taxon_range_map": taxon_range_map, "iucn_status": iucn_status}

    return None

detections = get_recent_detections(limit=25, min_confidence=0.5)

if not detections:
    st.write("No bird detections in the last 24 hours.")
else:
    for common_name, scientific_name, confidence, label, file_path, start_time, end_time, timestamp in detections:
        detected_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        time_since_detection = datetime.utcnow() - detected_time
        hours_ago = int(time_since_detection.total_seconds() // 3600)
        minutes_ago = int((time_since_detection.total_seconds() % 3600) // 60)

        bird_data = get_wikipedia_data(common_name, scientific_name)
        wikidata_info = get_wikidata_info(bird_data["wikidata_id"]) if bird_data and bird_data.get("wikidata_id") else None

        col1, col2, col3 = st.columns([.3, .5, .2], vertical_alignment='center', gap='medium')  # Image & Audio | Info | Range Map

        with col1:
            if bird_data and bird_data["image_url"]:
                st.markdown(
                    f'<img src="{bird_data["image_url"]}" style="width: auto; height: auto; max-width: 100%; max-height: 250px; object-fit: fit; border-radius: 10px;">',
                    unsafe_allow_html=True,
                )
                # st.image(bird_data["image_url"], caption=common_name, width=None)
            else:
                st.write("🖼️ No Image")

           

        with col2:
            st.write(f"**{common_name} ({scientific_name})**")
            st.write(f"Confidence: {confidence:.2f}")
            st.write(f"Detected: {hours_ago}h {minutes_ago}m ago")
            if bird_data and bird_data["summary"]:
                st.write(bird_data["summary"])
             # Audio player below the image
            if file_path:
                with open(file_path, "rb") as audio_file:
                    audio_bytes = audio_file.read()
                    st.audio(audio_bytes, format="audio/wav")
            # if bird_data and bird_data["page_url"]:
            #     st.write(f"[Read more on Wikipedia]({bird_data['page_url']})")
            
            # # Show IUCN Conservation Status
            # if wikidata_info and wikidata_info["iucn_status"]:
            #     st.write(f"[IUCN Conservation Status]({wikidata_info['iucn_status']})")

        with col3:
            # Display taxon range map if available
            if wikidata_info and wikidata_info["taxon_range_map"]:
                st.markdown(
                    f'<img src="{wikidata_info["taxon_range_map"]}" style="width: auto; height: auto; max-width: 100%; max-height: 250px; object-fit: contain; border-radius: 10px;">',
                    unsafe_allow_html=True,
                )

                # st.image(wikidata_info["taxon_range_map"], caption="Taxon Range Map", width=300)
            else:
                st.write("🌍 No Range Map Available")

        st.markdown("---")
