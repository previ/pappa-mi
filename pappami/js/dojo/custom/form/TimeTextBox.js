if(!dojo._hasResource["custom.form.TimeTextBox"]){
dojo._hasResource["custom.form.TimeTextBox"]=true;
dojo.provide("custom.form.TimeTextBox");

dojo.require("dijit.form.TimeTextBox");

dojo.declare("custom.form.TimeTextBox",dijit.form.TimeTextBox, {
      serialize: function(d, options) {
        return dojo.date.locale.format(d, {selector:'time',timePattern:'HH:mm:ss'}).toLowerCase();
      },
      postMixInProperties: function(){
                this.inherited(arguments);
                if(this.srcNodeRef){
                        var item = this.srcNodeRef.attributes.getNamedItem('value');
                        if(item){
                                this.value = dojo.date.locale.parse(item.value, {selector:'time',timePattern:'HH:mm:ss'});
                        }
                }
        },
        popupClass:""
});
}

