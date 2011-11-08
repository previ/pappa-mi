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
 if( $('#detail_'+key).css("display") == "none") {
  $('#detail_'+key).load('/public/detail?key='+key, function(){$('#summary_'+key).hide();$('#detail_'+key).slideDown();$('#detail_exp_'+key).addClass("col");});
 } else {
  $('#detail_'+key).slideUp();
  $('#summary_'+key).show(); 
  $('#detail_exp_'+key).removeClass("col")
 }
} 
function permalink(key) {
 url = "/public/act?key="+key;
 window.open(url);
} 

