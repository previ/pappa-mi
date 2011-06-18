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
  var marker = new google.maps.Marker({position:school.latlng, map:map, icon: image, shadow: shadow});
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
/*    itm.addEventListener("click", function(){
      //var htmliw = "<div id='info'><div id='tabs'><ul><li><a href='#general'>Generale</a></li><li><li><a href='/widget/stat?i=n&cm="+school.key+"'>Statistiche</a></li></ul>" + "<div id='general'><b>Nome: " + school.name + "<br/>Tipo: " + school.type + "</b><br/>Indirizzo: " + school.address + "</div>" + "<div id='menu'></div>" + "<div id='stat'></div>" + "</div></div>";      
       
      if (infowindow) infowindow.close();
      infowindow = new google.maps.InfoWindow({ content: htmliw });
      infowindow.open(map,marker);
      google.maps.event.addListener(infowindow, 'domready', function() {
        $("#tabs").tabs();
      });    
    }, false);*/ } else {
  }
  list.appendChild(itm);
}     
