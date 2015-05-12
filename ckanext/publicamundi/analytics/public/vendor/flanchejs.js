/**
 * Copyright (c) <2012> <S.C. Flanche Creative Labs SRL>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 * @author <a href="mailto:alex@flanche.net">Alex Dumitru</a>
 */

/**
 * This file is used together with InternalFooter.js to enclose the files on deployment
 * in a function to limit the scope of the variables in this library
 */

(function(){
  "use strict";
/**
 * Copyright (c) <2012> <S.C. Flanche Creative Labs SRL>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 * @author <a href="mailto:alex@flanche.net">Alex Dumitru</a>
 */

/**
 * Defines a set of constants that can be used across the library
 */

//Where should FlancheJs be deployed?
var MAIN_NAMESPACE = window;

//Log levels for the logger
var LOG_LEVEL = {
  all    : 0,
  debug  : 1,
  info   : 2,
  warning: 3,
  none   : 4
};
/**
 * Keeps track of all the configurations that can be done for the library
 * @constructor
 */
var ConfigManager = {
  //The path to where the scripts that can be loaded by the importer reside
  //If not set (=null), it will try to guess.
  applicationPath         : null,
  //Identifier to be placed at the beginning of a property
  propertyIdentifier      : "$",
  //Identifier to be placed at the beginning of a private field
  internalIdentifier      : "_",
  //Identifier to be placed at the beginning of a getter function
  getIdentifier           : "get",
  //Identifier to be placed at the beginning of a setter function
  setIdentifier           : "set",
  //Classes for static objects will start with this
  objectInternalIdentifier: "___",
  //The keyword to mark a meta action executed before the original method
  beforeKeyword           : "before",
  //The keyword to mark a meta action executed after the original method
  afterKeyword            : "after",
  //The log level, each smaller level contains all the messages of the higher levels.
  logLevel                : LOG_LEVEL.debug,
  //the specs object that describes your class structure
  specs                   : null
};

ConfigManager.setApplicationPath = function (appPath) {
  this.applicationPath = appPath;
};

ConfigManager.getApplicationPath = function () {
  if (this.applicationPath === null) {
    var scripts = window.document.getElementsByTagName("script");
    for (var i = 0; i < scripts.length; i++) {
      if (scripts[i].getAttribute("src").search("FlancheJs") != -1) {
        this.applicationPath = scripts[i].getAttribute("src").split("FlancheJs")[0];
      }
    }
    Util.log("No application path found, guessing: " + this.applicationPath + ". You can change it using FlancheJs.config.setApplicationPath().", LOG_LEVEL.warning);
  }
  return this.applicationPath;
};

ConfigManager.setPropertyIdentifier = function (propIdent) {
  this.propertyIdentifier = propIdent;
};

ConfigManager.getPropertyIdentifier = function () {
  return this.propertyIdentifier;
};

ConfigManager.setInternalIdentifier = function (internalIdentifier) {
  this.internalIdentifier = internalIdentifier;
};

ConfigManager.getInternalIdentifier = function () {
  return this.internalIdentifier;
};

ConfigManager.setGetIdentifier = function (getIdentifier) {
  this.getIdentifier = getIdentifier;
};

ConfigManager.getGetIdentifier = function () {
  return this.getIdentifier;
};

ConfigManager.setSetIdentifier = function (setIdentifier) {
  this.setIdentifier = setIdentifier;
};

ConfigManager.getSetIdentifier = function () {
  return this.setIdentifier;
};

ConfigManager.setObjectInternalIdentifier = function (objectInternalIdentifier) {
  this.objectInternalIdentifier = objectInternalIdentifier;
};

ConfigManager.getObjectInternalIdentifier = function () {
  return this.objectInternalIdentifier;
};

ConfigManager.setLogLevel = function (logLevel) {
  this.logLevel = logLevel;
};

ConfigManager.getLogLevel = function () {
  return this.logLevel;
};

ConfigManager.setSpecs = function (specs) {
  this.specs = specs;
};

ConfigManager.getSpecs = function () {
  return this.specs;
};/**
 * Copyright (c) <2012> <S.C. Flanche Creative Labs SRL>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 * @author <a href="mailto:alex@flanche.net">Alex Dumitru</a>
 */

/**
 * @description Defines a new Exception type in order to make it easier for clients to catch library exceptions
 * @constructor
 * @param {String} message the error message
 * @extends Error
 */

function FlancheJsException(message){
  this.message = message;
}
FlancheJsException.prototype.valueOf = FlancheJsException.prototype.toString = function () {
  return  this.name + ": " + this.message;
};

function BuildException(){
  FlancheJsException.apply(this, arguments);
}
BuildException.prototype = new FlancheJsException();
BuildException.prototype.constructor = BuildException;
BuildException.prototype.name = "BuildException";

function ImportException(message){
  FlancheJsException.apply(this, arguments);
}
ImportException.prototype = new FlancheJsException();
ImportException.prototype.constructor = ImportException;
ImportException.prototype.name = "ImportException";
/**
 * Copyright (c) <2012> <S.C. Flanche Creative Labs SRL>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 * @author <a href="mailto:alex@flanche.net">Alex Dumitru</a>
 */

/**
 * @description Utility functions for the library
 */
var Util = {
  /**
   * Adapted from: http://davidwalsh.name/javascript-clone
   * Performs a deep clone on the given object and returns the clone.
   * WARNING: This is a potential source of bugs as some object types might not be cloned properly
   *
   * @param {Object} src the object to be cloned
   * @return {Object}
   */
  clone: function(src){
    function mixin(dest, source, copyFunc){
      var name, s, i, empty = {};
      for(name in source){
        // the (!(name in empty) || empty[name] !== s) condition avoids copying properties in "source"
        // inherited from Object.prototype.   For example, if dest has a custom toString() method,
        // don't overwrite it with the toString() method that source inherited from Object.prototype
        s = source[name];
        if(!(name in dest) || (dest[name] !== s && (!(name in empty) || empty[name] !== s))){
          dest[name] = copyFunc ? copyFunc(s) : s;
        }
      }
      return dest;
    }

    if(!src || typeof src != "object" || Object.prototype.toString.call(src) === "[object Function]"){
      // null, undefined, any non-object, or function
      return src;  // anything
    }
    if(src.nodeType && "cloneNode" in src){
      // DOM Node
      return src.cloneNode(true); // Node
    }
    if(src instanceof Date){
      return new Date(src.getTime());  // Date
    }
    if(src instanceof RegExp){
      return new RegExp(src);
    }
    var r, i, l;
    if(src instanceof Array){
      // array
      r = [];
      for(i = 0, l = src.length; i < l; ++i){
        if(i in src){
          r.push(Util.clone(src[i]));
        }
      }
    } else{
      // generic objects
      r = src.constructor ? new src.constructor() : {};
    }
    return mixin(r, src, Util.clone);
  },

  /**
   * Determines if the variable exists by comparing it to undefined and null
   * @param {Object} variable any variable
   * @return {Boolean} true / false
   */
  exists: function(variable){
    if(variable === null || variable === undefined){
      return false;
    }
    return true;
  },

  /**
   * Merges the two given objects. The rules are the following:
   *  - obj1 is cloned, so no modification will be done upon it
   *  - if both obj1 and obj2 share a property name the more specific one is chosen (i.e. the hasOwnProperty(prop) == true)
   *  - if both obj1.prop and obj2.prop have the same specificity:
   *    - if forceOverride is set to true, obj2.prop is chosen
   *    - else obj1.prop is chosen
   * @return {Object} the merged object
   */
  merge: function(obj1, obj2, forceOverride){
    var newObj = null;
    if(!Util.exists(obj1)){
      newObj = Util.clone(obj2);
    }
    else if(!Util.exists(obj2)){
      newObj = Util.clone(obj1);
    }
    else{
      newObj = Util.clone(obj1);
      for(var index in obj2){
        if(newObj[index] === undefined){
          newObj[index] = Util.clone(obj2[index]);
        }
        else{
          if(!newObj.hasOwnProperty(index) && obj2.hasOwnProperty(index)){
            newObj[index] = obj2[index];
          }
          else if((newObj.hasOwnProperty(index) && obj2.hasOwnProperty(index)) ||
            (!newObj.hasOwnProperty(index) && !obj2.hasOwnProperty(index))){
            if(forceOverride){
              newObj[index] = Util.clone(obj2[index]);
            }
          }
        }
      }
    }
    return newObj;
  },

  /**
   * Empty function to be used as a default for inputs where a function is required
   */
  emptyFunction: function(){
  },

  /**
   * Replaces the first letter of the string to the upper case version of it
   * @param {String} string the string to which to apply
   * @return {String} the processed string
   */
  capitalizeFirstLetter: function(string){
    return string.charAt(0).toUpperCase() + string.slice(1);
  },

  /**
   * Checks if the given namespace exists and creates it otherwise
   * @param {String} namespace the namespace name
   * @return {Object} a reference to the created namespace
   */
  createNamespace: function(namespace){
    var parts = namespace.split(".");
    var current = Util.getMainNamespace();
    if(parts.length > 0){
      for(var i = 0; i < parts.length; i++){
        var part = parts[i];
        if(!Util.exists(current[part])){
          current[part] = {};
        }
        current = current[part];
      }
    }
    return current;
  },

  /**
   * Returns the main namespace where objects are deployed (i.e. window for browser, exports for node.js)
   * @return {Object}
   */
  getMainNamespace: function(){
    return MAIN_NAMESPACE;
  },

  /**
   * Returns the index of the value in the given array
   * Adapated from https://developer.mozilla.org/en-US/docs/JavaScript/Reference/Global_Objects/Array/indexOf
   * @param  {Array} array the array to search in
   * @param  {Object} searchElement the element to search for
   * @return {Number} the index of the element
   */
  indexOf: function(array, searchElement /*, fromIndex */){
    "use strict";
    if(array == null){
      throw new TypeError();
    }
    var t = Object(array);
    var len = t.length >>> 0;
    if(len === 0){
      return -1;
    }
    var n = 0;
    if(arguments.length > 1){
      n = Number(arguments[1]);
      if(n != n){ // shortcut for verifying if it's NaN
        n = 0;
      } else if(n != 0 && n != Infinity && n != -Infinity){
        n = (n > 0 || -1) * Math.floor(Math.abs(n));
      }
    }
    if(n >= len){
      return -1;
    }
    var k = n >= 0 ? n : Math.max(len - Math.abs(n), 0);
    for(; k < len; k++){
      if(k in t && t[k] === searchElement){
        return k;
      }
    }
    return -1;
  },

  /**
   * Logs a message to the console
   * @param {String} message the message to be sent
   * @param {Number} logLevel the importance level of the message (must be from LOG_LEVEL)
   */
  log: function(message, logLevel){
    if(!console){
      return;
    }
    var currentLogLevel = ConfigManager.getLogLevel();
    if(logLevel >= currentLogLevel){
      if(logLevel == LOG_LEVEL.warning){
        console.warn("[FJs]# " + message);
      }
      else{
        console.log("[FJs]# " + message);
      }
    }
  }


};

/**
 * Copyright (c) <2012> <S.C. Flanche Creative Labs SRL>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 * @author <a href="mailto:alex@flanche.net">Alex Dumitru</a>
 */

/**
 * Class for defining specification objects for javascript files created with
 * this framework
 * @param {String} objectName the name of the object for which the spec is written (e.g. class name)
 * @param {String} filePath the path to the file relative to ConfigManager.getApplicationPath
 * @param {Array} dependencies a list of specs that the file is dependent on
 * @constructor
 */
function Spec(objectName, filePath, dependencies){
  this.objectName = objectName;
  this.filePath = filePath;
  this.dependencies = dependencies || [];
}

/**
 * Adds a new dependency
 * @param {String} dependency the object name as listed in your specs object
 */
Spec.prototype.addDependency = function(dependency){
  this.dependencies.push(dependency);
};

/**
 * Removes a dependency from the list
 * @param {String} dependency the object name as listed in your specs object
 */
Spec.prototype.removeDependency = function(dependency){
  var remIndex = Util.indexOf(this.dependencies, dependency);
  this.dependencies.splice(remIndex, 1);
};

Spec.prototype.getDependencies = function(){
  return this.dependencies;
};

Spec.prototype.getObjectName = function(){
  return this.objectName;
};

Spec.prototype.getFilePath = function(){
  return this.filePath;
};
/**
 * Copyright (c) <2012> <S.C. Flanche Creative Labs SRL>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 *  @author <a href="mailto:alex@flanche.net">Alex Dumitru</a>
 */

/**
 * Packaging system for retrieving the files in which the classes are stored
 * @param specs a hash of type {objectName : objectSpec}
 * @constructor
 */

function Importer(specs){
  if(!specs){
    throw new ImportException("No specs object could be found. Maybe you forgot to add it via FlancheJs.getConfig().setSpecs()");
  }
  this.specs = specs;
  this.collectedObjects = {};
}

Importer.prototype.import = function (objectName, callback, context) {
  this.collectFiles(objectName);
  this.importCollectedObjects(callback, context);
  this.collectedObjects = {};
};

Importer.prototype.collectFiles = function (objectName) {
  if (!Util.exists(this.collectedObjects[objectName])) {
    if (!Util.exists(this.specs[objectName])) {
      throw new ImportException("Could not find a suitable spec object for " + objectName + ". Make sure it is included in FlancheJs.config.getSpecs();");
    }
    var spec = this.specs[objectName];
    var deps = spec.getDependencies();
    for (var i = 0; i < deps.length; i++) {
      this.collectFiles(deps[i]);
    }
    this.collectedObjects[objectName] = objectName;
  }
};

Importer.prototype.importCollectedObjects = function(callback, context){
  var paths = [];
  for(var objectName in this.collectedObjects){
    if(this.collectedObjects.hasOwnProperty(objectName)){
      if(!Util.exists(this.specs[objectName])){
        throw new ImportException("No object name *" + objectName + "* found in the specs.");
      }
      var pathToFile = ConfigManager.getApplicationPath() + this.specs[objectName].getFilePath();
      paths.push(pathToFile);
    }
  }
  var realContext = Util.exists(context) ? context : window;
  this.loadScripts.js(paths, callback, null, realContext);
};/*jslint browser: true, eqeqeq: true, bitwise: true, newcap: true, immed: true, regexp: false */

/**
 LazyLoad makes it easy and painless to lazily load one or more external
 JavaScript or CSS files on demand either during or after the rendering of a web
 page.

 Supported browsers include Firefox 2+, IE6+, Safari 3+ (including Mobile
 Safari), Google Chrome, and Opera 9+. Other browsers may or may not work and
 are not officially supported.

 Visit https://github.com/rgrove/lazyload/ for more info.

 Copyright (c) 2011 Ryan Grove <ryan@wonko.com>
 All rights reserved.

 Permission is hereby granted, free of charge, to any person obtaining a copy of
 this software and associated documentation files (the 'Software'), to deal in
 the Software without restriction, including without limitation the rights to
 use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
 the Software, and to permit persons to whom the Software is furnished to do so,
 subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
 COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
 IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

 @module lazyload
 @class LazyLoad
 @static
 @version 2.0.3 (git)
 */

Importer.prototype.loadScripts = (function(doc){
  // -- Private Variables ------------------------------------------------------

  // User agent and feature test information.
  var env,

  // Reference to the <head> element (populated lazily).
    head,

  // Requests currently in progress, if any.
    pending = {},

  // Number of times we've polled to check whether a pending stylesheet has
  // finished loading. If this gets too high, we're probably stalled.
    pollCount = 0,

  // Queued requests.
    queue = {css: [], js: []},

  // Reference to the browser's list of stylesheets.
    styleSheets = doc.styleSheets;

  // -- Private Methods --------------------------------------------------------

  /**
   Creates and returns an HTML element with the specified name and attributes.

   @method createNode
   @param {String} name element name
   @param {Object} attrs name/value mapping of element attributes
   @return {HTMLElement}
   @private
   */
  function createNode(name, attrs){
    var node = doc.createElement(name), attr;

    for(attr in attrs){
      if(attrs.hasOwnProperty(attr)){
        node.setAttribute(attr, attrs[attr]);
      }
    }

    return node;
  }

  /**
   Called when the current pending resource of the specified type has finished
   loading. Executes the associated callback (if any) and loads the next
   resource in the queue.

   @method finish
   @param {String} type resource type ('css' or 'js')
   @private
   */
  function finish(type){
    var p = pending[type],
      callback,
      urls;

    if(p){
      callback = p.callback;
      urls = p.urls;

      urls.shift();
      pollCount = 0;

      // If this is the last of the pending URLs, execute the callback and
      // start the next request in the queue (if any).
      if(!urls.length){
        callback && callback.call(p.context, p.obj);
        pending[type] = null;
        queue[type].length && load(type);
      }
    }
  }

  /**
   Populates the <code>env</code> variable with user agent and feature test
   information.

   @method getEnv
   @private
   */
  function getEnv(){
    var ua = navigator.userAgent;

    env = {
      // True if this browser supports disabling async mode on dynamically
      // created script nodes. See
      // http://wiki.whatwg.org/wiki/Dynamic_Script_Execution_Order
      async: doc.createElement('script').async === true
    };

    (env.webkit = /AppleWebKit\//.test(ua))
      || (env.ie = /MSIE/.test(ua))
      || (env.opera = /Opera/.test(ua))
      || (env.gecko = /Gecko\//.test(ua))
    || (env.unknown = true);
  }

  /**
   Loads the specified resources, or the next resource of the specified type
   in the queue if no resources are specified. If a resource of the specified
   type is already being loaded, the new request will be queued until the
   first request has been finished.

   When an array of resource URLs is specified, those URLs will be loaded in
   parallel if it is possible to do so while preserving execution order. All
   browsers support parallel loading of CSS, but only Firefox and Opera
   support parallel loading of scripts. In other browsers, scripts will be
   queued and loaded one at a time to ensure correct execution order.

   @method load
   @param {String} type resource type ('css' or 'js')
   @param {String|Array} urls (optional) URL or array of URLs to load
   @param {Function} callback (optional) callback function to execute when the
   resource is loaded
   @param {Object} obj (optional) object to pass to the callback function
   @param {Object} context (optional) if provided, the callback function will
   be executed in this object's context
   @private
   */
  function load(type, urls, callback, obj, context){
    var _finish = function(){
        finish(type);
      },
      isCSS = type === 'css',
      nodes = [],
      i, len, node, p, pendingUrls, url;

    env || getEnv();

    if(urls){
      // If urls is a string, wrap it in an array. Otherwise assume it's an
      // array and create a copy of it so modifications won't be made to the
      // original.
      urls = typeof urls === 'string' ? [urls] : urls.concat();

      // Create a request object for each URL. If multiple URLs are specified,
      // the callback will only be executed after all URLs have been loaded.
      //
      // Sadly, Firefox and Opera are the only browsers capable of loading
      // scripts in parallel while preserving execution order. In all other
      // browsers, scripts must be loaded sequentially.
      //
      // All browsers respect CSS specificity based on the order of the link
      // elements in the DOM, regardless of the order in which the stylesheets
      // are actually downloaded.
      if(isCSS || env.async || env.gecko || env.opera){
        // Load in parallel.
        queue[type].push({
          urls    : urls,
          callback: callback,
          obj     : obj,
          context : context
        });
      } else{
        // Load sequentially.
        for(i = 0, len = urls.length; i < len; ++i){
          queue[type].push({
            urls    : [urls[i]],
            callback: i === len - 1 ? callback : null, // callback is only added to the last URL
            obj     : obj,
            context : context
          });
        }
      }
    }

    // If a previous load request of this type is currently in progress, we'll
    // wait our turn. Otherwise, grab the next item in the queue.
    if(pending[type] || !(p = pending[type] = queue[type].shift())){
      return;
    }

    head || (head = doc.head || doc.getElementsByTagName('head')[0]);
    pendingUrls = p.urls;

    for(i = 0, len = pendingUrls.length; i < len; ++i){
      url = pendingUrls[i];

      if(isCSS){
        node = env.gecko ? createNode('style') : createNode('link', {
          href: url,
          rel : 'stylesheet'
        });
      } else{
        node = createNode('script', {src: url});
        node.async = false;
      }

      node.className = 'lazyload';
      node.setAttribute('charset', 'utf-8');

      if(env.ie && !isCSS){
        node.onreadystatechange = function(){
          if(/loaded|complete/.test(node.readyState)){
            node.onreadystatechange = null;
            _finish();
          }
          else{
            throw new ImportException("Failed to import the requested file ( " + (node.src) ? node.src : node.href + " ).");
          }
        };
      } else if(isCSS && (env.gecko || env.webkit)){
        // Gecko and WebKit don't support the onload event on link nodes.
        if(env.webkit){
          // In WebKit, we can poll for changes to document.styleSheets to
          // figure out when stylesheets have loaded.
          p.urls[i] = node.href; // resolve relative URLs (or polling won't work)
          pollWebKit();
        } else{
          // In Gecko, we can import the requested URL into a <style> node and
          // poll for the existence of node.sheet.cssRules. Props to Zach
          // Leatherman for calling my attention to this technique.
          node.innerHTML = '@import "' + url + '";';
          pollGecko(node);
        }
      } else{
        node.onload = node.onerror = _finish;
      }

      nodes.push(node);
    }

    for(i = 0, len = nodes.length; i < len; ++i){
      head.appendChild(nodes[i]);
    }
  }

  /**
   Begins polling to determine when the specified stylesheet has finished loading
   in Gecko. Polling stops when all pending stylesheets have loaded or after 10
   seconds (to prevent stalls).

   Thanks to Zach Leatherman for calling my attention to the @import-based
   cross-domain technique used here, and to Oleg Slobodskoi for an earlier
   same-domain implementation. See Zach's blog for more details:
   http://www.zachleat.com/web/2010/07/29/load-css-dynamically/

   @method pollGecko
   @param {HTMLElement} node Style node to poll.
   @private
   */
  function pollGecko(node){
    var hasRules;

    try{
      // We don't really need to store this value or ever refer to it again, but
      // if we don't store it, Closure Compiler assumes the code is useless and
      // removes it.
      hasRules = !!node.sheet.cssRules;
    } catch(ex){
      // An exception means the stylesheet is still loading.
      pollCount += 1;

      if(pollCount < 200){
        setTimeout(function(){
          pollGecko(node);
        }, 50);
      } else{
        // We've been polling for 10 seconds and nothing's happened. Stop
        // polling and finish the pending requests to avoid blocking further
        // requests.
        hasRules && finish('css');
      }

      return;
    }

    // If we get here, the stylesheet has loaded.
    finish('css');
  }

  /**
   Begins polling to determine when pending stylesheets have finished loading
   in WebKit. Polling stops when all pending stylesheets have loaded or after 10
   seconds (to prevent stalls).

   @method pollWebKit
   @private
   */
  function pollWebKit(){
    var css = pending.css, i;

    if(css){
      i = styleSheets.length;

      // Look for a stylesheet matching the pending URL.
      while(--i >= 0){
        if(styleSheets[i].href === css.urls[0]){
          finish('css');
          break;
        }
      }

      pollCount += 1;

      if(css){
        if(pollCount < 200){
          setTimeout(pollWebKit, 50);
        } else{
          // We've been polling for 10 seconds and nothing's happened, which may
          // indicate that the stylesheet has been removed from the document
          // before it had a chance to load. Stop polling and finish the pending
          // request to prevent blocking further requests.
          finish('css');
        }
      }
    }
  }

  return {

    /**
     Requests the specified CSS URL or URLs and executes the specified
     callback (if any) when they have finished loading. If an array of URLs is
     specified, the stylesheets will be loaded in parallel and the callback
     will be executed after all stylesheets have finished loading.

     @method css
     @param {String|Array} urls CSS URL or array of CSS URLs to load
     @param {Function} callback (optional) callback function to execute when
     the specified stylesheets are loaded
     @param {Object} obj (optional) object to pass to the callback function
     @param {Object} context (optional) if provided, the callback function
     will be executed in this object's context
     @static
     */
    css: function(urls, callback, obj, context){
      load('css', urls, callback, obj, context);
    },

    /**
     Requests the specified JavaScript URL or URLs and executes the specified
     callback (if any) when they have finished loading. If an array of URLs is
     specified and the browser supports it, the scripts will be loaded in
     parallel and the callback will be executed after all scripts have
     finished loading.

     Currently, only Firefox and Opera support parallel loading of scripts while
     preserving execution order. In other browsers, scripts will be
     queued and loaded one at a time to ensure correct execution order.

     @method js
     @param {String|Array} urls JS URL or array of JS URLs to load
     @param {Function} callback (optional) callback function to execute when
     the specified scripts are loaded
     @param {Object} obj (optional) object to pass to the callback function
     @param {Object} context (optional) if provided, the callback function
     will be executed in this object's context
     @static
     */
    js: function(urls, callback, obj, context){
      load('js', urls, callback, obj, context);
    }

  };
})(window.document);/**
 * @description Simple object type to keep track the class metadata
 * @author <a href="mailto:alex@flanche.net">Alex Dumitru</a>
 * @constructor
 * @param {String} className the full name including the namespace
 * @param {Function} init the constructor of the class
 * @param {Object} extendedClass the class that is extended or null
 * @param {Array} traits an array of traits to implement or null
 * @param {Object} properties a map of properties to be defined or null
 * @param {Object} methods a map of the methods to be defined or null
 * @param {Object} internals a map of private variables to be defined or null
 * @param {Object} statics a map of properties to be preserved across the class
 * @param {Object} meta a map of actions to be executed in special cases (e.g. before an accessor for a property is
 * called)
 */
function ClassMetadata(className, init, extendedClass, traits, properties, methods, internals, statics, meta){
  this.className = className;
  this.init = init || Util.emptyFunction();
  this.extendedClass = extendedClass;
  this.traits = traits || [];
  this.properties = properties || {};
  this.methods = methods || {};
  this.internals = internals || {};
  this.statics = statics || {};
  this.meta = meta || {};
  this.buildFinalDefinition();
}

/**
 * This function merges all the definitions from the extended class and from the traits
 * into the class metadata.
 */
ClassMetadata.prototype.buildFinalDefinition = function(){
  if(Util.exists(this.extendedClass)){
    this.properties = Util.merge(this.properties, this.extendedClass.prototype.__meta__.properties);
    //this.methods = Util.merge(this.methods, this.extendedClass.__meta__.methods);
    this.internals = Util.merge(this.internals, this.extendedClass.prototype.__meta__.internals);
    this.statics = Util.merge(this.statics, this.extendedClass.prototype.__meta__.statics);
  }
  for(var i = 0; i < this.traits.length; i++){
    this.checkTraitNeeds(this.traits[i]);
    this.properties = Util.merge(this.properties, this.traits[i].properties);
    this.methods = Util.merge(this.methods, this.traits[i].methods);
    this.internals = Util.merge(this.internals, this.traits[i].internals);
    this.statics = Util.merge(this.statics, this.traits[i].statics);
  }
};

/**
 * Checks if the needs of the trait are fulfilled.
 * @param trait
 */
ClassMetadata.prototype.checkTraitNeeds = function(trait){
  for(var index in trait.needs){
    var isInMethod = this.methods[index] !== undefined && this.methods[index] instanceof trait.needs[index];
    var isInInternals = this.internals[index] !== undefined && this.internals[index] instanceof trait.needs[index];
    var isInProperties = this.properties[index] !== undefined && this.properties[index] instanceof trait.needs[index];
    if(!isInMethod && !isInInternals && !isInProperties){
      throw new BuildException("The trait that you're trying to implement requires that your class contain " +
        index.toString() + " of type " + trait.needs[index].toString()
      );
    }
  }
};

/**
 * @description Allows creation of classes based on the metadata supplied
 * @author <a href="mailto:alex@flanche.net">Alex Dumitru</a>
 * @constructor
 * @param {ClassMetadata} classMetadata the class metadata supplied
 */
function ClassMaker(classMetadata) {
  this.constrClass = null;
  this.classMetadata = classMetadata;
}

/**
 * Creates the initial class object
 */
ClassMaker.prototype.createClass = function () {
  var parts = this.classMetadata.className.split(".");
  var className = parts.pop();
  var container = Util.createNamespace(parts.join("."));

  container[className] = function builder() {
    var properties = this.__meta__.properties;
    var internals = this.__meta__.internals;
    for (var index in properties) {
      this[ConfigManager.getPropertyIdentifier() + index] = Util.clone(properties[index].value);
    }
    for (index in internals) {
      this[ConfigManager.getInternalIdentifier() + index] = Util.clone(internals[index]);
    }
    this.__meta__.init.apply(this, arguments);
  };

  this.constrClass = container[className];
};


/**
 * Builds the prototype for the new class based on the existing class
 * if so
 */
ClassMaker.prototype.buildPrototype = function () {
  if (Util.exists(this.classMetadata.extendedClass)) {
    this.constrClass.prototype = new this.classMetadata.extendedClass();
    this.constrClass.prototype.constructor = this.constrClass;

    this.constrClass.prototype.callParent = function () {
      this.__meta__.extendedClass.apply(this, arguments);
    };
  }
};

/**
 * Adds the metadata to the class prototype
 */
ClassMaker.prototype.buildClassMeta = function () {
  this.constrClass.prototype.__meta__ = this.classMetadata;
};

/**
 * Adds the properties to the class prototype and generates setters and
 * getters for each based on their readability / writability
 */
ClassMaker.prototype.buildProperties = function () {
  for (var index in this.classMetadata.properties) {
    var property = this.classMetadata.properties[index];
    this.constrClass.prototype[ConfigManager.getPropertyIdentifier() + index] = property.value;
    if (property.readable !== false) {
      var getter = this.getPropertyAccessor(index, property, "get");
      this.constrClass.prototype[ConfigManager.getGetIdentifier() + Util.capitalizeFirstLetter(index)] = getter;
    }
    if (property.writable !== false) {
      var setter = this.getPropertyAccessor(index, property, "set");
      this.constrClass.prototype[ConfigManager.getSetIdentifier() + Util.capitalizeFirstLetter(index)] = setter;
    }
  }
};

/**
 *
 * @param {String} propertyName the property name
 * @param {Object} property the actual property, containing any user supplied getter or setter
 * @param {String} accessorType either get or set
 * @return {Function} the accessor function
 */
ClassMaker.prototype.getPropertyAccessor = function (propertyName, property, accessorType) {
  var preAccessor = Util.exists(property[accessorType]) ? property[accessorType] : null;
  if(preAccessor === null && accessorType === "get"){
    preAccessor = function () {
      return this[ConfigManager.getPropertyIdentifier() + propertyName];
    };
  }
  else if(preAccessor === null && accessorType === "set"){
    preAccessor = function (value) {
      this[ConfigManager.getPropertyIdentifier() + propertyName] = value;
    };
  }
  var accessor,
    beforeAccessor = this.classMetadata.meta["after" + Util.capitalizeFirstLetter(accessorType)],
    afterAccessor = this.classMetadata.meta["before" + Util.capitalizeFirstLetter(accessorType)],
    hasBeforeAccessor = Util.exists(beforeAccessor),
    hasAfterAccessor = Util.exists(afterAccessor);

  if (!hasBeforeAccessor && !hasAfterAccessor) {
    accessor = preAccessor;
  }
  else if (hasBeforeAccessor && !hasAfterAccessor) {
    accessor = function () {
      beforeAccessor.apply(this, arguments);
      preAccessor.apply(this, arguments);
    }
  }
  else if (!hasBeforeAccessor && hasAfterAccessor) {
    accessor = function (value) {
      preAccessor.apply(this, arguments);
      afterAccessor.apply(this, arguments);
    }
  }
  else {
    accessor = function (value) {
      beforeAccessor.apply(this, arguments);
      preAccessor.apply(this, arguments);
      afterAccessor.apply(this, arguments);
    }
  }
  return accessor;
};

/**
 * Adds the methods to the class prototype
 */
ClassMaker.prototype.buildMethods = function () {
  for (var index in this.classMetadata.methods) {
    this.constrClass.prototype[index] = this.classMetadata.methods[index];
  }
};

/**
 * Adds the private members (internals) to the class prototype
 */
ClassMaker.prototype.buildInternals = function () {
  for (var index in this.classMetadata.internals) {
    this.constrClass.prototype[ConfigManager.getInternalIdentifier() + index] = this.classMetadata.internals[index];
  }
};

/**
 * Adds the static memebers to the class prototype and the class object
 */
ClassMaker.prototype.buildStatics = function () {
  for (var index in this.classMetadata.statics) {
    this.constrClass[index] = this.classMetadata.statics[index];
    this.constrClass.prototype[index] = this.classMetadata.statics[index];
  }
};

/**
 * Builds the class from the initial definition
 */
ClassMaker.prototype.buildClass = function () {
  this.createClass();
  this.buildPrototype();
  this.buildMethods();
  this.buildProperties();
  this.buildInternals();
  this.buildStatics();
  this.buildClassMeta();
};

/**
 * Copyright (c) <2012> <S.C. Flanche Creative Labs SRL>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 * @author <a href="mailto:alex@flanche.net">Alex Dumitru</a>
 */

/**
 * @description A traitmetadat object contains all the necesarry information to build a trait
 * @constructor
 * @param {String} traitName
 * @param {Array} traits
 * @param {Object} properties
 * @param {Object} methods
 * @param {Object} internals
 * @param {Object} statics
 * @constructor
 */
function TraitMetadata(traitName, traits, properties, methods, internals, statics){
  this.traitName = traitName;
  this.traits = traits || [];
  this.properties = properties || {};
  this.methods = methods || {};
  this.internals = internals || {};
  this.statics = statics || {};
  this.buildFinalDefinition();
}

/**
 * Transforms the initial metadata into a complete one by merging the definitions
 * of any traits that are implemented
 */
TraitMetadata.prototype.buildFinalDefinition = function(){
  if(Util.exists(this.traits)){
    for(var i = 0; i < this.traits.length; i++){
      this.properties = Util.merge(this.properties, this.traits[i].properties);
      this.methods = Util.merge(this.methods, this.traits[i].methods);
      this.internals = Util.merge(this.internals, this.traits[i].internals);
      this.statics = Util.merge(this.statics, this.traits[i].statics);
    }
  }
};

/**
 * Copyright (c) <2012> <S.C. Flanche Creative Labs SRL>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 * @author <a href="mailto:alex@flanche.net">Alex Dumitru</a>
 */

/**
 * @description Class for building traits that can be mixed with class definitions
 * @constructor
 * @param {TraitMetadata} traitMeta the trait definition
 */
function TraitMaker(traitMeta){
  this.traitMeta = traitMeta;
}

/**
 * Builds the trait according to the definitions given
 */
TraitMaker.prototype.buildTrait = function(){
  var parts = this.traitMeta.traitName.split(".");
  var traitName = parts.pop();
  var container = Util.createNamespace(parts.join("."));
  container[traitName] = this.traitMeta;
};


/**
 * Copyright (c) <2012> <S.C. Flanche Creative Labs SRL>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 * @author <a href="mailto:alex@flanche.net">Alex Dumitru</a>
 */

/**
 * @description Allows creation of objects (singletons) by creating a new class and instantiating
 * only one object.
 * @constructor
 * @param objectMeta
 */
function ObjectMaker(objectMeta){
  this.objectMeta = objectMeta;
}

/**
 * Builds the object according to the specifications
 */
ObjectMaker.prototype.buildObject = function(){
  var parts = this.objectMeta.className.split(".");
  var objectName = parts.pop();
  var container = Util.createNamespace(parts.join("."));
  this.objectMeta.className = ConfigManager.getObjectInternalIdentifier() + this.objectMeta.className;
  var classMaker = new ClassMaker(this.objectMeta);
  classMaker.buildClass();
  var current = Util.getMainNamespace()[ConfigManager.getObjectInternalIdentifier() + parts[0]];
  for(var i = 1; i < parts.length; i++){
    current = current[parts[i]];
  }
  container[objectName] = new current[objectName]();
};


/**
 * Copyright (c) <2012> <S.C. Flanche Creative Labs SRL>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 * @author <a href="mailto:alex@flanche.net">Alex Dumitru</a>
 */

/**
 * The public API that the library exposes.
 * @type {Object}
 */
MAIN_NAMESPACE.FlancheJs = {

  /**
   * Creates a class based on the given configuration
   * @see The README.md for more details
   * @param {String} className the name of the class
   * @param {Object} config configuration object as per docs
   */
  defineClass: function (className, config) {
    var meta = new ClassMetadata(className,
      config.init,
      config.extends,
      config.implements,
      config.properties,
      config.methods,
      config.internals,
      config.statics);
    var classMaker = new ClassMaker(meta);
    classMaker.buildClass();
  },

  /**
   * Defines a trait based on the given configuration
   * @param {String} traitName the name of the trait
   * @param {Object} config configuration object as per docs
   */
  defineTrait: function (traitName, config) {
    var traitMeta = new TraitMetadata(traitName, config.implements, config.properties, config.methods, config.internals, config.statics);
    var traitMaker = new TraitMaker(traitMeta);
    traitMaker.buildTrait();
  },

  /**
   * Defines a singleton object
   * @param {String} objectName the name of the object
   * @param {Object} config configuration object as per docs
   */
  defineObject: function (objectName, config) {
    var meta = new ClassMetadata(objectName,
      config.init,
      config.extends,
      config.implements,
      config.properties,
      config.methods,
      config.internals,
      config.statics,
      config.meta
    );
    var objectMaker = new ObjectMaker(meta);
    objectMaker.buildObject();
  },

  /**
   * Imports an object and executes the given callback when the object was loaded
   * @param {String} objectName the name of the object to load (e.g. a class or some trait)
   * @param {Function} callback the function to be executed once the object was loaded
   * @param {Object} context the value of the *this* variable inside the callback
   */
  import: function (objectName, callback, context) {
    var specs = ConfigManager.getSpecs();
    var importer = new Importer(specs);
    importer.import(objectName, callback, context);
  },

  /**
   * Allows for some options to be configured according to the needs of the user program
   * @see ConfigManager for more information on which options can be modified or check the docs
   */
  config    : ConfigManager,
  /**
   * Class for defining specification objects for javascript files created with
   * this framework
   * @param {String} objectName the name of the object for which the spec is written (e.g. class name)
   * @param {String} filePath the path to the file relative to ConfigManager.getApplicationPath
   * @param {Array} dependencies a list of specs that the file is dependent on
   */
  Spec      : Spec,
  /**
   * A list of exceptions that can be thrown during the construction or importing of the objects
   */
  exceptions: {
    /**
     * This exception is thrown when an error occurred in the building process (i.e. some wrong config option)
     */
    BuildException    : BuildException,
    /**
     * This exception is thrown when an import fails for some reason
     */
    ImportException   : ImportException,
    /**
     * Generic Exception from which all the exceptions in the class inherit
     */
    FlancheJsException: FlancheJsException
  }
};/**
 * Copyright (c) <2012> <S.C. Flanche Creative Labs SRL>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 * @author <a href="mailto:alex@flanche.net">Alex Dumitru</a>
 */

/**
 * This files is used together with InternalHeader.js to enclose the files on deployment
 * in a function to limit the scope of the variables in this library
 */
})();
