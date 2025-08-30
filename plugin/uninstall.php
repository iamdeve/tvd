<?php
/**
 * Uninstall Twitter Video Downloader Plugin
 * 
 * This file is executed when the plugin is uninstalled.
 */

// If uninstall not called from WordPress, exit
if (!defined('WP_UNINSTALL_PLUGIN')) {
    exit;
}

// Delete plugin options
delete_option('tvd_api_base_url');
delete_option('tvd_enable_shortcode');
delete_option('tvd_enable_widget');

// Clean up any other plugin data if needed
// Note: This is a simple plugin, so we only need to remove options 