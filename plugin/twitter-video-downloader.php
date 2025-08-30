<?php
/**
 * Plugin Name: Twitter Video Downloader
 * Plugin URI: http://localhost:4000
 * Description: A WordPress plugin to download Twitter videos and GIFs from tweets with a beautiful interface.
 * Version: 1.0.0
 * Author: Your Name
 * License: GPL v2 or later
 * Text Domain: twitter-video-downloader
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('TVD_PLUGIN_URL', plugin_dir_url(__FILE__));
define('TVD_PLUGIN_PATH', plugin_dir_path(__FILE__));
define('TVD_PLUGIN_VERSION', '1.0.0');
define('TVD_API_BASE_URL', 'http://52.71.21.240/yt-api');
// define('TVD_API_BASE_URL', 'http://127.0.0.1:4000');
// update_option('tvd_api_base_url', TVD_API_BASE_URL);

// Include required files
require_once TVD_PLUGIN_PATH . 'includes/class-twitter-video-downloader.php';
require_once TVD_PLUGIN_PATH . 'includes/class-tvd-shortcode.php';
require_once TVD_PLUGIN_PATH . 'includes/class-tvd-admin.php';
require_once TVD_PLUGIN_PATH . 'includes/class-tvd-widget.php';

// Initialize the plugin
function tvd_init() {
    try {
        new Twitter_Video_Downloader();
        new TVD_Shortcode();
        new TVD_Admin();
    } catch (Exception $e) {
        // Log error for debugging
        error_log('Twitter Video Downloader Plugin Error: ' . $e->getMessage());
    }
}
add_action('plugins_loaded', 'tvd_init');

// Activation hook
register_activation_hook(__FILE__, 'tvd_activate');
function tvd_activate() {
    try {
        // Add default options
        add_option('tvd_api_base_url', TVD_API_BASE_URL);
        add_option('tvd_enable_shortcode', true);
        add_option('tvd_enable_widget', true);
    } catch (Exception $e) {
        // Log activation error
        error_log('Twitter Video Downloader Activation Error: ' . $e->getMessage());
        wp_die('Plugin activation failed: ' . $e->getMessage());
    }
}

// Deactivation hook
register_deactivation_hook(__FILE__, 'tvd_deactivate');
function tvd_deactivate() {
    // Clean up if needed
} 