"use strict";

var ulmsg=false;
window.onbeforeunload = closeAlert;

//$.metadata.setType("attr", "validate");

function closeAlert() {
  if(ulmsg) {
    if( confirm("Attenzione, la pagina contiene dati non salvati, uscire comunque ?") ) {
      $(".tooltip").remove();
      ulmsg=false;  
      return true;
    } else {
      return false;
    }
  }
}

function closedialog() {
  cleardirty();
  $(".tooltip").remove();
  $('#new-data').find(".error").tooltip("hide");
  $('#new-data').dialog('close');
}

function cleardirty() {
  ulmsg=false;
}

function initForm() {
  ulmsg=true;
  $('#new-data-form').find("[data-content]").popover({delay: { show: 500, hide: 1000 }, title:"Informazioni"});
  $("#item_tags_handler").tagHandler({
      getData: { 'msg': "" },
      getURL: '/comments/gettags',            
      autocomplete: true
  }); 
 $('#new-data').find( "[type='radio']" ).button();
}

function opennewmsg() {  
  if($('#new-msg').is(':visible') ) {
    $('#new-msg').slideUp();
  } else {
    //$('#e_message').remove();
    $('#e_message_container').html('<textarea cols="80" rows="4" class="span8 comment_textarea required" name="testo" id="e_message"></textarea>');
    $('#e_message').tinymce({
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
    if( $('#activity_list li:first-child').attr('id') ) {
      $('#new-msg').find('#act_last').val($('#activity_list li:first-child').attr('id').substring('activity_'.length));  
    }
    $("#new-msg-form").validate({errorClass: "error",
	  errorPlacement: function(error, element) {
	  var item = $(element).parents(".control-group");
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
	  item.tooltip('hide');
	}
    });
    $('#new-msg-form').ajaxForm({clearForm: true, success: function(data) { 
      $('#activity_list').prepend(data);
      $("#e_submit").button("reset");
    }, beforeSubmit: function(arr,$form) {
      $("#e_submit").button("loading");
      $('#new-msg').slideUp();
    }, beforeSerialize: function($form, options) {
      $("[name='tags']").attr('value','');
      var tags = $("#message_tags_handler").tagHandler("getTags")
      for(var tag in tags) {
	$($form).append("<input type='hidden' name='tags' value='"+tags[tag]+"'/>");
      }
    }});
    $("#message_tags_handler").tagHandler({
	getData: { 'msg': "" },
	getURL: '/comments/gettags',            
	autocomplete: true
    });
    $('#new-msg').slideDown();  
  }
}

var auto_open_nc = false;

jQuery.validator.addMethod("numpastibambini", function(value, element) { 
 return parseInt(value) <= $("#e_numeroPastiTotale").val(); 
} );
jQuery.validator.addMethod("numpastispeciali", function(value, element) { 
 return value <= $("#e_numeroPastiBambini").val(); 
} );

function opennewwiz(url) {
  $('#new-data-form').load(url, function(){
    initForm();    

    $("#form0").formwizard({ 
      formPluginEnabled: true,
      validationEnabled: true,
      validationOptions: {
	errorClass: "error",
	errorPlacement: function(error, element) {
	  var item = $(element).parents(".control-group");
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
	  item.tooltip('hide');
	}
      },
      focusFirstInput : true,
      textNext: "Avanti",
      textBack: "Indietro",
      disableUIStyles: true,
      remoteAjax : {"step1" : { // add a remote ajax call when moving next from the second step
	url : url + "val", 
	dataType : 'text',
	success : function(data){
	  if(data != "Ok") {	    
	    $("#formwiz-container").html('<div id="formwiz-error" class="alert alert-error fade in" style="display:none;"><a class="close" data-dismiss="alert" href="#">&times;</a>'+data+'</div>');
	    $("#formwiz-error").show();
	    $("#formwiz-error").alert();
	    //$('#formwiz-error').dialog({ modal: true, width: "40em", zIndex: 3, autoOpen: false,  buttons: [
	    //  { text: "Ok",
	    //	click: function() { $(this).dialog("close"); $('#formwiz-error').text(''); } } ] });
	    //$('#formwiz-error').dialog('open');	    
	    return false; //return false to stop the wizard from going forward to the next step (this will always happen)
	  } else {
	    $("#formwiz-error").alert("close");
	  }
	  return true; //return true to make the wizard move to the next step
	}
      }},
      formOptions :{
	// on new form submit
	success: function(data){
	  $('#new-data-preview').html(data);
	  if($('#form-error').html()) {	    
	    $('#form-error').dialog({ modal: true, width: "40em", zIndex: 3, autoOpen: false,  buttons: [
	      { text: "Ok",
		click: function() { $('#form-error').detach(); $(this).dialog("close"); $("#e_submit").button("reset"); } } ] });
	    $('#form-error').dialog('open');
	    $('#new-data-preview').html('');
	  } else {
	    $('#new-data-form').hide();  
	    $('#new-data-preview').show();
	    // on preview form submit
	    if( $('#activity_list li:first-child').attr('id') ) {	    
	      $('#form1').find('#act_last').val($('#activity_list li:first-child').attr('id').substring('activity_'.length)); 
	    }
	    $('#form1').ajaxForm( {beforeSubmit: function() {$('#form1').find("#e_submit").button("loading");}, success: function(data) {
	      $('#new-data').dialog('close');
	      $('#new-data-form').html('');
	      $('#new-data-preview').html('');
	      $('#activity_list').prepend(data);
	      if(auto_open_nc) {
		$('#new-nc').html("Inserire anche una Non conformit&agrave; ?")
		$('#new-nc').dialog({ title: "Nuova Non conformit&agrave;", modal: true, width: "40em", zIndex: 3, autoOpen: false,  buttons: [
		  { text: "Si",
		    click: function() { $(this).dialog("close"); opennewnc(); } }, 
		  { text: "No",
		    click: function() { $(this).dialog("close"); auto_open_nc = false; } } ] });
		$('#new-nc').dialog('open');
	      }
	    }});
	  }
	},
	resetForm: false,
	beforeSubmit: function(arr,$form) {
	  $('#form0').find("#e_submit").button("loading");;
	},
	beforeSerialize: function($form, options) {
	  $("[name='tags']").attr('value','');
	  var tags = $("#item_tags_handler").tagHandler("getTags")
	  for(var tag in tags) {
	    $form.append("<input type='hidden' name='tags' value='"+tags[tag]+"'/>");
	  }
        }
      }
    });
    $.validator.messages = {
	number: "Inserire in numero",
	required: "Inserire o selezionare un valore",
	range: "Inserire un valore compreso tra {0} e {1}",
	numpastibambini: "Il numero di pasti serviti ai bambini deve essere inferiore al numero di pasti totali.",
	numpastispeciali: "Il numero di pasti speciali deve essere inferiore al numero di pasti serviti ai bambini."};

    $("#form0").bind("step_shown", function(event, data){
      $("#formwiz-progress-" + data.previousStep).removeClass("active");
      $("#formwiz-progress-" + data.currentStep).addClass("active");
    });

    $('#new-data').show();
    $('#new-data-form').show();
    $("#formwiz-progress-step1").toggleClass("active");
    $('#new-data').dialog({ title: $('#title').text(), modal: true, height: 600, width: 810, zIndex: 2, autoOpen: false, beforeClose: closeAlert });
    $('#new-data').dialog('open');
  });
}

function opennewitem(url) {
  $('#new-data-form').load(url, function() {
    initForm();

    $.validator.messages = {
	required: "Inserire o selezionare un valore",
	range: "Inserire un valore compreso tra {0} e {1}" };
	
    $("#form0").validate({
       errorClass: "error",
       errorPlacement: function(error, element) {	      
	 var item = $(element).parents(".control-group");
	 item.tooltip({title:error.text(), trigger:'auto'});
	 item.tooltip('show');
	 $("#e_submit").button("reset");
       },
       highlight: function(element, errorClass, validClass) {
	 var item = $(element).parents(".control-group");
	 item.addClass(errorClass); 
       },
       unhighlight: function(element, errorClass, validClass) {
	 var item = $(element).parents(".control-group");
	 item.removeClass(errorClass); 
	 item.tooltip('hide');
       }
    });
    
    $('#form0').ajaxForm({clearForm: false, success: function(data) { 
      $('#new-data-preview').html(data);
      if($('#new-data-preview').find('#form-error').html()) {
	var err = $('#new-data-preview').find('#form-error');
	err.dialog({ modal: true, width: "40em", zIndex: 3, autoOpen: false,  buttons: [
	  { text: "Ok",
	    click: function() { $(this).dialog("close"); $('#new-data-preview').find('#form-error').detach(); $("#e_submit").button("reset"); } } ] });
	err.dialog('open');      
      } else {
	$('#new-data-form').hide();  
	$('#new-data-preview').show();
	if( $('#activity_list li:first-child').attr('id') ) {
  	  $('#form1').find('#act_last').val($('#activity_list li:first-child').attr('id').substring('activity_'.length)); 
	}
	$('#form1').ajaxForm( { beforeSubmit: function() {$('#form1').find("#e_submit").button("loading");}, success: function(data) {      	
	  $('#new-data').dialog('close');	
	  $('#new-data-form').html('');
	  $('#new-data-preview').html('');
	  $('#activity_list').prepend(data);	
	  if(auto_open_nc) {
	    $('#new-nc').html("Inserire altra Non conformit&agrave; ?")
	    $('#new-nc').dialog({ title: "Nuova Non conformit&agrave;", modal: true, width: "40em", zIndex: 3, autoOpen: false,  buttons: [
	      { text: "Si",
		click: function() { $(this).dialog("close"); opennewnc(); } }, 
	      { text: "No",
		click: function() { $(this).dialog("close"); auto_open_nc = false;} } ] });
	    $('#new-nc').dialog('open');
	  } else if( $.browser.msie && ($.browser.version == "7.0" || $.browser.version == "8.0") ) {
	    window.location.href = "/a";
	  }	
	}});
      }
	
    }, beforeSubmit: function(arr,$form) {
      $('#form0').find("#e_submit").button("loading");
    }, beforeSerialize: function($form, options) {
      $("[name='tags']").attr('value','');
      var tags = $("#item_tags_handler").tagHandler("getTags")
      for(var tag in tags) {
	$form.append("<input type='hidden' name='tags' value='"+tags[tag]+"'/>");
      }
    }});
	
    $('#new-data').show();
    $('#new-data-form').show();
    $('#new-data').dialog({ title: $('#title').text(), modal: true, height: 550, width: 810, zIndex: 2, autoOpen: false,  beforeClose: closeAlert});
    $('#new-data').dialog('open');
  }); 
}

function onclosenewitem() {
  ulmsg=false;
  $('#new-data').dialog('close');
  //$('#new-data').html('');
  return false;
}

function opennewisp() {
 auto_open_nc = true;
 $('#new-data-form').html("");
 $('#new-data-preview').html("");
 opennewwiz("/isp/isp");
}

function opennewnc() {
 auto_open_nc = true;
 $('#new-data-form').html("");
 $('#new-data-preview').html("");
 opennewitem("/isp/nc");
}

function opennewdieta() {
 $('#new-data-form').html("");
 $('#new-data-preview').html("");
  opennewwiz("/isp/dieta");
}

function opennewnota() {
 $('#new-data-form').html("");
 $('#new-data-preview').html("");
 opennewitem("/isp/nota");
}

function previewback() {
 $("#e_submit").button("reset");
 $('#new-data-preview').hide();
 $('#new-data-form').show();
}

function filteractivities(q) {
  if(q) {
    query = q;
  }
  offset=0;
  $("#nav-sec").children().removeClass("loading");
  var item = $("#"+query.replace(/&/gi, "").replace(/=/gi, ""))
  item.addClass("loading");
  $.ajax({url:'/comments/load?'+query+'&offset='+offset, success: function(data){
    $('#activity_list').html('');
    $('#activity_list').append(data);    
    offset += 1;
    $("#nav-sec").children().removeClass("active");
    item.removeClass("loading");
    item.addClass("active");
  }}); 
}

function moreactivities() {
  $('#e_act_more').button('loading');
  $.ajax({url:'/comments/load?'+query+'&ease=1'+'&offset='+offset, success: function(data){
    $('#activity_list').append(data);
    offset += 1;
    $('#e_act_more').button('reset');
  }}); 
}

function filtercm() {
  $('#dropdown').click(); 
  $('#dropdown').html('<b>'+$('#commissione_sel').val()+'</b><b class="caret"></b>'); 
  $('#dropdown').parent().attr("id", "cm" + $('#cm').val() + "typeusertag");
  filteractivities('cm='+$('#cm').val()+'&type=&user=&tag=');
}