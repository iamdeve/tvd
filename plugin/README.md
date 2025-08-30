# Twitter Video Downloader WordPress Plugin

A beautiful and functional WordPress plugin that allows users to download Twitter videos and GIFs directly from your website. The plugin integrates seamlessly with your existing Twitter video download API running at `http://localhost:4000`.

## Features

- 🎨 **Beautiful UI**: Modern, responsive design that matches your website's theme
- 📱 **Mobile Friendly**: Works perfectly on all devices
- 🔧 **Flexible Integration**: Use as shortcode, widget, or embed anywhere
- ⚡ **Fast Performance**: Optimized AJAX requests for smooth user experience
- 🛡️ **Secure**: WordPress nonce verification and input sanitization
- 🎯 **Customizable**: Easy to customize appearance and functionality

## Installation

1. Upload the `twitter-video-downloader-wp` folder to your `/wp-content/plugins/` directory
2. Activate the plugin through the 'Plugins' menu in WordPress
3. Configure the plugin settings in Settings > Twitter Video Downloader
4. Make sure your API server is running at `http://localhost:4000`

## Usage

### Shortcode

Use the shortcode in any post or page:

```
[twitter_video_downloader]
```

Or use the shorter version:

```
[tvd]
```

#### Shortcode Parameters

- `title` - Custom title (default: "Twitter Video Downloader")
- `subtitle` - Custom subtitle
- `show_instructions` - Show/hide instructions (true/false)
- `width` - Container width (e.g., "600px", "100%")

#### Examples

```
[tvd title="My Video Downloader" width="800px"]
[tvd show_instructions="false"]
[tvd title="Download Videos" subtitle="Get your favorite Twitter videos" width="100%"]
```

### Widget

1. Go to Appearance > Widgets
2. Add the "Twitter Video Downloader" widget to your sidebar
3. Configure the widget settings as needed

### Direct PHP Integration

You can also use the shortcode directly in your theme files:

```php
<?php echo do_shortcode('[tvd]'); ?>
```

## Configuration

### Admin Settings

Navigate to **Settings > Twitter Video Downloader** to configure:

- **API Base URL**: Set your video download API endpoint (default: `http://localhost:4000/api`)
- **Enable Shortcode**: Toggle shortcode functionality
- **Enable Widget**: Toggle widget functionality

### API Requirements

Your API server should provide these endpoints:

- `POST /api/extract` - Extract video information
- `POST /api/download-with-audio` - Download video with audio

## File Structure

```
twitter-video-downloader-wp/
├── twitter-video-downloader.php      # Main plugin file
├── README.md                         # This file
├── includes/
│   ├── class-twitter-video-downloader.php  # Main plugin class
│   ├── class-tvd-shortcode.php             # Shortcode handler
│   ├── class-tvd-admin.php                 # Admin settings
│   └── class-tvd-widget.php                # Widget class
└── assets/
    ├── css/
    │   └── twitter-video-downloader.css    # Styles
    └── js/
        └── twitter-video-downloader.js     # JavaScript
```

## Customization

### Styling

The plugin uses CSS classes prefixed with `tvd-` to avoid conflicts. You can customize the appearance by overriding these classes in your theme's CSS:

```css
.tvd-container {
    /* Your custom styles */
}

.tvd-download-btn {
    /* Custom button styles */
}
```

### JavaScript

The plugin uses jQuery and provides global functions for customization:

- `tvdExtractVideo()` - Extract video information
- `tvdDownloadVideo(url, quality, videoNumber)` - Download video
- `tvdPasteFromClipboard()` - Paste from clipboard

## API Integration

The plugin expects your API to return data in this format:

```json
{
  "tweet_info": {
    "title": "Tweet Title",
    "uploader": "Username"
  },
  "videos": [
    {
      "thumbnail": "thumbnail_url",
      "duration": 30.5,
      "video_formats": [
        {
          "quality": "720p",
          "format": "mp4",
          "width": 1280,
          "height": 720,
          "filesize": "5.2 MB"
        }
      ]
    }
  ]
}
```

## Troubleshooting

### Common Issues

1. **Plugin not working**: Check if your API server is running at the configured URL
2. **AJAX errors**: Verify WordPress AJAX is working and nonces are valid
3. **Styling conflicts**: Check for CSS conflicts with your theme
4. **Download issues**: Ensure your API returns proper video data

### Debug Mode

Enable WordPress debug mode to see detailed error messages:

```php
// In wp-config.php
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
```

## Support

For support and feature requests, please check:

1. WordPress plugin documentation
2. Your API server logs
3. Browser developer console for JavaScript errors

## Changelog

### Version 1.0.0
- Initial release
- Shortcode support
- Widget integration
- Admin settings page
- AJAX video extraction and download
- Responsive design
- Security features

## License

This plugin is licensed under the GPL v2 or later.

## Credits

- Built for WordPress
- Integrates with Twitter Video Download API
- Modern UI/UX design 