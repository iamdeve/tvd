<?php
/**
 * Widget Class
 */
class TVD_Widget extends WP_Widget {
    
    public function __construct() {
        parent::__construct(
            'tvd_widget',
            'Twitter Video Downloader',
            array('description' => 'Add Twitter Video Downloader to your sidebar')
        );
    }
    
    /**
     * Widget display
     */
    public function widget($args, $instance) {
        echo $args['before_widget'];
        
        if (!empty($instance['title'])) {
            echo $args['before_title'] . apply_filters('widget_title', $instance['title']) . $args['after_title'];
        }
        
        // Render the downloader using the shortcode function directly
        echo do_shortcode('[tvd title="' . esc_attr($instance['widget_title'] ?? 'Twitter Video Downloader') . '" subtitle="' . esc_attr($instance['widget_subtitle'] ?? 'Download Twitter videos') . '" show_instructions="false" width="100%"]');
        
        echo $args['after_widget'];
    }
    
    /**
     * Widget form
     */
    public function form($instance) {
        $title = !empty($instance['title']) ? $instance['title'] : '';
        $widget_title = !empty($instance['widget_title']) ? $instance['widget_title'] : 'Twitter Video Downloader';
        $widget_subtitle = !empty($instance['widget_subtitle']) ? $instance['widget_subtitle'] : 'Download Twitter videos';
        ?>
        <p>
            <label for="<?php echo $this->get_field_id('title'); ?>">Widget Title:</label>
            <input class="widefat" id="<?php echo $this->get_field_id('title'); ?>" name="<?php echo $this->get_field_name('title'); ?>" type="text" value="<?php echo esc_attr($title); ?>">
        </p>
        <p>
            <label for="<?php echo $this->get_field_id('widget_title'); ?>">Downloader Title:</label>
            <input class="widefat" id="<?php echo $this->get_field_id('widget_title'); ?>" name="<?php echo $this->get_field_name('widget_title'); ?>" type="text" value="<?php echo esc_attr($widget_title); ?>">
        </p>
        <p>
            <label for="<?php echo $this->get_field_id('widget_subtitle'); ?>">Downloader Subtitle:</label>
            <input class="widefat" id="<?php echo $this->get_field_id('widget_subtitle'); ?>" name="<?php echo $this->get_field_name('widget_subtitle'); ?>" type="text" value="<?php echo esc_attr($widget_subtitle); ?>">
        </p>
        <?php
    }
    
    /**
     * Widget update
     */
    public function update($new_instance, $old_instance) {
        $instance = array();
        $instance['title'] = (!empty($new_instance['title'])) ? strip_tags($new_instance['title']) : '';
        $instance['widget_title'] = (!empty($new_instance['widget_title'])) ? strip_tags($new_instance['widget_title']) : '';
        $instance['widget_subtitle'] = (!empty($new_instance['widget_subtitle'])) ? strip_tags($new_instance['widget_subtitle']) : '';
        return $instance;
    }
}

// Register widget
function tvd_register_widget() {
    if (get_option('tvd_enable_widget', true)) {
        register_widget('TVD_Widget');
    }
}
add_action('widgets_init', 'tvd_register_widget'); 