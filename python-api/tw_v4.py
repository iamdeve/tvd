import os
import json
import tempfile
import yt_dlp
import time
import subprocess
import shutil
import platform
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import cross_origin

app = Flask(__name__)

class TwitterVideoDownloader:
    def __init__(self, temp_dir=None):
        """
        Initialize downloader with configurable temp directory

        Args:
            temp_dir: Custom temporary directory path. If None, uses system default.
                     Can be set via environment variable TWITTER_DOWNLOADER_TEMP_DIR
        """
        # Priority: 1. Parameter, 2. Environment variable, 3. System default
        if temp_dir:
            self.temp_dir = os.path.abspath(temp_dir)
        elif os.environ.get('TWITTER_DOWNLOADER_TEMP_DIR'):
            self.temp_dir = os.path.abspath(os.environ.get('TWITTER_DOWNLOADER_TEMP_DIR'))
        else:
            # Use system temp, but prefer user directory on Windows
            if platform.system() == 'Windows':
                # Use user's temp directory or Downloads folder
                user_temp = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Temp', 'TwitterDownloader')
                self.temp_dir = user_temp
            else:
                # Linux/Unix - try user home first, then system temp
                #user_temp = os.path.join(os.path.expanduser('~'), '.twitter_downloader_temp')
                #self.temp_dir = user_temp
                self.temp_dir = "/home/ubuntu/video_downloads"

        # Ensure temp directory exists and is writable
        self._ensure_temp_dir()

        # Check available space on startup
        self._check_disk_space()

    def _ensure_temp_dir(self):
        """Ensure temp directory exists and is writable (cross-platform)"""
        try:
            # Use pathlib for better cross-platform path handling
            temp_path = Path(self.temp_dir)
            temp_path.mkdir(parents=True, exist_ok=True)

            # Test write permissions
            test_file = temp_path / 'test_write.tmp'
            test_file.write_text('test')
            test_file.unlink()  # Remove test file

            print(f"Using temp directory: {self.temp_dir}")
            print(f"Platform: {platform.system()}")

        except Exception as e:
            print(f"Error with temp directory {self.temp_dir}: {e}")
            # Fallback to system temp
            self.temp_dir = tempfile.gettempdir()
            print(f"Falling back to system temp: {self.temp_dir}")

            # Try to create fallback directory too
            try:
                Path(self.temp_dir).mkdir(parents=True, exist_ok=True)
            except Exception as fallback_error:
                print(f"Warning: Could not ensure fallback temp directory: {fallback_error}")

    def _check_disk_space(self, min_free_mb=100):
        """Check available disk space in temp directory"""
        try:
            stat = shutil.disk_usage(self.temp_dir)
            free_mb = stat.free / (1024 * 1024)
            total_mb = stat.total / (1024 * 1024)
            used_mb = (stat.total - stat.free) / (1024 * 1024)

            print(f"Disk space in {self.temp_dir}:")
            print(f"  Total: {total_mb:.1f} MB")
            print(f"  Used: {used_mb:.1f} MB")
            print(f"  Free: {free_mb:.1f} MB")

            if free_mb < min_free_mb:
                print(f"WARNING: Low disk space! Only {free_mb:.1f} MB free (minimum recommended: {min_free_mb} MB)")
                return False
            return True
        except Exception as e:
            print(f"Error checking disk space: {e}")
            return True  # Assume OK if we can't check

    def _cleanup_old_files(self, max_age_minutes=30):
        """Clean up old temporary files to free space (cross-platform)"""
        try:
            current_time = time.time()
            cleaned_count = 0
            temp_path = Path(self.temp_dir)

            if not temp_path.exists():
                return

            # Use pathlib for better cross-platform file handling
            for file_path in temp_path.iterdir():
                if file_path.name.startswith('twitter_video_') and file_path.is_file():
                    try:
                        file_age = current_time - file_path.stat().st_mtime
                        if file_age > (max_age_minutes * 60):
                            file_path.unlink()
                            cleaned_count += 1
                            print(f"Cleaned up old temp file: {file_path.name}")
                    except Exception as e:
                        print(f"Error cleaning file {file_path.name}: {e}")

            if cleaned_count > 0:
                print(f"Cleaned up {cleaned_count} old temporary files")

        except Exception as e:
            print(f"Error during cleanup: {e}")

    def get_video_info(self, tweet_url):
        """Extract video information from Twitter URL using yt-dlp"""
        try:
            # Enhanced ydl options to get all format information
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'noplaylist': False,
                'youtube_include_dash_manifest': False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(tweet_url, download=False)

                if not info:
                    return None

                videos = []

                # Check if this is a playlist (multiple videos)
                if 'entries' in info and info['entries']:
                    # Multiple videos case
                    for i, entry in enumerate(info['entries']):
                        if entry and 'formats' in entry:
                            video_data = self._extract_single_video_info(entry, i + 1)
                            if video_data:
                                videos.append(video_data)
                else:
                    # Single video case
                    video_data = self._extract_single_video_info(info, 1)
                    if video_data:
                        videos.append(video_data)

                if not videos:
                    return None

                return {
                    'success': True,
                    'video_count': len(videos),
                    'videos': videos,
                    'tweet_info': {
                        'title': info.get('title', 'Twitter Video'),
                        'uploader': info.get('uploader', ''),
                        'description': info.get('description', ''),
                    }
                }

        except Exception as e:
            print(f"Error extracting video info: {e}")
            return None

    def _extract_single_video_info(self, entry, video_number):
        """Extract information for a single video entry"""
        try:
            formats = entry.get('formats', [])
            if not formats:
                return None

            # Separate video and audio formats
            video_formats = []
            audio_formats = []
            combined_formats = []

            for fmt in formats:
                format_id = fmt.get('format_id', '')
                vcodec = fmt.get('vcodec', 'none')
                acodec = fmt.get('acodec', 'none')
                ext = fmt.get('ext', '')
                protocol = fmt.get('protocol', '')
                resolution = fmt.get('resolution', '')

                # Skip m3u8/HLS formats initially, prefer HTTP
                is_hls = protocol == 'm3u8_native' or 'hls' in format_id.lower()

                # Check for audio-only formats more comprehensively
                is_audio_only = (
                    vcodec == 'none' or
                    'audio' in format_id.lower() or
                    resolution == 'audio only' or
                    fmt.get('video_ext') == 'none'
                )

                # Check for video-only formats
                is_video_only = (
                    acodec == 'none' or
                    fmt.get('audio_ext') == 'none'
                ) and not is_audio_only

                if not is_audio_only and not is_video_only and vcodec != 'none' and acodec != 'none':
                    # Combined video+audio format
                    combined_formats.append({
                        'format_id': format_id,
                        'quality': f"{fmt.get('height', 'unknown')}p",
                        'url': fmt.get('url', ''),
                        'ext': ext,
                        'filesize': fmt.get('filesize_approx', 0),
                        'protocol': protocol,
                        'is_hls': is_hls,
                        'vcodec': vcodec,
                        'acodec': acodec,
                        'width': fmt.get('width', 0),
                        'height': fmt.get('height', 0),
                        'tbr': fmt.get('tbr', 0)
                    })
                elif is_video_only and vcodec != 'none':
                    # Video-only format
                    video_formats.append({
                        'format_id': format_id,
                        'quality': f"{fmt.get('height', 'unknown')}p",
                        'url': fmt.get('url', ''),
                        'ext': ext,
                        'filesize': fmt.get('filesize_approx', 0),
                        'protocol': protocol,
                        'is_hls': is_hls,
                        'vcodec': vcodec,
                        'width': fmt.get('width', 0),
                        'height': fmt.get('height', 0),
                        'tbr': fmt.get('tbr', 0)
                    })
                elif is_audio_only:
                    # Audio-only format
                    audio_formats.append({
                        'format_id': format_id,
                        'url': fmt.get('url', ''),
                        'ext': ext,
                        'protocol': protocol,
                        'is_hls': is_hls,
                        'acodec': fmt.get('acodec', 'unknown'),
                        'abr': fmt.get('abr', 0),
                        'tbr': fmt.get('tbr', 0),
                        'format_note': fmt.get('format_note', '')
                    })

            # Sort formats by quality (prefer HTTP over HLS, then by quality/bitrate)
            combined_formats.sort(key=lambda x: (x['is_hls'], -x['height']))
            video_formats.sort(key=lambda x: (x['is_hls'], -x['height']))
            audio_formats.sort(key=lambda x: (x['is_hls'], -x['tbr']))

            return {
                'video_number': video_number,
                'duration': entry.get('duration', 0),
                'thumbnail': entry.get('thumbnail', ''),
                'title': entry.get('title', f'Twitter Video #{video_number}'),
                'combined_formats': combined_formats,
                'video_formats': video_formats,
                'audio_formats': audio_formats,
                'has_separate_audio': len(audio_formats) > 0,
                'raw_formats': formats
            }

        except Exception as e:
            print(f"Error extracting single video info: {e}")
            return None

    def download_with_audio_fix(self, tweet_url, quality='360p', video_number=1):
        """Download video with proper audio handling and improved file management"""
        downloaded_file = None
        try:
            # Check disk space before starting download
            if not self._check_disk_space(min_free_mb=50):
                # Try to clean up old files
                self._cleanup_old_files()
                # Check again
                if not self._check_disk_space(min_free_mb=50):
                    raise Exception("Insufficient disk space for download. Please free up space or use a different temp directory.")

            # First, get video info to understand format structure
            video_info = self.get_video_info(tweet_url)
            if not video_info or not video_info['videos']:
                raise Exception("Could not extract video information")

            target_video = None
            for video in video_info['videos']:
                if video['video_number'] == video_number:
                    target_video = video
                    break

            if not target_video:
                raise Exception(f"Video #{video_number} not found")

            print(f"Found video with {len(target_video['audio_formats'])} audio formats and {len(target_video['video_formats'])} video formats")

            # Create unique temporary filename
            import uuid
            unique_id = str(uuid.uuid4())[:8]
            filename = f"twitter_video_{video_number}_{quality}_{unique_id}"

            # Strategy selection based on available formats
            success = False
            final_file = None

            # Strategy 1: Try combined formats first (if any)
            if target_video['combined_formats']:
                print("Attempting download with combined format...")
                combined_format = target_video['combined_formats'][0]
                format_selector = combined_format['format_id']
                success, final_file = self._attempt_download_fixed(tweet_url, format_selector, filename, "combined")

            # Strategy 2: Use separate video + audio streams with SAME PROTOCOL
            if not success and target_video['video_formats'] and target_video['audio_formats']:
                print("Attempting download with separate video+audio streams (matching protocols)...")
                success, final_file = self._try_separate_streams(tweet_url, target_video, filename)

            # Strategy 3: Try with yt-dlp's automatic format selection (simplified)
            if not success:
                print("Attempting download with automatic format selection...")
                format_selector = "best[height<=720]/best"
                success, final_file = self._attempt_download_fixed(tweet_url, format_selector, filename, "auto")

            # Strategy 4: Last resort - basic best format
            if not success:
                print("Attempting download with basic best format...")
                format_selector = "best"
                success, final_file = self._attempt_download_fixed(tweet_url, format_selector, filename, "fallback")

            if not success or not final_file:
                raise Exception("All download strategies failed")

            # Verify file exists and has content
            if not os.path.exists(final_file):
                raise Exception(f"Downloaded file does not exist: {final_file}")

            file_size = os.path.getsize(final_file)
            if file_size == 0:
                raise Exception("Downloaded file is empty")

            print(f"Download successful: {final_file} ({file_size / 1024:.1f} KB)")
            return final_file

        except Exception as e:
            print(f"Error in download_with_audio_fix: {e}")
            # Clean up any partial files
            if downloaded_file and os.path.exists(downloaded_file):
                try:
                    os.remove(downloaded_file)
                except:
                    pass
            raise e

    def _try_separate_streams(self, tweet_url, target_video, filename):
        """Try downloading with separate video and audio streams"""
        # Group formats by protocol
        video_by_protocol = {}
        audio_by_protocol = {}

        for vf in target_video['video_formats']:
            protocol = 'hls' if vf['is_hls'] else 'http'
            if protocol not in video_by_protocol:
                video_by_protocol[protocol] = []
            video_by_protocol[protocol].append(vf)

        for af in target_video['audio_formats']:
            protocol = 'hls' if af['is_hls'] else 'http'
            if protocol not in audio_by_protocol:
                audio_by_protocol[protocol] = []
            audio_by_protocol[protocol].append(af)

        # Try to find matching protocols, prefer HTTP over HLS
        preferred_protocols = ['http', 'hls']

        for protocol in preferred_protocols:
            if protocol in video_by_protocol and protocol in audio_by_protocol:
                # Sort video formats by quality (descending)
                video_formats = sorted(video_by_protocol[protocol],
                                     key=lambda x: x.get('height', 0), reverse=True)
                # Sort audio formats by bitrate (descending)
                audio_formats = sorted(audio_by_protocol[protocol],
                                     key=lambda x: x.get('tbr', 0), reverse=True)

                best_video = video_formats[0]
                best_audio = audio_formats[0]

                format_selector = f"{best_video['format_id']}+{best_audio['format_id']}"
                print(f"Using {protocol.upper()} protocol - Video: {best_video['format_id']} + Audio: {best_audio['format_id']}")

                success, final_file = self._attempt_download_fixed(tweet_url, format_selector, filename, f"separate_{protocol}")
                if success:
                    return success, final_file

        return False, None

    def _attempt_download_fixed(self, tweet_url, format_selector, filename_base, strategy_name):
        """Improved download attempt with better error handling and file management (cross-platform)"""
        temp_file_path = None
        try:
            print(f"Strategy '{strategy_name}': Using format selector: {format_selector}")

            # Create full temp file path using pathlib for cross-platform compatibility
            temp_file_path = str(Path(self.temp_dir) / f"{filename_base}.mp4")

            # Simple download options - avoid complex post-processing
            ydl_opts = {
                'format': format_selector,
                'outtmpl': temp_file_path,
                'quiet': False,
                'no_warnings': False,
                'prefer_ffmpeg': True,
                'merge_output_format': 'mp4',
                # Minimal post-processing to avoid issues
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }] if strategy_name != 'fallback' else [],
                # Add connection retry options
                'socket_timeout': 30,
                'retries': 3,
                'fragment_retries': 3,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([tweet_url])

            # Wait a moment for file system to sync
            time.sleep(0.5)

            # Check if the exact file exists using pathlib
            temp_path = Path(temp_file_path)
            if temp_path.exists():
                file_size = temp_path.stat().st_size
                if file_size > 0:
                    print(f"Strategy '{strategy_name}' succeeded. File: {temp_file_path} ({file_size} bytes)")
                    return True, temp_file_path
                else:
                    print(f"Strategy '{strategy_name}' created empty file")

            # If exact path doesn't exist, look for similar files using pathlib
            temp_dir_path = Path(self.temp_dir)
            basename = Path(filename_base).stem

            for file_path in temp_dir_path.iterdir():
                if (file_path.name.startswith(basename) and
                    file_path.suffix in ['.mp4', '.mkv', '.webm'] and
                    file_path.is_file()):
                    file_size = file_path.stat().st_size
                    if file_size > 0:
                        found_file = str(file_path)
                        print(f"Strategy '{strategy_name}' succeeded. Found file: {found_file} ({file_size} bytes)")
                        return True, found_file

            return False, None

        except Exception as e:
            print(f"Strategy '{strategy_name}' failed: {e}")
            # Clean up any partial files
            if temp_file_path:
                try:
                    temp_path = Path(temp_file_path)
                    if temp_path.exists():
                        temp_path.unlink()
                except Exception as cleanup_error:
                    print(f"Could not clean up partial file: {cleanup_error}")
            return False, None

    def safe_file_cleanup(self, file_path, delay=1.0):
        """Safely cleanup downloaded file with delay (cross-platform)"""
        if not file_path:
            return

        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return

        try:
            # Wait a bit to ensure file handles are closed
            time.sleep(delay)
            file_path_obj.unlink()
            print(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            print(f"Warning: Could not remove temporary file {file_path}: {e}")

# Global downloader instance with configurable temp dir
downloader_instance = None

def get_downloader():
    """Get or create downloader instance with configured temp directory"""
    global downloader_instance
    if downloader_instance is None:
        # You can set custom temp directory via environment variable or config
        custom_temp = os.environ.get('TWITTER_DOWNLOADER_TEMP_DIR')
        downloader_instance = TwitterVideoDownloader(temp_dir=custom_temp)
    return downloader_instance

# Flask routes with improved error handling
@cross_origin()
def extract_video():
    """Extract video information from Twitter URL"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400

        twitter_url = data.get('url', '').strip()

        if not twitter_url:
            return jsonify({'error': 'URL is required'}), 400

        # Validate URL
        if not any(domain in twitter_url for domain in ['twitter.com', 'x.com']):
            return jsonify({'error': 'Invalid Twitter URL'}), 400

        downloader = get_downloader()
        video_info = downloader.get_video_info(twitter_url)

        if not video_info:
            return jsonify({'error': 'Could not extract video information. The tweet may not contain a video or may be private.'}), 404

        return jsonify(video_info)

    except Exception as e:
        print(f"Extract video error: {e}")
        return jsonify({'error': str(e)}), 500

@cross_origin()
def download_with_audio():
    """Download video with explicit audio handling and improved file management"""
    if request.method == 'OPTIONS':
        return '', 200

    downloaded_file = None
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400

        twitter_url = data.get('url', '').strip()
        quality = data.get('quality', '360p')
        video_number = data.get('video_number', 1)

        if not twitter_url:
            return jsonify({'error': 'Twitter URL is required'}), 400

        downloader = get_downloader()
        downloaded_file = downloader.download_with_audio_fix(twitter_url, quality, video_number)

        if not downloaded_file or not os.path.exists(downloaded_file):
            return jsonify({'error': 'Failed to download video'}), 500

        # Verify file integrity before reading
        file_size = os.path.getsize(downloaded_file)
        if file_size == 0:
            return jsonify({'error': 'Downloaded file is empty'}), 500

        print(f"Reading file: {downloaded_file} ({file_size} bytes)")

        # Read the file with error handling
        try:
            with open(downloaded_file, 'rb') as f:
                video_data = f.read()
        except Exception as e:
            print(f"Error reading downloaded file: {e}")
            return jsonify({'error': 'Could not read downloaded file'}), 500

        if len(video_data) == 0:
            return jsonify({'error': 'Downloaded file contains no data'}), 500

        # Return base64-encoded data for WordPress plugin
        import base64
        try:
            encoded_data = base64.b64encode(video_data).decode('utf-8')
            print(f"Base64 encoding successful. Original size: {len(video_data)}, Encoded length: {len(encoded_data)}")
            print(f"Base64 data starts with: {encoded_data[:50]}")
        except Exception as e:
            print(f"Error encoding video data: {e}")
            return jsonify({'error': 'Could not encode video data'}), 500

        download_name = f"twitter_video_audio_{video_number}_{quality}.mp4"

        # Clean up the temporary file AFTER successful encoding
        downloader.safe_file_cleanup(downloaded_file)

        response_data = {
            'success': True,
            'video_data': encoded_data,
            'filename': download_name,
            'file_size': len(video_data)
        }

        print(f"Sending response with file_size: {len(video_data)}")
        return jsonify(response_data)

    except Exception as e:
        print(f"Download error: {e}")
        # Clean up file if there was an error
        if downloaded_file:
            try:
                downloader = get_downloader()
                downloader.safe_file_cleanup(downloaded_file)
            except:
                pass
        return jsonify({'error': str(e)}), 500

# Replace your existing routes with:
@app.route('/extract', methods=['POST', 'OPTIONS'])
def handle_extract_video():
    return extract_video()

@app.route('/download-with-audio', methods=['POST', 'OPTIONS'])
def handle_download_with_audio():
    return download_with_audio()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with disk space info"""
    try:
        downloader = get_downloader()
        stat = shutil.disk_usage(downloader.temp_dir)
        free_mb = stat.free / (1024 * 1024)

        return jsonify({
            'status': 'healthy',
            'service': 'twitter-video-downloader',
            'temp_dir': downloader.temp_dir,
            'free_space_mb': round(free_mb, 1)
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/test-download', methods=['POST', 'OPTIONS'])
@cross_origin()
def test_download():
    """Test endpoint to verify base64 encoding/decoding works correctly"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        # Create a simple test file with known content
        test_content = b'This is a test video file content for debugging purposes. ' * 1000

        # Encode to base64
        import base64
        encoded_data = base64.b64encode(test_content).decode('utf-8')

        print(f"Test file size: {len(test_content)}")
        print(f"Test base64 length: {len(encoded_data)}")

        return jsonify({
            'success': True,
            'video_data': encoded_data,
            'filename': 'test_file.txt',
            'file_size': len(test_content)
        })

    except Exception as e:
        print(f"Test download error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    print("=== Twitter Video Downloader Server ===")
    print(f"Platform: {platform.system()} {platform.release()}")

    # Check current configuration
    temp_dir = os.environ.get('TWITTER_DOWNLOADER_TEMP_DIR')
    if not temp_dir:
        if platform.system() == 'Windows':
            temp_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Temp', 'TwitterDownloader')
        else:
            temp_dir = os.path.join(os.path.expanduser('~'), '.twitter_downloader_temp')

    print(f"Configured temp directory: {temp_dir}")

    # Initialize downloader to check disk space
    try:
        downloader = get_downloader()
        print(f"Actual temp directory: {downloader.temp_dir}")
    except Exception as e:
        print(f"Warning: Could not initialize downloader: {e}")

    app.run(host="0.0.0.0", port=6000)