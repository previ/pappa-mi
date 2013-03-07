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

/*
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
*/

function drawSocialMap(data) {
  var f_citta = $("#e_citta").val();
  var f_cc = $("#e_cc").val();
  var f_type = $("#e_tipo").val();
  var f_numcm = $("#e_numcm").val();
  jmarkers = jQuery(data);
  jmarker = jmarkers.find("marker");
  
  jmarker.each(function() {
    var marker = jQuery(this);          
    var key = marker.attr("data-node-key");
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

// Flood control
function onSuccess(data){
  if(data.response=="success"){
    if(data.url) {
     window.location.href=data.url
    } else {
      $.pnotify({
	title: 'Info',
	text: 'Impostazioni salvate'
      });
    }
  }
}

function floodUpdate(){	
  time_left -=1
  if(time_left==0) {	  
    $("#flood_error").modal('hide')  
  }
  message=time_left+" second"
  if(time_left==1)
    message=message+"o"
  else
  message=message+"i"  
  span.html(message)
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


/*
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
*/

// Post
function getPostRootByElement(element) {
  return element.parents('[data-post-key]');
}

function getCommentRootByElement(element) {
  return element.parents('.s_comment');
}

function getPostElementByKey(post_key) {
  return $('div[data-post-key="'+post_key+'"]');
}

function getPostKeyByElement(element) {
  return getPostRootByElement(element).attr('data-post-key');
}

function initPost(post_root) {
  post_root.find("form.s_new_comment_form").validate({
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
  
  post_root.find('form.s_new_comment_form').ajaxForm({clearForm: true, dataType:'json', success: function(data) { 
    if (data.response!="success") {
      if(data.response=="flooderror"){
	onFloodError(data, function(){} )
	return			  
      }
    }
    post_root.find(".s_comment_list").append(data.html);
    post_root.find(".s_comment_submit").button("reset");
    tinymce.get('comment_content').setContent('');
  
  }, beforeSubmit: function(arr,$form) {
	  post_root.find(".s_comment_submit").button("loading");
	  //$('#new_comment').slideUp();
  }});	
  
  post_root.find('.s_post_comment').tinymce(tiny_mce_opts);
  post_root.find('.post_sub').click(onPostSubscribe);
  post_root.find('.post_unsub').click(onPostUnsubscribe);
  post_root.find('.post_del').click(onPostDelete);
  post_root.find('.post_edit').click(onPostEdit);
  post_root.find('.post_reshare').click(onPostReshare);  
  post_root.find('.post_vote').click(onPostVote);  
  post_root.find('.post_unvote').click(onPostVote);  
  initComment(post_root);
}

function initComment(element) {
  element.find('.post_comment_del').click(onCommentDelete);    
  element.find('.post_comment_edit').click(onCommentEdit);  
}

function onPostEdit(){
  var post_key = getPostKeyByElement($(this));
  var post_root = getPostRootByElement($(this));
  var post_container = $(this).parents('.s_post_container')
  var edit_post = $("#tools > .s_post_edit_form").clone();
  $.ajax({
    type: 'POST',
    url:'/social/managepost', 
    data: {'cmd': 'edit_post',
	   'post': post_key},
    dataType:'json',
    success:function(data){
      edit_post.html(data.html)
      $(document).ready(function(){
	var edit_form = edit_post.find("form");
	edit_form.ajaxForm({clearForm: true, dataType:'json', success:onEditSubmit});	
	var edit_undo = $('<div class="s_edit_undo" style="display:none;"></div>');
	edit_undo.append(post_container.contents());
	post_root.append(edit_undo);
	post_container.empty();
	post_container.append(edit_post);
	edit_post.find(".s_post_edit_content").tinymce(tiny_mce_opts);
	$(".s_post_commands").hide()
	edit_post.show()
	edit_post.find('input[name="attach_file"]').change(addAttach);
	edit_post.find('.post_attach_delete').click(onAttachDelete);  
	edit_post.find('.post_edit_cancel').click(onEditCancel);
      });
    }});
}

var onEditCancel = function (){
  var post_root = getPostRootByElement($(this));
  var post_container = $(this).parents('.s_post_container');
  var edit_undo = post_root.find('.s_edit_undo');
  post_container.empty()	
  post_container.append(edit_undo.contents())
  edit_undo.remove();
  post_root.find(".s_post_commands").show()
  post_root.find(".s_post_attachs").show()
  return false;
}

function onEditSubmit(data){
  if (data.response!="success") {
    if(data.response=="flooderror") {
      onFloodError(data, function(){})
      return
    }
  }
  getPostElementByKey(data.post).parent().html(data.html);
}

function onCommentEdit(){
  var comment_root = getCommentRootByElement($(this))
  var comment_key = comment_root.attr('data-comment-key');   
  var edit_post = $("#tools > .s_comment_edit_form").clone();
  var edit_form = edit_post.find("form");
  edit_form.find('[name="comment"]').attr('value', comment_key)
  edit_form.ajaxForm({clearForm: true, dataType:'json', success:onCommentSubmit});
  
  edit_post.find('.s_comment_edit_content').attr('value', $(this).parents(".s_post_container").find('.s_post_content').html())
  comment_root.find(".s_edit_hollow").append(edit_post);
  edit_post.find(".s_comment_edit_content").tinymce(tiny_mce_opts);
  comment_root.find(".s_post_commands").hide()
  comment_root.find('.s_post_content').hide()
  edit_post.find(".s_comment_edit_form").show()
  edit_post.show();
  edit_post.find('.post_comment_cancel').click(onCommentEditCancel);  
}

function onCommentSubmit(data){
  if (data.response!="success") {
    if(data.response=="flooderror") {
      onFloodError(data, function(){})
      return
    }
  }
  comment_root = $('[data-comment-key="'+ data.comment +'"]');
  comment_root.html(data.html);

  $(document).ready(function(){
    initComment(comment_root);
  });

}

var onCommentEditCancel = function (){
  var comment_root = getCommentRootByElement($(this))
  comment_root.find(".s_comment_edit_form").hide()  
  comment_root.find('.s_post_content').show();
  comment_root.find(".s_post_commands").show()
  comment_root.find(".s_edit_hollow").empty();
  return false;
}

/*
function onPostEditSubmit(){
  var post = $(this).parents('.s_post_root').attr("data-post-key");    
  var reply = $(this).parents('.s_comment').attr("data-reply-key");    
  
  if(reply) post = reply;

  var content = $(this).parents('.s_post_edit_form').find(".s_post_edit_content").attr("value");
  var data = {'cmd':'edit_open_post', 'post':post, 'content': content}
  
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
	    $(".s_post_edit_form").hide()
	    $(".s_post_commands").show()
	    $(".s_post_commands").show()
	    $(".s_post_attachs").show()
	    }})
}
*/

function onAttachDelete(){
  var form = getPostRootByElement($(this)).find('form.s_update_post_form');
  var attach = $(this).parents('.s_attach');  
  var attach_key = attach.attr('data-attach-key');  
  
  if(attach_key) {
    var att_delete = $('<input type="hidden" name="attach_delete">');
    att_delete.attr('value', attach_key);
    form.append(att_delete);
    attach.remove();
  } else {
    var input = $(this).parents('.s_attach').find('input[type="file"]');
    input.attr('value', '')
  }
}

/*
function onReplyEditSubmit(){
  var post = $(this).parents('.s_post_root').attr("data-post-key");    
  var reply = $(this).parents('.s_comment').attr("data-reply-key");    
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
*/

function onPostExpand() {
  var post_key = getPostKeyByElement($(this));
  var post_item = $(this).parents('.s_post_item');
  var data = {'cmd':'expand_post', 'post':post_item.attr('data-post-key') }
  
  $.ajax({
	  type: 'POST',
	  url:'/social/managepost', 
	  data: data,
	  dataType:'json',
	  success:function(data){
	    post_item.html(data.html);
	  }});
  
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
  var post = getPostKeyByElement($(this));    
  $.ajax({
    type: 'POST',
    url:'/social/dload', 
    data: {'cmd': 'modal_reshare'},
    dataType:'json',
    success:function(data){
      modal_reshare = $("#tools").find(".s_modal_reshare");
      modal_reshare.html(data.html);
      $(document).ready(function () {
	modal_reshare = $("#tools").find("#post_reshare")
	//$("#modal_reshare").find('#b_post_reshare_submit').click(onPostReshareSubmit);
	modal_reshare.find('input[name="post"]').attr("value", post);
	modal_reshare.find('#reshare_post_content_text').tinymce(tiny_mce_opts);
	modal_reshare.find('form').ajaxForm({clearForm: true, dataType:'json', success:function(data){
	  if(data.response!="success") {
	    if(data.response=="flooderror") {
	      $("#reshare_"+post).modal('hide');
	      onFloodError(data, function(){
		$("#reshare_"+post).modal('show')
	      });
	      return
	    }
	  }
	  if( $("#main_stream_list") ) {
	      $("#main_stream_list").prepend(data.html);
	      modal_reshare.modal('hide');
	      modal_reshare.empty();
	  } else {
	    onSuccess(data)
	  }
	}});
	modal_reshare.show();
	modal_reshare.modal();
      });
    }});
}

function onPostVote() {
  var post = getPostKeyByElement($(this));    
  var post_root = getPostRootByElement($(this))
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


function onCommentDelete() {
  var comment = getCommentRootByElement($(this)); 
  var comment_key = comment.attr("data-comment-key"); 
  var data= {'cmd': 'delete_comment', 'comment': comment_key}
  if( confirm("Sei sicuro di voler cancellare il commento?") ){
    $.ajax({type: 'POST',
	    url:'/social/managepost', 
	    data: data,
	    dataType:'json',
	    success:function(data){
	      comment.hide();
	      comment.remove();
	      $.pnotify({
		title: 'Info',
		text: 'Commento cancellato'
	      });
	      
	    }});
  }	  	
}

function onPostDelete(){
  var post = getPostKeyByElement($(this));    
  if( confirm("Sei sicuro di voler cancellare il post?") ){
    var data = {'cmd':'delete_open_post', 'post':post};
    $.ajax({
      type: 'POST',
      url:'/social/managepost', 
      data: data,
      dataType:'json',
      success:function(data){ window.location.href = "/social"; }});
  }	  	
}

function onPostItemDelete(){
  var post = getPostKeyByElement($(this));    
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
  var post = getPostKeyByElement($(this));    
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
  var post = getPostKeyByElement($(this));    
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


function redraw_node() {
  var subscribed = $('.node_root').attr('data-sub-status');
  var ntfy_period = $('.node_root').attr('data-ntfy-period');
  
  $('.ntfy_period > i').css('visibility', 'hidden');
  
  if( subscribed == 'true' ) {
	$('#subscribe_btn').html('Disiscriviti');
	$('#sub_prop').show();
	$('#ntfy_period_'+ ntfy_period + ' > i').css('visibility', 'visible');
  } else {
	$('#sub_prop').hide();
	$('#subscribe_btn').html('Iscriviti');
  }
}

function onSubUnsubNode() {
  var node_root = $(this).parents('.node_root');
  var node_key = node_root.attr('data-node-key');
  var sub_status = node_root.attr('data-sub-status');
  var data = {
    'node': node_key,
    'cmd': sub_status == 'true' ? 'unsubscribe' : 'subscribe'
  };
  $.ajax({url:'/social/subscribe', data: data, dataType:"JSON", success:function(data){
      node_root.attr('data-sub-status', sub_status == 'true' ? 'false' : 'true');
      onSuccess(data);
      redraw_node();
    }
  });	 
}

function onNotificationPeriod() {
  var node_root = $(this).parents('.node_root');
  var node_key = node_root.attr('data-node-key');
  var ntfy_period = $(this).attr('data-ntfy-period');
  var data = {'cmd': 'set_ntfy_period',
	      'node': node_key,
	      'ntfy_period': ntfy_period};

  $.ajax({url:'/social/subscribe',
	  data: data,
	  dataType:"JSON", 
	  success:function(data){ 
	    node_root.attr('data-ntfy-period', ntfy_period);
  	    onSuccess(data)
            redraw_node();
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
 key=node_item.attr('data-node-key');
 node_item.parent().siblings(".active").removeClass("active");
 node_item.parent().addClass("active");
 $("#node_title").find("span").text(node_item.text());
 if(key!="all") {
   $("#node_title > a").attr("href", "/social/node/"+key);
   $("#node_title > a").show();
 } else {
   $("#node_title > a").hide();
 }
 node_item.parent().addClass("active");
 //key=node_item.attr('data-node-key');
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
 $("#post_content_text").tinymce(tiny_mce_opts);
 $('#new_post_form').ajaxForm({clearForm: true, dataType:'json',success: function(data) { 
  if (data.response!="success") {
   if(data.response=="flooderror"){
    onFloodError(data)
    return			  
   }
  }
  $("#main_stream_list").prepend(data.html)
  $("#open_post_submit").button("reset");
  tinymce.get('post_content_text').setContent('');
 }, beforeSubmit: function(arr,$form) {
  $("#open_post_submit").button("loading");
  $('#new_post').slideUp();
 }});

 $("ul#node_list").find("a").click(onNodeClick);
 $("#more_posts").click(onMoreClick);

 $("#node_list").children().find('a[data-node-key="all"]')[0].click();
 $('input[name="attach_file"]').change(addAttach);
 $('.post_attach_delete').click(onAttachDelete);   
 var ntfy_pop = $('#ntf_cnt');
 ntfy_pop.attr("data-visible", 'false');

 $(document).click(function(e) {
  var ntfy_pop = $('#ntf_cnt');
  if(ntfy_pop.attr("data-visible") == 'true') {
    ntfy_pop.popover('hide');
    ntfy_pop.attr("data-visible", 'false');
    e.preventDefault()
  } else {
    clickedAway = true;
  }
 });

 var ntfy_pop = $('#ntf_cnt');
 ntfy_pop.popover({
	  html: true,
	  trigger: 'manual'
     }).click(function(e) {onOpenNotifications(e);});
  
 }

function onOpenNotifications(event) {
  var data = {'cmd': 'ntfy_summary'}
  var ntfy_pop = $('#ntf_cnt');
  if(ntfy_pop.attr("data-visible") == 'false') {
    $.ajax({
     type: 'POST',
     url:'/social/paginate', 
     data: data,
     dataType:'json',
     success:function(data) {
       ntfy_pop = $('#ntf_cnt');
       ntfy_pop.attr('data-content', data.html);
       ntfy_pop.popover('show');
       ntfy_pop.attr("data-visible", 'true');
       event.preventDefault();
     }});
  }
}

function addAttach() {
  attach = $(this)
  att_clone = attach.clone();
  att_clone.appendTo(attach.parent())
  //att_clone.change(addAttach);
}

function onMoreClick(){
 key = $('#node_list > li.active a').attr('data-node-key');
 loadPosts(key,$("#main_stream").attr('next_cursor'))
}


function loadPosts(node_key,current_cursor) {
 var data = {
  'cmd': 'post_main',
  'node': node_key,
  'cursor': current_cursor
  };
 $.ajax({
  type: 'POST',
  url:'/social/paginate',
  data: data,
  dataType:'json',
  success:function(data) { 
   $("#form_node").attr("value",node_key);
   $("#main_stream").attr("next_cursor",data.cursor)
   if(data.response=="success"){
    $("#main_stream_list").append(data.html)
    $('.post_del').click(onPostItemDelete);
    $('.post_sub').click(onPostSubscribe);
    $('.post_unsub').click(onPostUnsubscribe);
    $('.post_vote').click(onPostVote);
    $('.post_unvote').click(onPostVote);      
    $('.post_reshare').click(onPostReshare);
    $('.post_expand').click(onPostExpand); 
    $("a.node").click(onNodeClick);
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
