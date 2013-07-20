"use strict";

var current_user = "";
var guest_user_id = 0;

function setCookie(c_name, value, exdays) {
    var exdate = new Date();
    exdate.setDate(exdate.getDate() + exdays);
    var c_value = escape(value) + ((exdays == null) ? "" : "; expires=" + exdate.toUTCString());
    document.cookie = c_name + "=" + c_value;
}

function getCookie(c_name) {
    var i, x, y, ARRcookies = document.cookie.split(";");
    for (i = 0; i < ARRcookies.length; i++) {
        x = ARRcookies[i].substr(0, ARRcookies[i].indexOf("="));
        y = ARRcookies[i].substr(ARRcookies[i].indexOf("=") + 1);
        x = x.replace(/^\s+|\s+$/g, "");
        if (x == c_name) {
            return unescape(y);
        }
    }
}

function isUserLogged() {
 return current_user.type != "O";
}

function isUserCM() {
 return current_user.type == 'C';
}

$(document).ready(function(){
  var channel_id = $('body').attr('data-channel-id');
  if(channel == "" && channel_id != "") {
    channel = openChannel(channel_id);
  }
  getVotesTag();
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
    
    if(!isUserLogged() && getCookie('school_id')) {
      current_user.schools = [{id: getCookie('school_id'),
			       name: getCookie('school_name')}];
    }
    if(!isUserLogged()) {
      $.ajax({url:"/api/school/"+current_user.city+"/list", 
	      dataType:'json',
	      success:function(data) { 
		  var schools_list = $('#school_list');
		  for(var school in data) {
		    school = data[school];
		    schools_list.append('<li><a href="#" data-school-id="' + school.id + '">' + school.name + '</a></li>');
		  }
		  schools_list.find('a').on('click', function() {
		      current_user.schools = [{id: $(this).attr('data-school-id'),
					       name: $(this).text()}];
		      setCookie('school_id', current_user.schools[0].id);
		      setCookie('school_name', current_user.schools[0].name);
		      var now = new Date();
		      $.mobile.changePage('#page-menu');
		      initUI(current_user, current_user.schools[0].id, getPrevBizDay(new Date(now.getFullYear(), now.getMonth(), now.getDate())));
		    });
		  if( !getCookie('school_id') ) {
    		    $.mobile.changePage('#page-school-chooser', {transition: 'fade'});
		  }
		}
	      });
	    }
    }
  });    

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
  $('#post_delete').on('click', onPostDelete);
  $('#post_reshare').on('click', onPostReshare);
  $('#post_comment').on('click', onPostComment);
  $('#post_comment_submit').on('click', onPostCommentSubmit);
  $('#post_comments_expand').on('click', onPostShowComments);
  $('#post_vote').on('click', onPostVote);
  $('#post_unvote').on('click', onPostVote);
});

var channel = "";

function initCheck(event, entry) { 
  $.mobile.showPageLoadingMsg();

  if(current_user=="") {
    window.location.href="/mobile/app";
  }
}

$("#page-dish-detail").bind('pageinit', initCheck);
$("#page-dish-stat").bind('pageinit', initCheck);
$("#page-dish-vote").bind('pageinit', initCheck);

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

function onPostDelete() {
  var post_id = $(this).parents('[data-post-id]').attr('data-post-id');
  
  if(confirm("Cancellare il post?")) {
    $.ajax({url:"/api/post/"+post_id+'/delete', 
	    dataType:'json',
	    success:function(data) { 
	$.mobile.navigate('/mobile/app');
      }});
    
  }
}

function onPostReshare() {
}

function onPostVote() {
  var post_id = $(this).parents('[data-post-id]').attr('data-post-id');

  var data = {vote: $(this).attr('data-vote')};

  $.ajax({url:"/api/post/"+post_id+'/vote', 
	  type: 'POST',
	  dataType:'json',
	  data: data,
	  success:function(data) { 

      $('#vote_num').text(data.votes);
      if(data.vote == '1') {
	$('#post_vote_c').hide();
	$('#post_unvote_c').show();
      } else {
	$('#post_vote_c').show();
	$('#post_unvote_c').hide();
      }
  }});
}

function onPostShowComments() {
  var post_id = $(this).parents('[data-post-id]').attr('data-post-id');

  $.ajax({url:"/api/post/"+post_id+'/comment', 
	  type: 'GET',
	  dataType:'json',
	  success:function(data) { 
	    var comments = data.comments;
	    var comment_list = $('#comment_list');
	    comment_list.empty();
	    for ( var comment in comments ) {
	      comment = comments[comment];
	      var li = $('<li></li>');
	      li.append('<img class="avatar" src="'+comment.author.avatar+'"></img>');
	      li.append('<span>'+comment.author.name+'</span>');
	      li.append('<p>'+comment.content+'</p>');
	      comment_list.append(li);
	      $('#comment_add').show();
	    }
  }});
}

function onPostComment() {
  var post_id = $(this).parents('[data-post-id]').attr('data-post-id'); 
  $('#page-post-comment').find('#post_id').attr('data-post-id', post_id);
  onPostShowComments();
  $.mobile.changePage('#page-post-comment');
}

function onPostCommentSubmit() {
  var post_id = $(this).parents('[data-post-id]').attr('data-post-id'); 
  var data = {content: $('#comment_content').val()}
  $.ajax({url:"/api/post/"+post_id+'/comment', 
	  type: 'POST',
	  dataType:'json',
	  data: data,
	  success:function(data) { 
	  var comments = data.comments;
	  var comment_list = $('#comment_list');
	  for ( var comment in comments ) {
	    comment = comments[comment];
	    var li = $('<li></li>');
	    li.append('<img class="avatar" src="'+comment.author.avatar+'"></img>');
	    li.append('<span>'+comment.author.name+'</span>');
	    li.append('<p>'+comment.content+'</p>');
	    comment_list.append(li);
	  }
  }});
}

function loadPost(post_id) {
  $.ajax({url:"/api/post/"+post_id, 
	  dataType:'json',
	  success:function(data) { 
    var page_post_detail = $('#page-post-detail');
    var post = data;    
    page_post_detail.attr('data-post-id', post.id);
    page_post_detail.find('#author').text(post.author.name);
    page_post_detail.find('#avatar').attr('href', post.author.avatar);
    page_post_detail.find('#date').text(post.ext_date);
    page_post_detail.find('#title').html(post.title);
    page_post_detail.find('#content').html(post.content);
    page_post_detail.find('#comment_num').text(post.comments);
    page_post_detail.find('#vote_num').text(post.votes);
    
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
    if(isUserLogged()){     
      if(post.canadmin) {
	$('#post_delete').show();
      } else {
	$('#post_delete').hide();
      }
      if(post.cancomment && post.comments == 0) {
	$('#comment_add').show();
      } else {
	$('#comment_add').hide();
      }
      if(post.canvote) {
	$('#post_vote_c').show();
	$('#post_unvote_c').hide();
      } else {
	$('#post_vote_c').hide();
	$('#post_unvote_c').show();
      }      
      page_post_detail.find('#post_commands').show();
    } else {
      page_post_detail.find('#comment_add').hide();
      page_post_detail.find('#post_commands').hide();
    }
    page_post_detail.trigger("create");
    $.mobile.changePage('#page-post-detail', {transition:'slide'});
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
      $.mobile.changePage( "#page-stream" );
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
   a.append($('<img></img>').attr('src', post.images[0]));
  }
  if(post.comments > 0) {
   a.append($('<p class="ui-li-aside">Commenti: ' + post.comments + '</p>'));
  }
  if(post.votes > 0) {
   a.append($('<p class="ui-li-aside">Voti: ' + post.votes + '</p>'));
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

function initUI(current_user, sk, dt) {
  var params =  $('<fieldset id="params" data-role="controlgroup" data-type="vertical"></fieldset>');
  if(isUserLogged()) {
    params.append($('<select id="cm" name="school" data-mini="true" data-native-menu="false"/>'));  
  } else {
    params.append($('<input id="cm" type="hidden" name="cm" value="'+current_user.schools[0].id+'"/>')); 
    params.append($('<button data-mini="true">'+current_user.schools[0].name+'</button>').on('click', function() {
      $.mobile.changePage('#page-school-chooser');
    }));  
  }
  params.append($('<select id="data" name="cm" data-mini="true" data-native-menu="false"/>'))  
  
  var sel_sk = params.find("#cm");
  var sel_date = params.find("#data");
  
  if(isUserLogged()) {  
    for( var school in current_user.schools) {
      sel_sk.append( $("<option>").attr("value", current_user.schools[school].id).text(current_user.schools[school].name));
    }     
    sel_sk.find("option[value='" + sk + "']").attr("selected",1);
  }  
  
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
  $('.dish_name').text(dish_name);

  $.ajax({url:"/api/dish/"+dish_id+"/"+school_id, 
	  type: "GET",
	  dataType:'json',
	  success:function(data) {
	    //initVeespo(current_user.id, dish_id, dish_name);

	    $('#dish_components').empty();
	    var dish_info = data;
	    var components = dish_info["components"];
	    for (var nc in components) {
	      var comp = components[nc];
	      var tr = $('<tr></tr>').append('<td>' + comp['name'] + '</td>'+'<td>' + comp['qty'] + '</td>');
	      $('#dish_components').append(tr);
	    }
	    $('#page-dish-detail').attr('data-dish-id', dish_id);
  	    $.mobile.changePage( "#page-dish-detail", {transition:'slide'});
	  }});  
}

function onDishStat() {
  var dish_id = $(this).parents('[data-dish-id]').attr('data-dish-id');
  var dish_name = getDish(dish_id).desc1;
  
  getVotesAvg(dish_id, function() {
    var vote_map = createVoteMap(dish_id);
    createVoteChart(dish_id, vote_map, "dish_stat_graph");
    createVoteTable(dish_id, vote_map, "dish_stat_table");
  
    $.mobile.changePage( "#page-dish-stat", {transition:'flip'} );
  });
}

function onDishVote() {
  var dish_id = $(this).parents('[data-dish-id]').attr('data-dish-id');
  var dish_name = getDish(dish_id).desc1;
  $.mobile.changePage( "#page-dish-vote", {transition:'flip'});
  createWidget(current_user.id, dish_id, dish_name);
}

var context = {
  apiKey:"apk-f7adfcbc-7279-3107-15d0-cbf4bca01496", 
  group:"group-vsite", 
  lang:"it", 
  enviroment:"production",
  custom_button: 'http://www.pappa-mi.it/img/pappa-mi-logo.png'
};

var veespo_api_const = {
category: 'ctg-f86fbf9e-b53b-e7a5-d75d-57139ea6541d',
api_tag_list: 'http://production.veespo.com/v1/tag-frequency/category/ctg-f86fbf9e-b53b-e7a5-d75d-57139ea6541d?lang=it',
api_vote_avg: 'http://production.veespo.com/v1/average/target/',
api_last_vote: "http://production.veespo.com/v1/ratings/user/:user_id/target/:target_id"
};

var tag_map;
var vote_avg = Object();

function getVotesAvg(dish_id, success) {
  $.getJSON(veespo_api_const.api_vote_avg + 'tgt-pappa-mi-dish-' + dish_id+'?callback=?').then(function(json) {
	    vote_avg[dish_id] = json.data;
	    success();
	  });
}

function getVotesTag() {
  $.getJSON(veespo_api_const.api_tag_list+'&callback=?').then(function(json) {
	    tag_map = json.data;
	    tag_map["id-0"]={"freq":0,"label":"Complessivo"};
	  });
}

function getLastVote(user_id, dish_id, success) {
  var url = veespo_api_const.api_last_vote.replace(":user_id", "pappa-mi-user-"+user_id).replace(":target_id", "tgt-pappa-mi-dish-"+dish_id);
  $.getJSON(url+"?callback=?").then(function(json) {
    var votes = json.data;
    if(success) {
      success(votes);
    }
  });
}

function createWidget(user_id, dish_id, dish_name) {
  context.title = dish_name;
  context.targetId = "tgt-pappa-mi-dish-"+dish_id;
  context.userId = "pappa-mi-user-"+current_user.id;

  $("#widget_vote").veespo('widget.inject-to-dom',{context:context}).then(function(response) {
    if (response.code == 1) {     
      getLastVote(current_user.id, dish_id, function(votes) {
	getVotesAvg(dish_id, function() {
	  var vote_map = createVoteMap(dish_id, votes);
	  createVoteChart(dish_id, vote_map, "dish_stat_graph");
	  createVoteTable(dish_id, vote_map, "dish_stat_table");
	  $.mobile.changePage('#page-dish-stat', {transition:'flip'});
	});
      });
    }
  });
}

function createVoteMap(dish_id, votes) {
  console.log("votes: " + JSON.stringify(votes));
  console.log("avgs: " + JSON.stringify(vote_avg[dish_id].avgS));
  var vote_map = {};
  var dish_votes_avg = vote_avg[dish_id].avgS;
  for( var vote in dish_votes_avg ) {
    if(tag_map[vote]) {
      vote_map[vote] = {label:tag_map[vote].label,
			avg: dish_votes_avg[vote],
			rating: ""};
    }
  }
  if( votes ) {
    for(var vote in votes) {
      var vote = votes[vote];
      if( vote_map[vote.tag] ) {
	vote_map[vote.tag].rating = vote.rating;
      }
    }
  }
  console.log(JSON.stringify(vote_map));
  return vote_map;
}

function createVoteChart(dish_id, vote_map, chart_element_id) {  
  var cdata = {labels: [], datasets: []};
  cdata.datasets[0] = { fillColor : "rgba(127,255,127,0.5)",
			strokeColor : "rgba(127,255,127,1)",
			pointColor : "rgba(0,255,0,1)",
			pointStrokeColor : "#fff",
			data: []};
  if(vote_map['id-0'].rating != "") {
    cdata.datasets[1] = { fillColor : "rgba(127,127,255,0.5)",
			  strokeColor : "rgba(127,127,255,1)",
			  pointColor : "rgba(0,0,255,1)",
			  pointStrokeColor : "#fff",
			  data: []};
  }
  for( var vote in vote_map ) {
    var vote = vote_map[vote];
    cdata.labels.push(vote.label);
    cdata.datasets[0].data.push(vote.avg);
    if(vote_map['id-0'] && vote_map['id-0'].rating) {
      cdata.datasets[1].data.push(vote.rating);
    }
  }
  var radar = new Chart(document.getElementById(chart_element_id).getContext("2d")).Radar(cdata,{scaleShowLabels : false, pointLabelFontSize : 10});
}

function createVoteTable(dish_id, vote_map, table_id) {
  var thead = $('#'+ table_id).find('thead');
  thead.empty();
  var tr = $('<tr></tr>');
  tr.append('<td>Caratteristica</td>');
  tr.append('<td><span style="color:rgb(0,255,0);">Media</span></td>');
  if(vote_map['id-0'].rating!=""){
    tr.append('<td><span style="color:rgb(0,0,255);">Mio voto</span></td>');
  }
  thead.append(tr);

  var tbody = $('#'+ table_id).find('tbody');
  tbody.empty();
  
  for( var vote in vote_map ) {
    var vote = vote_map[vote];
    var tr = $('<tr></tr>');
    tr.append('<td>'+vote.label+'</td>');
    tr.append('<td>'+vote.avg+'</td>');
    if(vote_map['id-0'].rating!=""){
      tr.append('<td>'+vote.rating+'</td>');
    }
    tbody.append(tr);
  }

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
