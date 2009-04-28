if(!dojo._hasResource["custom.PTimeTextBox"]){
dojo._hasResource["custom.PTimeTextBox"]=true;
dojo.provide("custom.PTimeTextBox");

dojo.require("dijit.form.TimeTextBox");

alert("pippo");

dojo.declare("PTimeTextBox",dijit.form.TimeTextBox, {
      serialize: function(d, options) {
        return dojo.date.locale.format(d, {selector:'time', timePattern:'HH:mm:ss'}).toLowerCase();
      }
    });
