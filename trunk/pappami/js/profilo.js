fblogged = false;
var cache = {},	lastXhr, city = null;
// wait for the DOM to be loaded 
$(document).ready(function() { 
    $("#avatar_dialog").dialog({ modal: true, width: "30em", zIndex: 3, autoOpen: false });
    $("#avatar").click(function() {
        $("#avatar_dialog").dialog("open");
        $("#fbgetimage").click(function() {
            if(!fblogged) {
                FB.login(function(response) {
                    getimage();
                });
            } else {
                getimage();
            }            
        });
    });
    $("#form0").validate({ 
      rules: {
	commissione_sel: {
	  required: function(element) {
	    return ($("#tipo_cm").prop("checked") && ($("#commissione").val() == undefined));
	  }
	}
      }
    });
    
    $('#form0').ajaxForm({success: function(data) {
      message = data;
      if($('#form0').attr("action") == "/signup") {
	$("#message").find(".alert-actions").show();
      } else {
	$("#message").find(".alert-actions").hide();
      }
      $("#message").hide();      
      $("#message_body").text(message);
      $("#message").fadeIn(300);	  
      if($('#form0').attr("action") == "/signup") {	
      } else {
	setTimeout(function(){$("#message").fadeOut(1000, function(){$("#message_body").text('');});}, 2000);
      }
    }});

    function closeSignupNotification() {
      window.location.href = "/";
    }
    
    function getCommissioniFromCache(term) {
      found = Array();
      for(c in cache) {	
	if(term.toUpperCase() == c.substring(0,term.length).toUpperCase()) {
	  found.push({"label": c, "value": cache[c]});
	}
      }
      return found;
    }
    $("#commissione_sel").autocomplete({
      minLength: 2,
      source: function( request, response ) {
	var term = request.term;
	request.city = $("#citta").val();
	if ( city == null || city != $("#citta").val() ) {
	  cache = {};
	  lastXhr = $.getJSON( "/profilo/getcm", request, function( data, status, xhr ) {
	    items = data;
	    for (item in items) {
	      cache[items[item]["label"]] = items[item]["value"];
	    }
	    city = $("#citta").val();
	    response(getCommissioniFromCache(term));
	  });
	} else {
	  response(getCommissioniFromCache(term));
	}
      },
      select: function(event, ui) { 
	$("#commissioni").append('<div class="list-item" style="width:280px;"><input type="hidden" id="commissione" name="commissione" value="'+ui.item.value+'"/><a class="close" href="#" onclick="$(this).parent(\'div\').remove();">x</a><p><b>'+ui.item.label+'</b></p></div>');
        ui.item.value= ''; } 
    });    
    
    // bind 'myForm' and provide a simple callback function 
    $('#avatar_file').change(function(){
        $('#avatar_form').ajaxSubmit(function(data) { 
            $('#avatar_edit').attr("src", data);
            $('#avatar').attr("src", data);
            $("#avatar_dialog").dialog("close");            
        }); 
    }); 

    $('#cond_open').click(function(){
      $("#dialog").dialog({ title: "Cambia l'immagine del tuo profilo", modal: true, width: "40em", zIndex: 3, autoOpen: false, buttons: [
	      { text: "Ok", click: function() { $(this).dialog("close"); } } ] });
      $("#dialog").load("/condizioni", function(){$("#dialog").dialog("open");});
    });
    
    FB.init({ 
       appId:'103254759720309', cookie:true, 
       status:true, xfbml:true 
    });        
    FB.getLoginStatus(function(response) {
       if (response.session) {
         fblogged = true;
       }
    });
});     

function getimage() {
  FB.api('/me', function(user) {
    if(user != null) {
        picturl = 'https://graph.facebook.com/' + user.id + '/picture'
        $('#avatar').attr("src", picturl);
        $('#avatar_edit').attr("src", picturl);
        data = {cmd: 'saveurl', picture: picturl};
        $.post('/commissario/avatar', data, function() {
            $("#avatar_dialog").dialog("close");            
        });
    }
  });
}