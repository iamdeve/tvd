/**
 * Twitter Video Downloader JavaScript
 */
(function($) {
    'use strict';

    // Global variables
    let currentTwitterUrl = '';

    /**
     * Show message to user
     */
    function showMessage(message, type = 'error') {
        const messageDiv = $('#tvd-message');
        messageDiv.html(`<div class="tvd-${type}">${message}</div>`);
        setTimeout(() => {
            messageDiv.html('');
        }, 5000);
    }

    /**
     * Show/hide loading state
     */
    function showLoading(show) {
        $('#tvd-loading').toggle(show);
        $('#tvd-download-btn').prop('disabled', show);
    }

    /**
     * Paste from clipboard
     */
    window.tvdPasteFromClipboard = async function() {
        try {
            const text = await navigator.clipboard.readText();
            $('#tvd-twitter-url').val(text);
        } catch (err) {
            showMessage('Could not access clipboard. Please paste manually.');
        }
    };

    /**
     * Extract video information
     */
    window.tvdExtractVideo = function() {
        const url = $('#tvd-twitter-url').val().trim();

        if (!url) {
            showMessage('Please enter a Twitter URL');
            return;
        }

        if (!url.includes('twitter.com') && !url.includes('x.com')) {
            showMessage('Please enter a valid Twitter URL');
            return;
        }

        currentTwitterUrl = url;
        showLoading(true);
        $('#tvd-video-info').hide();
        $.ajax({
            url: tvd_ajax.ajax_url,
            type: 'POST',
            data: {
                action: 'tvd_extract_video',
                nonce: tvd_ajax.nonce,
                url: url
            },
            success: function(response) {
                if (response.success) {
                    displayVideoInfo(response.data, url);
                    showMessage('Video information extracted successfully!', 'success');
                } else {
                    console.log(response)
                    showMessage(response.data || 'Failed to extract video');
                }
            },
            error: function() {
                showMessage('Failed to connect to server');
            },
            complete: function() {
                showLoading(false);
            }
        });
    };

    /**
     * Display video information
     */
    function displayVideoInfo(data, originalUrl) {
        // Set tweet info
        $('#tvd-video-title').text(data.tweet_info?.title || 'Unknown');

        let metaText = '';
        if (data.tweet_info?.uploader) {
            metaText += `By: ${data.tweet_info.uploader} • `;
        }
        if (data.videos?.[0]?.duration) {
            metaText += `Duration: ${Math.floor(data.videos[0].duration)}s`;
        }
        $('#tvd-video-meta').text(metaText);

        const formatsGrid = $('#tvd-formats-grid');
        formatsGrid.empty();

        // Check if there are videos
        if (data.videos && data.videos.length > 0) {
            data.videos.forEach((video, index) => {
                console.log(video);

                // Display all available formats
                video.video_formats.forEach((format) => {
                    const formatCard = $('<div>').addClass('tvd-format-card');

                    // Create a more descriptive quality label
                    let qualityLabel = format.quality;
                    if (format.width && format.height) {
                        qualityLabel = `${format.height}p (${format.width}x${format.height})`;
                    }

                    formatCard.html(`
                        <img src="${video.thumbnail}" width="100px" alt="Thumbnail" />
                        <div class="tvd-format-quality">${qualityLabel}</div>
                        ${format.format ?  `<div class="tvd-format-type">${format.format}</div>` : ''}
                        ${format.filesize ? `<div class="tvd-format-size">${format.filesize}</div>` : ''}
                        <div class="tvd-download-icon">⬇️</div>
                    `);

                    formatCard.on('click', () => {
                        tvdDownloadVideo(originalUrl, qualityLabel, index + 1);
                    });
                    
                    formatsGrid.append(formatCard);
                });
            });
        } else {
            formatsGrid.html('<div class="no-formats">No video formats available</div>');
        }

        $('#tvd-video-info').show();
    }

    window.tvdDownloadVideo = function(twitterUrl, quality, videoNumber) {
        try {
            showMessage('Starting download...', 'success');
    
            $.ajax({
                url: tvd_ajax.ajax_url,
                type: 'POST',
                data: {
                    action: 'tvd_download_video',
                    nonce: tvd_ajax.nonce,
                    url: twitterUrl,
                    quality: quality.split(' ')[0],
                    video_number: videoNumber
                },
                success: function(response) {
                    console.log('Response received:', response); // Debug log
                    
                    if (response.success) {
                        try {
                            // Decode base64 data properly
                            const videoData = atob(response.data.video_data);
                            console.log('Decoded data length:', videoData.length); // Debug log
                            
                            // Convert string to Uint8Array for proper blob creation
                            const bytes = new Uint8Array(videoData.length);
                            for (let i = 0; i < videoData.length; i++) {
                                bytes[i] = videoData.charCodeAt(i);
                            }
                            
                            // Create blob with proper type
                            const blob = new Blob([bytes], { type: 'video/mp4' });
                            console.log('Blob created, size:', blob.size); // Debug log
                            
                            // Check if blob has content
                            if (blob.size === 0) {
                                showMessage('Error: Downloaded file is empty', 'error');
                                return;
                            }
                            
                            // Create download link
                            const url = window.URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = response.data.filename;
                            a.style.display = 'none';
                            
                            document.body.appendChild(a);
                            a.click();
                            
                            // Clean up
                            setTimeout(() => {
                                window.URL.revokeObjectURL(url);
                                document.body.removeChild(a);
                            }, 100);
    
                            showMessage('Download completed successfully!', 'success');
                        } catch (decodeError) {
                            console.error('Decode error:', decodeError);
                            showMessage('Error processing download data: ' + decodeError.message, 'error');
                        }
                    } else {
                        showMessage(response.data || 'Download failed', 'error');
                    }
                },
                error: function(xhr, status, error) {
                    console.error('AJAX error:', status, error);
                    showMessage('Failed to connect to download service: ' + error, 'error');
                }
            });
        } catch (error) {
            console.error('Download function error:', error);
            showMessage('Error: ' + error.message, 'error');
        }
    };

    /**
     * Initialize when document is ready
     */
    $(document).ready(function() {
        // Allow Enter key to trigger download
        $(document).on('keypress', '#tvd-twitter-url', function(e) {
            if (e.key === 'Enter') {
                tvdExtractVideo();
            }
        });

        // Handle multiple instances on the same page
        $(document).on('click', '.tvd-download-btn', function() {
            tvdExtractVideo();
        });

        $(document).on('click', '.tvd-paste-btn', function() {
            tvdPasteFromClipboard();
        });
    });

})(jQuery); 