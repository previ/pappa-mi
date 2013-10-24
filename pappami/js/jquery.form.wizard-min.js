(function(a){a.widget("ui.formwizard",{_init:function(){var b=this;var c=this.options.formOptions.success;var d=this.options.formOptions.complete;var e=this.options.formOptions.beforeSend;var f=this.options.formOptions.beforeSubmit;var g=this.options.formOptions.beforeSerialize;this.options.formOptions=a.extend(this.options.formOptions,{success:function(a,d,e){if(c){c(a,d,e)}if(b.options.formOptions&&b.options.formOptions.resetForm||!b.options.formOptions){b._reset()}},complete:function(a,c){if(d){d(a,c)}b._enableNavigation()},beforeSubmit:function(a,c,d){if(f){var e=f(a,c,d);if(!e)b._enableNavigation();return e}},beforeSend:function(a){if(e){var c=e(a);if(!c)b._enableNavigation();return c}},beforeSerialize:function(a,c){if(g){var d=g(a,c);if(!d)b._enableNavigation();return d}}});this.steps=this.element.find(".step").hide();this.firstStep=this.steps.eq(0).attr("id");this.activatedSteps=new Array;this.isLastStep=false;this.previousStep=undefined;this.currentStep=this.steps.eq(0).attr("id");this.nextButton=this.element.find(this.options.next).click(function(){return b._next()});this.nextButtonInitinalValue=this.nextButton.val();this.nextButton.val(this.options.textNext);this.backButton=this.element.find(this.options.back).click(function(){b._back();return false});this.backButtonInitinalValue=this.backButton.val();this.backButton.val(this.options.textBack);if(this.options.validationEnabled&&jQuery().validate==undefined){this.options.validationEnabled=false;if(window["console"]!==undefined){console.log("%s","validationEnabled option set, but the validation plugin is not included")}}else if(this.options.validationEnabled){this.element.validate(this.options.validationOptions)}if(this.options.formPluginEnabled&&jQuery().ajaxSubmit==undefined){this.options.formPluginEnabled=false;if(window["console"]!==undefined){console.log("%s","formPluginEnabled option set but the form plugin is not included")}}if(this.options.disableInputFields==true){a(this.steps).find(":input:not('.wizard-ignore')").attr("disabled","disabled")}if(this.options.historyEnabled){a(window).bind("hashchange",undefined,function(c){var d=c.getState("_"+a(b.element).attr("id"))||b.firstStep;if(d!==b.currentStep){if(b.options.validationEnabled&&d===b._navigate(b.currentStep)){if(!b.element.valid()){b._updateHistory(b.currentStep);b.element.validate().focusInvalid();return false}}if(d!==b.currentStep)b._show(d)}})}this.element.addClass("ui-formwizard");this.element.find(":input").addClass("ui-wizard-content");this.steps.addClass("ui-formwizard-content");this.backButton.addClass("ui-formwizard-button ui-wizard-content");this.nextButton.addClass("ui-formwizard-button ui-wizard-content");if(!this.options.disableUIStyles){this.element.addClass("ui-helper-reset ui-widget ui-widget-content ui-helper-reset ui-corner-all");this.element.find(":input").addClass("ui-helper-reset ui-state-default");this.steps.addClass("ui-helper-reset ui-corner-all");this.backButton.addClass("ui-helper-reset ui-state-default");this.nextButton.addClass("ui-helper-reset ui-state-default")}this._show(undefined);return a(this)},_next:function(){if(this.options.validationEnabled){if(!this.element.valid()){this.element.validate().focusInvalid();return false}}if(this.options.remoteAjax!=undefined){var b=this.options.remoteAjax[this.currentStep];var c=this;if(b!==undefined){var d=b.success;var e=b.beforeSend;var f=b.complete;b=a.extend({},b,{success:function(a,b){if(d!==undefined&&d(a,b)||d==undefined){c._continueToNextStep()}},beforeSend:function(b){c._disableNavigation();if(e!==undefined)e(b);a(c.element).trigger("before_remote_ajax",{currentStep:c.currentStep})},complete:function(b,d){if(f!==undefined)f(b,d);a(c.element).trigger("after_remote_ajax",{currentStep:c.currentStep});c._enableNavigation()}});this.element.ajaxSubmit(b);return false}}return this._continueToNextStep()},_back:function(){if(this.activatedSteps.length>0){if(this.options.historyEnabled){this._updateHistory(this.activatedSteps[this.activatedSteps.length-2])}else{this._show(this.activatedSteps[this.activatedSteps.length-2],true)}}return false},_continueToNextStep:function(){if(this.isLastStep){for(var a=0;a<this.activatedSteps.length;a++){this.steps.filter("#"+this.activatedSteps[a]).find(":input").not(".wizard-ignore").removeAttr("disabled")}if(!this.options.formPluginEnabled){return true}else{this._disableNavigation();this.element.ajaxSubmit(this.options.formOptions);return false}}var b=this._navigate(this.currentStep);if(b==this.currentStep){return false}if(this.options.historyEnabled){this._updateHistory(b)}else{this._show(b,true)}return false},_updateHistory:function(b){var c={};c["_"+a(this.element).attr("id")]=b;a.bbq.pushState(c)},_disableNavigation:function(){this.nextButton.attr("disabled","disabled");this.backButton.attr("disabled","disabled");if(!this.options.disableUIStyles){this.nextButton.removeClass("ui-state-active").addClass("ui-state-disabled");this.backButton.removeClass("ui-state-active").addClass("ui-state-disabled")}},_enableNavigation:function(){if(this.isLastStep){this.nextButton.val(this.options.textSubmit)}else{this.nextButton.val(this.options.textNext)}if(a.trim(this.currentStep)!==this.steps.eq(0).attr("id")){this.backButton.removeAttr("disabled");if(!this.options.disableUIStyles){this.backButton.removeClass("ui-state-disabled").addClass("ui-state-active")}}this.nextButton.removeAttr("disabled");if(!this.options.disableUIStyles){this.nextButton.removeClass("ui-state-disabled").addClass("ui-state-active")}},_animate:function(a,b,c){this._disableNavigation();var d=this.steps.filter("#"+a);var e=this.steps.filter("#"+b);d.find(":input").not(".wizard-ignore").attr("disabled","disabled");e.find(":input").not(".wizard-ignore").removeAttr("disabled");var f=this;d.animate(f.options.outAnimation,f.options.outDuration,f.options.easing,function(){e.animate(f.options.inAnimation,f.options.inDuration,f.options.easing,function(){if(f.options.focusFirstInput){try{e.find(":input:first").focus()}catch(a){}}f._enableNavigation();c.apply(f)});return})},_checkIflastStep:function(b){this.isLastStep=false;if(a("#"+b).hasClass(this.options.submitStepClass)||this.steps.filter(":last").attr("id")==b){this.isLastStep=true}},_getLink:function(b){var c=undefined;var d=this.steps.filter("#"+b).find(this.options.linkClass);if(d!=undefined){if(d.filter(":radio,:checkbox").size()>0){c=d.filter(this.options.linkClass+":checked").val()}else{c=a(d).val()}}return c},_navigate:function(a){var b=this._getLink(a);if(b!=undefined){if(b!=""&&b!=null&&b!=undefined&&this.steps.filter("#"+b).attr("id")!=undefined){return b}return this.currentStep}else if(b==undefined&&!this.isLastStep){var c=this.steps.filter("#"+a).next().attr("id");return c}},_show:function(b){var c=false;var d=b!==undefined;if(b==undefined||b==""){this.activatedSteps.pop();b=this.firstStep;this.activatedSteps.push(b)}else{if(a.inArray(b,this.activatedSteps)>-1){c=true;this.activatedSteps.pop()}else{this.activatedSteps.push(b)}}if(this.currentStep!==b||b===this.firstStep){this.previousStep=this.currentStep;this._checkIflastStep(b);this.currentStep=b;var e=function(){if(d)a(this.element).trigger("step_shown",a.extend({isBackNavigation:c},this._state()))};this._animate(this.previousStep,b,e)}},_reset:function(){this.element.resetForm();a("label,:input,textarea",this).removeClass("error");for(var b=0;b<this.activatedSteps.length;b++){this.steps.filter("#"+this.activatedSteps[b]).hide().find(":input").attr("disabled","disabled")}this.activatedSteps=new Array;this.previousStep=undefined;this.isLastStep=false;if(this.options.historyEnabled){this._updateHistory(this.firstStep)}else{this._show(this.firstStep)}},_state:function(a){var b={settings:this.options,activatedSteps:this.activatedSteps,isLastStep:this.isLastStep,isFirstStep:this.currentStep===this.firstStep,previousStep:this.previousStep,currentStep:this.currentStep,backButton:this.backButton,nextButton:this.nextButton,steps:this.steps,firstStep:this.firstStep};if(a!==undefined)return b[a];return b},show:function(a){if(this.options.historyEnabled){this._updateHistory(a)}else{this._show(a)}},state:function(a){return this._state(a)},reset:function(){this._reset()},next:function(){this._next()},back:function(){this._back()},destroy:function(){this.element.find("*").removeAttr("disabled").show();this.nextButton.unbind("click").val(this.nextButtonInitinalValue).removeClass("ui-state-disabled").addClass("ui-state-active");this.backButton.unbind("click").val(this.backButtonInitinalValue).removeClass("ui-state-disabled").addClass("ui-state-active");this.backButtonInitinalValue=undefined;this.nextButtonInitinalValue=undefined;this.activatedSteps=undefined;this.previousStep=undefined;this.currentStep=undefined;this.isLastStep=undefined;this.options=undefined;this.nextButton=undefined;this.backButton=undefined;this.formwizard=undefined;this.element=undefined;this.steps=undefined;this.firstStep=undefined},update_steps:function(){this.steps=this.element.find(".step").addClass("ui-formwizard-content");this.steps.not("#"+this.currentStep).hide().find(":input").addClass("ui-wizard-content").attr("disabled","disabled");this._checkIflastStep(this.currentStep);this._enableNavigation();if(!this.options.disableUIStyles){this.steps.addClass("ui-helper-reset ui-corner-all");this.steps.find(":input").addClass("ui-helper-reset ui-state-default")}},options:{historyEnabled:false,validationEnabled:false,validationOptions:undefined,formPluginEnabled:false,linkClass:".link",submitStepClass:"submit_step",back:":reset",next:":submit",textSubmit:"Submit",textNext:"Next",textBack:"Back",remoteAjax:undefined,inAnimation:{opacity:"show"},outAnimation:{opacity:"hide"},inDuration:400,outDuration:400,easing:"swing",focusFirstInput:false,disableInputFields:true,formOptions:{reset:true,success:function(a){if(window["console"]!==undefined){console.log("%s","form submit successful")}},disableUIStyles:false}}})})(jQuery)