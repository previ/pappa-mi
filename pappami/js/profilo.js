"use strict";

var cache = {},	lastXhr, city = null;
var combo_config = {
  'lang'        : 'it',
  'sub_info'    : false,
  'select_only' : true,
  'bind_to'	: 'selected',
  'primary_key' : 'value',
  'field'	: 'label',
  'button_img'  : '/img/combobox_button.png',
  'load_img'    : '/img/ajax-loader.gif'
}


// wait for the DOM to be loaded 
$(document).ready(function() { 
    var parts = window.location.href.slice(window.location.href.indexOf('?') + 1).split('#');
    
    $('a[href=#'+parts[1]+"]").tab('show');
	
    $("#avatar_dialog").dialog({ title:"Immagine", modal: true, width: "30em", zIndex: 3, autoOpen: false });
    $("#avatar").click(function() {
        $("#avatar_dialog").dialog("open");
    });
    $("#form0").validate({
      errorClass: "error",
      errorPlacement: function(error, element) {
	var item = $(element);
	item.tooltip({title:error.text(), trigger:'manual'});
	item.tooltip('show');
      },
      highlight: function(element, errorClass, validClass) {
	var item = $(element).parents(".control-group");
	item.addClass(errorClass); 
      },
      unhighlight: function(element, errorClass, validClass) {
	var item = $(element).parents(".control-group");
	item.removeClass(errorClass); 
	$(element).tooltip('hide');
      },  
      rules: {
	commissione_sel: {
	  required: function(element) {
	    return ($("#tipo_cm").prop("checked") && ($("#commissione").val() == undefined));
	  }
	}
      }
    });
    
    $('#form0').ajaxForm({success: function(data) {
      var message = data;
      if($('#form0').attr("action") == "/signup2") {
	$("#message").find(".alert-actions").show();
      } else {
	$("#message").find(".alert-actions").hide();
      }
      $("#message").hide();      
      $("#message_body").text(message);
      $("#message").fadeIn(300);	  
      if($('#form0').attr("action") == "/signup2") {	
	setTimeout(function(){location.href="/";}, 2000);
      } else {
	setTimeout(function(){$("#message").fadeOut(1000, function(){$("#message_body").text('');});}, 2000);
      }
    }});
        
    // bind 'myForm' and provide a simple callback function 
    $('#avatar_file').change(function(){
        $('#avatar_form').ajaxSubmit(function(data) { 
            $('#avatar_edit').attr("src", data + "&size=big");
	    $('#avatar_url').attr("value", data);
            $('#avatar').attr("src", data + "&size=big");
            $("#avatar_dialog").dialog("close");            
        }); 
    }); 

    $('#citta').change(oncitychanged);    
    if($('#citta').val() != "") oncitychanged();
    
    $("[data-content]").popover({delay: { show: 500, hide: 2000 }, title:"Informazioni"});    
    $('.ntfy_period').click(onNotificationPeriodProfile)
});     

function oncitychanged() {
  if( $("#citta").val() != "" && $("#citta").val() != city) {        
    if( !cache[$("#citta").val()] ) {
      var query = { 'city': $("#citta").val() }
      lastXhr = $.getJSON( "/profilo/getcm", query, function( data, status, xhr ) {
	city = $("#citta").val()
	cache[city] = data
	$('#commissione_sel').parent().html('<input id="commissione_sel" name="commissione_sel" type="text"/>');	
	$('#commissione_sel').ajaxComboBox(data, combo_config).bind("selected", function() { 
	  $("#commissioni").append('<div class="list-item" style="width:280px;"><input type="hidden" id="commissione" name="commissione" value="'+$("#commissione_sel_hidden").val()+'"/><a class="close" href="#" onclick="$(this).parent(\'div\').remove();">x</a><p><b>'+$(this).val()+'</b></p></div>');
	  $(this).val(''); 
	}); 
      });    
    } else {
      city = $("#citta").val()
      $('#commissione_sel').parent().html('<input id="commissione_sel" name="commissione_sel" type="text"/>');	
      $('#commissione_sel').ajaxComboBox(cache[city], combo_config).bind("selected", function(event, ui) { 
	  $("#commissioni").append('<div class="list-item" style="width:280px;"><input type="hidden" id="commissione" name="commissione" value="'+$("#commissione_sel_hidden").val()+'"/><a class="close" href="#" onclick="$(this).parent(\'div\').remove();">x</a><p><b>'+$(this).val()+'</b></p></div>');
	  $(this).val(''); 
	});    
    }
  }
}

function closeSignupNotification() {
  window.location.href = "/";
}

function getimage( p) {
  var postdata = {cmd: 'getimage', provider: p};
  $.post('/profilo/avatar', postdata, function(picturl) {
      $("#avatar_dialog").dialog("close");            
      $('#avatar_url').attr("value", picturl);
      $('#avatar').attr("src", picturl);
      $('#avatar_edit').attr("src", picturl);
  });
}

function removeAuth(provider) {
  $.ajax({ url:"/eauth/rmauth?p="+provider, 
	  success: function() {
	    $("#"+provider+"_on").attr("checked", false);
	    $("#"+provider+"_on_lbl").removeClass("active");
	    $("#"+provider+"_off").attr("checked", true);
	    $("#"+provider+"_off_lbl").addClass("active");
	    }
	  });
}