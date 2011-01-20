;(function($){
    $.fn.confirmedPost = function(options) {
        var opts = $.extend({}, $.fn.confirmedPost.defaults, options);

        return this.each(function() {
            var self = $(this);
            var wrap = opts.createWrap.call(this);
            var button = opts.createButton()
                .text(opts.buttonText)
                .addClass(opts.buttonClass)
                .appendTo(wrap);
            var confirmation = opts.createConfirmation()
                .text(opts.confirmationText)
                .addClass(opts.confirmationClass)
                .appendTo(wrap)
                .hide()
            var yes = opts.createYes()
                .text(opts.yesText)
                .appendTo(wrap)
                .addClass(opts.yesNoClass)
                .hide()
            var no = opts.createNo()
                .text(opts.noText)
                .appendTo(wrap)
                .addClass(opts.yesNoClass)
                .hide()

            button.click(function() {
                button.hide();
                confirmation.show();
                yes.show();
                no.show();
            });

            no.click(function() {
                confirmation.hide();
                yes.hide();
                no.hide();
                button.show();
            });

            yes.click(function() {
                self.addClass('loading');
                confirmation.hide();
                yes.hide();
                no.hide();
                $.post(opts.url, opts.getData.call(self), function(response) {
                    opts.onComplete.call(self, response);
                }, opts.responseFormat);
            });

        });
    }
    $.fn.confirmedPost.defaults = {
        url: '',
        getData: function() {},
        onComplete: function(response) {},
        responseFormat: 'text',
        buttonText: '',
        confirmationText: 'Are you sure?',
        yesText: 'yes',
        noText: 'no',
        createWrap: function() {
            return $('<span/>', {class: 'confirmed-post-wrap'}).insertAfter(this);
        },
        createButton: function() {
            return $('<span/>', {class: 'confirmed-post-button'});
        },
        createConfirmation: function() {
            return $('<span/>', {class: 'confirmed-post-confirmation'});
        },
        createYes: function() {
            return $('<span/>', {class: 'confirmed-post-yes'});
        },
        createNo: function() {
            return $('<span/>', {class: 'confirmed-post-no'});
        },
        wrapClass: '',
        buttonClass: '',
        yesNoClass: ''
    }
})(jQuery);
