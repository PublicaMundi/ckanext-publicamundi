/*
 * Provide support for select2-based inputs.
 * This module only acts as a (simplified) wrapper to select2
 * functionality.
 */
this.ckan.module('input-select2', function ($, _) {
  return {
    options: {
        width: 'element',
        placeholder: null,
        minimuminputlength: null,
        maximuminputlength: null,
        minimumresultsforsearch: -1,
        tags: null,
        separator: null,
    },
    
    initialize: function() 
    {
        var module = this
        if ($.fn.select2) {
            
            // Prepare init options for a select2 widget
            
            var opts = $.extend({}, {
                placeholder: module.options.placeholder,
                width: module.options.width, 
            })

            if (module.options.minimumresultsforsearch != null) {
                opts.minimumResultsForSearch = Number(module.options.minimumresultsforsearch) 
            } 
            
            if (module.options.tags != null) {
                var t = typeof(module.options.tags) 
                if (t == 'boolean') {
                    opts.tags = module.options.tags
                } else if (t == 'string') {
                    var tags = module.options.tags.split(',')
                    opts.tags = $.map(tags, function(v) { return v.trim() })
                }
            }

            if (module.options.minimuminputlength != null) {
                opts.minimumInputLength = Number(module.options.minimuminputlength)
            }

            if (module.options.maximuminputlength != null) {
                opts.maximumInputLength = Number(module.options.maximuminputlength)
            }
            
            // Initialize select2 widget

            window.console.info('Creating select2 widget with: ' + JSON.stringify(opts))
            
            $(this.el).select2(opts)

        } else {
            window.console.error('The jQuery extension "select2" is not loaded')
        }
        window.console.log('Initialized module: input-select2')
    },
    
    teardown: function() 
    { 
        window.console.log('Tearing down module: input-select2')
    },
  }
})

/*
 * A module for select2-based input for tags
 */
this.ckan.module('input-select2-tags', function ($, _) {
  return {

    options: {
        width: 'element',
        placeholder: null,
        minimuminputlength: 2,
        maximuminputlength: 24,
        tags: null,
        separator: null,
        query: null,
        itemize: false, 
    },
    
    initialize: function() 
    {
        var module = this
        if ($.fn.select2) {
            
            // Prepare init options for a select2 widget
            
            var opts = $.extend({}, {
                placeholder: module.options.placeholder,
                width: module.options.width,
                minimumResultsForSearch: -1,
            })

            if (module.options.tags != null) {
                var t = typeof(module.options.tags) 
                if (t == 'boolean') {
                    opts.tags = module.options.tags
                } else if (t == 'string') {
                    var tags = module.options.tags.split(',')
                    opts.tags = $.map(tags, function(v) { return v.trim() })
                }
            }

            if (module.options.minimuminputlength != null) {
                opts.minimumInputLength = Number(module.options.minimuminputlength)
            }

            if (module.options.maximuminputlength != null) {
                opts.maximumInputLength = Number(module.options.maximuminputlength)
            }
            
            var qname = module.el.attr('name')

            if (module.options.itemize) {
                // Replace original input with a pseudo-input and provide N hidden inputs,
                // where N is the number of entered tags.
                var $h = $('<div>').addClass('hide itemized-tags')
                
                module.el.attr('name', qname + '-' + 'joined')
                $h.appendTo(module.el.closest('.controls'))

                var itemize_tags = function() {
                    var $input = module.el
                    var $h = $input.closest('.controls').find('.itemized-tags')
                    var tags = $input.val().split(',')
                    tags = $.grep(tags, function (tag) { return tag.length })
                    $h.empty()
                    $.each(tags, function (i, tag) {
                        var $i = $('<input>')
                            .attr('type', 'hidden')
                            .attr('name', qname + '.' + i.toString())
                            .val(tag)
                        $h.append($i)
                    })
                }

                itemize_tags()
                module.el.on('change', itemize_tags)
            }

            // Initialize select2 widget

            window.console.info('Creating select2 widget with: ' + JSON.stringify(opts))
            
            $(this.el).select2(opts)

        } else {
            window.console.error('The jQuery extension "select2" is not loaded')
        }
        window.console.log('Initialized module: input-select2-tags')
    },
    
    teardown: function() 
    { 
        window.console.log('Tearing down module: input-select2-tags')
    },
    
    _randName: function(prefix) 
    {
        return prefix + Math.random().toString(36).substring(2)
    },
  }
})

