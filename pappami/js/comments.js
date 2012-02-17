function onvote(key, vote) {
  $.ajax({url:'/comments/vote?msg='+key+'&voto='+vote, success:function(data){
  $('#vnum_'+key).text(data);
  $('#vnum_'+key+'_me').show();
  $('#vote_1_'+key).hide();
  $('#vote_2_'+key).show(); 
  if (data > 0 ) $('#votes_'+key).show(); 
  else $('#votes_'+key).hide();}})
}
function onunvote(key) {
  $.ajax({url:'/comments/vote?msg='+key+'&voto=0', success:function(data){
  $('#vnum_'+key).text(data); 
  $('#vote_2_'+key).hide(); 
  $('#vote_1_'+key).show(); 
  $('#vnum_'+key+'_me').hide();
  if (data > 0 ) $('#votes_'+key).show();
  else $('#votes_'+key).hide();}})
}    
function onshowvotes(key) {
 if($("#voters").attr('id') == null) {
  $("body").append('<div id="voters" title="Questa pagina &egrave; piaciuta a:"></div>');
 }
 $('#voters').load('/comments/voters?msg='+key);
 $('#voters').dialog({
  modal: true,
  buttons: {
   Ok: function() {
    $( this ).dialog( "close" );
   }
  }
 });
}
function ondetail(key) {
 if( !$('#detail_'+key).is(':visible') ) {
  $('#detail_'+key).load('/public/detail?key='+key, function(){
   $('#summary_'+key).hide();
   $('#detail_'+key).slideDown();
   $('#detail_exp_'+key).addClass("col");
  });
 } else {
  $('#detail_'+key).slideUp();
  $('#summary_'+key).show(); 
  $('#detail_exp_'+key).removeClass("col")
 }
} 
function onexpcomments(key) {
 if( !$('#comments_container_'+key).is(':visible')) {
  $('#comment_list_'+key).load('/comments/comment?par='+key, function(){
   $('#comments_container_'+key).slideDown();
   $('#comment_new_exp_'+key).show();
   $('#comments_exp_'+key).addClass("colcmt");
   $('#comments_num_'+key).text($('#comment_list_'+key).children().length);
  });
 } else {
  $('#comment_new_container_'+key).hide();
  $('#comment_new_exp_'+key).hide();
  $('#comments_container_'+key).slideUp();
  $('#comments_exp_'+key).removeClass("colcmt")
  $('#comment_new_exp_'+key).hide();
 }
} 
function onexpcommentnew(key) {
 if( $('#comments_container_'+key).css("display") == "none" &&
     $('#comment_new_container_'+key).css("display") == "none") {
  $('#comment_list_'+key).load('/comments/comment?par='+key, function(){
   if($('#comment_list_'+key).children().length > 0) {
    last = $('#comment_list_'+key).children().last().children().first().attr('id').substring("comment_".length);
    $('#comment_last_'+key).val(last);
    $('#comments_num_'+key).text($('#comment_list_'+key).children().length);
   }
   $('#comments_container_'+key).slideDown();
   $('#comment_new_exp_'+key).show();
   $('#comments_exp_'+key).addClass("colcmt");
   $('#comment_new_exp_'+key).hide();
   $('#comment_new_container_'+key).show();
  });
 } else if( $('#comment_new_container_'+key).css("display") == "none") {
  if($('#comment_list_'+key).children().length > 0) {
   last = $('#comment_list_'+key).children().last().children().first().attr('id').substring("comment_".length);
   $('#comment_last_'+key).val(last); 
  }
  $('#comment_new_exp_'+key).hide();
  $('#comment_new_container_'+key).show();
 } else {
  $('#comment_new_container_'+key).hide();
  $('#comment_new_exp_'+key).show();
 }
} 

function permalink(key) {
 url = "/public/act?key="+key;
 window.open(url);
} 

