$(document).ready(function(){
});

function profile() {
  $('body').append("<div id='profile'></div>");
  $('#profile').load('/profilo');
  $('#profile').dialog({ title: $('#title').text(), modal: true, width: 400, zIndex: 2, autoOpen: false,  beforeClose: closeIt });
  $('#profile').dialog('open');
}