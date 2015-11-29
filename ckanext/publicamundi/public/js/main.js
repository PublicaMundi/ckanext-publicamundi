this.ckanext || (this.ckanext = {})
this.ckanext.publicamundi || (this.ckanext.publicamundi = {})

jQuery(document).ready(function ($) {
    
    var console = window.console
    var debug = $.proxy(console, 'debug') 
    
    var Package = function (data) {
        this.data = data;
    }

    var lookup = function (res, key) 
    {
        if ($.isPlainObject(res)) {
            return res[key];
        } else if ($.isArray(res)) {
            key = parseInt(key);
            return res[key]
        }
        return null;
    };

    Package.prototype.get = function (key) 
    {
        var kp = ($.isArray(key))? (key) : (key.split('.'));
        return kp.reduce(lookup, this.data); 
    };

    Package.prototype.set = function (key, value) 
    {
        // This setter will not recursively create nested objects
        var kp = ($.isArray(key))? (key) : (key.split('.'));
        var key1 = kp.pop();
        var o1 = kp.reduce(lookup, this.data);
        if ($.isPlainObject(o1)) {
            return (o1[key1] = value);
        } else if ($.isArray(o1)) {
            key1 = parseInt(key1);
            return (o1[key1] = value);
        } else {
            return null;
        }
    };

    ckanext.publicamundi.Package = Package;

    return
});

