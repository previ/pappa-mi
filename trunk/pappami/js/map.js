var infowindow;
var locations = {};
var list;
var xml = null;
var map;
var iLast;
var locArray;
var offset = 0;
var markersArray = [];
var image = new google.maps.MarkerImage('http://google-maps-icons.googlecode.com/files/school.png',
      new google.maps.Size(32, 37),
      new google.maps.Point(0,0),
      new google.maps.Point(16, 0));
var shadow = new google.maps.MarkerImage('http://google-maps-icons.googlecode.com/files/shadow.png',
      new google.maps.Size(51, 37),
      new google.maps.Point(0,0),
      new google.maps.Point(16, 0));
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
  var f_cc = dojo.byId("e_cc").value;
  var f_type = dojo.byId("e_tipo").value;
  var f_numcm = dojo.byId("e_numcm").value;
  jdata = jQuery(data).find("marker");
  
  jdata.each(function() {
    var marker = jQuery(this);          
    var key = marker.attr("key");
    var name = marker.attr("nome");
    var address = marker.attr("indirizzo");
    var type = marker.attr("tipo");
    var numcm = marker.attr("numcm");
    var cc = marker.attr("cc");
    if(( !f_cc || cc == f_cc) && (!f_type || type == f_type) && (f_numcm == 0 || numcm > 0)) {
      var latlng = new google.maps.LatLng(parseFloat(marker.attr("lat")),
                              parseFloat(marker.attr("lon")));
      var school = {key: key, latlng: latlng, name: name, address: address, type: type};
      createMarker(school)
    }
  });

  if( jdata.length == limit) {
    offset = offset + limit;
    jQuery.get("/map?cmd=all&offset="+offset, {}, drawMap);
  } else {
    $("#loading").hide();
    fluster.initialize();
  }
}    

function redraw() {
  $("#loading").show();
  while (list.firstChild) {
    list.removeChild(list.firstChild);
  }
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
  
  jQuery.get("/map?cmd=all&limit="+limit, {}, drawMap );
}

function load(lat, lon) {
  var myOptions = {
    zoom: 12,
    center: new google.maps.LatLng(lat,lon),
    mapTypeId: google.maps.MapTypeId.ROADMAP
  }    
  map = new google.maps.Map(document.getElementById("map"), myOptions);

  list = dojo.byId("left_list");

  redraw();
}

function createMarker(school) {
  var marker = new google.maps.Marker({position:school.latlng, icon: image, shadow: shadow});
  fluster.addMarker(marker);
  markersArray.push(marker)

  var html = "<div id='info'><div id='tabs'><ul><li><a href='#general'>Generale</a></li><li><li><a href='/widget/stat?i=n&cm="+school.key+"'>Statistiche</a></li></ul>" + "<div id='general'><b>Nome: " + school.name + "<br/>Tipo: " + school.type + "</b><br/>Indirizzo: " + school.address + "</div>" + "<div id='menu'></div>" + "<div id='stat'></div>" + "</div></div>";
  
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
  list.appendChild(itm);
}     

function loadSmallMap(lat,lon) {
  var myOptions = {
    zoom: 10,
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
  
  jQuery.get("/map", {}, function(data) {
    jQuery(data).find("marker").each(function() {
      var marker = jQuery(this);
      var name = marker.attr("nome");
      var address = marker.attr("indirizzo");
      var type = marker.attr("tipo");
      var latlng = new google.maps.LatLng(parseFloat(marker.attr("lat")),
                              parseFloat(marker.attr("lon")));
      var marker = new google.maps.Marker({position:latlng, icon: image, shadow: shadow});
      fluster.addMarker(marker);
    });
    fluster.initialize();
  });
}  
