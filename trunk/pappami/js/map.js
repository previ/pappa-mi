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

function drawMap(data) {
  var f_citta = $("#e_citta").val();
  var f_z = $("#e_z").val();
  var f_cc = $("#e_cc").val();
  var f_type = $("#e_tipo").val();
  var f_numcm = $("#e_numcm").val();
  jmarkers = jQuery(data);
  jmarker = jmarkers.find("marker");
  
  jmarker.each(function() {
    var marker = jQuery(this);          
    var key = marker.attr("key");
    var name = marker.attr("nome");
    var address = marker.attr("indirizzo");
    var type = marker.attr("tipo");
    var numcm = marker.attr("numcm");
    var citta = marker.attr("citta");
    var z = marker.attr("zona");
    var cc = marker.attr("cc");
    if(( !f_citta || citta == f_citta) && ( !f_z || z == f_z) && ( !f_cc || cc == f_cc) && (!f_type || type == f_type) && (f_numcm == 0 || numcm > 0)) {
      var latlng = new google.maps.LatLng(parseFloat(marker.attr("lat")),
                              parseFloat(marker.attr("lon")));
      var school = {key: key, latlng: latlng, name: name, address: address, type: type};
      createMarker(school)
    }
  });

  if( jmarkers.find("markers").attr('cur') ) {
    offset = offset + 1;
    jQuery.get("/map?cmd=all&cur="+jmarkers.find("markers").attr('cur')+"&offset="+offset, {}, drawMap);
  } else {
    $("#loading").hide();
    fluster.initialize();
  }
}    

function redraw() {
  $("#loading").show();
  
  $("#l_citta").html($("#e_citta option[value='"+$("#e_citta").val()+"']").text());

  var myOptions = {
    zoom: 12,
    center: new google.maps.LatLng(lat,lon),
    mapTypeId: google.maps.MapTypeId.ROADMAP
  }    
  map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
  
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
  
  jQuery.get("/map?cmd=all", {}, drawMap );
}

function load(_lat, _lon) {

  lat = _lat
  lon = _lon
  list = $("#left_list");

  redraw();
}

function createMarker(school) {
  var marker = new google.maps.Marker({position:school.latlng, icon: image, shadow: shadow});
  fluster.addMarker(marker);
  markersArray.push(marker)

  //var html = "<div id='info'><ul class='nav nav-tabs'><li class='active'><a href='#general' data-toggle='tab'>Generale</a></li><li><a href='#contacts' data-toggle='tab'>Contatti</a></li></ul><div class='tab-contents' id='content'><div id='general'><b>Nome: " + school.name + "<br/>Tipo: " + school.type + "</b><br/>Indirizzo: " + school.address + "</div><div id='contacts'>contatti...</div></div></div>";

  var html = "<div id='info'><ul class='nav nav-tabs'><li class='active'><a href='#general' data-toggle='tab'>Generale</a></li></ul><div class='tab-contents' id='content'><div id='general'><b>Nome: " + school.name + "<br/>Tipo: " + school.type + "</b><br/>Indirizzo: " + school.address + "</div></div><a class='btn btn-normal' href='/node/res/" + school.key + "/cm'>Post</a><a class='btn btn-normal' href='/contatti?cm=" + school.key + "'>Contatti</a></div>";  
  var openiw = function (){
    if (infowindow) infowindow.close();
    infowindow = new google.maps.InfoWindow({ content: html });
    infowindow.open(map,marker);
    google.maps.event.addListener(infowindow, 'domready', function() {
      $("#tabs").tabs();
    });
  };
   
  google.maps.event.addListener(marker, 'click', openiw);
  addLocationToList(list, school, marker, openiw);

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
    jQuery.get("/map?cur="+jmarkers.find("markers").attr('cur')+"&offset="+offset, {}, drawSmallMap);
  } else {
    fluster.initialize();
  }
}    

function loadSmallMap(lat,lon) {
  var myOptions = {
    zoom: 4,
    center: new google.maps.LatLng(lat,lon),
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    mapTypeControl: false,
    scrollwheel: false,
    navigationControl: false,
    scaleControl: false,
    draggable: false
  }    
  var map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
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
  
  jQuery.get("/map", {}, drawSmallMap );
}  
