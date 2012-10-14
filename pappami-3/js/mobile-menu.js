jQuery(document).ready(function(){
    
  var templateId = 'p-pappa-mi-menu';
  var userpappami = {};
  veespo.templates.add( templateId, 'pagecreate', function(event, entry){
    
    entry.refs.header.find('span[data-v-title]').text("Pappa Mi");    
    entry.refs.content.html("");

    // School
    var sel_sk = $('<select data-native-menu="false">').change(function(evt){});
    var sel_date = $('<select data-native-menu="false">');    

    //veespo.ready(function(){

      $.ajax({url:"/api/getuser", 
	      dataType:'json',
	      success:function(data) { 

	userpappami = data;
       
	veespo.set.group("group-pappa-mi");
	veespo.set.lang("it");
	veespo.set.userId("uid-" + userpappami.id);
	veespo.set.userName(userpappami.fullname);
       
	for( school in userpappami.schools) {	
	  sel_sk.append( $("<option>").attr("value", "sk-pappa-mi-" + userpappami.schools[school].id).text(userpappami.schools[school].name));
	}     
	sel_sk.find("option[value='" + "sk-pappa-mi-" + userpappami.schools[school].id + "']").attr("selected",1);
        entry.refs.content.append(sel_sk);
  

	// spacer
	entry.refs.content.append($('<div style="height: 20px;"></div>'));

	// Data
	sel_date.change(
	    function(evt){
	      
	      var date  = mutils.event.elem(evt).val();
	      if (date == "data-pappa-mi-0"){
		entry.refs.menuAnc.empty();
		return false;
	      }
	      
	      pappami.resetMenu = false;
	      var menu  = window.pappami.td.getMenu();
	      console.log("menu", menu);
	      
	      var list = [];
	      for (var k in menu){
		list.push(menu[k]);
	      };
	      
	      var template = '';
	      template += '<table class="pappa-mi-menu">';
	      template += '{{#list}}'; 
	      template += '<tr data-veespo-id="{{id}}">';
	      template += '<td class="left">{{desc1}}</td>';
	      template += '<td class="right"><span data-role="button" data-mini="true" data-icon="plus" data-iconpos="right">Vota</span></td>';
	      template += '</tr>';
	      template += '{{/list}}'; 
	      template += '</table>';
	      
	      var html = $(Mustache.to_html(template, {list:list} ));
	      entry.refs.menuAnc.html($(html)).trigger("create");
		   
	      entry.refs.menuAnc.find('span[data-role]="button"').bind('tap', function(evt){
		var e  = mutils.event.elem(evt);
		var id = mutils.geu(e, "data-veespo-id", "att");
		var title = pappami.td.getDish(id).desc1;
		veespo.set.target(id, "group-pappa-mi", title);
		veespo.display();
	      }); 
	  });
    
	var dates = {"data-pappa-mi-0" : "Scegli Giorno"};
	now = new Date();
	for( i=0;i<=7;i++) {
	 date = new Date(now.getFullYear(), now.getMonth(), now.getDate()-i);
	 if(date.getDay()<6 && date.getDay()>0) {
	  dates["data-pappa-mi-" + date.toJSON()]=date.toLocaleDateString();
	  sel_date.append( $("<option>").attr("value", date.toJSON()).text(date.toLocaleDateString()));
	 }
	}
    
	sel_date.find("option[value='" + pappami.data + "']").attr("selected",1);
	entry.refs.content.append(sel_date);  
	
	entry.refs.content.append($('<p style="margin: 30px 0 5px 0">Menu:</p>'));
	entry.refs.menuAnc = $("<div/>");
	entry.refs.content.append(entry.refs.menuAnc);
	
	entry.refs.footer.find('span[data-v-back]').bind('tap', function(){
	  $.mobile.changePage('#page-init', {changeHash: true, transition: 'fade'});  
	 });

      }});    
    //});

    
   
  });
  
  veespo.templates.add( templateId, 'pagebeforeshow', function(event, entry){ 
    console.log("Schools page...");
    entry.refs.header.find('span[data-v-title]').text(userpappami.fullname);
    if (pappami.resetMenu){
      //entry.refs.menuAnc.empty();
    } else {
      var lrt = veespo.get.lastSavedTargetId();
      entry.refs.menuAnc.find('span[data-role]="button"').each(function(){
        var e = $(this);
        var id = mutils.geu(e, "data-veespo-id", "att");
        if (id == lrt){
          console.log("setting data icon for: " + lrt);
          e.find(".ui-icon").addClass("ui-icon-check").removeClass("ui-icon-plus");
        }
      });
    }  
  }); 
  
});  
  
