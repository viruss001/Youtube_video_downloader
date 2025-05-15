# downloader/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
import yt_dlp
import logging
import os
import uuid

logger = logging.getLogger(__name__)

@api_view(['POST'])
def get_video_info(request):
    url = request.data.get('url')
    if not url:
        return Response({'error': 'URL is required'}, status=status.HTTP_400_BAD_REQUEST)

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if 'entries' in info:
                return Response({'error': 'Playlists are not supported'}, status=status.HTTP_400_BAD_REQUEST)

            formats = []
            for f in info.get('formats', []):
                # Only include combined (muxed) formats with both audio and video
                if f.get('url') and f.get('acodec') != 'none' and f.get('vcodec') != 'none':
                    resolution = f.get('resolution') or (f"{f.get('height', 'audio')}p" if f.get('height') else 'audio')
                    formats.append({
                        'format_id': f['format_id'],
                        'ext': f['ext'],
                        'resolution': resolution,
                        'filesize': f.get('filesize') or f.get('filesize_approx'),
                        'url': f['url']
                    })

            formats.sort(key=lambda x: x.get('filesize') or 0, reverse=True)

            return Response({
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'formats': formats,
                'duration': info.get('duration'),
            })

    except Exception as e:
        logger.error(f"Failed to extract video info: {e}")
        return Response({'error': 'Failed to extract video info'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def download_and_merge(request):
    url = request.data.get('url')
    if not url:
        return Response({'error': 'URL is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Use a unique filename to avoid conflicts
    filename_base = f"/tmp/{uuid.uuid4()}"
    output_path = f"{filename_base}.%(ext)s"

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': output_path,
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_path = ydl.prepare_filename(info).replace('.webm', '.mp4').replace('.mkv', '.mp4')

        if not os.path.exists(downloaded_path):
            return Response({'error': 'File not found after download'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response = FileResponse(open(downloaded_path, 'rb'), as_attachment=True, filename=info.get('title', 'video') + '.mp4')

        # Optional cleanup
        def cleanup_file(path):
            try:
                os.remove(path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {e}")

        request._request._cleanup_file = lambda: cleanup_file(downloaded_path)

        return response

    except Exception as e:
        logger.error(f"Download error: {e}")
        return Response({'error': 'Download failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
