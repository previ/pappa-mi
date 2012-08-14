

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
$('#reply_message').tinymce({
    // Location of TinyMCE script
    script_url : '/js/tiny_mce/tiny_mce.js',     
    // General options
    width : "100%",
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


function onReplySubmitted(user,post,node){
	data= {}
	data['user']= user
	data['post']=post
	data['node']=node
	data['content']=$("#reply_message").attr("value")
	
	$.ajax({
		 type: 'POST',
		 url:'/social/managepost?cmd=create_reply_post', 
		 data: data,
		 success:function(data){
			 window.location.reload()
			 }})
	
}

function onOpenPostSubmitted(user,node){
	data= {}
	data['user']= user
	data['node']=node
	data['content']=$("#post_content_text").attr("value")
	data['title']=$("#post_title_text").attr("value")

	$.ajax({
		 type: 'POST',
		 url:'/social/managepost?cmd=create_open_post', 
		 data: data,
		 success:function(data){
			 window.location.reload()
			 }})
	
}

function onReplyDelete(node,post,reply){
	data= {}
	data['post']=post
	data['node']=node
	data['reply']=reply
	$.ajax({
		 type: 'POST',
		 url:'/social/managepost?cmd=delete_reply_post', 
		 data: data,
		 success:function(data){
			 window.location.reload()
			 }})
	
}

function onPostDelete(node,post){
	data= {}
	data['post']=post
	data['node']=node
	$.ajax({
		 type: 'POST',
		 url:'/social/managepost?cmd=delete_open_post', 
		 data: data,
		 success:function(data){
			 window.location.reload()
			 }})
	
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
	 $.ajax({url:'/social/subscribe?node='+node_key+'&user='+user_key+ '&cmd=subscribe', success:function(data){
		  $('#subscribe_btn').hide();
		  $('#unsubscribe_btn').show();
		 
		}
	 });
	 
}

function onUnsubscription(user_key,node_key)
{
	 $.ajax({url:'/social/subscribe?node='+node_key+'&user='+user_key+ '&cmd=unsubscribe', success:function(data){
		  $('#unsubscribe_btn').hide();
		  $('#subscribe_btn').show();
		 
		}
	 });
	 
}