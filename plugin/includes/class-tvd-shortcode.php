<?php
/**
 * Shortcode Handler Class
 */
class TVD_Shortcode {
    
    public function __construct() {
        add_shortcode('twitter_video_downloader', array($this, 'render_shortcode'));
        add_shortcode('tvd', array($this, 'render_shortcode')); // Short alias
		
    }
    
    /**
     * Render the shortcode
     */
    public function render_shortcode($atts) {
        $atts = shortcode_atts(array(
            'title' => 'Twitter Video Downloader',
            'subtitle' => 'Download Twitter videos & GIFs from tweets',
            'show_instructions' => 'true',
            'width' => '600px'
        ), $atts);
        
        ob_start();

        ?>
        <div class="tvd-container" style="max-width: <?php echo esc_attr($atts['width']); ?>; margin: 0 auto;">
            <div class="tvd-input-group">
                <input
                    type="text"
                    class="tvd-url-input"
                    id="tvd-twitter-url"
                    placeholder="Paste Twitter video URL here..."
                />
                <button class="tvd-paste-btn" onclick="tvdPasteFromClipboard()">Paste</button>
            </div>

            <button class="tvd-download-btn" id="tvd-download-btn" onclick="tvdExtractVideo()">
                Download
            </button>

            <div class="tvd-loading" id="tvd-loading">
                <div class="tvd-spinner"></div>
                <p>Extracting video information...</p>
            </div>

            <div id="tvd-message"></div>

            <div class="tvd-video-info" id="tvd-video-info">
                <div class="tvd-video-title" id="tvd-video-title"></div>
                <div class="tvd-video-meta" id="tvd-video-meta"></div>
                <div class="tvd-formats-grid" id="tvd-formats-grid"></div>
            </div>

            <?php if ($atts['show_instructions'] === 'true'): ?>
            <?php endif; ?>
        </div>
        <?php
        return ob_get_clean();
    }
}