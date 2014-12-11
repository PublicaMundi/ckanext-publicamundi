(function () {

    var debug = $.proxy(window.console, 'debug')
    var warn = $.proxy(window.console, 'warn')
    
    var render = Mustache.render

    this.ckan.module('table-collapsible-rows', function ($, _) {

        return {
            options: {
                numcols: null,
                i18n: {
                    show: _('Show more'),
                    hide: _('Hide'),
                },
            },

            templates: {
                togglerow: 
                    '<tr class="toggle-show toggle-show-more">' +
                      '<td colspan="{{numcols}}"><small>' +
                        '<a href="#" class="show-more">{{showText}}</a>' +
                        '<a href="#" class="show-less">{{hideText}}</a>' +
                      '</small></td>' +
                    '</tr>',
                separator: 
                    '<tr class="toggle-separator"><td colspan="{{numcols}}"></td></tr>',
            },

            initialize: function () 
            {
                var module = this,
                    $el = this.el,
                    opts = this.options,
                    templates = this.templates;

                var numcols = parseInt(opts.numcols || $el.find('colgroup col').length),
                    $separator = $(render(templates.separator, { 
                        numcols: numcols 
                    })),
                    $togglerow = $(render(templates.togglerow, { 
                        numcols: numcols,
                        showText: this.i18n('show'),
                        hideText: this.i18n('hide'),
                    }));
                
                $el.addClass(
                    opts.state == 'more' ? 
                        ('table-toggle-more') : ('table-toggle-less'));
                
                $separator.insertAfter($el.find('tbody > tr:last-child'));
                $togglerow.insertAfter($separator);

                $togglerow.find('a.show-more').on('click', function (ev) {
                    $el.addClass('table-toggle-less')
                    $el.removeClass('table-toggle-more')
                    return false;
                });

                $togglerow.find('a.show-less').on('click', function (ev) {
                    $el.addClass('table-toggle-more')
                    $el.removeClass('table-toggle-less')
                    return false;
                });

                debug('Initialized module: table-collapsible-rows, opts=', opts);
            },

            teardown: function () 
            { 
                debug('Tearing down module: table-collapsible-rows');
            },
        };
    });

}).apply(this);
