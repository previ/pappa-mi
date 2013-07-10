"use strict"
var current_user = "";
var guest_user_id = 0;

function isUserLogged() {
 return current_user.id != guest_user_id
}

$(document).ready(function(){
  var channel_id = $('body').attr('data-channel-id');
  if(channel == "" && channel_id != "") {
    channel = openChannel(channel_id);
  }
});

$("#page-menu").bind('pageinit', function(event, entry) {
  var now = new Date()

  if(current_user=="") {
    window.location.href="/mobile/app";
  }
  initUI(current_user, current_user.schools[0].id, getPrevBizDay(new Date(now.getFullYear(), now.getMonth(), now.getDate())));
  
  $('#user').text(user.fullname); 
});

$("#page-stream").bind('pageinit', function(event, entry) {

  $.mobile.showPageLoadingMsg();
  $.ajax({url:"/api/user/current", 
	  dataType:'json',
	  success:function(data) { 

    current_user = data;    
    $('.user_info').append($('<img class="avatar"></img>').attr('src', current_user.avatar));
    $('.user_info').append($('<span></span>').text(current_user.fullname));

  }});    

  $.ajax({url:"/api/node/list", 
	  dataType:'json',
	  success:function(data) { 
    var node_lists = $('#node_lists');
    var c = $('<div data-role="collapsible"></div>');
    c.append('<h2>I tuoi argomenti</h2>');
    node_lists.append(c);
    var node_list = $('<ul data-role="listview" data-divider-theme="d"></ul>');
    var node_list_select = $('#node_select');
    c.append(node_list);

    if(isUserLogged()) {
      var all = $('<li data-mini="true"><a href="#" data-node-id="all">I tuoi argomenti</a></li>');
      all.find('a').on('click', onNodeClick);
      node_list.append(all);
    }

    var news = $('<li data-mini="true"><a href="#" data-node-id="news">Tutte le novità</a></li>');
    news.find('a').on('click', onNodeClick);
    node_list.append(news);
    if( data.subs_nodes.length) {
      for (var n = 0; n < data.subs_nodes.length;n++) {
	var node = data.subs_nodes[n];
	var li = $('<li data-mini="true"></li>');
	var a = $('<a href="#"></a>').attr('data-node-id', node.id).text(node.name).on('click', onNodeClick);
	li.append(a);
	node_list.append(li);
	node_list_select.append($('<option></option>').attr('value', node.id).text(node.name));
      }
      c.append(node_list)
    }
    if( data.active_nodes.length) {
      var c = $('<div data-role="collapsible"></div>');
      c.append('<h2>Più attivi</h2>');
      node_lists.append(c);
      var node_list = $('<ul data-role="listview" data-divider-theme="d"></ul>');
      for (var n = 0; n < (data.active_nodes.length > 5 ? 5 : data.active_nodes.length);n++) {
	node = data.active_nodes[n];
	var li = $('<li data-mini="true"></li>');
	var a = $('<a href="#"></a>').attr('data-node-id', node.id).text(node.name).on('click', onNodeClick);
	li.append(a);
	node_list.append(li);
      }
      c.append(node_list)
    }
    if( data.recent_nodes.length) {
      var c = $('<div data-role="collapsible"></div>');
      c.append('<h2>Più recenti</h2>');
      node_lists.append(c);
      var node_list = $('<ul data-role="listview" data-divider-theme="d"></ul>');
      for (var n = 0; n < (data.recent_nodes.length > 5 ? 5 : data.recent_nodes.length);n++) {
	node = data.recent_nodes[n];
	var li = $('<li data-mini="true"></li>');
	var a = $('<a href="#"></a>').attr('data-node-id', node.id).text(node.name).on('click', onNodeClick);
	li.append(a);
	node_list.append(li);
      }
      c.append(node_list);
    }
    if(isUserLogged()) {
      $('#page-stream-content').prepend('<a data-role="button" data-transition="flip" href="#page-post-new" id="create_new">Nuovo messaggio</a>');
    }
    $('#page-stream').trigger("create");
  }});
  loadNode('news');
});

var channel = "";

$("#page-notifiche").bind('pageinit', function(event, entry) { 
  $.mobile.showPageLoadingMsg();

  if(current_user=="") {
    window.location.href="/mobile/app";
  }

  $.ajax({url:"/api/user/online/list", 
	  dataType:'json',
	  success:function(data) { 
    var users_online = data;
    var user_list = $('#user_list');
    var user_to = $('#user_to');
    user_list.append('<li data-role="list-divider">In linea</li>');
    for ( var user_id in users_online ) {
      var user = users_online[user_id];
      var li = $('<li></li>');
      var a = $('<a href="#"></a>').attr('data-user-id', user_id).text(user.name).on('click', onUserClick);
      li.append(a);
      user_list.append(li);
      console.log(a.attr('data-user-id'));
      user_to.append($('<option></option>').attr('value', user_id).text("A: " + user.name));
    }
    user_list.listview('refresh');
    user_to.selectmenu();
  }});
  
  $('#message_send').on('click', onMessageSend);
  
  var channel_id = $('body').attr('data-channel-id');
  if(channel == "" && channel_id != "") {
    channel = openChannel(channel_id);
  }
});

function loadPost(post_id) {
  $.ajax({url:"/api/post/"+post_id, 
	  dataType:'json',
	  success:function(data) { 
    var page_post_detail = $('#page-post-detail');
    var post = data;    
    page_post_detail.find('#author').text(post.author.name);
    page_post_detail.find('#avatar').attr('href', post.author.avatar);
    page_post_detail.find('#date').text(post.ext_date);
    page_post_detail.find('#title').html(post.title);
    page_post_detail.find('#content').html(post.content);
    var res_list = $('<ul class="unstyled"></ul>').empty();
    for (var rn in post.resources) {
      var res = post.resources[rn]
      res_list.append($('<li></li>').append($('<a></a>').attr('href', res.url).text(res.desc)));
    }      
    page_post_detail.find('#resources').html(res_list);
    var att_list = $('<ul class="unstyled"></ul>').empty();
    for (var an in post.attachments) {
      var att = post.attachments[an]
      if (att.imgthumb) {
	att_list.append($('<li></li>').append($('<a></a>').attr('href', att.url).append($('<img></img>').attr('src', att.imgthumb))));
      } else {
	att_list.append($('<li></li>').append($('<a></a>').attr('href', att.url).text(att.desc)));
      }
    }      
    page_post_detail.find('#attachments').html(att_list);    
    page_post_detail.trigger("create");
    $.mobile.navigate('#page-post-detail');
  }});    
}

function onNodeClick() {
  console.log(this);
  var node_id = $(this).attr('data-node-id');
  $('#post_list').empty();
  loadNode(node_id);
  var node_list_select = $('#node_select');
  node_list_select.find('option').removeAttr('selected')
  node_list_select.find('option[value="'+node_id+'"]').attr('selected', 'true');
  node_list_select.selectmenu(); 
  $('#node-panel').panel('close');
}

function onUserClick() {
  console.log(this);
  var user_id = $(this).attr('data-user-id');
  var user_to = $('#user_to');
  user_to.find('option').removeAttr('selected')
  user_to.selectmenu('refresh'); 
  user_to.find('option[value="'+user_id+'"]').attr('selected', 'true');
  user_to.selectmenu('refresh');    
}

function onMessageSend() {
  var user_id = $('#user_to').val();
  var message = $('#message').val();
  var data = {'user': user_id,
	      'message': message}
  $.ajax({url:"/api/message/send", 
	  type: "POST",
	  data: data,
	  dataType:'json',
	  success:function(data) {
	  }});
}

function onChannelMessage(m){
  console.log(m.data);
  var m = jQuery.parseJSON(m.data);
  var textmessage=""
  if(m.type=='message') {
    textmessage = '<strong>'+m.user+'</strong>: '+m.body;
  } else if(m.type=='post'|| m.type=='comment') {
    textmessage = m.user + ' ha aggiunto un <a href="' + m.source_uri +'">' + m.source_desc + '</a> su <a href="' + m.target_uri + '">' + m.target_desc + '</a>';
  }
  $('#message_list').append($('<li></li>').append(textmessage));
  $('#message_list').listview('refresh');
}

function openChannel(channel_id) {
    channel = new goog.appengine.Channel(channel_id);
    var socket = channel.open();
    socket.onopen = function (){/*alert("channel opened")*/};
    socket.onmessage = onChannelMessage;
    socket.onerror = function (){/*alert("error")*/};
    socket.onclose = function (){/*alert("channel closed")*/};
    return socket;
}

function loadNode(node_id, cursor) {
  console.log(node_id);
  cursor = cursor ? cursor : ""
  $('#post_list').attr('data-node-id', node_id);
  $('#load_more').on('click', function(){loadPostList($('#post_list').attr('data-node-id'), $('#post_list').attr('data-next-cursor'));});
  loadPostList(node_id);
  $('#form_post_new').ajaxForm({dataType:'json', success:function(data) {
      var post = data;
      $('#post_list').prepend(createPostItem(post));
      $('#post_list').listview("refresh");
      $.mobile.navigate( "#page-stream" );
  }});
}

function loadPostList(node_id, cursor) {
  cursor = cursor ? cursor : ""
  $.mobile.showPageLoadingMsg();
  $.ajax({url:"/api/node/"+node_id+"/stream/" + cursor, 
	  dataType:'json',
	  success:function(data) {
    var post_list = $('#post_list');
    for (var p in data.posts) {
      var post = data.posts[p];      
      post_list.append(createPostItem(post));
    }
    $('#post_list').attr('data-next-cursor', data.next_cursor);
    post_list.listview("refresh");
    $.mobile.hidePageLoadingMsg();
  }});
  
}

function createPostItem(post) {
  var lit = $('<li data-role="list-divider"><img src="'+post.author.avatar+'" alt="Autore" style="left:8px;top:8px;" class="ui-li-icon ui-corner-none"><span class="s_post_title">'+post.title.substring(0,20)+'</span><span class="ui-li-aside"><div class="s_post_node">' + post.node.name +'</div><div class="s_post_author"> di '+ post.author.name + ' </div><div class="s_post_date">' + post.ext_date +'</div></span></li>');
  var li = $('<li></li>');
  var a = $('<a href="#" data-transition="slide"></a>').attr('data-post-id',post.id).on('click', function() {
    loadPost($(this).attr('data-post-id'));
  });
  if(post.images.length > 0) {
   a.append($('<img></img>').attr('src', post.images[0]))
  }
  a.append($('<span class="s_post_content"></span>').append(post.content_summary));
  //a.append($('<p class="ui-li-aside"><small>' + post.node.name +' di '+ post.author.name + ' ' + post.ext_date +'</small></p>'));
  li.append(a);
  return [lit, li]
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
  var date = new Date(date_v[0], date_v[1]-1, date_v[2]);
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
  if(next_date) initUI(current_user, cur_sk.val(), next_date);
});
  
$("#page-menu").bind('swiperight', function(event) {
  $.mobile.showPageLoadingMsg();
  var cur_date = $('#data');    
  var cur_sk = $('#cm');    
  var date = getDateFromStr(cur_date.val());
  var next_date = getPrevBizDay(new Date(date.getFullYear(), date.getMonth(), date.getDate()-1));  
  if(next_date) initUI(current_user, cur_sk.val(), next_date);
});

$("#page-menu").bind('pagebeforeshow', function(event){ 
  console.log("Schools page...");
    $("#page-menu").find('span[data-role="button"]').each(function(){
      var e = $(this);
    });
}); 

var back = function(){
  $.mobile.changePage("#page-menu");
  return false;
};

function initUI(current_user, sk, dt) {
  var params = $('<fieldset id="params" data-role="controlgroup" data-type="vertical"><select id="cm" name="school" data-mini="true" data-native-menu="false"/><select id="data" name="cm" data-mini="true" data-native-menu="false"/></fieldset>');
  //var params = $('<select id="cm" name="school" data-mini="true" data-native-menu="true"/><div data-role="controlgroup" data-type="horizontal"><a href="#" data-role="button" data-mini="true" data-inline="true" data-icon="arrow-l">&nbsp</a><select id="data" name="data" data-role="button" data-mini="true" data-inline="true" data-native-menu="true"/><a href="#" data-inline="true" data-mini="true" data-role="button" data-icon="arrow-r" data-iconpos="right">&nbsp</a></div>');
  var sel_sk = params.find("#cm");
  var sel_date = params.find("#data");
  
  for( var school in current_user.schools) {
    sel_sk.append( $("<option>").attr("value", current_user.schools[school].id).text(current_user.schools[school].name));
  }     
  sel_sk.find("option[value='" + sk + "']").attr("selected",1);
  
  for( var i=-7;i<=7;i++) {
   var date = new Date(dt.getFullYear(), dt.getMonth(), dt.getDate()-i);

   if(date.getDay()<6 && date.getDay()>0) {
    var d = $("<option>");
    if(date.getTime() == dt.getTime()){      
      d.attr("selected",1);
    }
    sel_date.append( d.attr("value", date.getFullYear()+"-"+(date.getMonth()+1)+"-"+date.getDate()).text(date.toLocaleDateString("it")));
   }
  }
  
  $('#menu_form').html(params).trigger("create");
  
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
  
  $.ajax({url:"/api/menu/" + cm +'/'+date,
	dataType:'json',
	success:function(data) { 
    menu = data;
    
    var ul = $('#menu_list').empty();
    for (var dish_id in menu) {
      var dish =menu[dish_id];
      var li = $('<li></li>').attr('data-dish-id', dish.id);
      var a = $('<a class="dish_info" href=""></a>').text(dish.desc1);
      li.append(a);
      ul.append(li);
    }
    $('#menu_list').trigger("create");
    ul.listview('refresh');

    $('#menu').trigger("create");
    $('.dish_info').on('click', onDishInfo);
    $('.dish_stat').on('click', onDishStat);
    $('.dish_vote').on('click', onDishVote);
    
    $.mobile.hidePageLoadingMsg();
    }});
}

function onDishInfo() {
  var dish_id = $(this).parents('li').attr('data-dish-id');
  var school_id = $('#cm').val();
  var dish_name = getDish(dish_id).desc1
  $('#dish_name').text(dish_name);

  $.ajax({url:"/api/dish/"+dish_id+"/"+school_id, 
	  type: "GET",
	  dataType:'json',
	  success:function(data) {
	    $('#dish_components').empty();
	    var dish_info = data;
	    var components = dish_info["components"];
	    for (var nc in components) {
	      var comp = components[nc];
	      var tr = $('<tr></tr>').append('<td>' + comp['name'] + '</td>'+'<td>' + comp['qty'] + '</td>');
	      $('#dish_components').append(tr);
	    }
	    $('#page-dish-detail').attr('data-dish-id', dish_id);
  	    $.mobile.navigate( "#page-dish-detail" );
	  }});  
}

function onDishStat() {
  var dish_id = $(this).parents('[data-dish-id]').attr('data-dish-id');
  var dish_name = getDish(dish_id).desc1
  alert("Stats for: " + dish_name);
}

var _veespo_push = _veespo_push || [];
var handler = function(response) {
      alert("Grazie per il tuo feedback.");
};
_veespo_push.push(['widget.button-modal','target_tgt-aee57d3e-9742-d5dd-64b3-bcca9bdb4a17',{handler:handler}]);

function onDishVote() {
  var dish_id = $(this).parents('[data-dish-id]').attr('data-dish-id');
  var dish_name = getDish(dish_id).desc1    
}
/*
 * Torna l'oggetto relativo al id del piatto passato
 */
function getDish(id){
  for(var dish in menu) {
    if(menu[dish].id == id){
      return menu[dish];
    }
  }
  throw(new Error("Failed to find dish: " + id));
};
