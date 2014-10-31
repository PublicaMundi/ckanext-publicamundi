(function () {
 
    var debug = $.proxy(window.console, 'debug')
    var warn = $.proxy(window.console, 'warn')
    
    this.ckan.module('input-thesaurus-terms', function ($, _) {
        
        return {
                      
            options: { 
                qname: null,
                thesaurusAttrs: [
                    'version', 'title', 'name', 'reference_date', 'date_type'],  
                thesaurusName: null,
                select: 'select', // select | select2
                placeholder: 'Enter a keyword ...',  // select2
                width: null, // select2 
            },
            
            _getVocabulary: function (name)
            {
                var url = '/api/publicamundi/vocabularies/' + name.trim()
                var p = $.getJSON(url)
                
                p.fail(function () {
                    warn('Failed to fetch terms for vocabulary "%s"', name)
                })

                return p
            },

            initialize: function () 
            {
                var module = this,
                    $el = this.el,
                    opts = this.options,
                    qname = opts.qname
                
                // Initialize multiple select
                
                var $select = $el.children('select[multiple]')

                if (!$select.children('option').length) {
                    // Find out the machine-friendly name of our thesaurus
                    var name = null

                    if (typeof(opts.thesaurusName) == 'string') { 
                        name = opts.thesaurusName
                    } else {
                        name = qname.split('.').slice(-1)[0]
                    }

                    this._getVocabulary(name)
                        .done(function (res) {
                            debug('Fetched %d terms for vocabulary "%s"', res.terms.length, name)
                            // Load select
                            $.each(res.terms, function (i, term) {
                                $('<option/>')
                                    .attr('value', term.value)
                                    .text(term.title)
                                    .appendTo($select)
                            })
                            // Assign hidden inputs
                            $.each(opts.thesaurusAttrs, function (i, k) {
                                var inp_name = qname + '.' + 'thesaurus' + '.' + k
                                $el.find('input[name="' + inp_name +'"]')
                                    .val(res[k])
                            })
                        })
                }
                
                // Transform select widget, if requested so

                if ($.fn.select2 && opts.select == 'select2') {
                    $select.select2({ 
                        width: opts.width || 'resolve', 
                        placeholder: opts.placeholder 
                    })
                }

                // Itemize terms 
                
                $('<div/>')
                    .addClass('hide itemized-choices')
                    .appendTo($el)
              
                $select.attr('name', qname + '.terms' + '-multiple')

                $el.closest('form').on('submit', function () {
                    var choices = $select.val()
                    if (choices) { 
                        var $h = $el.find('.itemized-choices')
                        $h.empty()
                        $.each(choices, function (i, choice) {
                            $('<input/>', { type: 'hidden' })
                                .attr('name', qname + '.' + 'terms' + '.' + i.toString())
                                .val(choice)
                                .appendTo($h)
                        })
                    }
                    return true
                })

                debug('Initialized module: input-thesaurus-terms with opts:', opts)
            },
 
            teardown: function () 
            { 
                debug('Tearing down module: input-thesaurus-terms')
            },
        };
    })
 
}).apply(this);

