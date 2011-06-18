var locations = {};

function load(lat,lon) {
  var myOptions = {
    zoom: 10,
    center: new google.maps.LatLng(lat,lon),
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    mapTypeControl: false
  }    
  var map = new google.maps.Map(document.getElementById("map"), myOptions);
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
      var marker = new google.maps.Marker({position:latlng, map:map, icon: image, shadow: shadow});
    });
  });
}  
