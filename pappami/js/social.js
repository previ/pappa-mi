var channel = "";

$(document).ready(function() {
  channel_id = $('body').attr('data-channel-id');
  if(channel == "" && channel_id != "") {
    channel = openChannel(channel_id);
  }
  getNotificationsNum()
});

function openChannel(channel_id) {
    channel = new goog.appengine.Channel(channel_id);
    socket = channel.open();
    socket.onopen = function (){/*alert("channel opened")*/};
    socket.onmessage = onChannelMessage;
    socket.onerror = function (){/*alert("error")*/};
    socket.onclose = function (){/*alert("channel closed")*/};
    return socket;
}

function getNotificationsNum() {
  $.ajax({
    type: 'POST',
    url:'/social/notifications', 
    data: {'cmd': 'get_num'},
    dataType:'json',
    success:function(data){
      $('.s_glob_ntfy').text(data.ntfy_num);
      if(parseInt(data.ntfy_num) > 0 && !$('.s_glob_ntfy').hasClass('badge-warning')) {
	  $('.s_glob_ntfy').addClass('badge-warning')
      } else if(parseInt(data.ntfy_num) == 0 && $('.s_glob_ntfy').hasClass('badge-warning')) {
	  $('.s_glob_ntfy').removeClass('badge-warning')
      }
    }});
  
}

function onChannelMessage(m) {
  m=jQuery.parseJSON(m.data)
  getNotificationsNum();
  var textmessage = m.user + ' ha aggiunto un <a href="/social/post/' + m.source_id +'">' + m.source_desc + '</a> su <a href=/social/node/' + m.target_id + '">' + m.target_desc + '</a>';
  $.pnotify({
    title: 'Notifica',
    text: textmessage
  });
}

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

// Post
function getPostRootByElement(element) {
  return element.parents('.s_post_root');
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
    post_root.find(".s_post_comment_num").text(data.num);
    post_root.find(".s_comment_submit").button("reset");
    tinymce.get('comment_content').setContent('');
    comment = post_root.find(".s_comment_list").find('li:last-child');

    $(document).ready(function(){
      initComment(comment);
    });
  
  }, beforeSubmit: function(arr,$form) {
	  post_root.find(".s_comment_submit").button("loading");
	  //$('#new_comment').slideUp();
  }});	
  
  post_root.find('.s_post_comment').tinymce(tiny_mce_opts);
  post_root.find('.post_sub').click(onPostSubscribe);
  post_root.find('.post_unsub').click(onPostUnsubscribe);
  post_root.find('.post_del').click(onPostDelete);
  post_root.find('.post_pin').click(onPostPin);
  post_root.find('.post_collapse').click(onPostCollapse);
  post_root.find('.post_edit').click(onPostEdit);
  post_root.find('.post_reshare').click(onPostReshare);  
  post_root.find('.post_vote').click(onPostVote);  
  post_root.find('.post_unvote').click(onPostVote);  
  post_root.find('.s_post_votes_c').click(onVotesDetail)
  post_root.find('.s_post_reshares_c').click(onResharesDetail)
  post_root.find('.show_comment_form').click(onPostCommentFormExpand)
  post_root.find('.show_comment_form').click(onPostCommentsExpand)
  post_root.find('.post_comments_expand').click(onPostCommentsExpand)
  
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
  var edit_post = post_root.find(".s_post_tools > .s_post_edit_form").clone();
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
	post_root.find(".s_post_commands").hide()
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
  var post_root = getPostRootByElement($(this))
  var comment_root = getCommentRootByElement($(this))
  var comment_key = comment_root.attr('data-comment-key');   
  var edit_post = post_root.find(".s_post_tools > .s_comment_edit_form").clone();
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
  var exp_comments = $(this).hasClass('s_post_comments_c');
  var post_key = getPostKeyByElement($(this));
  var post_item = $(this).parents('.s_post_item');
  var data = {'cmd':'expand_post', 'post':post_key, 'exp_comments': exp_comments }
  
  $.ajax({
	  type: 'POST',
	  url:'/social/managepost', 
	  data: data,
	  dataType:'json',
	  success:function(data){
	    post_item.html(data.html);
	  }});
  
}

function onPostCollapse() {
  var post_key = getPostKeyByElement($(this));
  var post_item = $(this).parents('.s_post_item');
  var data = {'cmd':'collapse_post', 'post':post_key }
  
  $.ajax({
	  type: 'POST',
	  url:'/social/managepost', 
	  data: data,
	  dataType:'json',
	  success:function(data){
	    post_item.html(data.html);
	    post_item.find('.post_del').click(onPostItemDelete);
	    post_item.find('.post_sub').click(onPostSubscribe);
	    post_item.find('.post_unsub').click(onPostUnsubscribe);
	    post_item.find('.post_vote').click(onPostVote);
	    post_item.find('.post_unvote').click(onPostVote);      
	    post_item.find('.post_reshare').click(onPostReshare);
	    post_item.find('.post_expand').click(onPostExpand); 
	    post_item.find('.s_post_votes_c').click(onVotesDetail)
	    post_item.find('.s_post_reshares_c').click(onResharesDetail)	    
	  }});
  
}

function onPostCommentsExpand() {
  var post_root = getPostRootByElement($(this))
  post_root.find('.s_comment_list').show();
}

function onPostCommentExpandEx() {
  var post_key = getPostKeyByElement($(this));
  var post_comments = $(this).parents('.s_post_comment_num');
  var data = {'cmd':'expand_comments', 'post':post_key }
  
  $.ajax({
	  type: 'POST',
	  url:'/social/managepost', 
	  data: data,
	  dataType:'json',
	  success:function(data){
	    post_comments.html(data.html);
	  }});
  
}

function onPostCommentFormExpand() {
  $(this).parents('.s_comment_form').find('li.s_comment_form').show();
  $(this).parents('.s_comment_form').find('li.s_comment_placeholder').hide()
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
  var post_root = getPostRootByElement($(this))
  $.ajax({
    type: 'POST',
    url:'/social/managepost', 
    data: {'cmd': 'reshare_modal',
	   'post': post },
    dataType:'json',
    success:function(data){
      modal_reshare = post_root.find(".s_post_tools").find(".s_modal_reshare");
      modal_reshare.html(data.html);
      $(document).ready(function () {
	//modal_reshare = $("#tools").find("#post_reshare")
	//$("#modal_reshare").find('#b_post_reshare_submit').click(onPostReshareSubmit);
	modal_reshare.find('input[name="post"]').attr("value", post);
	modal_reshare.find('#reshare_post_content_text').tinymce(tiny_mce_opts);
	modal_reshare.find('form').ajaxForm({clearForm: true, dataType:'json', success:function(data){
	  if(data.response!="success") {
	    if(data.response=="flooderror") {
	      modal_reshare.modal('hide');
	      onFloodError(data, function(){
		modal_reshare.modal('show')
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
  var comment_num = getPostRootByElement($(this)).find('.s_post_comment_num')
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
	      comment_num.text(data.num)
	      $.pnotify({
		title: 'Info',
		text: 'Commento cancellato'
	      });
	      
	    }});
  }	  	
}

function onPostPin(){
  var post = getPostKeyByElement($(this));
  var days = $(this).attr("data-days")
  var data = {'cmd':'pin_post', 'post':post, 'days': days};
  $.ajax({
    type: 'POST',
    url:'/social/managepost', 
    data: data,
    dataType:'json',
    success:function(data){
	$.pnotify({
	  title: 'Info',
	  text: 'Post evidenziato'
	});
      }
  });
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

function redraw_node(node_root) {
  
  var subscribed = node_root.attr('data-sub-status');
  var ntfy_period = node_root.attr('data-ntfy-period');
  node_root.find('.ntfy_period > i').css('visibility', 'hidden');
  
  if( subscribed == 'true' ) {
	node_root.find('#subscribe_btn').html('Disiscriviti');
	node_root.find('#sub_prop').removeAttr("disabled");
	node_root.find('#ntfy_period_'+ ntfy_period + ' > i').css('visibility', 'visible');
  } else {
	node_root.find('#sub_prop').attr("disabled", "true");
	node_root.find('#subscribe_btn').html('Iscriviti');
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
      node_root.attr('data-sub-status', data.subscribed );
      node_root.attr('data-ntfy-period', data.ntfy_period);
      onSuccess(data);
      $(document).ready(function() {
	redraw_node(node_root);
      });
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
            redraw_node(node_root);
	  }
  });	 
}

function onNotificationPeriodProfile() {
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
            node_root.find('.ntfy_period').removeClass('btn-primary');
	    node_root.find('[data-ntfy-period="'+ ntfy_period +'"]').addClass('btn-primary');
  	    onSuccess(data)
	  }
  });	 
}

function init_search(){
  $('#search_text').typeahead({minLength:2,
    source: function (query, process) {
      $("#search_node_list").empty()
      return $.post('/social/paginate', { query: query,cmd:"search_nodes"}, function (data) {
	data=jQuery.parseJSON(data)
	if(data.html) {
	  $("#search").tab('show')
	  $("#search_node_list").html(data.html)
	}
      });
    }
  });
}

function onSearchPaginate() {
  var offset = $(this).attr('data-offset')
  $('input[name="offset"]').attr('value', offset);
  $('div.active > form').submit()
}

function onNodeClick(){
 var node_item = $(this);
 key=node_item.attr('data-node-key');
 node_item.parent().siblings(".active").removeClass("active");
 node_item.parent().addClass("active");
 var node_name = node_item.find(".node_name").attr('title');
 $("#node_title").find("span").text(node_name);
 if(key!="all" && key!="news") {
   $("#node_title > a").attr("href", "/social/node/"+key);
   $("#node_title > a").show();
   node_item.find(".sub_ntfy").hide();
 } else {
   $("#node_title > a").hide();
 }
 node_item.parent().addClass("active");
 //key=node_item.attr('data-node-key');
 $("#node_container").empty();
 //loadPosts(key,$("#main_stream_"+key).attr('next_cursor'))
 loadNode(key, node_name);
}

function initNode(node_key){
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
  var post_root = $("#main_stream_list li:first-child");
  post_root.find('.post_del').click(onPostItemDelete);
  post_root.find('.post_sub').click(onPostSubscribe);
  post_root.find('.post_unsub').click(onPostUnsubscribe);
  post_root.find('.post_vote').click(onPostVote);
  post_root.find('.post_unvote').click(onPostVote);      
  post_root.find('.post_reshare').click(onPostReshare);
  post_root.find('.post_expand').click(onPostExpand); 
  post_root.find('.s_post_votes_c').click(onVotesDetail)
  post_root.find('.s_post_reshares_c').click(onResharesDetail)
  post_root.find('.show_comment_form').click(onPostCommentFormExpand)
  post_root.find('.show_comment_form').click(onPostCommentsExpand)
  post_root.find('.post_comments_expand').click(onPostCommentsExpand)  
  tinymce.get('post_content_text').setContent('');
 }, beforeSubmit: function(arr,$form) {
  $("#open_post_submit").button("loading");
  $('#new_post').slideUp();
 }});
 $('#subscribe_btn').on('click', onSubUnsubNode)
 $('.ntfy_period').on('click', onNotificationPeriod)
 $("#more_posts").click(onMoreClick);
 if(node_key!="all"&&node_key!="news") {
  redraw_node($('.node_root'));
 }
 
 $('input[name="attach_file"]').change(addAttach);
 $('.post_attach_delete').click(onAttachDelete);   
}


function init(){

 $("ul#node_list").find("a").click(onNodeClick);
 $("#node_list").children().find('a[data-node-key]').first().click();
 
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
       $('.s_glob_ntfy').text("0");
       $('.s_glob_ntfy').removeClass('badge-warning')
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
 key = $(this).parents('.node_root').attr('data-node-key');
 loadPosts(key,$("#main_stream").attr('next_cursor'))
}


function loadNode(node_key, node_name) {
 var data = {
  'cmd': 'node_main',
  'node': node_key,
  'node_name': node_name,
  };
 $.ajax({
  type: 'POST',
  url:'/social/paginate',
  data: data,
  dataType:'json',
  success:function(data) { 
   if(data.response=="success"){
    $("#node_container").empty();   
    $("#node_container").append(data.html)
    initNode(node_key)
    loadPosts(node_key, "")
   } 
  }
 });  
}

function loadPosts(node_key,current_cursor) {
 $("#main_stream_list").append('<li class="s_loading"><span class="offset3 span2">Loading... <img src="/img/loading.gif"></span></li>');

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
    $('#main_stream_list').find('li.s_loading').remove();   
    $('#main_stream_list').append(data.html)
    initPostList($('#main_stream_list'));
    if(data.eof == true){
     $("#more_posts").hide();   
     $("#no_more_posts").show();   
     $("#no_more_posts").alert();
    } else {
     $("#more_posts").show();   
     $("#no_more_posts").hide();   
    }
   } 
  }
 });
 //} else {
  //$("ul#node_list li").click(onNodeClick)
  //$("#node_stream_"+key).siblings().hide()
  //$("div#node_stream_"+key).show()
 //}
}

function initPostList(list) {
  list.find('.post_del').click(onPostItemDelete);
  list.find('.post_sub').click(onPostSubscribe);
  list.find('.post_unsub').click(onPostUnsubscribe);
  list.find('.post_vote').click(onPostVote);
  list.find('.post_unvote').click(onPostVote);      
  list.find('.post_reshare').click(onPostReshare);
  list.find('.post_expand').click(onPostExpand); 
  list.find('.s_post_votes_c').click(onVotesDetail)
  list.find('.s_post_reshares_c').click(onResharesDetail)
}

function onVotesDetail() {
 var post = getPostKeyByElement($(this));    

 var data = {
  'cmd': 'vote_list',
  'post': post
  };
 $.ajax({
  type: 'POST',
  url:'/social/managepost',
  data: data,
  dataType:'json',
  success:function(data) { 
   $('body').append(data.html);
   $('#votes_modal').modal()
  }
  });
}

function onResharesDetail() {
 var post = getPostKeyByElement($(this));    

 var data = {
  'cmd': 'reshare_list',
  'post': post
  };
 $.ajax({
  type: 'POST',
  url:'/social/managepost',
  data: data,
  dataType:'json',
  success:function(data) { 
   $('body').append(data.html);
   $('#reshares_modal').modal()
  }
  });
}

function loadNotifications() {
  cursor = $("#notifications_list").attr('data-cursor');
  data = {'cmd': 'notifications',
	  'cursor': cursor };
  $.ajax({
	  type: 'POST',
          url:"/social/paginate",
	  data: data,
          dataType:'json',
	  success:function(data){
	    if(data.response=="success"){
	      $("#notifications_list").attr('data-cursor', data.cursor);
	      $("#notifications_list").last().append(data.html)
	      /*mark as visited
	      $("#notifications_list>div").each(function(){
	        date=new Date($(this).attr("date"))
		if(date<last_visit){
		  $(this).addClass("visited")
		}
	      });*/
	      } 
	      if(data.eof) {
	        $("#load_notifications").hide()
		if($("#notifications_list").children().length>0) {
		  $(".no_more_data").show()
		} else {
		  $(".empty_errors").show()
		}
	      }
	    }})
}


function mark_visited(){
  $("div.notification").each(function(){
    date=new Date(this.attr("date"))
  });
}
