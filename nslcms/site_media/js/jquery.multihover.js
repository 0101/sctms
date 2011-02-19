;(function($){
    $.fn.multiHover = function(options) {
        var opts = $.extend({}, $.fn.multiHover.defaults, options);

        var items = this;

        function init() {
            items.hover(
                function() { opts.onEnter.call(this, items); },
                function() { opts.onLeave.call(this, items); }
            );
            items.click(
                function() { return opts.onClick.call(this, items); }
            );
        }

        items.bind('attach', function(event, newItems) {
            items = items.add(newItems);
            init();
        });

        init();

        return items;
    }
    $.fn.multiHover.defaults = {
        onEnter: function(items) { items.addClass('hover'); },
        onLeave: function(items) { items.removeClass('hover'); },
        onClick: function(items) { return true; }
    }
    $.multiHover = {
        auto: function() {
            var hrefs = {};
            var links = $('a');

            links.each(function() {
                var link = $(this);
                var href = link.attr('href');
                if (href in hrefs) {
                    hrefs[href].trigger('attach', [link]);
                } else {
                    link.multiHover();
                    hrefs[href] = link;
                }
            });
        }
    }
})(jQuery);
