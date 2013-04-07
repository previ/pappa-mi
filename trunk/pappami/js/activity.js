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
  $('#new-data').find( "[type='radio']" ).button();
}

var auto_open_nc = false;

jQuery.validator.addMethod("numpastibambini", function(value, element) { 
 return parseInt(value) <= parseInt($("#e_numeroPastiTotale").val()); 
} );
jQuery.validator.addMethod("numpastispeciali", function(value, element) { 
 return value <= parseInt($("#e_numeroPastiBambini").val()); 
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
	    $('#form1').find('#node').val($('#form_node').val()); 

	    // on preview form submit
	    if( $('#activity_list li:first-child').attr('id') ) {	    
	      $('#form1').find('#act_last').val($('#activity_list li:first-child').attr('id').substring('activity_'.length)); 
	    }
	    $('#form1').ajaxForm( {beforeSubmit: function() {$('#form1').find("#e_submit").button("loading");}, success: function(data) {
	      data=jQuery.parseJSON(data)
	      $('#new-data').dialog('close');
	      $('#new-data-form').html('');
	      $('#new-data-preview').html('');
	      if (data.response!="success") {
	       if(data.response=="flooderror"){
		onFloodError(data)
		return			  
	       }
	      }
	      $("#main_stream_list").prepend(data.html)	      
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
	$('#form1').find('#node').val($('#form_node').val()); 
	if( $('#activity_list li:first-child').attr('id') ) {
  	  $('#form1').find('#act_last').val($('#activity_list li:first-child').attr('id').substring('activity_'.length)); 
	}
	$('#form1').ajaxForm( { beforeSubmit: function() {$('#form1').find("#e_submit").button("loading");}, success: function(data) {
	  data=jQuery.parseJSON(data)
	  $('#new-data').dialog('close');	
	  $('#new-data-form').html('');
	  $('#new-data-preview').html('');
	  if (data.response!="success") {
	    if(data.response=="flooderror"){
	      onFloodError(data)
	      return			  
	    }
	  }
	  $("#main_stream_list").prepend(data.html)	      
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
    }
    });
	
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


