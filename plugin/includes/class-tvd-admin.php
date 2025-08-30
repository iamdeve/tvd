<?php
/**
 * Admin Settings Class
 */
class TVD_Admin {
    
    public function __construct() {
        add_action('admin_menu', array($this, 'add_admin_menu'));
        add_action('admin_init', array($this, 'register_settings'));
    }
    
    /**
     * Add admin menu
     */
    public function add_admin_menu() {
        add_options_page(
            'Twitter Video Downloader Settings',
            'Twitter Video Downloader',
            'manage_options',
            'twitter-video-downloader',
            array($this, 'admin_page')
        );
    }
    
    /**
     * Register settings
     */
    public function register_settings() {
        register_setting('tvd_options', 'tvd_api_base_url');
        register_setting('tvd_options', 'tvd_enable_shortcode');
        register_setting('tvd_options', 'tvd_enable_widget');
        
        add_settings_section(
            'tvd_general_section',
            'General Settings',
            array($this, 'section_callback'),
            'twitter-video-downloader'
        );
        
        add_settings_field(
            'tvd_api_base_url',
            'API Base URL',
            array($this, 'api_url_callback'),
            'twitter-video-downloader',
            'tvd_general_section'
        );
        
        add_settings_field(
            'tvd_enable_shortcode',
            'Enable Shortcode',
            array($this, 'enable_shortcode_callback'),
            'twitter-video-downloader',
            'tvd_general_section'
        );
        
        add_settings_field(
            'tvd_enable_widget',
            'Enable Widget',
            array($this, 'enable_widget_callback'),
            'twitter-video-downloader',
            'tvd_general_section'
        );
    }
    
    /**
     * Section callback
     */
    public function section_callback() {
        echo '<p>Configure your Twitter Video Downloader settings below.</p>';
    }
    
    /**
     * API URL field callback
     */
    public function api_url_callback() {
        $value = get_option('tvd_api_base_url', TVD_API_BASE_URL);
        echo '<input type="url" name="tvd_api_base_url" value="' . esc_attr($value) . '" class="regular-text" />';
        echo '<p class="description">The base URL for your video download API (e.g., http://52.71.21.240/yt-api)</p>';
    }
    
    /**
     * Enable shortcode callback
     */
    public function enable_shortcode_callback() {
        $value = get_option('tvd_enable_shortcode', true);
        echo '<input type="checkbox" name="tvd_enable_shortcode" value="1" ' . checked(1, $value, false) . ' />';
        echo '<span class="description">Enable shortcode [twitter_video_downloader] or [tvd]</span>';
    }
    
    /**
     * Enable widget callback
     */
    public function enable_widget_callback() {
        $value = get_option('tvd_enable_widget', true);
        echo '<input type="checkbox" name="tvd_enable_widget" value="1" ' . checked(1, $value, false) . ' />';
        echo '<span class="description">Enable widget for sidebar</span>';
    }
    
    /**
     * Admin page
     */
    public function admin_page() {
        ?>
        <div class="wrap">
            <h1>Twitter Video Downloader Settings</h1>
            
            <form method="post" action="options.php">
                <?php
                settings_fields('tvd_options');
                do_settings_sections('twitter-video-downloader');
                submit_button();
                ?>
            </form>
            
            <div class="tvd-admin-info">
                <h2>Usage</h2>
                <h3>Shortcode</h3>
                <p>Use the shortcode <code>[twitter_video_downloader]</code> or <code>[tvd]</code> in your posts or pages.</p>
                
                <h4>Shortcode Parameters:</h4>
                <ul>
                    <li><code>title</code> - Custom title (default: "Twitter Video Downloader")</li>
                    <li><code>subtitle</code> - Custom subtitle</li>
                    <li><code>show_instructions</code> - Show/hide instructions (true/false)</li>
                    <li><code>width</code> - Container width (e.g., "600px", "100%")</li>
                </ul>
                
                <h4>Examples:</h4>
                <pre>[tvd title="My Video Downloader" width="800px"]
[tvd show_instructions="false"]</pre>
                
                <h3>Widget</h3>
                <p>Go to Appearance > Widgets to add the Twitter Video Downloader widget to your sidebar.</p>
            </div>
        </div>
        <?php
    }
} 