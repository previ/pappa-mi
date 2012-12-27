var infowindow;
var locations = {};
var list;
var xml = null;
var map;
var iLast;
var locArray;
var offset = 0;
var markersArray = [];
var lat;
var lon;
var time_left;
var floodErrorTimer;
var image = new google.maps.MarkerImage('http://google-maps-icons.googlecode.com/files/school.png',
      new google.maps.Size(32, 37),
      new google.maps.Point(0,0),
      new google.maps.Point(16, 37));
var shadow = new google.maps.MarkerImage('http://google-maps-icons.googlecode.com/files/shadow.png',
      new google.maps.Size(51, 37),
      new google.maps.Point(0,0),
      new google.maps.Point(16, 37));
var fluster = null;
var fstyles = {
  // This style will be used for clusters with more than 0 markers
  0: {
	  image: 'http://gmaps-utility-library.googlecode.com/svn/trunk/markerclusterer/1.0/images/m1.png',
	  textColor: '#FFFFFF',
	  width: 53,
	  height: 52
  },
  // This style will be used for clusters with more than 10 markers
  10: {
	  image: 'http://gmaps-utility-library.googlecode.com/svn/trunk/markerclusterer/1.0/images/m2.png',
	  textColor: '#FFFFFF',
	  width: 56,
	  height: 55
  },
  20: {
	  image: 'http://gmaps-utility-library.googlecode.com/svn/trunk/markerclusterer/1.0/images/m3.png',
	  textColor: '#FFFFFF',
	  width: 66,
	  height: 65
  }
};

var tiny_mce_opts = {
  // Location of TinyMCE script
  script_url : '/js/tiny_mce/tiny_mce.js',     
  // General options
  width : "100%",
  //height: "300px",
  content_css : "/js/tiny_mce/themes/advanced/skins/default/custom_content.css",
  theme_advanced_font_sizes: "10px,12px,13px,14px,16px,18px,20px",
  font_size_style_values : "10px,12px,13px,14px,16px,18px,20px",  
  theme : "advanced",
  plugins : "autolink, autoresize", 
  theme_advanced_buttons1 : "bold,italic,underline,separator,strikethrough,bullist,numlist,undo,redo",
  theme_advanced_buttons2 : "",
  theme_advanced_buttons3 : "",			
  theme_advanced_toolbar_location : "top",
  theme_advanced_toolbar_align : "left",
  theme_advanced_resizing : false     
};

$(document).ready(function() { 
  $('#post_content_text,#node_description_text,#reply_message').tinymce({
    // Location of TinyMCE script
    script_url : '/js/tiny_mce/tiny_mce.js',     
    // General options
    width : "100%",
    //height: "300px",
    content_css : "/js/tiny_mce/themes/advanced/skins/default/custom_content.css",
    theme_advanced_font_sizes: "10px,12px,13px,14px,16px,18px,20px",
    font_size_style_values : "10px,12px,13px,14px,16px,18px,20px",  
    theme : "advanced",
    plugins : "autolink, autoresize", 
    theme_advanced_buttons1 : "bold,italic,underline,separator,strikethrough,bullist,numlist,undo,redo",
    theme_advanced_buttons2 : "",
    theme_advanced_buttons3 : "",			
    theme_advanced_toolbar_location : "top",
    theme_advanced_toolbar_align : "left",
    theme_advanced_resizing : false     
   });
});

function initPost() {
  $("#reply_form").validate({
	  errorClass: "error",
	  errorPlacement: function(error, element) {
	  var item = $(element);
	  item.tooltip({title:error.text(), trigger:'manual'});
	  item.tooltip('show');
  },
  highlight: function(element, errorClass, validClass) {
	  var item = $(element).parents(".form_parent");
	  item.addClass(errorClass); 
  },
  unhighlight: function(element, errorClass, validClass) {
	  var item = $(element).parents(".form_parent");
	  item.removeClass(errorClass); 
	  $(element).tooltip('hide');
  },  
  rules: {}
  });
  
  $('#new_comment_form').ajaxForm({clearForm: true, dataType:'json', success: function(data) { 
    if (data.response!="success") {
      if(data.response=="flooderror"){
	onFloodError(data, function(){} )
	return			  
      }
    }
    $("#comment_list").append(data.html)
    $("#comment_submit").button("reset");
    $(document).ready(function(){
      $('.post_reply_del').click(onReplyDelete);    
      $('.post_reply_edit').click(onPostEdit);  
    });
  }, beforeSubmit: function(arr,$form) {
	  $("#comment_submit").button("loading");
	  //$('#new_comment').slideUp();
  }});	
  
  $('.post_sub').click(onPostSubscribe);
  $('.post_unsub').click(onPostUnsubscribe);
  $('.post_del').click(onPostDelete);
  $('.post_edit').click(onPostEdit);
  $('.post_reshare').click(onPostReshare);  
  $('.post_vote').click(onPostVote);  
  $('.post_unvote').click(onPostVote);  
  $('.post_reply_del').click(onReplyDelete);
  $('.post_reply_edit').click(onPostEdit);
}

function drawSocialMap(data) {
  var f_citta = $("#e_citta").val();
  var f_cc = $("#e_cc").val();
  var f_type = $("#e_tipo").val();
  var f_numcm = $("#e_numcm").val();
  jmarkers = jQuery(data);
  jmarker = jmarkers.find("marker");
  
  jmarker.each(function() {
    var marker = jQuery(this);          
    var key = marker.attr("key");
    var name= marker.attr("name")
      var latlng = new google.maps.LatLng(parseFloat(marker.attr("lat")),
                              parseFloat(marker.attr("lon")));
      var node = {key: key, latlng: latlng, name: name};
      createMarker(node)
    
  });

  if( jmarkers.find("markers").attr('cur') ) {
    offset = offset + 1;
    jQuery.get("/social/socialmap?cmd=all&cur="+jmarkers.find("markers").attr('cur')+"&offset="+offset, {}, drawMap);
  } else {
    $("#loading").hide();
    fluster.initialize();
  }
}    

function redrawSocial() {
  $("#loading").show();
  
  $("#l_citta").html($("#e_citta option[value='"+$("#e_citta").val()+"']").text());

  var myOptions = {
    zoom: 12,
    center: new google.maps.LatLng(lat,lon),
    mapTypeId: google.maps.MapTypeId.ROADMAP
  }    
  map = new google.maps.Map(document.getElementById("map"), myOptions);
  
  list.children().remove();
  list.lenght = 0;
  for (var i = 0; i < markersArray.length; i++) {
   markersArray[i].setMap(null);
  }
  markersArray.length = 0;
  offset = 0;
  
  fluster = new Fluster2(map);

  // Set styles
  // These are the same styles as default, assignment is only for demonstration ...
  fluster.styles = fstyles;
  
  jQuery.get("/social/socialmap?cmd=all", {}, drawSocialMap );
}

function loadSocialMap(_lat, _lon) {

  lat = _lat
  lon = _lon
  list = $("#left_list");

  redrawSocial();
}

function createMarker(node) {
  var marker = new google.maps.Marker({position:node.latlng, icon: image, shadow: shadow});
  fluster.addMarker(marker);
  markersArray.push(marker)

  //var html = "<div id='info'><ul class='nav nav-tabs'><li class='active'><a href='#general' data-toggle='tab'>Generale</a></li><li><a href='#contacts' data-toggle='tab'>Contatti</a></li></ul><div class='tab-contents' id='content'><div id='general'><b>Nome: " + node.name + "<br/>Tipo: " + node.type + "</b><br/>Indirizzo: " + node.address + "</div><div id='contacts'>contatti...</div></div></div>";

  var html = "<div id='info'><ul class='nav nav-tabs'><li class='active'><a href='#general' data-toggle='tab'>Generale</a></li></ul><div class='tab-contents' id='content'><div id='general'><b>Nome: " + node.name + "<br/>Tipo: " + node.type + "</b><br/>Indirizzo: " + node.address + "</div></div></div>";  
  var openiw = function (){
    if (infowindow) infowindow.close();
    infowindow = new google.maps.InfoWindow({ content: html });
    infowindow.open(map,marker);
    google.maps.event.addListener(infowindow, 'domready', function() {
      $("#tabs").tabs();
    });
  };
   
  google.maps.event.addListener(marker, 'click', openiw);
  addLocationToList(list, node, marker, openiw);

  return marker;
}

function addLocationToList(list, school, marker,openiw) {
  itm = document.createElement("div");
  itm.style.cursor = "hand";
  var html = "<b>" + school.name + " - " + school.type + "</b> <br/>" + school.address + "";
  itm.innerHTML = html;
  if(itm.addEventListener) {
    itm.addEventListener("click", openiw);
 } else {
  }
  list.append(itm);
}     

function drawSmallMap(data) {
  jmarkers = jQuery(data);
  jmarker = jmarkers.find("marker");
  
  jmarker.each(function() {
    var marker = jQuery(this);
    var name = marker.attr("nome");
    var address = marker.attr("indirizzo");
    var type = marker.attr("tipo");
    var latlng = new google.maps.LatLng(parseFloat(marker.attr("lat")),
			    parseFloat(marker.attr("lon")));
    var marker = new google.maps.Marker({position:latlng, icon: image, shadow: shadow});
    fluster.addMarker(marker);
  });

  if( jmarkers.find("markers").attr('cur') ) {
    offset = offset + 1;
    jQuery.get("/social/socialmap?cur="+jmarkers.find("markers").attr('cur')+"&offset="+offset, {}, drawSmallMap);
  } else {
    fluster.initialize();
  }
}    

function onSuccess(data){
  if(data.response=="success"){
    if(data.url) {
     window.location.href=data.url
    } else {
     window.location.reload()
    }
  }
}

function floodUpdate(){
	
	time_left -=1
	if(time_left==0){
		
		$("#flood_error").modal('hide')
	
	}
		
	
	message=time_left+" second"
	if(time_left==1)
		message=message+"o"
	else
		message=message+"i"
	
	span.html(message)
	
}



function onReplySubmitted(user,post,node){	
  if($("#reply_form").valid()){
    data= {}
    data['user']= user
    data['post']=post
    data['node']=node
    data['content']=$("#reply_message").attr("value")
	
	$.ajax({
		 type: 'POST',
		 url:'/social/managepost?cmd=create_reply_post', 
		 data: data,
		 dataType:'json',
		 success:function(data){
			
			 
			 if (data.response!="success")
				 {
				if(data.response=="flooderror")
				 {
					onFloodError(data, function(){})
					
					 return
						
				 }
			 	 }
			 
			 onSuccess(data)
			 }})
	}
}


function onPostEdit(){
  var post = $(this).parents('.s_post_root').attr("data-post-key");    
  var reply = $(this).parents('.s_reply').attr("data-reply-key");    
    
  if(reply) post = reply;
  
  var edit_post = $(".edit_post").clone();
  edit_post.find('.edit_content').attr('value', $(this).parents(".s_post_content").find('.post_content').html())
  $(this).parents(".s_post_content").find(".edit_hollow").append(edit_post);
  edit_post.find(".edit_content").tinymce(tiny_mce_opts);
  $(".s_post_commands").hide()
  $(this).parents(".s_post_content").find('.post_content').hide()

  edit_post.show();

  $(document).ready(function(){
    edit_post.find('.s_post_edit_submit').click(onPostEditSubmit);
    edit_post.find('.s_post_edit_cancel').click(onEditCancel);
  });
}

var onEditCancel = function (){
  $(".s_post_commands").show()
  $(this).parents(".s_post_content").find('.post_content').show();
  $(this).parents(".edit_hollow").empty();
}

function onPostEditSubmit(){
  var post = $(this).parents('.s_post_root').attr("data-post-key");    
  var reply = $(this).parents('.s_reply').attr("data-reply-key");    
  
  if(reply) post = reply;

  var edit_post = $(this).parents('.edit_post');
  var data = {'cmd':'edit_open_post', 'post':post, 'content': edit_post.find(".edit_content").attr("value")}
  
  $.ajax({
	  type: 'POST',
	  url:'/social/managepost', 
	  data: data,
	  dataType:'json',
	  success:function(data){
	    if (data.response!="success") {
	      if(data.response=="flooderror") {
		onFloodError(data, function(){})
		return
  	      }
	    }
	    $("#post_content_"+post).html(data.content)
	    $("#edit_hollow_"+post).empty()
	    $("#post_content_"+post).show()		   
	    $(".s_post_commands").show()
	    }})
}

function onReplyEditSubmit(){
  var post = $(this).parents('.s_post_root').attr("data-post-key");    
  var reply = $(this).parents('.s_reply').attr("data-reply-key");    
  var data = {'cmd':'edit_open_post', 'node':node, 'post':reply, 'content': $(this).parents('.edit_post').find(".edit_content").attr("value")}
  
  $.ajax({
	  type: 'POST',
	  url:'/social/managepost', 
	  data: data,
	  dataType:'json',
	  success:function(data){
	    if (data.response!="success") {
	      if(data.response=="flooderror") {
		onFloodError(data, function(){})
		return
  	      }
	    }
	    $("#post_content_"+post).html(data.content)
	    $("#edit_hollow_"+post).empty()
	    $("#post_content_"+post).show()		   
	    $(".s_post_commands").show()
	    }})
}


function onOpenPostForm(){
  if(!$('#new_post').is(':visible')){
    $("#new_post").slideDown()
  } else {
    $("#new_post").slideUp()  
  }
}

function onOpenPostFormCancel() {
  $("#new_post").slideUp()
}
	
function onPostReshare() {
  var post = $(this).parents('.s_post_root').attr("data-post-key");    
  $.ajax({
    type: 'POST',
    url:'/social/dload', 
    data: {'cmd': 'modal_reshare'},
    dataType:'json',
    success:function(data){
      $("#modal_reshare").html(data.html);
      $(document).ready(function () {
	//$("#modal_reshare").find('#b_post_reshare_submit').click(onPostReshareSubmit);
	$("#modal_reshare").find('#form_post').attr("value", post);
	$('#post_content_text').tinymce(tiny_mce_opts);
	$('form#post_reshare').ajaxForm({clearForm: true, dataType:'json', success:function(data){
	  if(data.response!="success") {
	    if(data.response=="flooderror") {
	      $("#reshare_"+post).modal('hide');
	      onFloodError(data, function(){
		$("#reshare_"+post).modal('show')
	      });
	      return
	    }
	  }
	  onSuccess(data)
	}});
      });
      $("#post_reshare").show();
      $("#post_reshare").modal();
    }});
}

function onPostVote() {
  var post_root = $(this).parents('.s_post_root');
  var post = $(this).parents('.s_post_root').attr("data-post-key");    
  var vote = $(this).attr("data-vote");  
  $.ajax({
    type: 'POST',
    url:'/social/managepost', 
    data: {'cmd': 'vote_post',
	   'post': post,
	   'vote': vote },
    dataType:'json',
    success:function(data){
      if(data.response!="success") {
	if(data.response=="flooderror") {
	  onFloodError(data, function(){
	    $("#reshare_"+post).modal('show')
	  });
	  return
	}
      }
      post_root.find('.s_post_votes').html(data.votes);
      if(parseInt(data.votes) > 0) {
	post_root.find('.s_post_votes_c').show();
      } else {
	post_root.find('.s_post_votes_c').hide();
      }      
      if(parseInt(vote) == 1) {
	post_root.find('.post_vote').hide();
	post_root.find('.post_unvote').show();
      } else {
	post_root.find('.post_vote').show();
	post_root.find('.post_unvote').hide();
      }
    }});
}

function onFloodError(data,callback){
  $(".main").append(data.html)
  $("#flood_error").modal()
  $('#flood_error').on('hide', function () {
    clearInterval( floodErrorTimer)
    $("#flood_error").remove()
    callback()
  });
  i=0
  time_left=data.time
  span=$('.seconds_left')
  time_left
  floodUpdate()
  floodErrorTimer=setInterval(function() {floodUpdate() }, 980);
}


function onReplyDelete() {
  var node = $(this).parents('.s_post_root').attr("data-node-key");
  var post = $(this).parents('.s_post_root').attr("data-post-key");    
  var reply = $(this).parents('.s_reply').attr("data-reply-key");    
  var data= {'cmd': 'delete_reply_post', 'post': post, 'node': node, 'reply': reply}
  if( confirm("Sei sicuro di voler cancellare il commento?") ){
    $.ajax({type: 'POST',
	    url:'/social/managepost', 
	    data: data,
	    dataType:'json',
	    success:function(data){
	      $('[data-reply-key="'+reply+'"]').hide();
	      $('[data-reply-key="'+reply+'"]').remove();
	    }});
  }	  	
}

function onPostDelete(){
  var node = $(this).parents('.s_post').attr("data-node-key");
  var post = $(this).parents('.s_post').attr("data-post-key");    
  if( confirm("Sei sicuro di voler cancellare il post?") ){
    var data = {'cmd':'delete_open_post', 'post':post, 'node':node};
    $.ajax({
      type: 'POST',
      url:'/social/managepost', 
      data: data,
      dataType:'json',
      success:function(data){ window.location.href = "/social"; }});
  }	  	
}

function onPostItemDelete(){
  var post = $(this).parents('.s_post').attr("data-post-key");    
  if( confirm("Sei sicuro di voler cancellare il post?") ){
    var data = {'cmd':'delete_open_post', 'post':post };
    $.ajax({
      type: 'POST',
      url:'/social/managepost', 
      data: data,
      dataType:'json',
      success:function(data){
	      $('[data-post-key="'+post+'"]').remove();
      }});
  }	  	
}

function onPostSubscribe(){
  var post = $(this).parents('.s_post_root').attr("data-post-key");    
  var data = {'cmd':'subscribepost', 'post':post};
  $.ajax({url:'/social/subscribe',
	  data: data,
          dataType:'json',
	  success:function(data){
	    $("#postsub").hide();
	    $("#postunsub").show();
  	    $.pnotify({
	      title: 'Info',
	      text: 'Sei iscritto a questo post'
	    });
	  }
	 });
}

function onPostUnsubscribe(post){
  var post = $(this).parents('.s_post_root').attr("data-post-key");    
  var data = {'cmd':'unsubscribepost', 'post':post};
  $.ajax({url:'/social/subscribe',
	  data: data,
          dataType:'json',
	  success:function(data){
	    $("#postsub").show();
	    $("#postunsub").hide();
	    $.pnotify({
	      title: 'Info',
              text: 'Non sei più iscritto a questo post'
	    });
	  }
	});	
}

function loadSmallMap(lat,lon) {
  var myOptions = {
    zoom: 4,
    center: new google.maps.LatLng(lat,lon),
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    mapTypeControl: false
  }    
  var map = new google.maps.Map(document.getElementById("map"), myOptions);
  fluster = new Fluster2(map); 
  
  var image = new google.maps.MarkerImage('/img/school.png',
        new google.maps.Size(16, 18),
        new google.maps.Point(0,0),
        new google.maps.Point(8, 0));
  var shadow = new google.maps.MarkerImage('/img/shadow.png',
        new google.maps.Size(26, 19),
        new google.maps.Point(0,0),
        new google.maps.Point(8, 0));

  fluster = new Fluster2(map);

  // Set styles
  // These are the same styles as default, assignment is only for demonstration ...
  fluster.styles = fstyles;
  
  jQuery.get("/social/socialmap", {}, drawSmallMap );
}  

function onSubscription(user_key,node_key)
{
	 $.ajax({url:'/social/subscribe?node='+node_key+'&user='+user_key+ '&cmd=subscribe',dataType:"JSON", success:function(data){
		  
		 onSuccess(data)
		}
	 });
	 
}

function onUnsubscription(user_key,node_key)
{
	 $.ajax({url:'/social/subscribe?node='+node_key+'&user='+user_key+ '&cmd=unsubscribe',dataType:"JSON", success:function(data){
		 onSuccess(data)
		 
		}
	 });
	 
}

function init_search(){
$('#search_text').typeahead({minLength:2,

    source: function (query, process) {

        return $.post('/social/paginate', { query: query,cmd:"search_nodes"}, function (data) {
        	data=jQuery.parseJSON(data)
        	if(data.html){
        	$("#search_result").empty().hide().html(data.html).show(200)
			}
        });
    }
});
}

function onNodeClick(){
 node_item = $(this);
 key=node_item.attr('key');
 node_item.parent().siblings(".active").removeClass("active");
 node_item.parent().addClass("active");
 $("#node_title").find("span").text(node_item.text());
 $("#node_title > a").attr("href", "/social/node/"+key);
 node_item.parent().addClass("active");
 key=node_item.attr('key');
 $("#main_stream_list").empty();
 $("#no_more_posts").hide(); 
 loadPosts(key,$("#main_stream_"+key).attr('next_cursor'))
}

function init(){
 $("#new_post_form").validate({
  errorClass: "error",
  errorPlacement: function(error, element) {
    var item = $(element);
    item.tooltip({title:error.text(), trigger:'manual'});
    item.tooltip('show');
  },
  highlight: function(element, errorClass, validClass) {
    var item = $(element).parents(".form_parent");
    item.addClass(errorClass); 
  },
  unhighlight: function(element, errorClass, validClass) {
    var item = $(element).parents(".form_parent");
    item.removeClass(errorClass); 
    $(element).tooltip('hide');
  },  
  rules: {
  }
 });
 $('#new_post_form').ajaxForm({clearForm: true, dataType:'json',success: function(data) { 
  if (data.response!="success") {
   if(data.response=="flooderror"){
    onFloodError(data)
    return			  
   }
  }
  $("#main_stream_list").prepend(data.html)
  $("#open_post_submit").button("reset");
 }, beforeSubmit: function(arr,$form) {
  $("#open_post_submit").button("loading");
  $('#new_post').slideUp();
 }});

 $("ul#node_list").find("a").click(onNodeClick);
 $("#more_posts").click(onMoreClick);

 $("#node_list").children().find("[key]")[0].click();
  $('#m_allegato_file_1').change(function(){
   $('#m_allegato_file_2').show(); 
  });
  $('#m_allegato_file_2').change(function(){
   $('#m_allegato_file_3').show();
  }); 
}

function onMoreClick(){
 key = $('#node_list > li.active a').attr('key');
 loadPosts(key,$("#main_stream").attr('next_cursor'))
}


function loadPosts(key,current_cursor){
 $.ajax({
  type: 'POST',
  url:'/social/paginate?cmd=post_main&node='+key+'&cursor='+current_cursor, 
  dataType:'json',
  success:function(data) { 
   $("#form_node").attr("value",key);
   $("#main_stream").attr("next_cursor",data.cursor)
   if(data.response=="success"){
    $("#main_stream_list").append(data.html)
    $('.post_del').click(onPostItemDelete);
   } else if(data.response="no_posts"){
   $("#no_more_posts").alert();
   $("#no_more_posts").show();   
   }
  }
 });
 //} else {
  //$("ul#node_list li").click(onNodeClick)
  //$("#node_stream_"+key).siblings().hide()
  //$("div#node_stream_"+key).show()
 //}
}
