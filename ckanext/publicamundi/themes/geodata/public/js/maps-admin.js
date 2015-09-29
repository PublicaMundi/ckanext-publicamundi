

jQuery(document).ready(function ($, _) {
    
    var console = window.console;
    var debug = $.proxy(console, 'debug');

    
    var SOURCE, CLIPBOARD;
    var tree_node_id;
    var tree = null;
    var table = null;
    var root = null;
    var active = null;
    var active_fields = null;

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
                console.log('success!!');
                console.log(res);
                try {
                    res = JSON.parse(res);
                    SOURCE = res.config || {};
                }
                catch(err) {
                    console.log('error parsing json');
                    console.log(err);
                    SOURCE = [];
                }
                console.log(SOURCE);
                tree_node_id = res.tree_node_id;

                if (!SOURCE.hasOwnProperty('children')){
                    // previous options not found
                    SOURCE = [];
                    tree_node_id = 0;
                }
                console.log('SOURCE');
                console.log(SOURCE);
                console.log(SOURCE["key"]);
                
                table = initTable(SOURCE);
                tree = initTree();
                root = tree.fancytree("getRootNode");
                
                $(".fancytree-folder").droppable(dropOptions);


                // handle buttons
                $('#add-parent-node').on('click', function(e){
                    var dict = {
                        parent: null,
                        visible: true
                    }
                    addNode(root, dict);
                }); 
                $('#add-child-node').on('click', function(e){
                    //var active = tree.fancytree("getTree").getActiveNode();
                    
                    // allow children only on 1 level
                    if (active && active.parent == root){
                        
                        var dict = {
                            parent: active.data.id,
                            visible: true
                        }

                        addNode(active, dict);
                    }

                });

                $('#rename-node').on('click', function(e){
                    //var active = tree.fancytree("getTree").getActiveNode();
                    
                    if (active){
                        active.editStart();
                    }
                });
                
                $('#delete-node').on('click', function(e){
                    //var active = tree.fancytree("getTree").getActiveNode();

                    if (active && !active.children){
                        var refNode = active.getNextSibling() || active.getPrevSibling() || active.getParent();
                        active.remove();
                        var d = tree.fancytree("getTree").toDict(true);
                        initTable(d);
                    if( refNode ) {
                        refNode.setActive();
                        }
                    }

                });


                $('#save-tree').on('click', function(e){
                     var allGood = true;
                    // check if necessary node name_en, name_el values are set
                    root.visit(function(node){
                        if (node.data.node){
                            if (!node.data.name_en || !node.data.name_el){
                                alert('You need to fill in english & greek name for all nodes');
                                allGood = false;
                                return (false);
                            }
                        }
                    });
                    
                    if (allGood){
                        var d = tree.fancytree("getTree").toDict(true);
                        var dict = { tree_node_id: tree_node_id, config: d};
                        console.log(JSON.stringify(dict));
                        console.log(root);
                        $.ajax({
                            url: '/publicamundi/util/save_maps_configuration',
                            type: 'POST',
                            data: {json: JSON.stringify(dict)},
                            beforeSend: loadStart,
                            complete: loadEnd,
                            success: function(res) {
                                console.log('success');
                                console.log(res);
                            }
                        });
                    }
                });
                
                $('#map-name-translation').on('submit', function(e){
                    e.preventDefault();
                    console.log('submit');
                    if (active){
                        console.log(active);
                        console.log($('#map-name-translation-en').val());
                        active.data.name_en = $('#map-name-translation-en').val();
                        if (active.data.node){
                            active.setTitle($('#map-name-translation-en').val());
                        }
                        active.data.name_el = $('#map-name-translation-el').val();
                    }
                });
                
                
                $('#map-fields-form').on('submit', function(e){
                    e.preventDefault();

                    if (active_fields){
                        var fdefault = $('#map-options-default input[type="radio"]:checked').val();
                        console.log('sel def');
                        console.log(fdefault);

                        //for (var idx in fields){
                        //var field = fields[idx];
                        //if (field.name == e.target.value){

                        var factive = $('#map-options-activate input[type="checkbox"]:checked');
                        console.log('sel act');
                        console.log(factive);
                                            
                        var fexport = $('#map-options-export input[type="checkbox"]:checked');
                        console.log('sel exp');
                        console.log(fexport);

                        for (var idx in active_fields){
                            var field = active_fields[idx];
                            field.active = false;
                            field.export = false;
                            field.default = false;

                            if (field.name == fdefault){
                                field.default = true;     
                            } 
                            factive.each(function(idx){    
                                if (field.name == $(this).val()){
                                   field.active = true;
                                } 
                            });
                            
                            fexport.each(function(idx){    
                                if (field.name == $(this).val()){
                                   field.export = true;
                                } 
                            });

   
                        }
                        console.log("ACTIVE FIELDS");
                        console.log(active_fields);
                        $.ajax({
                            url: '/publicamundi/util/update_resource_fields',
                            type: 'POST',
                            data: {json:JSON.stringify({fields:active_fields})},
                            beforeSend: loadStart,
                            complete: loadEnd,
                            success: function(res) {
                                console.log('success update fields');
                                console.log(res);
                            }
                        });

                        
                    }
                })

                }
            });

    

    function loadStart(){
        $('.ajax-loader').css({'display': 'block'});
    }
    function loadEnd(){
        $('.ajax-loader').css({'display': 'none'});
    }
    function addNode(parent, dict){
        dict.node = true;

        var added = parent.addChildren({
            title: 'New node',
            key: tree_node_id,
            folder: true,
            data: dict,
        });
            added.data.index = added.getIndex();
            added.data.id = tree_node_id;
            added.setActive();
            
            //console.log('ID');
            //console.log(keyToInt(added.key));
            console.log('id=');
            console.log(added.data.id); 
            console.log('parent=');
            console.log(added.data.parent); 
            console.log(root); 
            
            tree_node_id += 1;
            var drop = $(added.tr).droppable(dropOptions);
    }
    function addResource(parent, dict){
        dict.node = false;
        console.log('ID');
        console.log(dict.id);
        var added = parent.addChildren({
            title: dict.name_en,
            key: dict.id,
            folder: false,
            data: dict,
        });
            // index under parent node (0-based)
            added.data.tree_node_index = added.getIndex();
            
            console.log('idx=');
            console.log(added.data.tree_node_index); 
            console.log('parent=');
            console.log(added.data.tree_node_id); 

            console.log(root); 
            added.setActive();
        
    }

    function onDrag(event, ui){
        c.tr = this;
        c.helper = ui.helper;
    };

    function onDrop(event, ui){
        var draggable = ui.draggable[0];

        var ftnode = event.target.ftnode;
        
        var dict = {}
        dict.name_en = $(draggable).attr('name_en');
        dict.name_el = $(draggable).attr('name_el');
        dict.id = $(draggable).attr('id');
        
        //dict.fields = $(draggable).attr('fields');
        //dict.field_num = parseInt($(draggable).attr('field_num'));
        //dict.field_names = $(draggable).attr('field_names');
        //dict.field_default = $(draggable).attr('field_default');
        //dict.field_active = $(draggable).attr('field_active');
        //dict.field_export = $(draggable).attr('field_export');
        //res = JSON.parse(res);
        dict.visible = true;
        dict.tree_node_id = ftnode.data.id;
        
        addResource(ftnode, dict);
        
        $(c.tr).hide();
        $(c.helper).remove(); //remove clone

    };

    function keyToInt(key){
        return parseInt(key.substring(1));
    }


    function initTable(src){
        var layers =  $("#map-admin-table .layer");
        console.log('layers');
        layers.each(function(idx){    
            var layer = $(this);
            console.log(layer.attr('name_en'));
            console.log(layer.attr('id'));
            console.log(findObjectByLabel(src, layer.attr('id')));
            if (findObjectByLabel(src, layer.attr('id'))){
                layer.hide();
            }
            else{
                layer.show();
            }
        });
        return layers.draggable({
            helper: "clone",
            start: onDrag
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

    function initTree() {
        var tree = $("#tree").fancytree({
        //checkbox: true,
        titlesTabbable: true,     // Add all node titles to TAB chain
        quicksearch: true,        // Jump to nodes when pressing first character
        source: SOURCE,
        activate: function(event, data) {
            console.log('activated');
            console.log(data);

                $('#map-fields-table thead').empty();
                $('#map-options-default').empty();
                $('#map-options-activate').empty();
                $('#map-options-export').empty();
                $('<td></td>').appendTo('#map-fields-table thead');
                                
                $('#map-name-translation-en').val(data.node.data.name_en);
                $('#map-name-translation-el').val(data.node.data.name_el);

            if (!data.node.data.node){ 
                
                //get fields with ajax
                
                $.ajax({
                        url: '/publicamundi/util/get_resource_fields',
                        type: 'POST',
                        data: {id: data.node.data.id},
                        beforeSend: loadStart,
                        complete: loadEnd,
                        success: function(res) {
                            console.log('success load fields!');
                            console.log(res);
                             
                            var fields = {};
                            active_fields = null;
                            try{
                                fields = JSON.parse(res);
                            }
                            catch(err){
                                console.log(err);
                                active_fields = null;
                            }
                            
                            console.log('FIELDS');
                            console.log(fields);
                            //var num = fields.num;
                            fields = fields.fields;
                            active_fields = fields;
                            console.log(fields);
                            console.log("ACTIVE");
                            console.log(active_fields.length);
                            
                            if (active_fields.length){
                            $('<td>default</td>').appendTo('#map-options-default');
                            $('<td>activate</td>').appendTo('#map-options-activate');
                            $('<td>export</td>').appendTo('#map-options-export');
                            }
                            for (var idx in fields){
                                var field = fields[idx];
                                console.log(field);
                                if (field.type !== 'geometry'){
                                    $('<td>'+ field.name +'</td>').appendTo('#map-fields-table thead');
                                    $('<td><input type="radio" name="default" value="' + field.name +'"></input></td>').appendTo('#map-options-default');
                                    $('<td><input type="checkbox" name="activate" value="' + field.name +'"></input></td>').appendTo('#map-options-activate');
                                    $('<td><input type="checkbox" name="export" value="' + field.name +'"></input></td>').appendTo('#map-options-export');

                                if (field.default){
                                    $("#map-options-default input[value='"+ field.name +"']").prop('checked',true);
                                }
                                if (field.active){ 
                                    $("#map-options-activate input[value='"+ field.name +"']").prop('checked',true);
                                }
                                if (field.export){ 
                                    $("#map-options-export input[value='"+ field.name +"']").prop('checked',true);
                                }
                                }
                            };

            }
            });

            }
            active = data.node;
            
        },
        // extensions: ["edit", "table", "gridnav"],
        extensions: ["edit", "dnd", "table", "gridnav"],
        //extensions: ["dnd", "table", "gridnav"],
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
                    // dont allow moving around nodes
                    //
                    //if (target.parent == root){
                        //data.otherNode.moveTo(node, data.hitMode);
                        //node.data.parent = node.id;
                        //source.data.parent = target.data.id;
                        //console.log('TARGET');
                        //console.log(target.data);
                        //console.log(target.data.id);
                        //console.log(root);
                    //}
                }
                else{
                    //source is layer
                    if (data.hitMode == 'over'){
                        // only allow moving layer over node (and not next to)
                    //get source parent before moving
                    var sParent = source.getParent(); 
                    
                    data.otherNode.moveTo(node, data.hitMode);
                    source.data.tree_node_id = target.data.id;
                    /*target.visit(function(node){
                        if (!node.data.node){ 
                            node.data.tree_node_index = node.getIndex();
                        }
                        else{
                            node.data.index = node.getIndex();
                        }
                    });*/
                    root.visit(function(node){
                        if (!node.data.node){ 
                            node.data.tree_node_index = node.getIndex();
                        }
                        else{
                            node.data.index = node.getIndex();
                        }
                    });

                    console.log(root);
                    }
                }
            }
            else{
                // target is layer
                if (source.data.node === false){
                    // source is layer
                    if (data.hitMode != 'over'){
                    data.otherNode.moveTo(node, data.hitMode);
                    source.data.tree_node_id = target.getParent().data.id;
                    
                    /*target.getParent().visit(function(node){
                        if (!node.data.node){ 
                            node.data.tree_node_index = node.getIndex();
                        }
                    });
                    */
                    root.visit(function(node){
                        if (!node.data.node){ 
                            node.data.tree_node_index = node.getIndex();
                        }
                        else{
                            node.data.index = node.getIndex();
                        }
                    });

                    console.log(root);
                    }
                }
            }
        }
        },
        edit: {
        triggerStart: ["shift+mac+ctrl+alt+f2", "shift+ctrl+mac+enter+click", "ctrl+shift+mac+enter"],
        close: function(event, data) {
                //data.node.data.name_en = data.node.title;
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
        indentation: 20,
        nodeColumnIdx: 2,
        checkboxColumnIdx: 0
        },
        gridnav: {
        autofocusInput: false,
        handleCursorKeys: true
        },

        lazyLoad: function(event, data) {
        data.result = {url: "../demo/ajax-sub2.json"};
        },
        renderColumns: function(event, data) {
        var node = data.node,
            $select = $("<select />"),
            $tdList = $(node.tr).find(">td");

        // (Index #0 is rendered by fancytree by adding the checkbox)
        $tdList.eq(1).text(node.getIndexHier()).addClass("alignRight");
        // Index #2 is rendered by fancytree, but we make the title cell
        // span the remaining columns if it is a folder:
        if( node.isFolder() ) {
            $tdList.eq(2)
            .prop("colspan", 6)
            .nextAll().remove();
        }
        $tdList.eq(3).html("<input type='input' value='" + "" + "'>");
        }
    });

    /*
    * Tooltips
    */
    $("#tree").tooltip({
        content: function () {
        return $(this).attr("title");
        }
    });
    
    return tree;

    }

});
