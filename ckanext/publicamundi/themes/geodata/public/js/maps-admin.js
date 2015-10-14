

jQuery(document).ready(function ($, _) {
    
    var console = window.console;
    var debug = $.proxy(console, 'debug');
    
    
    var SOURCE, CLIPBOARD;
    var tree_node_id;
    var tree = null;
    var resources = {};
    var tree_nodes = {};
    var resources_fields = {};
    var resources_queryable = {};

    var table = null;
    var root = null;
    var active = null;
    var active_fields = null;

    var dirty_tree = false;
    var status_filter = 'all';

    var c = {};  

    var dropOptions = {
        drop:onDrop, 
        hoverClass:'fancytree-active'
    };
    
    // look for previously saved config options    
    $.ajax({
            url: '/publicamundi/util/get_maps_configuration',
            type: 'POST',
            beforeSend: loadStart,
            complete: loadEnd,
            error: function(res) {
                console.log('oops..');
            },
            failure: function(res) {
                console.log('something went wrong..');
            },
            success: function(res) {
                try {
                    res = JSON.parse(res);
                    SOURCE = res.config || {};
                }
                catch(err) {
                    console.log('error parsing json');
                    console.log(err);
                SOURCE = [];
            }
            tree_node_id = res.tree_node_id;

            if (!SOURCE.hasOwnProperty('children')){
                // previous options not found
                SOURCE = [];
                tree_node_id = 0;
            }
            
            table = initTable(SOURCE);
            //updateTable(SOURCE);
            tree = initTree();
            root = tree.fancytree("getRootNode");
           
            $(".fancytree-folder").droppable(dropOptions);


            // Handle listeners
           
            // left side
            //
            // listeners for status
            $('#map-filter-layers-all').on('click', function(e){
                e.preventDefault();
                //$('#map-filter-layers-status .label').text('All');
                $('#map-filter-layers-status-ignored').hide();
                $('#map-filter-layers-status-all').show();
                $('#map-filter-layers-status-new').hide();
                status_filter = 'all';
                updateTable(SOURCE);
            });

            $('#map-filter-layers-new').on('click', function(e){
                e.preventDefault();
                //$('#map-filter-layers-status .label').text('New');
                $('#map-filter-layers-status-ignored').hide();
                $('#map-filter-layers-status-all').hide();
                $('#map-filter-layers-status-new').show();
                status_filter = 'new';
                updateTable(SOURCE);
            });

            $('#map-filter-layers-inactive').on('click', function(e){
                e.preventDefault();
                //$('#map-filter-layers-status .label').text('Ignored');
                $('#map-filter-layers-status-ignored').show();
                $('#map-filter-layers-status-all').hide();
                $('#map-filter-layers-status-new').hide();
                status_filter = 'inactive'; 
                updateTable(SOURCE);
            });

            // checkbox ignore-layers listener
            
            $('#map-admin-layers-inactive input[type="checkbox"]').on('change', function(e){
                var visibility;
                var target = $(this).parent().parent().parent().parent();
                var layer_id = target.data('id');

                if (e.target.checked){
                    visibility = 'False';
                }
                else{
                    visibility = 'None';
                }
            
                
                target.attr('data-visible', visibility);
                if (!resources[layer_id]){
                    resources[layer_id] = {visible: stringToBoolean(visibility), tree_node_id: null, tree_node_index: null};
                }
                else{
                    resources[layer_id]['visible'] = stringToBoolean(visibility);
                    resources[layer_id]['tree_node_id'] = null;
                    resources[layer_id]['tree_node_index'] = null;
                }
                updateTable(SOURCE);
            });
            
            // right side
            // 
            $('#map-admin-right').on('click', function(e){
                //tree.setSelected(false);

                if (e.target.id && e.target.id == 'map-admin-right'){
                if (active){
                    active.setActive(false);
                    //active.setSelected(false);
                    //active = null;
                    $('.map-options-bar').hide();
                }
            }
            });
            // input type listeners
            $('#map-name-translation-en').on('input',function(e){
                dirty_tree = true;
            
                if (active.data.node){
                    active.setTitle($('#map-name-translation-en').val());
                    active.data.caption_en = $('#map-name-translation-en').val();

                    if (tree_nodes[active.data.id]){
                        tree_nodes[active.data.id]['caption_en'] = active.data.caption_en;
                    }
                    else{
                        tree_nodes[active.data.id] = active.data;
                    }

                }
                else{
                    active.setTitle($('#map-name-translation-en').val());
                    var title = active.title;
                    if (title.indexOf(" (*)") == -1){
                        active.setTitle(active.title+" (*)");
                    }

                    active.data.tree_node_caption_en = $('#map-name-translation-en').val();
                    if (resources[active.data.id]){
                        resources[active.data.id]['tree_node_caption_en'] = active.data.tree_node_caption_en;
                    }
                    else{
                        resources[active.data.id] = active.data;
                    }
                }
            });

            $('#map-name-translation-el').on('input',function(e){
                dirty_tree = true;

                if (active.data.node){
                    active.setTitle($('#map-name-translation-en').val());
                    active.data.caption_el = $('#map-name-translation-el').val();

                    if (tree_nodes[active.data.id]){
                        tree_nodes[active.data.id]['caption_el'] = active.data.caption_el;
                    }
                    else{
                        tree_nodes[active.data.id] = active.data;
                    }

                }
                else{
                    active.setTitle($('#map-name-translation-en').val());
                    var title = active.title;
                    if (title.indexOf(" (*)") == -1){
                        active.setTitle(active.title+" (*)");
                    }

                    active.data.tree_node_caption_el = $('#map-name-translation-el').val();
                    if (resources[active.data.id]){
                        resources[active.data.id]['tree_node_caption_el'] = active.data.tree_node_caption_el;
                    }
                    else{
                        resources[active.data.id] = active.data;
                    }
                }

            });



            // handle buttons
            $('#add-parent-node').on('click', function(e){
                var dict = {
                    parent: null,
                    visible: true
                }
                addNode(root, dict);
            }); 
            $('#add-child-node').on('click', function(e){
                
                // allow children only on 1 level
                if (active && active.parent == root){
                    
                    var dict = {
                        parent: active.data.id,
                        visible: true
                    }

                    addNode(active, dict);
                }

            });

            $('#delete-node').on('click', function(e){
                
                if (active && !active.children){
                 
                    var refNode = active.getNextSibling() || active.getPrevSibling() || active.getParent();
                    dirty_tree = true;
                    if (active.data.node){
                        deleteNode(active);
                        
                    }
                    else{
                        deleteResource(active);

                    }
                    
                    if( refNode ) {
                    refNode.setActive();
                    }
                }

            });


            $('#save-tree').on('click', function(e){
                console.log("RES QUER");
               console.log(resources_queryable);
              console.log("RES FIELDS");
                console.log(resources_fields); 
                // check if field options have been changed 
               // handle field save
                    
                // check if necessary name_en, name_el values are set for all node
                var captions_ok = true; 
                root.visit(function(node){
                    if (node.data.node){
                        if (!node.data.caption_en || !node.data.caption_el){
                            alert('You need to fill in captions in english and greek for all nodes');
                            captions_ok = false;
                            return (false);
                        }
                    }
                });
                
                /* 
                var default_found = false;
                if (resources_fields.length){
                    for (var idx in resources_fields){
                        var fields = resources_fields[idx];
                        if (fields.default === true){
                            default_found = true;
                        }
                    } 
                }
                else{
                    default_found = true;
                }
                if (default_found === false){
                    alert('You need to select a default value in all resources');
                } 
                */

                if (captions_ok){
                    // clear dirty
                    root.visit(function(node){
                        var title = node.title;
                        if (title.indexOf(" (*)") > -1){
                            node.setTitle(title.substr(0, title.indexOf(" (*)")));
                        }
                    });

                    //dirty_tree = false;
                    var d = tree.fancytree("getTree").toDict(true);
                    var dict = { tree_node_id: tree_node_id, config: d};
                    $.ajax({
                        url: '/publicamundi/util/save_maps_configuration',
                        type: 'POST',
                        //data: {dirty:JSON.stringify({bool:dirty_tree}), resources:JSON.stringify({resources:resources}), json: JSON.stringify(dict)},
                        data: {resources:JSON.stringify(resources), tree_nodes: JSON.stringify(tree_nodes), resources_fields:JSON.stringify(resources_fields), resources_queryable: JSON.stringify(resources_queryable), config: JSON.stringify(dict)},
                        beforeSend: loadStart,
                        complete: loadEnd,
                        success: function(res) {
                            dirty_tree = false;
                            resources = {};
                            resources_fields = {};
                            tree_nodes = {};
                            resources_queryable = {}; 
                        }
                    });
                }
            });
               
                }
            });

    

    function loadStart(){
        $('#map-loader-primary').css({'display': 'block'});
    }
    function loadEnd(){
        $('#map-loader-primary').css({'display': 'none'});
    }

    function loadStartSec(){
        $('#map-loader-secondary').css({'display': 'block'});
    }
    function loadEndSec(){
        $('#map-loader-secondary').css({'display': 'none'});
    }

    function addNode(parent, dict){
        dirty_tree = true;

        dict.node = true;
        var added = parent.addChildren({
            title: 'New node',
            key: tree_node_id,
            folder: true,
            data: dict,
        });
            added.data.index = added.getIndex()+1;
            added.data.id = tree_node_id;
            added.setActive();
            
            tree_nodes[added.data.id] = added.data;

            tree_node_id += 1;
            var drop = $(added.tr).droppable(dropOptions);
    }
    function deleteNode(node){
        if (!node){
           return;
        }
        //delete tree_nodes[active.data.id];
        if (tree_nodes[node.data.id]){
            tree_nodes[node.data.id]['visible'] = false;
        }
        else{
            tree_nodes[node.data.id] = {};
            tree_nodes[node.data.id]['visible'] = false;
        }
        if (node.children){
            node.visit(function(nd){
                if (nd.data.node){

                    deleteNode(nd);
                }
                else{
                    deleteResource(nd);
                }
            });
        }
        var parent = node.getParent();
        node.remove();
        parent.visit(function(nd){
            calculateNodeIndex(nd); 
        });
    }
    function addResource(parent, dict){
        dirty_tree = true;
        
        dict.node = false;
        var title = dict.res_name;
        if (dict.tree_node_caption_en){
            title = dict.tree_node_caption_en;
        }
        var added = parent.addChildren({
            title: title,
            key: dict.id,
            folder: false,
            data: dict,
        });
            // index under parent node (0-based)
            added.data.tree_node_index = added.getIndex() +1;
            //added.data.tree_node_caption_en = $('#map-name-translation-en').val();
            //added.data.tree_node_caption_el = $('#map-name-translation-el').val();
            var layer_id = added.data.id;
            resources[layer_id] = added.data;


            added.setActive();
            //added.setTitle(added.title+" package: "+dict.package_title_en+" ");
        
            for (var idx in resources){
                var res = resources[idx];
                if (res.id == added.data.id){
                    //delete resource;
                    res.visible = true;
                }
            }
    }

    function deleteResource(node) {
        if (!node){
           return;
        } 
        if (resources[node.data.id]){
            resources[node.data.id]['visible'] = null;
            resources[node.data.id]['tree_node_id'] = null;
            resources[node.data.id]['tree_node_index'] = null;
        }
        else{
            resources[node.data.id] = {};
            resources[node.data.id]['visible'] = null;
            resources[node.data.id]['tree_node_id'] = null;
            resources[node.data.id]['tree_node_index'] = null;
        }
                    
        var layers =  $("#map-admin-table .layer");

        layers.each(function(idx){    
            var layer = $(this);
            if (layer.attr('data-id') == node.data.id){
                var visible = stringToBoolean(layer.attr('data-visible'));
                layer.attr('data-visible', 'None');
                layer.attr('data-tree_node_caption_en', node.data.tree_node_caption_en);
                layer.attr('data-tree_node_caption_el', node.data.tree_node_caption_el);
                layer.find('input[type="checkbox"]').prop('checked', false);
                updateTable(SOURCE);
            }
        });
        var parent = node.getParent();
        node.remove();
        parent.visit(function(nd){
            calculateNodeIndex(nd); 
        });


    }

    function onDrag(event, ui){
        //c.tr = this;
        c.helper = ui.helper;
        //$(c.helper).css('max-width', '30px');
        $(c.helper).find(':not(:first-child)').hide();
    };

    function onDrop(event, ui){
        var draggable = ui.draggable[0];

        var ftnode = event.target.ftnode;
        
        var dict = {}
        dict.res_name = $(draggable).data('res-name');
       
        //dict.package_title = $(draggable).data('package_title');
        //dict.organization_title = $(draggable).data('organization_title');
        
        dict.tree_node_caption_en = $(draggable).data('tree_node_caption_en');
        dict.tree_node_caption_el = $(draggable).data('tree_node_caption_el');
        dict.id = $(draggable).data('id');
        
        dict.visible = 'True';
        dict.tree_node_id = ftnode.data.id;
        
        $(draggable).hide();
        $(draggable).attr('data-visible', 'True');
        $(c.helper).remove(); //remove clone
        
        addResource(ftnode, dict);

    };

    function keyToInt(key){
        return parseInt(key.substring(1));
    }


    function initTable(src){
        var layers =  $("#map-admin-table .layer");
        layers.each(function(idx){    
            var layer = $(this);
            var visible = stringToBoolean(layer.attr('data-visible'));
            var layer_id = layer.data('id');
            
            if (visible === false){
                $("#map-admin-layers-inactive input[value='"+ layer.data('res-name') +"']").prop('checked', true);
            }
        });
        return layers.draggable({
            helper: "clone",
            start: onDrag
        });

    }
    function updateTable(src){
        var layers =  $("#map-admin-table .layer");
        
        layers.each(function(idx){    
            var layer = $(this); 
            var visible = layer.attr('data-visible');
            visible = stringToBoolean(visible);
            
            // display or not according to status filter
            if (status_filter === 'new'){
                if (visible === true || visible === false){
                    layer.hide();
                }
                else{
                    layer.show();
                }        
            }
            else if (status_filter === 'inactive'){
                if (visible === true || visible === null){
                    layer.hide();
                }
                else{
                    layer.show();
                }        
            }
            else{ //all
                if (visible === true){
                    layer.hide();
                }
                else{
                    layer.show();
                }
            }
        });
    }

    function findObjectByLabel(obj, label) {
        if ($.isEmptyObject(obj)){ return false;}
        if(obj.key === label) { return true; }
        obj = obj.children;
        for(var i in obj) {
            if(obj.hasOwnProperty(i)){
                var foundLabel = findObjectByLabel(obj[i], label);
                if(foundLabel) { return foundLabel; }
            }
        }
        return false;
    };
    function stringToBoolean(string){
        switch(string.toLowerCase().trim()){
            case "true": case "True": return true;
            case "false": case "False": return false;
            default: return null;
        }
    } 
    function calculateNodeIndex(node){
        if (node.data.node){
            node.data.index = node.getIndex()+1;
            if (tree_nodes[node.data.id]){
                tree_nodes[node.data.id]['index'] = node.data.index;
            }
            else{
                tree_nodes[node.data.id] = {};
                tree_nodes[node.data.id]['index'] = node.data.index;
            }
        }
        else{
            node.data.tree_node_index = node.getIndex() +1;
            if (resources[node.data.id]){
                resources[node.data.id]['tree_node_index'] = node.data.tree_node_index;
            }
            else{
                resources[node.data.id] = {};
                resources[node.data.id]['tree_node_index'] = node.data.tree_node_index;
            }
        }
    }

    function updateFields(fields){
        if (fields && fields.length){
                
            $(".map-options-fields span").text("");
            $('#map-fields-form').show();
            //$('<td>default</td>').appendTo('#map-options-default');
           
            //$('<td>active</td>').appendTo('#map-options-activate');
            //$('<td>export</td>').appendTo('#map-options-export');
            
            for (var idx in fields){
                var field = fields[idx];
                if (field.type !== 'geometry'){
                    $('<td>'+ field.name +'</td>').appendTo('#map-fields-table thead');
                    var disabled = '';
                    if (field.type !== 'varchar'){
                        disabled = 'disabled';
                    }
                        
                    /*
                    $('<td><input type="radio" name="default" value="' + field.name +'" ' + disabled + '></input></td>').appendTo('#map-options-default');
                    disabled = '';
                    if (field.type !== 'varchar'){
                        disabled = 'disabled';
                    }
                    */

                    $('<td><input type="checkbox" name="activate" value="' + field.name + '" ' + disabled + '></input></td>').appendTo('#map-options-activate');
                    $('<td><input type="checkbox" name="export" value="' + field.name +'"></input></td>').appendTo('#map-options-export');

                /*
                if (field.default){
                    $("#map-options-default input[value='"+ field.name +"']").prop('checked',true);
                }
                */
                if (field.active){ 
                    $("#map-options-activate input[value='"+ field.name +"']").prop('checked',true);
                }
                if (field.export){ 
                    $("#map-options-export input[value='"+ field.name +"']").prop('checked',true);
                }
                }
            };
            
            /*
            $('#map-options-default input[type="radio"]').on('change', function(e){
                console.log("DEFAULT CHANGED");
                console.log(e);

                var title = active.title;
                if (title.indexOf(" (*)") == -1){
                    active.setTitle(active.title+" (*)");
                }

                for (var idx in fields){
                    var afield = fields[idx];
                    if (e.target.value == afield.name){
                        afield.default = true;
                    }
                    else{
                        afield.default = false;
                    }
                    resources_fields[active.data.id] = fields;
                }
            });
            */

            $('#map-options-fields-template-input').on('input',function(e){
            
                //active.setTitle($('#map-name-translation-en').val());
                var title = active.title;
                if (title.indexOf(" (*)") == -1){
                    active.setTitle(active.title+" (*)");
                }
                resources_queryable[active.data.queryable_id] = {template: e.target.value};
            });

            $('#map-options-activate input[type="checkbox"]').on('change', function(e){
                var title = active.title;
                if (title.indexOf(" (*)") == -1){
                    active.setTitle(active.title+" (*)");
                }
                for (var idx in fields){
                    var afield = fields[idx];
                    if (e.target.value == afield.name){
                        if (e.target.checked){
                            afield.active = true;
                        }
                        else{
                            afield.active = false;
                        }
                        resources_fields[active.data.id] = fields;
                    }
                }

            });

            $('#map-options-export input[type="checkbox"]').on('change', function(e){
    
                var title = active.title;
                if (title.indexOf(" (*)") == -1){
                    active.setTitle(active.title+" (*)");
                }
                for (var idx in fields){
                    var afield = fields[idx];
                    if (e.target.value == afield.name){
                        if (e.target.checked){
                            afield.export = true;
                        }
                        else{
                            afield.export = false;
                        }
                        resources_fields[active.data.id] = fields;
                    }
                }
            });
        }

    }
    function initTree() {
        var tree = $("#tree").fancytree({
        //checkbox: true,
        titlesTabbable: true,     // Add all node titles to TAB chain
        quicksearch: true,        // Jump to nodes when pressing first character
        source: SOURCE,
        activate: function(event, data) {

            active = data.node;

                $('.map-options-bar').show();
                $('#map-options-fields-template').hide();
                $('#map-fields-template').hide();
                $('#map-fields-form').hide();
                                
               if (active.data.node){ 
                    $('.map-options-metadata').hide();
                    $('.map-options-fields').hide();

               }
               else{
                    $('.map-options-metadata').show();
                    $('.map-options-fields').show();
              
                    if (active.data.package_title){ 
                        $('#map-options-package-title').html(active.data.package_title);
                    }
                    else{
                        $('#map-options-package-title').html('');
                    }
                    
                    var layers =  $("#map-admin-table .layer");
                    layers.each(function(idx){    
                        var layer = $(this);
                        if (layer.data('id') == active.data.id){
                            $('#map-options-resource-title').html(layer.data('res-name'));
                            $('#map-options-organization-title').html(layer.data('organization_title'));
                            $('#map-options-package-title').html(layer.data('package_title'));
                            
                        }
                    });

                    
               }
                $('#map-fields-table thead').empty();
                //$('#map-options-default').empty();
                
                $('#map-options-activate td:not(:first)').remove();
                $('#map-options-export td:not(:first)').remove();
                
                $('<td></td>').appendTo('#map-fields-table thead');

                $('#map-options-fields-template-input').val('');
                $('#map-name-translation-en').val('');
                $('#map-name-translation-el').val('');
                // Node
                if (data.node.data.node){
                        $('#map-name-translation-en').val(data.node.data.caption_en);
                        $('#map-name-translation-el').val(data.node.data.caption_el);
                }
                // Resource
                else{
                        $('#map-name-translation-en').val(data.node.data.tree_node_caption_en);
                        $('#map-name-translation-el').val(data.node.data.tree_node_caption_el);
 
                if (active.data.id in resources_fields){
                    active_fields = resources_fields[active.data.id];
                    updateFields(active_fields);
                }
                else{
                    //fetch resource fields with ajax
                    $.ajax({
                            url: '/publicamundi/util/get_resource_queryable',
                            type: 'POST',
                            data: {id: data.node.data.id},
                            beforeSend: loadStartSec,
                            complete: loadEndSec,
                            success: function(res) {

                                if (data.node.data.id != active.data.id){
                                    // user changed selection in between so return
                                return
                                }

                                var fields = {};
                                var template = '';
                                var queryable = null;
                                active_fields = null;
                                try{
                                    if (!res){
                                        return;
                                    }
                                    var parsed = JSON.parse(res);
                                    fields = parsed['fields'];
                                    
                                    queryable = parsed['queryable'];
                                    active.data.queryable_id = queryable.id;
                                    template = queryable['template'];
                                    
                                    $('#map-options-fields-template').show();
                                    $('#map-options-fields-template-input').val(template);
                                }
                                catch(err){
                                    active_fields = null;
                                }
                                active_fields = fields;
                                
                                //active_fields = resources_fields[active.data.id];
                                updateFields(active_fields);
                                     
                        }
                    });
                    
                    }
                }

                //var active_queryable = null;

                /*
                if (active.data.id in resources_queryable){
                    active_queryable = resources_queryable[active.data.id];
                    //updateFields(active_fields);
                    $('#map-options-fields-template').text(active_queryable);
                }
                else{
                    //fetch resource queryable with ajax
                    $.ajax({
                            url: '/publicamundi/util/get_resource_queryable',
                            type: 'POST',
                            data: {id: active.data.id},
                            beforeSend: loadStartSec,
                            complete: loadEndSec,
                            success: function(res) {
                                console.log('success load queryable!');
                                console.log(res);

                                //if (data.node.data.id != active.data.id){
                                    // user changed selection in between so return
                                //return
                                //}
                                
                                queryable = res;
                                $('#map-options-fields-template').text(queryable);
                                                                
                                     
                        }
                    });
                        console.log("ACTIVE QUERYABLE");
                        console.log(active_queryable);
                    
                    }
                    */
        },
        extensions: ["edit", "dnd", "table", "gridnav", "glyph"],
        dnd: {
        preventVoidMoves: true,
        preventRecursiveMoves: true,
        autoExpandMS: 400,
        dragStart: function(node, data) {
            return true;
        },
        dragEnter: function(node, data) {
            // return ["before", "after"];
            return true;
        },
        dragDrop: function(node, data) {
            //var active = tree.fancytree("getTree").getActiveNode();
            var target = node;
            var source = data.otherNode;
            // handle moving nodes/resources
            // update data fields when moving nodes/resources around
            if (target.data.node === true){
                // target is node
                if (source.data.node === true){
                // source is node 
                // TODO: not yet supported moving nodes 
                    /*
                    var sParent = source.getParent();
                    data.otherNode.moveTo(node, data.hitMode);
                    
                    // recalculate indexes for source and destination
                    sParent.visit(function(node){
                       calculateNodeIndex(node); 
                    });
                    target.visit(function(node){
                        calculateNodeIndex(node);
                    });
                    if (data.hitMode == 'over'){
                        source.data.parent = target.data.id;
                        tree_nodes[source.data.id]['parent'] = source.data.parent;
                    }
                    else{
                        source.data.parent = target.getParent().data.id;
                        tree_nodes[source.data.id]['parent'] = source.data.parent;
                    }
                    */

                }
                else{
                    //source is layer
                    if (data.hitMode == 'over'){
                    // TODO:
                    // currently only allow moving layer over node (and not next to)
                    //get source parent before moving
                    var sParent = source.getParent(); 
                    
                    dirty_tree = true; 
                    data.otherNode.moveTo(node, data.hitMode);
                    
                    // recalculate indexes for source and destination
                    sParent.visit(function(node){
                       calculateNodeIndex(node); 
                    });
                    target.visit(function(node){
                        calculateNodeIndex(node);
                    });
                    source.data.tree_node_id = target.data.id;
                    resources[source.data.id]['tree_node_id'] = source.data.tree_node_id;
                    /*
                    root.visit(function(node){
                        if (!node.data.node){ 
                            node.data.tree_node_index = node.getIndex();
                            resources[node.data.id] = node.data;
                        }
                        else{
                            node.data.index = node.getIndex();
                            tree_nodes[node.data.id] = node.data;
                        }
                    });
                    */
                    }
                }
            }
            else{
                // target is layer
                if (source.data.node === false){
                    // source is layer
                    if (data.hitMode != 'over'){
                    dirty_tree = true; 
                    
                    var sParent = source.getParent(); 
                    var tParent = target.getParent();

                    data.otherNode.moveTo(node, data.hitMode);
                    
                    
                    sParent.visit(function(node){
                       calculateNodeIndex(node); 
                    });
                    tParent.visit(function(node){
                        calculateNodeIndex(node);
                    });

                    source.data.tree_node_id = target.getParent().data.id;
                    //source.data.tree_node_id = target.data.id;
                    resources[source.data.id]['tree_node_id'] = source.data.tree_node_id;
                    /*root.visit(function(node){
                        if (!node.data.node){ 
                            node.data.tree_node_index = node.getIndex();
                            resources[node.data.id] = node.data;

                        }
                        else{
                            node.data.index = node.getIndex();
                            tree_nodes[node.data.id] = node.data;
                        }
                    });
                    */
                    }
                }
            }
        }
        },
        edit: {
        triggerStart: ["shift+mac+ctrl+alt+f2", "shift+ctrl+mac+enter+click", "ctrl+shift+mac+enter"],
        close: function(event, data) {
            if( data.save && data.isNew ){
            // Quick-enter: add new nodes until we hit [enter] on an empty title
            $("#tree").trigger("nodeCommand", {cmd: "addSibling"});
            }
        },
        edit: function(event, data){ 
            //onEditStart(data.node)

        },
        },
        table: {
        checkbox: false,
        indentation: 20,
        nodeColumnIdx: 0,
        //checkboxColumnIdx: 0
        },
        gridnav: {
        autofocusInput: false,
        handleCursorKeys: true
        },

        lazyLoad: function(event, data) {
        //data.result = {url: "../demo/ajax-sub2.json"};
        },
        renderColumns: function(event, data) {
        var node = data.node,
            $select = $("<select />"),
            $tdList = $(node.tr).find(">td");

        // (Index #0 is rendered by fancytree by adding the checkbox)
        //$tdList.eq(1).text(node.getIndexHier()).addClass("alignRight");
        // Index #2 is rendered by fancytree, but we make the title cell
        // span the remaining columns if it is a folder:
        if( node.isFolder() ) {
            $tdList.eq(2)
            .prop("colspan", 6)
            .nextAll().remove();
        }
        //$tdList.eq(1).html("<input type='input' value='" + "" + "'>");
        }
    });

    /*
    * Tooltips
    */
    $("#tree").tooltip({
        content: function () {
        return $(this).data("res-name");
        }
    });
    
    return tree;

    }

});
