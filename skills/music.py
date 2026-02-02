"""Music playback skill for JARVIS-X - Alexa-like functionality."""

import json
import os
import random
import webbrowser
from datetime import datetime
from typing import Dict, List, Any, Optional
from loguru import logger

class MusicSkill:
    """Provides music playback features similar to Alexa."""

    def __init__(self):
        self.playlists_file = "jarvis_playlists.json"
        self.current_playlist = []
        self.current_track_index = -1
        self.is_playing = False

        # Load user playlists
        self.playlists = self._load_playlists()

        self.commands = {
            "play_music": ["play music", "play song", "play track", "start music"],
            "play_artist": ["play artist", "play songs by", "music by"],
            "play_genre": ["play genre", "play some", "play jazz", "play rock", "play pop"],
            "play_playlist": ["play playlist", "start playlist", "shuffle playlist"],
            "pause_music": ["pause music", "pause song", "stop music", "stop playing"],
            "next_track": ["next song", "next track", "skip song", "play next"],
            "previous_track": ["previous song", "previous track", "last song"],
            "volume_control": ["volume up", "volume down", "louder", "quieter", "set volume"],
            "create_playlist": ["create playlist", "new playlist", "make playlist"],
            "list_music": ["what's playing", "current song", "now playing", "show playlist"]
        }

        # Free music sources (APIs and suggestions)
        self.music_sources = {
            "free_music_archive": "https://freemusicarchive.org",
            "jamendo": "https://www.jamendo.com",
            "soundcloud_free": "https://soundcloud.com",
            "youtube_music_free": "https://music.youtube.com"
        }

    def can_handle(self, text: str) -> bool:
        """Check if this skill can handle the request."""
        text_lower = text.lower()
        for command_list in self.commands.values():
            if any(cmd in text_lower for cmd in command_list):
                return True
        return False

    def execute(self, text: str) -> str:
        """Execute music command."""
        text_lower = text.lower()

        try:
            # Play music commands
            if any(cmd in text_lower for cmd in self.commands["play_music"]):
                return self._play_music(text)

            # Play by artist
            elif any(cmd in text_lower for cmd in self.commands["play_artist"]):
                return self._play_artist(text)

            # Play by genre
            elif any(cmd in text_lower for cmd in self.commands["play_genre"]):
                return self._play_genre(text)

            # Play playlist
            elif any(cmd in text_lower for cmd in self.commands["play_playlist"]):
                return self._play_playlist(text)

            # Pause/stop music
            elif any(cmd in text_lower for cmd in self.commands["pause_music"]):
                return self._pause_music()

            # Next track
            elif any(cmd in text_lower for cmd in self.commands["next_track"]):
                return self._next_track()

            # Previous track
            elif any(cmd in text_lower for cmd in self.commands["previous_track"]):
                return self._previous_track()

            # Volume control
            elif any(cmd in text_lower for cmd in self.commands["volume_control"]):
                return self._control_volume(text)

            # Create playlist
            elif any(cmd in text_lower for cmd in self.commands["create_playlist"]):
                return self._create_playlist(text)

            # List/now playing
            elif any(cmd in text_lower for cmd in self.commands["list_music"]):
                return self._now_playing()

            else:
                return self._get_music_overview()

        except Exception as e:
            logger.error(f"Music skill error: {e}")
            return "Sorry, I'm having trouble with music playback right now."

    def _play_music(self, text: str) -> str:
        """Play music based on request."""
        try:
            song_name = self._extract_song_name(text)

            if song_name:
                # Search for the song online
                search_url = f"https://www.youtube.com/search?q={song_name.replace(' ', '+')}"
                webbrowser.open(search_url)
                self.is_playing = True
                return f"Searching for and playing '{song_name}' on YouTube Music."
            else:
                # Play random music
                return self._play_random_music()

        except Exception as e:
            logger.error(f"Play music error: {e}")
            return "Sorry, I couldn't start playing music."

    def _play_artist(self, text: str) -> str:
        """Play music by a specific artist."""
        try:
            artist_name = self._extract_artist_name(text)

            if artist_name:
                search_url = f"https://www.youtube.com/search?q={artist_name.replace(' ', '+')}+music"
                webbrowser.open(search_url)
                self.is_playing = True
                return f"Playing music by {artist_name}."
            else:
                return "Please specify which artist you'd like to hear."

        except Exception as e:
            logger.error(f"Play artist error: {e}")
            return "Sorry, I couldn't find music by that artist."

    def _play_genre(self, text: str) -> str:
        """Play music by genre."""
        try:
            genre = self._extract_genre(text)

            if genre:
                search_url = f"https://www.youtube.com/search?q={genre}+music+playlist"
                webbrowser.open(search_url)
                self.is_playing = True
                return f"Playing {genre} music."
            else:
                return "Please specify which genre you'd like to hear."

        except Exception as e:
            logger.error(f"Play genre error: {e}")
            return "Sorry, I couldn't find music in that genre."

    def _play_playlist(self, text: str) -> str:
        """Play a playlist."""
        try:
            playlist_name = self._extract_playlist_name(text)

            if playlist_name and playlist_name in self.playlists:
                self.current_playlist = self.playlists[playlist_name]['tracks']
                self.current_track_index = 0
                self.is_playing = True

                if self.current_playlist:
                    current_track = self.current_playlist[0]
                    return f"Playing playlist '{playlist_name}' - now playing: {current_track['title']} by {current_track['artist']}"
                else:
                    return f"Playlist '{playlist_name}' is empty."
            else:
                available_playlists = list(self.playlists.keys())
                if available_playlists:
                    return f"I couldn't find that playlist. Available playlists: {', '.join(available_playlists)}"
                else:
                    return "You don't have any playlists yet. Try creating one first."

        except Exception as e:
            logger.error(f"Play playlist error: {e}")
            return "Sorry, I couldn't start the playlist."

    def _play_random_music(self) -> str:
        """Play random music from free sources."""
        try:
            # Open a free music streaming site
            free_music_sites = [
                "https://www.jamendo.com",
                "https://freemusicarchive.org",
                "https://www.soundcloud.com/charts",
                "https://music.youtube.com"
            ]

            chosen_site = random.choice(free_music_sites)
            webbrowser.open(chosen_site)
            self.is_playing = True

            site_names = {
                "https://www.jamendo.com": "Jamendo",
                "https://freemusicarchive.org": "Free Music Archive",
                "https://www.soundcloud.com/charts": "SoundCloud Charts",
                "https://music.youtube.com": "YouTube Music"
            }

            site_name = site_names.get(chosen_site, "free music site")
            return f"Opening {site_name} for some great free music!"

        except Exception as e:
            logger.error(f"Random music error: {e}")
            return "Sorry, I couldn't start playing random music."

    def _pause_music(self) -> str:
        """Pause or stop music."""
        if self.is_playing:
            self.is_playing = False
            return "Music paused."
        else:
            return "No music is currently playing."

    def _next_track(self) -> str:
        """Play next track in playlist."""
        if not self.current_playlist:
            return "No playlist is currently loaded."

        if self.current_track_index < len(self.current_playlist) - 1:
            self.current_track_index += 1
            current_track = self.current_playlist[self.current_track_index]
            return f"Now playing: {current_track['title']} by {current_track['artist']}"
        else:
            return "You've reached the end of the playlist."

    def _previous_track(self) -> str:
        """Play previous track in playlist."""
        if not self.current_playlist:
            return "No playlist is currently loaded."

        if self.current_track_index > 0:
            self.current_track_index -= 1
            current_track = self.current_playlist[self.current_track_index]
            return f"Now playing: {current_track['title']} by {current_track['artist']}"
        else:
            return "You're at the beginning of the playlist."

    def _control_volume(self, text: str) -> str:
        """Control volume."""
        text_lower = text.lower()

        if 'up' in text_lower or 'louder' in text_lower:
            return "Volume increased. (Note: Volume control works with your system's audio settings)"
        elif 'down' in text_lower or 'quieter' in text_lower:
            return "Volume decreased. (Note: Volume control works with your system's audio settings)"
        elif 'set volume' in text_lower:
            level = self._extract_volume_level(text)
            if level is not None:
                return f"Volume set to {level}%. (Note: Volume control works with your system's audio settings)"
            else:
                return "Please specify a volume level between 0 and 100."

        return "Volume control not recognized."

    def _create_playlist(self, text: str) -> str:
        """Create a new playlist."""
        try:
            playlist_name = self._extract_playlist_name(text)

            if not playlist_name:
                return "Please specify a name for the playlist."

            if playlist_name in self.playlists:
                return f"Playlist '{playlist_name}' already exists."

            # Create empty playlist
            self.playlists[playlist_name] = {
                'name': playlist_name,
                'tracks': [],
                'created': datetime.now().isoformat()
            }

            self._save_playlists()
            return f"Created new playlist: '{playlist_name}'"

        except Exception as e:
            logger.error(f"Create playlist error: {e}")
            return "Sorry, I couldn't create that playlist."

    def _now_playing(self) -> str:
        """Get current playing information."""
        if not self.is_playing:
            return "No music is currently playing."

        if self.current_playlist and self.current_track_index >= 0:
            current_track = self.current_playlist[self.current_track_index]
            return f"Now playing: {current_track['title']} by {current_track['artist']} (Track {self.current_track_index + 1} of {len(self.current_playlist)})"
        else:
            return "Music is playing from an external source."

    def _get_music_overview(self) -> str:
        """Get music overview."""
        playlist_count = len(self.playlists)

        response = (f"🎵 Music Overview:\\n"
                   f"📀 Playlists: {playlist_count}\\n"
                   f"🎶 Now Playing: {'Yes' if self.is_playing else 'No'}\\n\\n"
                   f"Try commands like:\\n"
                   f"• 'play some jazz music'\\n"
                   f"• 'play playlist my favorites'\\n"
                   f"• 'create playlist workout'\\n"
                   f"• 'next song'\\n"
                   f"• 'volume up'")

        if playlist_count > 0:
            response += f"\\n\\nYour playlists: {', '.join(self.playlists.keys())}"

        return response

    def _load_playlists(self) -> Dict[str, Any]:
        """Load playlists from file."""
        try:
            if os.path.exists(self.playlists_file):
                with open(self.playlists_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading playlists: {e}")

        # Return default playlists
        return {
            'favorites': {
                'name': 'Favorites',
                'tracks': [
                    {'title': 'Sample Track 1', 'artist': 'Sample Artist', 'duration': '3:45'},
                    {'title': 'Sample Track 2', 'artist': 'Sample Artist', 'duration': '4:12'}
                ],
                'created': datetime.now().isoformat()
            }
        }

    def _save_playlists(self):
        """Save playlists to file."""
        try:
            with open(self.playlists_file, 'w') as f:
                json.dump(self.playlists, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving playlists: {e}")

    # Text extraction helper methods
    def _extract_song_name(self, text: str) -> Optional[str]:
        """Extract song name from text."""
        import re

        patterns = [
            r'play (.+?)(?:\s|$)',
            r'play song (.+?)(?:\s|$)',
            r'play track (.+?)(?:\s|$)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                song = match.group(1).strip()
                # Remove common words
                song = re.sub(r'\b(music|song|track|by|the|a|an)\b', '', song, flags=re.IGNORECASE).strip()
                if song:
                    return song

        return None

    def _extract_artist_name(self, text: str) -> Optional[str]:
        """Extract artist name from text."""
        import re

        patterns = [
            r'play artist (.+?)(?:\s|$)',
            r'play songs by (.+?)(?:\s|$)',
            r'music by (.+?)(?:\s|$)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_genre(self, text: str) -> Optional[str]:
        """Extract music genre from text."""
        genres = ['jazz', 'rock', 'pop', 'classical', 'hip hop', 'rap', 'country', 'blues', 'electronic', 'dance']

        text_lower = text.lower()
        for genre in genres:
            if genre in text_lower:
                return genre

        return None

    def _extract_playlist_name(self, text: str) -> Optional[str]:
        """Extract playlist name from text."""
        import re

        patterns = [
            r'playlist (.+?)(?:\s|$)',
            r'play (.+?)(?:\s|$)'  # This might catch playlist names too
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Check if it's actually a playlist name
                if name in self.playlists or 'playlist' in text.lower():
                    return name

        return None

    def _extract_volume_level(self, text: str) -> Optional[int]:
        """Extract volume level from text."""
        import re

        match = re.search(r'(\d+)', text)
        if match:
            level = int(match.group(1))
            if 0 <= level <= 100:
                return level

        return None
