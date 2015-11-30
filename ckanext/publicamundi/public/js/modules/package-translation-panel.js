(function () {

    var debug = $.proxy(window.console, 'debug');
    var debug1 = (s) => null;

    var warn = $.proxy(window.console, 'warn');
    var error = $.proxy(window.console, 'error');
    
    var assert = $.proxy(window.console, 'assert');
    
    this.ckan.module('package-translation-panel', function ($, _) {

        return {
            actions: {
                updateField: '/api/action/package_translation_update_field',
                showPackage: '/api/action/package_show',
            },

            options: {
                sourceLanguage: null,
                packageIdentifier: null,
                packageName: null,
            },

            initialize: function () 
            {
                var module = this, $el = this.el, opts = this.options;
                
                this.$selectLanguage = $el.find('select#input-language');
                this.$toggle = $el.find('input#toggle-translated');
                
                this.targetLanguage = null;
                this.translatedPackage = null;
                this.showTranslated = false;
                
                // Publish events based on own input

                this.$selectLanguage.on('change', $.proxy(this._onChangeLanguage, this));
                this.$toggle.on('change', $.proxy(this._onToggleView, this));

                var tid = null;
                tid = window.setInterval(function () {
                    if (ckanext.publicamundi && ckanext.publicamundi.Package) {
                        window.clearInterval(tid);
                        // Fire change events so that fields can be populated
                        module.$selectLanguage.trigger('change');
                        module.$toggle.trigger('change');
                    }
                }, 500);

                // Listen to events from translatable fields
                
                this.sandbox.subscribe(
                    'package-translation.update-field',
                    $.proxy(this._updateField, this)
                ); 

                debug('Initialized: package-translation-panel opts=', opts);
            },
            
            publishLanguage: function ()
            {
                // Publish target language and translated package data
                
                this.sandbox.publish(
                    'package-translation.change-language',
                    {
                        sourceLanguage: this.options.sourceLanguage,
                        targetLanguage: this.targetLanguage,
                        translatedPackage: this.translatedPackage
                    }
                );
            },

            _onChangeLanguage: function ()
            {
                var Package = ckanext.publicamundi.Package;
                
                // Update state
                
                var $opt = this.$selectLanguage.find(':selected:first')

                this.targetLanguage = {
                    code: $opt.attr('value'),
                    name: $opt.data('name')
                }

                // Load translatedPackage, publish to translatable fields
                
                var module = this;
                $.getJSON(
                    '/' + this.targetLanguage.code + this.actions.showPackage, 
                    { 
                        'id': this.options.packageIdentifier
                    })
                    .done(function (obj) {
                        module.translatedPackage = new Package(obj.result);
                        module.publishLanguage();
                    })
                    .fail(function () {
                        error('Cannot fetch package ' + module.options.packageName);
                    })

                debug('The language has changed to ' + this.targetLanguage.code);
            },
             
            _onToggleView: function ()
            {
                // Update state
                
                this.showTranslated = this.$toggle.prop('checked');
                
                // Publish 

                this.sandbox.publish(
                    'package-translation.toggle-translated',
                    { show: this.showTranslated }
                );
            },

            _updateField: function (ev)
            {
                var module = this;
                
                debug('The translation for ' + ev.qname + ' is updated')
                assert(ev.targetLanguage.code = this.targetLanguage.code);
                 
                // Update local translatedPackage
                 
                this.translatedPackage.set(ev.qname, ev.translatedValue);

                // Save to backend
                // Todo What about race conditions
                
                var post_url = '/' + 
                    this.targetLanguage.code + this.actions.updateField;
                var payload = JSON.stringify({
                    'id': this.options.packageIdentifier,
                    'key': ev.qname,
                    'value': ev.translatedValue,
                });
                $.ajax(post_url, {
                        type: 'POST',
                        data: payload, 
                        contentType: 'application/json',
                    })
                    .done(function () {
                        debug('Saved translation for ' + ev.qname);
                        module.sandbox.publish(
                            'package-translation.updated-field',
                            { qname: ev.qname }
                        );
                    })
                    .fail(function () {
                        error('Failed to update field: ' + ev.qname);
                    });
                
                return
            },

            teardown: function () 
            { 
                debug('Tearing down: package-translation-panel');
            },
        };
    });

}).apply(this);

