var ulmsg=false;
window.onbeforeunload = closeAlert;

function closeAlert() {
  if(ulmsg) {
    if( confirm("Attenzione, la pagina contiene dati non salvati, uscire comunque ?") ) {
      ulmsg=false;  
      return true;
    } else {
      return false;
    }
  }
}

function closedialog() {
  cleardirty();
  $('#new-data').dialog('close');
}

function cleardirty() {
  ulmsg=false;
}

function initForm() {
  ulmsg=true;
  $('#new-data').find("[title]").tooltip({"delay":3000});
  $("#item_tags_handler").tagHandler({
      getData: { 'msg': "" },
      getURL: '/comments/gettags',            
      autocomplete: true
  }); 
 $('#new-data').find( "[type='radio']" ).button();
 $('#new-data').find('.radio-group > label').radioGroup();
 $('#new-data').find('.btn.toggle').toggleBtn();
}

function opennewmsg() {  
  if($('#new-msg').is(':visible') ) {
    $('#new-msg').slideUp();
  } else {
    $('#act_last').val($('#activity_list li:first-child').attr('id').substring('activity_'.length));  
    $('#new-msg-form').ajaxForm({clearForm: true, success: function(data) { 	
      $('#activity_list').prepend(data);
      //$('#act_last').val($('ul.activity_list > li').attr('id').substring('activity_'.length));
    }, beforeSubmit: function(arr,$form) {     
      $("[name='tags']").attr('value','');
      tags = $("#message_tags_handler").tagHandler("getTags")
      for(tag in tags) {
	arr.push({name: "tags", value: tags[tag]});
      }
      $('#new-msg').slideUp();
    }}); 
    $("#message_tags_handler").tagHandler({
	getData: { 'msg': "" },
	getURL: '/comments/gettags',            
	autocomplete: true
    });
    $('#new-msg').slideDown();  
  }
}

function opennewwiz(url) {
  $('#new-data-form').load(url, function(){
    initForm();
    $("#form0").formwizard({ 
      formPluginEnabled: true,
      validationEnabled: true,
      validationOptions: {
	errorClass: "error",
	errorPlacement: function(error, element) {	
	  //alert(element);
	  //$('<span class="help-inline">' + error.text() + "</span>").appendTo( $(element).parents(".control-group") );	  
	  item = $(element).parents(".control-group");
	  //item.attr("err-title", error.text());
	  item.tooltip({title:error.text(), trigger:'manual'});
	  item.tooltip('show');
        },
	highlight: function(element, errorClass, validClass) {
	    item = $(element).parents(".control-group");
	    item.addClass(errorClass); 
    	    //item.tooltip('show');
	    //$($($(element).parent()).parent()).tooltip('show');
	    //alert("pippo");
	    //$($($($($(element).parent()).parent()).parent()).parent()).addClass(errorClass).removeClass(validClass);
	 },
	unhighlight: function(element, errorClass, validClass) {
	    item = $(element).parents(".control-group");
	    item.removeClass(errorClass); 
    	    item.tooltip('hide');
	    //$(element).parents(".control-group").removeClass(errorClass); 
	    //$(element).parents(".control-group").find(".help-inline").remove()
	    //$($($(element).parent()).parent()).tooltip('hide');
	    //alert("pappo");	
	    //$($($($($(element).parent()).parent()).parent()).parent()).addClass(validClass).removeClass(errorClass);
	 }
      },
      focusFirstInput : true,
      textNext: "Avanti",
      textBack: "Indietro",
      disableUIStyles: true,
      remoteAjax : {"step1" : { // add a remote ajax call when moving next from the second step
	url : url + "val", 
	dataType : 'text',
	//beforeSend : function(){alert("Starting validation.")},
	//complete : function(){alert("Validation complete.")},
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
		click: function() { $('#form-error').detach(); $(this).dialog("close"); } } ] });
	    $('#form-error').dialog('open');
	    $('#new-data-preview').text('');
	  } else {
	    $('#new-data-form').hide();  
	    $('#new-data-preview').show();
	    // on preview form submit
	    $('#form1').find('#act_last').val($('#activity_list li:first-child').attr('id').substring('activity_'.length)); 
	    $('#form1').ajaxForm(function(data) {
	      $('#new-data').dialog('close');
	      $('#new-data-form').text('');
	      $('#new-data-preview').text('');
	      $('#activity_list').prepend(data);
	      $('#new-nc').html("Inserire anche una Non conformit&agrave; ?")
	      $('#new-nc').dialog({ title: "Nuova Non conformità", modal: true, width: "40em", zIndex: 3, autoOpen: false,  buttons: [
		{ text: "Si",
		  click: function() { $(this).dialog("close"); opennewnc(); } }, 
		{ text: "No",
		  click: function() { $(this).dialog("close"); } } ] });
	      $('#new-nc').dialog('open');
	    });
	  }
	},
	resetForm: false,
	beforeSubmit: function() {
	  $("[name='tags']").attr('value','');
          tags = $("#wiz_tags_handler").tagHandler("getTags")
          for(tag in tags) {
    	    arr.push({name: "tags", value: tags[tag]});
	  }
	}
      }
    });
    $.validator.messages = {
	number: "Inserire in numero",
	required: "Inserire o selezionare un valore",
	range: "Inserire un valore compreso tra {0} e {1}" };
    $("#form0").bind("step_shown", function(event, data){
      $("#formwiz-progress-" + data.previousStep).toggleClass("active");
      $("#formwiz-progress-" + data.currentStep).toggleClass("active");
    });
    $('#new-data').show();
    $('#new-data-form').show();
    $("#formwiz-progress-step1").toggleClass("active");
    $('#new-data').dialog({ title: $('#title').text(), modal: true, height: 600, width: 810, zIndex: 2, autoOpen: false, beforeClose: closeAlert });
    $('#new-data').dialog('open');
  });
}

function onopennewitem() {
 initForm();
 
 $("#form0").validate({
   errorClass: "error",
   errorPlacement: function(error, element) {	
     //error.appendTo( element.parent().parent() );
     //alert(error.text());
     $($($(element).parent()).parent()).attr("title", error.text());
     $($($(element).parent()).parent()).tooltip({title:'data-original-title', trigger:'manual'});
     $($($(element).parent()).parent()).tooltip('show');
   },
   highlight: function(element, errorClass, validClass) {
       $($($(element).parent()).parent()).tooltip('show');
    },
   unhighlight: function(element, errorClass, validClass) {
       $($($(element).parent()).parent()).tooltip('hide');
    }
  });
  
  $('#form0').ajaxForm({clearForm: false, success: function(data) { 
    $('#new-data-preview').html(data);
    if(data.indexOf('form-error')>0) {
      $('#form-error').dialog({ modal: true, width: "40em", zIndex: 3, autoOpen: false,  buttons: [
	{ text: "Ok",
          click: function() { $('#form-error').detach(); $(this).dialog("close"); } } ] });
      $('#form-error').dialog('open');      
    } else {
      $('#new-data-form').hide();  
      $('#new-data-preview').show();
      $('#form1').find('#act_last').val($('#activity_list li:first-child').attr('id').substring('activity_'.length)); 
      $('#form1').ajaxForm(function(data) {      
	$('#new-data').dialog('close');
	$('#new-data-form').text('');
	$('#new-data-preview').text('');
	$('#activity_list').prepend(data);
	$('#new-nc').html("Inserire altra Non conformit&agrave; ?")
	$('#new-nc').dialog({ title: "Nuova Non conformità", modal: true, width: "40em", zIndex: 3, autoOpen: false,  buttons: [
	  { text: "Si",
	    click: function() { $(this).dialog("close"); opennewnc(); } }, 
	  { text: "No",
	    click: function() { $(this).dialog("close"); } } ] });
	$('#new-nc').dialog('open');
      });
    }
      
  }, beforeSubmit: function(arr,$form) {
    $("[name='tags']").attr('value','');
    tags = $("#item_tags_handler").tagHandler("getTags")
    for(tag in tags) {
      arr.push({name: "tags", value: tags[tag]});
    }
  }});
  //$('textarea').autogrow();
  $.validator.messages = {
      required: "Inserire o selezionare un valore",
      range: "Inserire un valore compreso tra {0} e {1}" };
  $('#new-data').show();
  $('#new-data-form').show();
  $('#new-data').dialog({ title: $('#title').text(), modal: true, height: 550, width: 810, zIndex: 20000, autoOpen: false,  beforeClose: closeAlert});
  $('#new-data').dialog('open');
}

function onclosenewitem() {
  ulmsg=false;
  $('#new-data').dialog('close');
  //$('#new-data').html('');
  return false;
}

function opennewisp() {
 $('#new-data-form').text("");
 $('#new-data-preview').text("");
 opennewwiz("/isp/isp");
}

function opennewnc() {
 $('#new-data-form').text("");
 $('#new-data-preview').text("");
 $('#new-data-form').load("/isp/nc", onopennewitem);
}

function opennewdieta() {
 $('#new-data-form').text("");
 $('#new-data-preview').text("");
  opennewwiz("/isp/dieta");
}

function opennewnota() {
 $('#new-data-form').text("");
 $('#new-data-preview').text("");
 $('#new-data-form').load("/isp/nota", onopennewitem);
}

function previewback() {
 $('#new-data-preview').hide();
 $('#new-data-form').show();
}

function filteractivities(q) {
  if(q) {
    query = q;
  }
  offset=0;
  $.ajax({url:'/comments/load?'+query+'&offset='+offset, success: function(data){
    $('#activity_list').html('');
    $('#activity_list').append(data);    
    offset += 1;
    $("#nav-sec").children().removeClass("active");
    $("#"+query.replace(/&/gi, "").replace(/=/gi, "")).addClass("active");
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
