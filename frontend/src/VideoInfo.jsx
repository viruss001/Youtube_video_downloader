import React from 'react';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';

function VideoInfo({ videoInfo }) {
  const handleDownload = (formatUrl) => {
    window.open(formatUrl, '_blank');
  };

  return (
    <div className="mt-8 border-t pt-6">
      <div className="flex flex-col md:flex-row gap-6">
        <div className="md:w-1/3">
          <img
            src={videoInfo.thumbnail}
            alt={videoInfo.title}
            className="w-full rounded-lg shadow-md"
          />
        </div>
        
        <div className="md:w-2/3">
          <h2 className="text-xl font-bold text-gray-900 mb-2">{videoInfo.title}</h2>
          <div className="flex items-center gap-2 mb-4">
            <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs font-medium rounded">
              {Math.floor(videoInfo.duration / 60)}:{String(videoInfo.duration % 60).padStart(2, '0')}
            </span>
          </div>

          <h3 className="text-lg font-medium text-gray-900 mb-3">Available Formats:</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {videoInfo.formats.map((format) => (
              <button
                key={format.format_id}
                onClick={() => handleDownload(format.url)}
                className="flex items-center justify-between px-4 py-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition"
              >
                <div>
                  <span className="block font-medium text-gray-900">{format.resolution || 'Audio'}</span>
                  <span className="block text-xs text-gray-500">{format.ext.toUpperCase()} • {format.filesize ? `${Math.round(format.filesize / (1024 * 1024))}MB` : 'Size unknown'}</span>
                </div>
                <ArrowDownTrayIcon className="h-5 w-5 text-red-600" />
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default VideoInfo;