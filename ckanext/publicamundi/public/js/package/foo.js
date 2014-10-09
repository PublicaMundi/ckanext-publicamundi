
this.ckan.module('input-contacts-foo', function ($, _) {
    return {
        options: {
            qname: null,
            keys: null,
            titles: null,
        },
        initialize: function() {
            var module = this
             
            window.console.log('Initialized module: input-contacts-foo')
        },
        teardown: function() { 
            window.console.log('Tearing down module: input-contacts-foo')
        },
    }
})

