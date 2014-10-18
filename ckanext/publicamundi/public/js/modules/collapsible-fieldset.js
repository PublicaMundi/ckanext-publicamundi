/*
 * (deprecated)
 * A simple module to provide collapsible fieldsets in forms
 */
this.ckan.module('collapsible-fieldset', function ($) {
  return {
    options: {
        state: 'open',
    },
    initialize: function () {
        var $fieldset = this.el
        var $legend   = this.el.find("legend");
        var $body     = this.el.find(".fieldset-body"); 

        if (!($fieldset.is('fieldset'))) {
            console.error ('Encountered an invalid module-target element')
            return
        }
        
        $fieldset.addClass('module-collapsible-fieldset')

        if (this.options.state == 'closed') {
            $body.hide({duration: 0})
            $legend.find('span.toggle-body').toggleClass('state-closed')
        }
        
        $legend.find("span.hints").hide(); 
        $legend
        .on ('click.collapsible-fieldset', function (ev) {
            $body.toggle();
            $legend.find('span.toggle-body').toggleClass('state-closed')
            return false
        })
        .on ('mouseenter.collapsible-fieldset', function (ev) {
            if ($body.is(':hidden')) {
                $legend.find("span.hints").fadeIn();
            }
            return false
        })
        .on ('mouseleave.collapsible-fieldset', function (ev) {
            $legend.find("span.hints").fadeOut();  
            return false
        });
                
        return
    },
  }
})

