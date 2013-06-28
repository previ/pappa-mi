$("#page-menu").bind('pageinit', function(event, entry) {

  $.ajax({url:"/api/user/current", 
	  dataType:'json',
	  success:function(data) { 

    userpappami = data;
    now = new Date()
    initUI(userpappami, userpappami.schools[0].id, getPrevBizDay(new Date(now.getFullYear(), now.getMonth(), now.getDate())));
    
    $('#user').text(userpappami.fullname);
      
  }});    
 
});

$("#page-stream").bind('pageinit', function(event, entry) {

  $.ajax({url:"/api/user/current", 
	  dataType:'json',
	  success:function(data) { 

    userpappami = data;    
    $('#user').text(userpappami.fullname);
    //$('[data-role="content"]').text(userpappami.fullname);

  }});    

  $.ajax({url:"/api/node/list", 
	  dataType:'json',
	  success:function(data) { 
    var node_lists = $('#node_lists');
    if( data.subs_nodes.length) {
      var node_list = $('<ul data-role="listview" data-inset="true"></ul>');
      var node_list_select = $('#node_select');
      for (var n = 0; n < data.subs_nodes.length;n++) {
	var node = data.subs_nodes[n];
	var li = $('<li></li>');
	var a = $('<a href="#"></a>').attr('data-node-id', node.id).text(node.name).on('click', onNodeClick);
	li.append(a);
	node_list.append(li);
	node_list_select.append($('<option></option>').attr('value', node.id).text(node.name));
      }
      node_lists.append('<p>Miei argomenti</p>');
      node_lists.append(node_list)
    }
    if( data.active_nodes.length) {
      var node_list = $('<ul data-role="listview" data-inset="true"></ul>');
      for (var n = 0; n < (data.active_nodes.length > 5 ? 5 : data.active_nodes.length);n++) {
	node = data.active_nodes[n];
	node_list.append($('<li></li>').attr('data-node-id', node.id).text(node.name));
      }
      node_lists.append('<p>Attivi</p>');
      node_lists.append(node_list)
    }
    if( data.recent_nodes.length) {
      var node_list = $('<ul data-role="listview" data-inset="true"></ul>');
      for (var n = 0; n < (data.recent_nodes.length > 5 ? 5 : data.recent_nodes.length);n++) {
	node = data.recent_nodes[n];
	node_list.append($('<li></li>').attr('data-node-id', node.id).text(node.name));
      }
      node_lists.append('<p>Recenti</p>');
      node_lists.append(node_list);
    }

    $('#page-stream').trigger("create");
  }});
  loadNode('news');
});

function loadPost(post_id) {
  $.ajax({url:"/api/post/"+post_id, 
	  dataType:'json',
	  success:function(data) { 
    var page_post_detail = $('#page-post-detail');
    var post = data;    
    page_post_detail.find('#title').html(post.title);
    page_post_detail.find('#content').html(post.content);
    page_post_detail.find('#date').text(post.ext_date);
    page_post_detail.trigger("create");
  }});    
}

function onNodeClick() {
  console.log(this);
  var node_id = $(this).attr('data-node-id');
  $('#stream').empty();
  loadNode(node_id);
  var node_list_select = $('#node_select');
  node_list_select.find('option').removeAttr('selected')
  node_list_select.find('option[value="'+node_id+'"]').attr('selected', 'true');
  $('#page-post-new').trigger("create");
  $('#post_save').on("click", function() {
    var node_id = $('#page-post-new [name="node"]').val();
    var title = $('#page-post-new [name="title"]').val();
    var content = $('#page-post-new [name="content"]').val();
    var data = {'node':node_id, 'title':title, 'content': content }
    $.ajax({url:"/api/post/create", 
	    type: "POST",
	    data: data,
	    dataType:'json',
	    success:function(data) {
	      //alert(data);  
	    }});
  });
  
}
function loadNode(node_id, cursor) {
  console.log(node_id);
  cursor = cursor ? cursor : ""
  $.ajax({url:"/api/node/"+node_id+"/stream/" + cursor, 
	  dataType:'json',
	  success:function(data) {
    for (p in data.posts) {
      post = data.posts[p];
      console.log(post.title)
      stream = $('<ul data-role="listview" data-inset="true"></ul>')

      var li = $('<li></li>');
      var a = $('<a href="#page-post-detail" data-transition="slide"></a>').attr('data-post-id',post.id).on('click', function() {
	loadPost($(this).attr('data-post-id'));
      });
      a.append($('<h2></h2>').text(post.title))
       .append($('<p></p>').html(post.content_summary.substring(0, 50)))
       .append($('<p class="ui-li-aside"></p>').html(post.node.name));
      if(post.images.length > 0) {
       a.append($('<img></img>').attr('src', post.images[0]))
      }
      stream.prepend(
       li.append(a)
      );
      $('#stream').append(stream);
    }
    $('#load_more').on('click', function(){loadNode(node_id, data.next_cursor);});
    $('#page-stream').trigger("create");
  }});
  
}

function getPrevBizDay(date) {
  var dt = date;
  while(dt.getDay()>5 || dt.getDay()==0) {
    dt = new Date(dt.getFullYear(), dt.getMonth(), dt.getDate()-1)
  }
  return dt;
}

function getNextBizDay(date) {
  var dt = date;
  while(dt.getDay()>5 || dt.getDay()==0) {
    dt = new Date(dt.getFullYear(), dt.getMonth(), dt.getDate()+1)
  }
  return dt;
}

function getDateFromStr(date_str) {
  var date_v = date_str.split("-");
  date = new Date(date_v[0], date_v[1]-1, date_v[2]);
  return date;
}

$(document).bind( "pageloadfailed", function( event, data ){

	// Let the framework know we're going to handle things.
	event.preventDefault();

	window.location.href="/eauth/login?next="+data.absUrl;
	//$.mobile.changePage("#page-login");
	data.deferred.reject( data.absUrl, data.options );
});  
 
$("#page-menu").bind('swipeleft', function(event) {
  $.mobile.showPageLoadingMsg();
  var cur_date = $('#data');   
  var cur_sk = $('#cm');    
  var date = getDateFromStr(cur_date.val());
  var next_date = getNextBizDay(new Date(date.getFullYear(), date.getMonth(), date.getDate()+1));  
  if(next_date) initUI(userpappami, cur_sk.val().substring("sk-pappa-mi-".length), next_date);
});
  
$("#page-menu").bind('swiperight', function(event) {
  $.mobile.showPageLoadingMsg();
  var cur_date = $('#data');    
  var cur_sk = $('#cm');    
  date = getDateFromStr(cur_date.val());
  next_date = getPrevBizDay(new Date(date.getFullYear(), date.getMonth(), date.getDate()-1));  
  if(next_date) initUI(userpappami, cur_sk.val().substring("sk-pappa-mi-".length), next_date);
});

$("#page-menu").bind('pagebeforeshow', function(event){ 
  console.log("Schools page...");
  /*$("#page-menu").find('span[data-v-title]').text(userpappami.fullname);
  if (pappami.resetMenu){
    //entry.refs.menuAnc.empty();
  } else {*/
    $("#page-menu").find('span[data-role="button"]').each(function(){
      var e = $(this);
    });
  //}  
}); 

var back = function(){
  $.mobile.changePage("#page-menu");
  return false;
};

function initUI(userpappami, sk, dt) {
  var params = $('<fieldset id="params" data-role="controlgroup" data-type="vertical"><select id="cm" name="school" data-mini="true" data-native-menu="false"/><select id="data" name="cm" data-mini="true" data-native-menu="false"/></fieldset>');
  //var params = $('<select id="cm" name="school" data-mini="true" data-native-menu="true"/><div data-role="controlgroup" data-type="horizontal"><a href="#" data-role="button" data-mini="true" data-inline="true" data-icon="arrow-l">&nbsp</a><select id="data" name="data" data-role="button" data-mini="true" data-inline="true" data-native-menu="true"/><a href="#" data-inline="true" data-mini="true" data-role="button" data-icon="arrow-r" data-iconpos="right">&nbsp</a></div>');
  var sel_sk = params.find("#cm");
  var sel_date = params.find("#data");
  
  for( school in userpappami.schools) {
    sel_sk.append( $("<option>").attr("value", "sk-pappa-mi-" + userpappami.schools[school].id).text(userpappami.schools[school].name));
  }     
  sel_sk.find("option[value='" + "sk-pappa-mi-" + sk + "']").attr("selected",1);
  
  for( i=-7;i<=7;i++) {
   date = new Date(dt.getFullYear(), dt.getMonth(), dt.getDate()-i);

   if(date.getDay()<6 && date.getDay()>0) {
    var d = $("<option>");
    if(date.getTime() == dt.getTime()){      
      d.attr("selected",1);
    }
    sel_date.append( d.attr("value", date.getFullYear()+"-"+(date.getMonth()+1)+"-"+date.getDate()).text(date.toLocaleDateString("it")));
   }
  }
  
  $('#page-menu').find('[data-role="content"]').html(params).trigger("create");
  
  sel_date.change( loadMenu );
  sel_sk.change( loadMenu );
  
  sel_date.trigger("change");
}

var menu = {};
function loadMenu() {
  
  var date = $('#data').val(); 
  var cm = $('#cm').val();
  
  var date_d = getDateFromStr(date);
  var today = getPrevBizDay(new Date());
  
  $.ajax({url:"/api/menu/"+cm.substring("sk-pappa-mi-".length)+'/'+date,
	dataType:'json',
	success:function(data) { 
    menu = data;
  
    var list = [];
    for (var k in menu){
      list.push(menu[k]);
    };
  
    var template = '';
    template += '<table class="pappa-mi-menu">';
    template += '{{#list}}'; 
    template += '<tr data-veespo-id="demo-pappa-mi-{{id}}">';
    template += '<td class="left">{{desc1}}</td>';
    
    if(today.getTime() >= date_d.getTime()) {
      template += '<td class="right"><span data-role="button" data-mini="true" data-icon="plus" data-iconpos="right">Vota</span></td>';
    } else {
      template += '<td class="right"><span data-role="button" data-mini="true" data-icon="plus" data-iconpos="right" class="ui-disabled">Vota</span></td>';
    }
    template += '</tr>';
    template += '{{/list}}'; 
    template += '</table>';
  
    var html = $(Mustache.to_html(template, {list:list} ));
    $('#menu').html($(html)).trigger("create");
    
    $.mobile.hidePageLoadingMsg();
       
    $('#menu').find('span[data-role="button"]').bind('tap', function(evt){
      var title = getDish(id.substring('demo-pappa-mi-'.length)).desc1;
    });
  }});
}

/*
 * Torna l'oggetto relativo al id del piatto passato
 */
function getDish(id){
  for(dish in menu) {
    if(menu[dish].id == id){
      return menu[dish];
    }
  }
  throw(new Error("Failed to find dish: " + id));
};
