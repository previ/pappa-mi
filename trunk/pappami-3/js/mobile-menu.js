//$(document).ready(function() {
  $("#page-menu").bind('pageinit', function(event, entry) {
    //$("page-menu").find('span[data-v-title]').text("Pappa Mi");    

    // School
    var params = $('<fieldset id="params" data-role="controlgroup" data-type="horizontal"/>');
    var sel_sk = $('<select id="cm" name="school" data-mini="true" data-native-menu="false"/>');
    var sel_date = $('<select id="data" name="cm" data-mini="true" data-native-menu="false"/>');    

    veespo.ready(function(){

      $.ajax({url:"/api/getuser", 
	      dataType:'json',
	      success:function(data) { 

	userpappami = data;
       
	$('#user').text(userpappami.fullname);
	veespo.set.group("group-pappa-mi");
	veespo.set.lang("it");
	veespo.set.userId("uid-" + userpappami.id);
	veespo.set.userName(userpappami.fullname);
       
	for( school in userpappami.schools) {

	  sel_sk.append( $("<option>").attr("value", "sk-pappa-mi-" + userpappami.schools[school].id).text(userpappami.schools[school].name));
	}     
	sel_sk.find("option[value='" + "sk-pappa-mi-" + userpappami.schools[school].id + "']").attr("selected",1);

	now = new Date();
	for( i=0;i<=7;i++) {
	 date = new Date(now.getFullYear(), now.getMonth(), now.getDate()-i);
	 if(date.getDay()<6 && date.getDay()>0) {
	  var d = $("<option>");
	  if(i==0){
	    d.attr("selected",1);
	  }
	  sel_date.append( d.attr("value", "dt-pappa-mi-"+(date.getFullYear())+"-"+date.getMonth()+"-"+date.getDate()).text(date.toLocaleDateString("it")));
	 }
	}
    
	// Data
	params.append(sel_sk);
	params.append(sel_date);
	$('#page-menu').find('[data-role="content"]').append(params).trigger("create");

	sel_date.change( loadMenu );
	sel_sk.change( loadMenu );
    
	sel_date.trigger("change");
      }});    
    });
   
  });
  
  $("#page-menu").bind('swipeleft', function(event, entry) {
    var sel_date = $('#data');    
    var cur_sel = sel_date.find("[selected]");
    next_sel = cur_sel.next();
    if(next_sel) {
      next_sel.attr("selected", "true");
      cur_sel.removeAttr("selected");
    }
  });
  $("#page-menu").bind('swiperight', function(event, entry) {
    var sel_date = $('#data');    
    var cur_sel = sel_date.find("[selected]");
    next_sel = cur_sel.previous();
    if(next_sel) {
      next_sel.attr("selected", "true");
      cur_sel.removeAttr("selected");
    }
  });

  $("#page-menu").bind('pagebeforeshow', function(event){ 
    console.log("Schools page...");
    /*$("#page-menu").find('span[data-v-title]').text(userpappami.fullname);
    if (pappami.resetMenu){
      //entry.refs.menuAnc.empty();
    } else {*/
      var lrt = veespo.get.lastSavedTargetId();
      $("#page-menu").find('span[data-role]="button"').each(function(){
        var e = $(this);
        var id = mutils.geu(e, "data-veespo-id", "att");
        if (id == lrt){
          console.log("setting data icon for: " + lrt);
          e.find(".ui-icon").addClass("ui-icon-check").removeClass("ui-icon-plus");
        }
      });
    //}  
  }); 

//});  

var menu = {};
function loadMenu() {
  
  var date = $('#data').val(); 
  var cm = $('#cm').val();
  var params = {'date': date.substring("dt-pappa-mi-".length), 'school': cm.substring("sk-pappa-mi-".length) };
  
  $.ajax({url:"/api/getmenu",
	data: params,
	dataType:'json',
	success:function(data) { 
    menu = data;
  
    var list = [];
    for (var k in menu){
      list.push(menu[k]);
    };
  
    var template = '';
    template += '<table class="pappa-mi-menu">';
    template += '{{#list}}'; 
    template += '<tr data-veespo-id="demo-pappa-mi-{{id}}">';
    template += '<td class="left">{{desc1}}</td>';
    template += '<td class="right"><span data-role="button" data-mini="true" data-icon="plus" data-iconpos="right">Vota</span></td>';
    template += '</tr>';
    template += '{{/list}}'; 
    template += '</table>';
  
    var html = $(Mustache.to_html(template, {list:list} ));
    $('#menu').html($(html)).trigger("create");
       
    $('#menu').find('span[data-role]="button"').bind('tap', function(evt){
      for (var i=$.mobile.urlHistory.activeIndex-1; i>=0; i--){
	if ($.mobile.urlHistory.stack[i].url.indexOf("page-veespo") == -1){
	  return i;
	}
      }

      var e  = mutils.event.elem(evt);
      var id = mutils.geu(e, "data-veespo-id", "att");
      var title = getDish(id.substring('demo-pappa-mi-'.length)).desc1;
      veespo.set.target(id, "group-pappa-mi", title);
      veespo.display();
    });
  }});
}

/*
 * Torna l'oggetto relativo al id del piatto passato
 */
function getDish(id){
  for(dish in menu) {
    if(menu[dish].id == id){
      return menu[dish];
    }
  }
  throw(new Error("Failed to find dish: " + id));
};
