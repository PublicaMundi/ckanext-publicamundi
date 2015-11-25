(function () {

    var debug = $.proxy(window.console, 'debug');
    var debug1 = (s) => null;

    var warn = $.proxy(window.console, 'warn');
    var assert = $.proxy(window.console, 'assert');
    
    var states = {
        CLEAN: 'clean', // not touched
        DIRTY: 'dirty', // edited by the user, not saved back
        SAVING: 'saving', // published changes
        SAVED: 'saved', // saved, i.e published and acknowledged as saved
    };
   
    var renderSnippet = function (name, params) {
        // A modified version of module.sandbox.client.getTemplate that respects 
        // active language (and requests on LOCALE_ROOT)
        var snippet_url = window.ckan.LOCALE_ROOT + '/api/1/util/snippet/' + name
        return $.get(snippet_url, (params || {}))
    };
 
    this.ckan.module('package-translatable-field', function ($, _) {

        return {
            options: {
                qname : null,
                dialogTemplate: 'translate-text-field.html',
                i18n: {
                    'translate': _('edit'), 
                },
            },

            initialize: function () 
            {
                var module = this, $el = this.el;
                
                this.value = $el.text();
                this.$td = $el.closest('td')
                this.$th = module.$td.prev('th.name')
                
                this.state = states.CLEAN;
                this.qname = this._computeQualName();
                this.title = this._computeTitle();
                this.qtitle = this._computeQualTitle();
                
                this.sourceLanguage = null;
                this.targetLanguage = null;
                this.translatedValue = null;
                this.showTranslated = false;
                this.scratchValue = null;
                
                this._initializeControls();
                
                this.sandbox.subscribe(
                    'package-translation.change-language', 
                    $.proxy(this._changeLanguage, this)      
                );
                
                this.sandbox.subscribe(
                    'package-translation.toggle-translated', 
                    $.proxy(this._showTranslated, this)      
                );
                
                this.sandbox.subscribe(
                    'package-translation.updated-field', 
                    $.proxy(this._complete, this)      
                );

                debug('Initialized package-translatable-field qname=', module.qname);
            },

            teardown: function () 
            { 
                debug('Tearing down package-translatable-field');
            },
            
            _initializeControls: function () 
            {
                var $el = this.el;

                // Build the (dialog) form

                this.$dialog = null;
                renderSnippet(this.options.dialogTemplate, 
                    {
                        'title': this.title,
                    })
                    .done($.proxy(this._createDialog, this))
                
                // Build buttons and statuses
                
                this.$icon = $('<i/>', 
                    {
                        'class': 'icon icon-pencil translation-status'
                    })
                this.$btn = $('<button/>', 
                    {
                        'class': "btn btn-small translate"
                    })
                    .text(this.i18n('translate'))
                this.$btn.hide()
                
                // Find hover parent, react on hover 

                this.$hover = $el.closest('dd')
                if (!this.$hover.length)
                   this.$hover = $el.closest('li[data-key]')
                if (!this.$hover.length)
                   this.$hover = this.$td

                this.$hover.append(this.$btn)
                //this.$hover.append(this.$icon)
                this.$hover.on('mouseover', $.proxy(this._onMouseEnter, this))
                this.$hover.on('mouseleave', $.proxy(this._onMouseLeave, this))
                
                // Add event listeners
                
                this.$btn.on('click', $.proxy(this._openDialog, this))

                return
            },
            
            _redraw: function ()
            {
                var $el = this.el, $dialog = this.$dialog;

                // Refresh TD/DD text contents

                if (this.showTranslated) {
                    if (this.translatedValue != null) {
                        $el.text(this.translatedValue);
                    }
                } else {
                    $el.text(this.value);
                }
                
                // Refresh state classes

                var expected_class = 'translation-status-' + this.state;
                if (!$el.hasClass(expected_class)) {
                    // Replace existing state-related class
                    var match = (s) => /^translation-status-([a-z]*)$/.test(s), 
                        existing_class = $el.attr('class').split(' ').find(match);
                    if (existing_class != null) {
                        $el.removeClass(existing_class);
                    }
                    $el.addClass(expected_class);
                }
                
                // Reset dialog, if created till now

                if ($dialog && (this.translatedValue != null)) {
                    $dialog.find('textarea.translated-value')
                        .val(this.scratchValue);
                    $dialog.find('.title > .source-language')
                        .text(this.sourceLanguage.name);
                    $dialog.find('.title > .target-language')
                        .text(this.targetLanguage.name);
                }
                
                return
            },

            _changeLanguage: function (ev)
            {
                var Package = ckanext.publicamundi.Package;

                // Reset language context
                
                this.sourceLanguage = ev.sourceLanguage
                this.targetLanguage = ev.targetLanguage

                // Lookup for a translated value
                
                assert(ev.translatedPackage.constructor == Package); 
                
                this.translatedValue = ev.translatedPackage.get(this.qname);
                this.scratchValue = this.translatedValue;
                this.state = states.CLEAN;

                if (this.value.length && (this.translatedValue == null)) {
                    warn('Expected a non-null translated value for ' + this.qname);
                }
                
                // Done
                
                this._redraw();

                debug1('The field ' + this.qname + ' is notified on changed language')
            },
            
            _showTranslated: function (ev)
            {
                var $el = this.el
                if (this.showTranslated != ev.show) {
                    this.showTranslated = ev.show;
                    this._redraw();
                }

                debug1('The field ' + this.qname + ' is notified to switch to ' +
                    '(' +  ((ev.show)? ('TRANSLATED') : ('SOURCE'))  + ')')
            },

            _openDialog: function (ev)
            {   
                if (this.state == states.SAVING) {
                    warn('Cannot open dialog: pending changes for ' + this.qname);
                    return;
                }
                
                this.$dialog.modal('show'); 
                
                // Fixme: Check accross browsers
                //// Center modal in the middle of the screen.
                //this.$dialog.css({
                //    'margin-top': this.$dialog.height() * (-0.5),
                //    'top': '50%'
                //});
                
                return false;
            },

            _createDialog: function (markup)
            {
                if (!this.$dialog) {
                    var module = this, $dialog = $(markup);
                    
                    this.$dialog = $dialog;
                    
                    $dialog.modal({ show: false, keyboard: true });
                    
                    // Fill (readonly) text in source language

                    $dialog.find('textarea.value').val(this.value);
                    
                    // Add event listeners for dialog controls
                    
                    $dialog.on('hide', $.proxy(this._checkInputText, this));

                    $dialog.on('click', '.btn.btn-primary', function (ev) {
                        $dialog.one('hidden', $.proxy(module._saveAsTranslated, module));
                        $dialog.modal('hide');
                    });

                    // If a translated value is available, a redraw is needed

                    this._redraw();
                }
                return
            },
           
            _saveAsTranslated: function (ev)
            {
                debug('About to save ' + this.qname + ' ('  + this.state.toUpperCase() + ')'); 
                
                // Check if needs to be saved

                if (this.state != states.DIRTY) {
                    debug('No changes for field ' + this.qname + ': noop')
                    return // noop
                }
                
                this.translatedValue = this.scratchValue;

                // Publish upstairs and move to SAVING
                // Note: Move to SAVED once we receive ack from sandbox

                this.sandbox.publish(
                    'package-translation.update-field',
                    { 
                        qname: this.qname,
                        targetLanguage: this.targetLanguage,
                        translatedValue: this.translatedValue
                    }
                );

                this.state = states.SAVING;
                
                // Redraw this widget

                this._redraw();
                
                return;
            },
            
            _complete: function (ev)
            {
                // A full edit is complete (for some field). 
                // If this is addressed to our field, move to SAVED.
                
                if (ev.qname != this.qname) {
                    return // ignore it, is for someone else
                }

                // Cannot reach this otherwise!
                assert(this.state == states.SAVING); 
                
                this.state = states.SAVED;

                this._redraw();
            },

            _checkInputText: function ()
            { 
                this.scratchValue = this.$dialog.find('textarea.translated-value').val();

                if (this.translatedValue != this.scratchValue) {
                    this.state = states.DIRTY;
                    this._redraw();
                }
                
                debug('Checking field ' + this.qname + ': ' + this.state.toUpperCase());
            },

            _computeQualName: function ()
            {
                var th_kp = this.$th.data('qname').split('.'), 
                    td_kp = this.options.qname.split('.');
                
                td_kp.shift(); // pop placeholder name

                return th_kp.concat(td_kp).join('.')
            },

            _computeTitle: function ()
            {
                var titles = [this.$th.text().trim()]
                
                // Note
                // The value inside TD can be nested (multiple times) as
                // DL -> DT[data-key=*] + DD or
                // OL -> LI[data-key=*]
                
                var td = this.$td.get(0), 
                    $p = this.el, $p1 = null, t1 = null, td_titles = [];
                do {
                    $p1 = $p.closest('dd');
                    if ($p1.length) {                   
                        if ($.contains(td, $p1.get(0))) {
                            t1 = $p1.prev('dt[data-key]').text().trim();
                        } else {
                            $p1 = null;
                        }
                    } else {
                        $p1 = $p.closest('li[data-key]')
                        if ($p1.length) {
                            if ($.contains(td, $p1.get(0))) {
                                t1 = '#' + (parseInt($p1.data('key')) + 1);
                            } else {
                                $p1 = null;
                            }
                        }
                    }
                    if ($p1 && $p1.length) {
                        $p = $p1.parent();
                        td_titles.push(t1);
                    } else {
                        $p = null;
                    }
                } while ($p);
                
                td_titles.reverse();
                titles = titles.concat(td_titles);
                
                return titles.join(' / ');
            },

            _computeQualTitle: function ()
            {
                // Fixme 
                // Compute the qualified title by visiting all enclosing TH elements 
                
                return this._computeTitle() 
            },

            _onMouseEnter: function ()
            {
                this.el.addClass('nearby')
                //this.$icon.hide()
                this.$btn.show()
            },

            _onMouseLeave: function ()
            {
                this.el.removeClass('nearby')
                this.$btn.hide()
                //this.$icon.show()
            },
        };
    });

}).apply(this);

