/*
 * A module for select-based input for choices
 */
this.ckan.module('input-select-choices', function ($, _) {
  
    var debug = $.proxy(window.console, 'debug')
    var warn = $.proxy(window.console, 'warn')
    
    return {
  
      options: {
          itemize: true,
          select: 'select', // select | select2
          placeholder: 'Enter ...',
          width: null,
      },
      
      initialize: function() 
      {
          var module = this,
              $el = this.el,
              opts = this.options,
              qname = $el.attr('name')
  
          if ($el.is('select[multiple]') && opts.itemize) {
              
              // Replace original input with a pseudo-input and provide N hidden inputs,
              // where N is the number of selected options.
              var $h = $('<div/>').addClass('hide itemized-choices')
              
              $el.attr('name', qname + '-' + 'multiple')
              $h.appendTo($el.closest('.controls'))
  
              var itemize = function() {
                  var choices = $el.val()
                  if (choices) {
                      var $h = $el.closest('.controls').find('.itemized-choices')
                      $h.empty()
                      $.each(choices, function (i, choice) {
                          $('<input/>', { type: 'hidden', name: qname + '.' + i.toString() })
                            .val(choice)
                            .appendTo($h)
                      })
                  }
              }
  
              itemize()
              $el.on('change', itemize)
              
              // Transform to a proper widget, if needed
  
              if ($.fn.select2 && opts.select == 'select2') {
                  $el.select2({
                      width: opts.width || 'resolve', 
                      placeholder: opts.placeholder 
                  })
              }
  
          } else {
              warn('Skipped initialization of input-select-choices at element', $el)
          }
  
          debug('Initialized module: input-select-choices')
      },
      
      teardown: function() 
      { 
          debug('Tearing down module: input-select-choices')
      },
    }
});

/*
 * Provide support for select2-based inputs.
 * This module acts as a (simplified) wrapper to select2 functionality.
 */
this.ckan.module('input-select2', function ($, _) {
  
    var debug = $.proxy(window.console, 'debug')
    var warn = $.proxy(window.console, 'warn')
    
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
  
              debug('Creating select2 widget with:', opts)
              
              $(this.el).select2(opts)
  
          } else {
              warn('The jQuery extension "select2" is not loaded')
          }
  
          debug('Initialized module: input-select2')
      },
      
      teardown: function() 
      { 
          debug('Tearing down module: input-select2')
      },
    }
});

/*
 * A module for select2-based input for tags
 */
this.ckan.module('input-select2-tags', function ($, _) {
  
    var debug = $.proxy(window.console, 'debug')
    var warn = $.proxy(window.console, 'warn')
    
    return {
  
      options: {
          width: 'element',
          placeholder: null,
          minimuminputlength: 2,
          maximuminputlength: 24,
          tags: null,
          separator: null,
          query: null,
          itemize: true, 
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
                          $('<input>', { type: 'hidden' })
                              .attr('name', qname + '.' + i.toString())
                              .val(tag)
                              .appendTo($h)
                      })
                  }
  
                  itemize_tags()
                  module.el.on('change', itemize_tags)
              }
  
              // Initialize select2 widget
  
              debug('Creating select2 widget with:', opts)
              
              $(this.el).select2(opts)
  
          } else {
              warn('The jQuery extension "select2" is not loaded')
          }
  
          debug('Initialized module: input-select2-tags')
      },
      
      teardown: function() 
      { 
          debug('Tearing down module: input-select2-tags')
      },
      
      _randName: function(prefix) 
      {
          return prefix + Math.random().toString(36).substring(2)
      },
    }
});

/*
 * A module for checkboxes-based input for choices
 */
this.ckan.module('input-checkbox-choices', function ($, _) {

    var debug = $.proxy(window.console, 'debug')

    return {
        options: {
            qname: null,
            itemize: true,
        },
      
        initialize: function () 
        {
            var module = this,
                $el = this.el,
                opts = this.options,
                qname = opts.qname
            

            if (opts.itemize) {
                // Create pseudo-inputs and populate on submit

                $('<div/>')
                    .addClass('hide itemized-choices')
                    .appendTo($el)
                
                $el.find('input:checkbox')
                    .attr('name', qname + '-' + 'checkbox')

                $el.closest('form')
                    .on('submit', function () {
                        var $h = module.el.find('.itemized-choices')
                        $h.empty()
                        $el.find('input:checkbox:checked').each(function (i, check) {
                            $('<input/>', { type: 'hidden' }) 
                                .attr('name', qname + '.' + i.toString())
                                .val($(check).val())
                                .appendTo($h)
                        })
                        return true;
                    })
            }
            
            debug('Initialized module: input-checkbox-choices opts=', opts)
        },

        teardown: function () 
        { 
            debug('Tearing down module: input-checkbox-choices')
        },
    };
});

