import os
import requests
import re
import uvicorn
import csv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import syncedlyrics
from googleapiclient.discovery import build
from pocketbase import PocketBase
import json
import isodate
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

pb = PocketBase(os.getenv("PB_URL", "http://127.0.0.1:8090"))

class LyricsResponse(BaseModel):
    upload_id: str

def log_error(file_name, video_id, error_details):
    file_exists = os.path.isfile(file_name)
    with open(file_name, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['video_id', 'error_details'])
        writer.writerow([video_id, error_details])

def log_success(file_name, video_id, artist_name, song_name, extracted_title, video_title):
    file_exists = os.path.isfile(file_name)
    with open(file_name, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            # Write the header row if the file does not exist
            writer.writerow(['video_id', 'artist_name', 'song_name', 'extracted_title', 'video_title'])
        writer.writerow([video_id, artist_name, song_name, extracted_title, video_title])

def simplify_title(long_title):
    long_title = re.sub(r'\s*ft\..*', '', long_title)
    long_title = re.sub(r'//.*', '', long_title)
    long_title = re.sub(r'\s*\|.*', '', long_title)
    long_title = re.sub(r'\s*[\(\[].*?[\)\]]', '', long_title)
    return long_title.strip()

def extract_title_from_description(description):
    lines = description.strip().split('\n')
    title_info = lines[2]
    if ' · ' in title_info:
        info = title_info.split(' · ')
        real_title = f"{info[1]} - {info[0]}"
        return real_title
    else:
        raise ValueError("Failure extracting title from description")

def get_title_from_info(info):
    first_guess = info["title"]
    if ' - ' in first_guess:
        return first_guess
    else:
        second_guess = extract_title_from_description(info["description"])
        if ' - ' in second_guess:
            return second_guess
    raise ValueError(f"Couldn't fetch title for video id: {info['id']} with title: {info['title']}")

def lrc_to_json(video_id, artist_name, song_name, lrc_content):
    lines = lrc_content.strip().split('\n')
    lyrics = []
    
    if len(lines) < 1:
        return {
            "video_id": video_id,
            "artist_name": artist_name,
            "song_name": song_name,
            "lyrics": lyrics
        }
        
    first_timestamp = lines[0].split(']')[0][1:]
    if first_timestamp != "00:00.00":
        minutes, seconds = map(float, first_timestamp.split(':'))
        timestamp = minutes * 60 + seconds
        lyrics.append({
            "content": "",
            "timestamp": 0.00,
            "timestampEnd": round(timestamp, 2),
        })
    
    for index, line in enumerate(lines):
        timestamp_str, content = line.split(']', 1)
        timestamp_str = timestamp_str[1:]
        minutes, seconds = map(float, timestamp_str.split(':'))
        timestamp = minutes * 60 + seconds
        
        if index <= len(lines) - 2:
            end_timestamp_str = lines[index + 1].split(']')[0][1:]
            end_minutes, end_seconds = map(float, end_timestamp_str.split(':'))
            timestamp_end = end_minutes * 60 + end_seconds
            lyrics.append({
                "content": content.strip(),
                "timestamp": round(timestamp, 2),
                "timestampEnd": round(timestamp_end, 2)
            })
        else:
            timestamp_end = 'end'
            lyrics.append({
                "content": content.strip(),
                "timestamp": round(timestamp, 2),
                "timestampEnd": timestamp_end
            })

    result = {
        "video_id": video_id,
        "artist_name": artist_name,
        "song_name": song_name,
        "lyrics": lyrics
    }
    
    return result

def plain_to_json(video_id, artist_name, song_name, plain_lines):
    lines = plain_lines.strip().split('\n')
    lyrics = []
    
    for line in lines:
        lyrics.append({
            "content": line.strip(),
        })

    result = {
        "video_id": video_id,
        "artist_name": artist_name,
        "song_name": song_name,
        "lyrics": lyrics
    }
    
    return result

def download_info(video_id):
    API_KEY = os.getenv("YOUTUBE_API_KEY")

    youtube = build('youtube', 'v3', developerKey=API_KEY)

    request = youtube.videos().list(
        part='snippet, contentDetails',
        id=video_id
    )
    response = request.execute()

    if 'items' in response and len(response['items']) > 0:
        video_data = response['items'][0]
        metadata = {
            'id': video_data['id'],
            'title': video_data['snippet']['title'],
            'description': video_data['snippet']['description'],
            'channelTitle': video_data['snippet']['channelTitle'],
            'publishTime': video_data['snippet']['publishedAt'],
            'duration': isodate.parse_duration(video_data['contentDetails']['duration']).total_seconds(),
        }
        return metadata
    else:
        return None

@app.get("/", response_model=LyricsResponse)
async def get_lyrics(video_id: str):
    if not video_id:
        raise HTTPException(status_code=400, detail="video_id is required")

    try:
        video_info = download_info(video_id)
        
        try:
            title = get_title_from_info(video_info)
        except ValueError as ve:
            raise HTTPException(status_code=422, detail=str(ve))

        simplified_title = simplify_title(title)
        parts = simplified_title.split(" - ", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid title format - expected 'Artist - Song' but got: {simplified_title}")
        artist, song_title = parts

        # Use the duration fetched from YouTube API
        duration = int(video_info['duration'])  # Duration in seconds
        lrclib_url = "https://lrclib.net/api/get"
        lrclib_params = {
            "artist_name": artist,
            "track_name": song_title,
            "duration": duration
        }

        lrclib_response = requests.get(lrclib_url, params=lrclib_params)

        lyricsAreFound = False

        if lrclib_response.status_code == 200:
            lrclib_data = lrclib_response.json()
            if 'syncedLyrics' in lrclib_data:
                json_submission = lrc_to_json(video_info["id"], artist, song_title, lrclib_data['syncedLyrics'])
                lyricsAreFound = True

        if not lyricsAreFound:
            # Fallback to syncedlyrics if lrclib fails
            print("Error fetching from lrclib.net/api/get:", lrclib_response.status_code, lrclib_response.text)

            lyrics = syncedlyrics.search(simplified_title, synced_only=True, providers=["Lrclib"])
            if lyrics == None:
                raise ValueError(f"Syncedlyrics failed for simplified_title: {simplified_title} with title: {title}")

            json_submission = lrc_to_json(video_info["id"], artist, song_title, lyrics)

        if not json_submission:
            raise ValueError(f"This shouldn't happen. This is a bug.")

        record = {
            "song_id": json_submission["video_id"],
            "song_data": json.dumps(json_submission),
            "popularity_score": 0,
        }

        try:
            created_record = pb.collection("song_uploads").create(record)
            print(f"Record created with ID: {created_record.id}")
            log_success("success_sync.csv", video_info["id"], artist, song_title, title, video_info["title"])
            return { "upload_id": created_record.id }
        except Exception as e:
            print(f"Error: {e}")
            raise e

    except Exception as e:
        log_error("error_sync.csv", video_id, str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/plain", response_model=LyricsResponse)
async def plain_lyrics(video_id: str):
    if not video_id:
        raise HTTPException(status_code=400, detail="video_id is required")

    try:
        video_info = download_info(video_id)
        
        try:
            title = get_title_from_info(video_info)
        except ValueError as ve:
            raise HTTPException(status_code=422, detail=str(ve))

        simplified_title = simplify_title(title)
        parts = simplified_title.split(" - ", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid title format - expected 'Artist - Song' but got: {simplified_title}")
        artist, song_title = parts
        
        lyrics = syncedlyrics.search(simplified_title, plain_only=True, providers=["Genius", "Musixmatch", "Lrclib"])
        if lyrics == None:
            raise ValueError(f"Syncedlyrics failed for simplified_title: {simplified_title} with title: {title}")

        json_submission = plain_to_json(video_info["id"], artist, song_title, lyrics)

        record = {
            "song_id": json_submission["video_id"],
            "song_data": json.dumps(json_submission),
        }

        try:
            created_record = pb.collection("unlabeled_songs").create(record)
            print(f"Record created with ID: {created_record.id}")
            log_success("success_plain.csv", video_info["id"], artist, song_title, title, video_info["title"])
            return { "upload_id": created_record.id }
        except Exception as e:
            print(f"Error: {e}")
            raise e

    except Exception as e:
        log_error("error_plain.csv", video_id, str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
