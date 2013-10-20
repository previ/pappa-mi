var Ieresizefix = {
	body : null, 
	currheight : null, 
	currwidth : null, 
	flag : true, 
	onresize : function() {
		if(Ieresizefix.currheight != document.documentElement.clientHeight ||
		   Ieresizefix.currwidth != document.documentElement.clientWidth
		) {
			if (Ieresizefix.flag) {
				Ieresizefix.flag = false;
				$("body").addClass('iedummy');
			} else {
				Ieresizefix.flag = true;
				$("body").removeClass('iedummy');
			}
		}		
		Ieresizefix.currheight = document.documentElement.clientHeight;
		Ieresizefix.currwidth = document.documentElement.clientWidth;
	}
}

function initIeresizefix() { 
	Ieresizefix.body = $('body');
	window.onresize = Ieresizefix.onresize;
}

$(document).ready(function () {
  initIeresizefix();
}); 