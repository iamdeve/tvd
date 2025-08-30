<?php
/**
 * Main Twitter Video Downloader Class
 */
class Twitter_Video_Downloader {
    
    public function __construct() {
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        add_action('wp_ajax_tvd_extract_video', array($this, 'ajax_extract_video'));
        add_action('wp_ajax_nopriv_tvd_extract_video', array($this, 'ajax_extract_video'));
        add_action('wp_ajax_tvd_download_video', array($this, 'ajax_download_video'));
        add_action('wp_ajax_nopriv_tvd_download_video', array($this, 'ajax_download_video'));
    }
    
    /**
     * Enqueue scripts and styles
     */
    public function enqueue_scripts() {
        wp_enqueue_style(
            'tvd-styles',
            TVD_PLUGIN_URL . 'assets/css/twitter-video-downloader.css',
            array(),
            TVD_PLUGIN_VERSION
        );
        
        wp_enqueue_script(
            'tvd-script',
            TVD_PLUGIN_URL . 'assets/js/twitter-video-downloader.js',
            array('jquery'),
            TVD_PLUGIN_VERSION,
            true
        );
        
        // Localize script for AJAX
        wp_localize_script('tvd-script', 'tvd_ajax', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('tvd_nonce'),
            'api_base_url' => get_option('tvd_api_base_url', TVD_API_BASE_URL)
        ));
    }
    
    /**
     * AJAX handler for video extraction
     */
    public function ajax_extract_video() {
        check_ajax_referer('tvd_nonce', 'nonce');
        
        $url = sanitize_text_field($_POST['url']);
        
        if (empty($url)) {
            wp_send_json_error('Please enter a Twitter URL');
        }
        
        if (!strpos($url, 'twitter.com') && !strpos($url, 'x.com')) {
            wp_send_json_error('Please enter a valid Twitter URL');
        }
        
        // Forward request to your API
        $api_url = get_option('tvd_api_base_url', TVD_API_BASE_URL) . '/extract';
        
        $response = wp_remote_post($api_url, array(
            'headers' => array(
                'Content-Type' => 'application/json',
            ),
            'body' => json_encode(array('url' => $url)),
            'timeout' => 30
        ));
        
        if (is_wp_error($response)) {
            wp_send_json_error('Failed to connect to video service');
        }
        
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        
        if (wp_remote_retrieve_response_code($response) !== 200) {
            wp_send_json_error($data['error'] ?? 'Failed to extract video');
        }
        
        wp_send_json_success($data);
    }
    
/**
 * AJAX handler for video download - FIXED VERSION
 */
public function ajax_download_video() {
    check_ajax_referer('tvd_nonce', 'nonce');
    
    $url = sanitize_text_field($_POST['url']);
    $quality = sanitize_text_field($_POST['quality']);
    $video_number = intval($_POST['video_number']);
    
    if (empty($url)) {
        wp_send_json_error('Invalid request');
    }
    
    // Forward request to your API
    $api_url = get_option('tvd_api_base_url', TVD_API_BASE_URL) . '/download-with-audio';
    error_log('API URL: ' . $api_url);
    $response = wp_remote_post($api_url, array(
        'headers' => array(
            'Content-Type' => 'application/json',
        ),
        'body' => json_encode(array(
            'url' => $url,
            'quality' => $quality,
            'video_number' => $video_number
        )),
        'timeout' => 300
    ));
    
    if (is_wp_error($response)) {
        error_log('WP Error: ' . $response->get_error_message());
        wp_send_json_error('Failed to connect to download service');
    }
    
    $response_code = wp_remote_retrieve_response_code($response);
    $body = wp_remote_retrieve_body($response);
    
    // Log for debugging
    error_log('API Response Code: ' . $response_code);
    error_log('API Response Body Length: ' . strlen($body));
    
    if ($response_code !== 200) {
        $data = json_decode($body, true);
        $error_message = isset($data['error']) ? $data['error'] : 'Download failed';
        error_log('API Error: ' . $error_message);
        wp_send_json_error($error_message);
    }
    
    // Decode the JSON response from your Python API
    $data = json_decode($body, true);
    
    if (!$data || !isset($data['success']) || !$data['success']) {
        error_log('Invalid API response structure');
        wp_send_json_error('Invalid response from download service');
    }
    
    if (!isset($data['video_data']) || empty($data['video_data'])) {
        error_log('No video data in response');
        wp_send_json_error('No video data received');
    }
    
    // The video_data is already base64-encoded by your Python script
    // DO NOT encode it again!
    wp_send_json_success(array(
        'video_data' => $data['video_data'],  // ← Use directly, no double encoding!
        'filename' => $data['filename'] ?? ('twitter_video_' . $quality . '.mp4'),
        'file_size' => isset($data['file_size']) ? $data['file_size'] : null
    ));
}
} 