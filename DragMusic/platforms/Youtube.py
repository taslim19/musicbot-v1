import asyncio
import os
import re
import json
import httpx  # Make sure to import httpx
from typing import Union
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
from DragMusic.utils.database import is_on_off
from DragMusic.utils.formatters import time_to_seconds
import tempfile
import logging

# --- Logger Setup ---
# This configuration is correct and remains the same.
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more detailed logs
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def shell_cmd(cmd):
    """Executes a shell command asynchronously."""
    logger.debug(f"Executing shell command: {cmd}")
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        error_str = errorz.decode("utf-8").strip()
        if "unavailable videos are hidden" in error_str.lower():
            logger.warning("yt-dlp indicated that some unavailable videos were hidden.")
            return out.decode("utf-8")
        else:
            logger.error(f"Shell command failed: {error_str}")
            return error_str
    return out.decode("utf-8")


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        logger.info("YouTubeAPI instance created.")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        """Checks if a link is a valid YouTube URL."""
        if videoid:
            link = self.base + link
        is_youtube_link = bool(re.search(self.regex, link))
        logger.debug(f"Checking existence for '{link}'. Result: {is_youtube_link}")
        return is_youtube_link

    async def url(self, message_1: Message) -> Union[str, None]:
        """Extracts a URL from a Pyrogram message."""
        logger.debug("Attempting to extract URL from message.")
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        logger.info(f"Extracted text link: {entity.url}")
                        return entity.url
        if offset is None:
            logger.warning("No URL entity found in the message.")
            return None
        
        extracted_url = text[offset : offset + length]
        logger.info(f"Extracted standard URL: {extracted_url}")
        return extracted_url

    async def details(self, link: str, videoid: Union[bool, str] = None):
        """Fetches comprehensive details for a video."""
        logger.info(f"Fetching details for link: {link}")
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        try:
            results = VideosSearch(link, limit=1)
            video_result = (await results.next())["result"]
            if not video_result:
                logger.error(f"No results found for link: {link}")
                return None
            
            result = video_result[0]
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
            
            logger.info(f"Details found for video ID {vidid}: '{title}'")
            return title, duration_min, duration_sec, thumbnail, vidid
        except Exception as e:
            logger.error(f"Failed to fetch video details for '{link}'. Error: {e}")
            return None, None, None, None, None

    # The following methods are simplified wrappers around 'details'.
    # Logging is focused on the main 'details' method.
    async def title(self, link: str, videoid: Union[bool, str] = None):
        details_tuple = await self.details(link, videoid)
        return details_tuple[0] if details_tuple else None

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        details_tuple = await self.details(link, videoid)
        return details_tuple[1] if details_tuple else None

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        details_tuple = await self.details(link, videoid)
        return details_tuple[3] if details_tuple else None

    async def video(self, link: str, videoid: Union[bool, str] = None):
        """Gets the direct streamable URL for a video."""
        logger.info(f"Getting direct video stream URL for: {link}")
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
            
        cmd = [
            "yt-dlp", "-g", "-f", "best[height<=?720][width<=?1280]", f"{link}"
        ]
        
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        
        if stdout:
            url = stdout.decode().split("\n")[0]
            logger.info(f"Successfully retrieved stream URL for {link}")
            return 1, url
        else:
            logger.error(f"Failed to get stream URL for {link}. Stderr: {stderr.decode()}")
            return 0, stderr.decode()

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        """Fetches video IDs from a playlist."""
        logger.info(f"Fetching playlist for link: {link} with limit: {limit}")
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        
        command = f"yt-dlp -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link}"
        playlist_data = await shell_cmd(command)
        
        try:
            result = [key for key in playlist_data.split("\n") if key]
            logger.info(f"Successfully fetched {len(result)} items from playlist.")
            return result
        except Exception as e:
            logger.error(f"Failed to parse playlist data. Error: {e}")
            logger.debug(f"Raw playlist data was: '{playlist_data}'")
            return []

    async def track(self, link: str, videoid: Union[bool, str] = None):
        """Fetches a dictionary of track details."""
        logger.info(f"Fetching track details for: {link}")
        details_tuple = await self.details(link, videoid)
        if not details_tuple or not details_tuple[4]:
            logger.error(f"Could not get details to form track for {link}")
            return None, None

        title, duration_min, _, thumbnail, vidid = details_tuple
        yturl = f"https://youtube.com/watch?v={vidid}"
        
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        logger.info(f"Track details created for video ID {vidid}")
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        """Fetches available download formats for a video."""
        logger.info(f"Fetching available formats for: {link}")
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        ytdl_opts = {"quiet": True}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        
        try:
            with ydl:
                formats_available = []
                r = ydl.extract_info(link, download=False)
                for f in r["formats"]:
                    # Check for essential keys before appending
                    if all(k in f for k in ["format", "filesize", "format_id", "ext", "format_note"]):
                        if "dash" not in str(f["format"]).lower():
                            formats_available.append({k: f[k] for k in f if k in [
                                "format", "filesize", "format_id", "ext", "format_note"
                            ]})
                            formats_available[-1]["yturl"] = link
                    else:
                        logger.debug(f"Skipping incomplete format: {f.get('format_id', 'N/A')}")
            logger.info(f"Found {len(formats_available)} suitable formats for {link}.")
            return formats_available, link
        except Exception as e:
            logger.error(f"Could not extract formats for {link}. Error: {e}")
            return [], link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        """Gets details for a specific item from a search result list."""
        logger.info(f"Fetching slider result for query '{link}' at index {query_type}")
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        try:
            a = VideosSearch(link, limit=10)
            result = (await a.next()).get("result")
            if not result or len(result) <= query_type:
                logger.error(f"Query '{link}' did not return enough results for index {query_type}.")
                return None, None, None, None
            
            q_result = result[query_type]
            title = q_result["title"]
            duration_min = q_result["duration"]
            vidid = q_result["id"]
            thumbnail = q_result["thumbnails"][0]["url"].split("?")[0]
            logger.info(f"Slider details found for video ID {vidid}: '{title}'")
            return title, duration_min, thumbnail, vidid
        except Exception as e:
            logger.error(f"Failed to fetch slider details for '{link}'. Error: {e}")
            return None, None, None, None


    async def get_video_info_from_bitflow(self, url: str, video: bool):
        """Queries the Bitflow API for video information."""
        logger.info(f"Querying Bitflow API for URL: {url} (video={video})")
        api_url = "https://bitflow.in/api/youtube"
        params = { "query": url, "format": "video" if video else "audio", "download": True, "api_key": "1spiderkey2" }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(api_url, params=params, timeout=150)
                response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                logger.info("Successfully fetched data from Bitflow API.")
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Bitflow API request failed with status {e.response.status_code} for URL: {e.request.url}")
                return {"status": "error", "message": "Failed to fetch data from Bitflow API."}
            except Exception as e:
                logger.error(f"An unexpected error occurred while calling Bitflow API: {e}")
                return {"status": "error", "message": "An unexpected error occurred."}

    async def download(
        self, link: str, mystic, video: bool = None, videoid: bool = None,
        songaudio: bool = None, songvideo: bool = None,
        format_id: str = None, title: str = None
    ) -> str:
        """Main download handler."""
        logger.info(f"Download initiated for: {link} with params: video={video}, songaudio={songaudio}, songvideo={songvideo}")
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        loop = asyncio.get_running_loop()
        
        # --- Helper functions for downloading ---
        def run_download(ydl_opts, download_link, file_path):
            if os.path.exists(file_path):
                logger.warning(f"File already exists, skipping download: {file_path}")
                return file_path
            try:
                logger.debug(f"yt-dlp options: {ydl_opts}")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([download_link])
                logger.info(f"Download successful: {file_path}")
                return file_path
            except Exception as e:
                logger.error(f"yt-dlp download failed for {download_link}. Error: {e}")
                raise e # Re-raise to be caught by the main logic

        def song_video_dl():
            temp_dir = tempfile.gettempdir()
            fpath = os.path.join(temp_dir, f"{title}.mp4")
            ydl_opts = {
                "format": f"{format_id}+140", "outtmpl": fpath, "geo_bypass": True,
                "nocheckcertificate": True, "quiet": True, "no_warnings": True,
                "prefer_ffmpeg": True, "merge_output_format": "mp4",
            }
            logger.info(f"Starting song video download for '{title}'")
            run_download(ydl_opts, link, fpath)
            return fpath

        def song_audio_dl():
            temp_dir = tempfile.gettempdir()
            # yt-dlp will add the extension
            fpath_template = os.path.join(temp_dir, f"{title}.%(ext)s")
            final_fpath = os.path.join(temp_dir, f"{title}.mp3")
            ydl_opts = {
                "format": format_id, "outtmpl": fpath_template, "geo_bypass": True,
                "nocheckcertificate": True, "quiet": True, "no_warnings": True,
                "prefer_ffmpeg": True,
                "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
            }
            logger.info(f"Starting song audio download for '{title}'")
            run_download(ydl_opts, link, final_fpath)
            return final_fpath

        # --- Main Download Logic ---
        try:
            if songvideo:
                return await loop.run_in_executor(None, song_video_dl)
            elif songaudio:
                return await loop.run_in_executor(None, song_audio_dl)

            # Fallback to Bitflow API
            logger.info("Using Bitflow API for direct download.")
            bitflow_info = await self.get_video_info_from_bitflow(link, video)

            if not bitflow_info or bitflow_info.get("status") != "success":
                logger.error(f"Bitflow API failed for {link}. Cannot proceed with download.")
                return None
            
            download_url = bitflow_info['url']
            file_ext = bitflow_info['ext']
            video_id = bitflow_info['videoid']
            
            temp_dir = tempfile.gettempdir()
            downloaded_file_path = os.path.join(temp_dir, f"{video_id}.{file_ext}")

            if os.path.exists(downloaded_file_path):
                logger.warning(f"File from Bitflow URL already exists, using cached: {downloaded_file_path}")
                return downloaded_file_path, True

            logger.info(f"Downloading from Bitflow URL: {download_url}")
            async with httpx.AsyncClient() as client:
                async with client.stream("GET", download_url, timeout=300) as response:
                    response.raise_for_status()
                    with open(downloaded_file_path, "wb") as f:
                        async for chunk in response.aiter_bytes():
                            f.write(chunk)
            
            logger.info(f"Direct download from Bitflow complete: {downloaded_file_path}")
            return downloaded_file_path, True

        except Exception as e:
            logger.exception(f"An unhandled error occurred during the download process for {link}.")
            return None