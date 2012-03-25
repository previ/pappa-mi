/*
Infomation
==========================================================================================
jQuery Plugin
	Name       : jquery.ajaxComboBox
	Version    : 4.3
	Update     : 2012-03-09
	Author     : sutara_lumpur
	Author-URI : http://d.hatena.ne.jp/sutara_lumpur/20090124/1232781879
	License    : MIT License (http://www.opensource.org/licenses/mit-license.php)
	Based-on   : Uses code and techniques from following libraries...
		* jquery.suggest 1.1
			Author     : Peter Vulgaris
			Author-URI : http://www.vulgarisoip.com/
==========================================================================================

Contents
==========================================================================================
01.å¤‰æ•°ãƒ»éƒ¨å“�ã�®å®šç¾©
	å¤‰æ•°ã�®åˆ�æœŸåŒ–
	éƒ¨å“�ã�®å®šç¾©
	éƒ¨å“�ã‚’ãƒšãƒ¼ã‚¸ã�«é…�ç½®

02.ã‚¤ãƒ™ãƒ³ãƒˆãƒ�ãƒ³ãƒ‰ãƒ©
	å…¨ä»¶å�–å¾—ãƒœã‚¿ãƒ³
	ãƒ†ã‚­ã‚¹ãƒˆå…¥åŠ›ã‚¨ãƒªã‚¢
	ãƒšãƒ¼ã‚¸ãƒŠãƒ“
	ã‚µãƒ–æƒ…å ±
	bodyå…¨ä½“

03.åˆ�æœŸå€¤
	ComboBoxã�«åˆ�æœŸå€¤ã‚’æŒ¿å…¥
	ãƒ‡ãƒ¼ã‚¿ãƒ™ãƒ¼ã‚¹ã�§ã�¯ã�ªã��ã€�JSONã�‹ã‚‰åˆ�æœŸå€¤ã‚’å¾—ã‚‹
	åˆ�æœŸåŒ–ç”¨Ajaxå¾Œã�®å‡¦ç�†

04.ãƒœã‚¿ãƒ³
	ãƒœã‚¿ãƒ³ã�®titleå±žæ€§ åˆ�æœŸ
	ãƒœã‚¿ãƒ³ã�®titleå±žæ€§ ãƒªã‚¹ãƒˆå±•é–‹ä¸­
	ãƒœã‚¿ãƒ³ã�®titleå±žæ€§ ãƒ­ãƒ¼ãƒ‰ä¸­
	ãƒœã‚¿ãƒ³ã�®ç”»åƒ�ã�®ä½�ç½®ã‚’èª¿æ•´ã�™ã‚‹
	ãƒ­ãƒ¼ãƒ‰ç”»åƒ�ã�®è¡¨ç¤ºãƒ»è§£é™¤

05.æœªåˆ†é¡ž
	é�¸æŠžå€™è£œã‚’è¿½ã�„ã�‹ã�‘ã�¦ç”»é�¢ã‚’ã‚¹ã‚¯ãƒ­ãƒ¼ãƒ«
	ã‚¿ã‚¤ãƒžãƒ¼ã�«ã‚ˆã‚‹å…¥åŠ›å€¤å¤‰åŒ–ç›£è¦–
	ã‚­ãƒ¼å…¥åŠ›ã�¸ã�®å¯¾å¿œ

06.Ajax
	Ajaxã�®ä¸­æ–­
	ãƒ‡ãƒ¼ã‚¿ãƒ™ãƒ¼ã‚¹ã�¸ã�®å•�ã�„å�ˆã‚�ã�›
	ãƒ‡ãƒ¼ã‚¿ãƒ™ãƒ¼ã‚¹ã�§ã�¯ã�ªã��ã€�JSONã‚’æ¤œç´¢
	searchInsteadOfDBå†…ã�®sortç”¨ã�®æ¯”è¼ƒé–¢æ•°
	å•�ã�„å�ˆã‚�ã�›å¾Œã�®å‡¦ç�†

07.ãƒšãƒ¼ã‚¸ãƒŠãƒ“
	ãƒŠãƒ“éƒ¨åˆ†ã‚’ä½œæˆ�
	1ãƒšãƒ¼ã‚¸ç›®ã�¸
	å‰�ã�®ãƒšãƒ¼ã‚¸ã�¸
	æ¬¡ã�®ãƒšãƒ¼ã‚¸ã�¸
	æœ€å¾Œã�®ãƒšãƒ¼ã‚¸ã�¸

08.å€™è£œãƒªã‚¹ãƒˆ
	å€™è£œä¸€è¦§ã�®<ul>æˆ�å½¢ã€�è¡¨ç¤º
	ç�¾åœ¨é�¸æŠžä¸­ã�®å€™è£œã�®æƒ…å ±ã‚’å�–å¾—
	ç�¾åœ¨é�¸æŠžä¸­ã�®å€™è£œã�«æ±ºå®šã�™ã‚‹
	é�¸æŠžå€™è£œã‚’æ¬¡ã�«ç§»ã�™
	é�¸æŠžå€™è£œã‚’å‰�ã�«ç§»ã�™
	å€™è£œã�®æ¶ˆåŽ»ã‚’æœ¬å½“ã�«å®Ÿè¡Œã�™ã‚‹ã�‹åˆ¤æ–­
	å€™è£œã‚¨ãƒªã‚¢ã‚’æ¶ˆåŽ»

09.ã‚µãƒ–æƒ…å ±
	ã‚µãƒ–æƒ…å ±ã�§é »ç¹�ã�«ä½¿ç”¨ã�™ã‚‹è¦�ç´ ã�®ã‚µã‚¤ã‚ºã‚’ç®—å‡º
	ã‚µãƒ–æƒ…å ±ã‚’è¡¨ç¤ºã�™ã‚‹

10.å‡¦ç�†ã�®å§‹ã�¾ã‚Š
	ã‚ªãƒ—ã‚·ãƒ§ãƒ³
	ãƒ¡ãƒƒã‚»ãƒ¼ã‚¸ã‚’è¨€èªžåˆ¥ã�«ç”¨æ„�

==========================================================================================
*/
(function($) {
	$.ajaxComboBox = function(combo_input, source, options, msg) {

		//Ajaxã�«ã�Šã�‘ã‚‹ã‚­ãƒ£ãƒƒã‚·ãƒ¥ã‚’ç„¡åŠ¹ã�«ã�™ã‚‹
		$.ajaxSetup({cache: false});
		
		//================================================================================
		//01.å¤‰æ•°ãƒ»éƒ¨å“�ã�®å®šç¾©
		//--------------------------------------------------------------------------------
		//**********************************************
		//å¤‰æ•°ã�®åˆ�æœŸåŒ–
		//**********************************************
		var show_hide        = false; //å€™è£œã‚’ã€�ã‚¿ã‚¤ãƒžãƒ¼å‡¦ç�†ã�§è¡¨ç¤ºã�™ã‚‹ã�‹ã�©ã�†ã�‹ã�®äºˆç´„
		var timer_show_hide  = false; //ã‚¿ã‚¤ãƒžãƒ¼ã€‚ãƒ•ã‚©ãƒ¼ã‚«ã‚¹ã�Œå¤–ã‚Œã�Ÿå¾Œã€�å€™è£œã‚’é�žè¡¨ç¤ºã�«ã�™ã‚‹ã�‹
		var timer_delay      = false; //hold timeout ID for suggestion result_area to appear
		var timer_val_change = false; //ã‚¿ã‚¤ãƒžãƒ¼å¤‰æ•°(ä¸€å®šæ™‚é–“ã�”ã�¨ã�«å…¥åŠ›å€¤ã�®å¤‰åŒ–ã‚’ç›£è¦–)
		var type_suggest     = false; //ãƒªã‚¹ãƒˆã�®ã‚¿ã‚¤ãƒ—ã€‚false=>å…¨ä»¶ / true=>äºˆæ¸¬
		var page_num_all     = 1;     //å…¨ä»¶è¡¨ç¤ºã�®éš›ã�®ã€�ç�¾åœ¨ã�®ãƒšãƒ¼ã‚¸ç•ªå�·
		var page_num_suggest = 1;     //å€™è£œè¡¨ç¤ºã�®éš›ã�®ã€�ç�¾åœ¨ã�®ãƒšãƒ¼ã‚¸ç•ªå�·
		var max_all          = 1;     //å…¨ä»¶è¡¨ç¤ºã�®éš›ã�®ã€�å…¨ãƒšãƒ¼ã‚¸æ•°
		var max_suggest      = 1;     //å€™è£œè¡¨ç¤ºã�®éš›ã�®ã€�å…¨ãƒšãƒ¼ã‚¸æ•°
		var now_loading      = false; //Ajaxã�§å•�ã�„å�ˆã‚�ã�›ä¸­ã�‹ã�©ã�†ã�‹ï¼Ÿ
		var reserve_btn      = false; //ãƒœã‚¿ãƒ³ã�®èƒŒæ™¯è‰²å¤‰æ›´ã�®äºˆç´„ã�Œã�‚ã‚‹ã�‹ã�©ã�†ã�‹ï¼Ÿ
		var reserve_click    = false; //ãƒžã‚¦ã‚¹ã�®ã‚­ãƒ¼ã‚’æŠ¼ã�—ç¶šã�‘ã‚‹æ“�ä½œã�«å¯¾å¿œã�™ã‚‹ã�Ÿã‚�mousedownã‚’æ¤œçŸ¥
		var $xhr             = false; //XMLHttpã‚ªãƒ–ã‚¸ã‚§ã‚¯ãƒˆã‚’æ ¼ç´�
		var key_paging       = false; //ã‚­ãƒ¼ã�§ãƒšãƒ¼ã‚¸ç§»å‹•ã�—ã�Ÿã�‹ï¼Ÿ
		var key_select       = false; //ã‚­ãƒ¼ã�§å€™è£œç§»å‹•ã�—ã�Ÿã�‹ï¼Ÿï¼Ÿ
		var prev_value       = '';    //ComboBoxã�®ã€�ä»¥å‰�ã�®å€¤

		//ã‚µãƒ–æƒ…å ±
		var size_navi        = null;  //ã‚µãƒ–æƒ…å ±è¡¨ç¤ºç”¨(ãƒšãƒ¼ã‚¸ãƒŠãƒ“ã�®é«˜ã�•)
		var size_results     = null;  //ã‚µãƒ–æƒ…å ±è¡¨ç¤ºç”¨(ãƒªã‚¹ãƒˆã�®ä¸Šæž ç·š)
		var size_li          = null;  //ã‚µãƒ–æƒ…å ±è¡¨ç¤ºç”¨(å€™è£œä¸€è¡Œåˆ†ã�®é«˜ã�•)
		var size_left        = null;  //ã‚µãƒ–æƒ…å ±è¡¨ç¤ºç”¨(ãƒªã‚¹ãƒˆã�®æ¨ªå¹…)
		var select_field;             //ã‚µãƒ–æƒ…å ±è¡¨ç¤ºã�®å ´å�ˆã�«å�–å¾—ã�™ã‚‹ã‚«ãƒ©ãƒ 
		if(options.sub_info){
			if(options.show_field && !options.hide_field){
				select_field = options.field + ',' + options.show_field;
			} else {
				select_field = '*';
			}
		} else {
			select_field = options.field;
			options.hide_field = '';
		}
		if(options.select_only && select_field != '*'){
			select_field += ',' + options.primary_key;
		}

		//ã‚»ãƒ¬ã‚¯ãƒˆå°‚ç”¨æ™‚ã€�ãƒ•ã‚©ãƒ¼ãƒ é€�ä¿¡ã�™ã‚‹ä¸€æ„�ã�®æƒ…å ±ã‚’æ ¼ç´�ã�™ã‚‹
		var primary_key = (options.select_only)
			? options.primary_key
			: '';

		//**********************************************
		//éƒ¨å“�ã�®å®šç¾©
		//**********************************************
		//ComboBoxæœ¬ä½“
		$(combo_input)
			.attr('autocomplete', 'off')
			.addClass(options.input_class)
			.wrap('<div>');

		var $container = $(combo_input).parent().addClass(options.container_class);
		
		var $button = $('<div>').addClass(options.button_class);
		var $img = $('<img>').attr('src', options.button_img);
		$container.append($button);
		$button.append($img);
		$container.append('<div style="clear:left"></div>');

		//ã‚µã‚¸ã‚§ã‚¹ãƒˆãƒªã‚¹ãƒˆ
		var $result_area = $('<div></div>')
			.addClass(options.re_area_class);

		var $navi = $('<div></div>')
			.addClass(options.navi_class);

		var $results = $('<ul></ul>')
			.addClass(options.results_class);

		$result_area.append($navi).append($results);
		$container.after($result_area);
		//ã‚µãƒ–æƒ…å ±
		var $attached_dl_set = $('<div></div>')
			.addClass(options.sub_info_class);

		//"ã‚»ãƒ¬ã‚¯ãƒˆå°‚ç”¨"ã‚ªãƒ—ã‚·ãƒ§ãƒ³ç”¨
		var $hidden = $('<input type="hidden" />')
			.attr({
				'name': $(combo_input).attr('name'),
				'id'  : $(combo_input).attr('name') + '_hidden'
			})
			.val('');

		//**********************************************
		//éƒ¨å“�ã‚’ãƒšãƒ¼ã‚¸ã�«é…�ç½®
		//**********************************************
		//ã‚»ãƒ¬ã‚¯ãƒˆå°‚ç”¨æ™‚ã€�hiddenã‚’è¿½åŠ 
		if(options.select_only) $container.append($hidden);

		//ComboBoxã�®å¹…ã‚’æ±ºå®š
		$container.width(
			$(combo_input).outerWidth() + $button.outerWidth()
/* &&& 2012å¹´3æœˆ9æ—¥ rz3005ã�•ã‚“ä¿®æ­£ã€‚å•�é¡Œã�Œã�ªã�‘ã‚Œã�°ã�„ã�šã‚Œå‰Šé™¤ã€‚
			$(combo_input).width() +
			parseInt($(combo_input).css('margin-left'), 10) +
			parseInt($(combo_input).css('margin-right'), 10) +
			parseInt($(combo_input).css('padding-left'), 10) +
			parseInt($(combo_input).css('padding-right'), 10) +
			parseInt($(combo_input).css('border-left-width'), 10) +
			parseInt($(combo_input).css('border-right-width'), 10) +
			$button.width() +
			parseInt($button.css('margin-left'), 10) +
			parseInt($button.css('margin-right'), 10) +
			parseInt($button.css('padding-left'), 10) +
			parseInt($button.css('padding-right'), 10) +
			parseInt($button.css('border-left-width'), 10) +
			parseInt($button.css('border-right-width'), 10)
*/
		);
		//ãƒœã‚¿ãƒ³ã�®é«˜ã�•ã€�ã‚¿ã‚¤ãƒˆãƒ«å±žæ€§ã€�ç”»åƒ�ã�®ä½�ç½®
		$button.height(
			$(combo_input).innerHeight()
/* &&& 2012å¹´3æœˆ9æ—¥ rz3005ã�•ã‚“ä¿®æ­£ã€‚å•�é¡Œã�Œã�ªã�‘ã‚Œã�°ã�„ã�šã‚Œå‰Šé™¤ã€‚		
			$(combo_input).height() +
			parseInt($(combo_input).css('padding-top'), 10) +
			parseInt($(combo_input).css('padding-bottom'), 10)
*/
		);
		btnAttrDefault();
		btnPositionAdjust();

		//ComboBoxã�«åˆ�æœŸå€¤ã‚’æŒ¿å…¥
		setInitVal();

		//================================================================================
		//02.ã‚¤ãƒ™ãƒ³ãƒˆãƒ�ãƒ³ãƒ‰ãƒ©
		//--------------------------------------------------------------------------------
		//**********************************************
		//å…¨ä»¶å�–å¾—ãƒœã‚¿ãƒ³
		//**********************************************
		$button.mouseup(function(ev) {
			if($result_area.css('display') == 'none') {
				clearInterval(timer_val_change);
				
				type_suggest = false;
				suggest();
				$(combo_input).focus();
			} else {
				hideResult();
			}
			ev.stopPropagation();
		});
		$button.mouseover(function() {
			reserve_btn = true;
			if (now_loading) return;
			$button
				.addClass(options.btn_on_class)
				.removeClass(options.btn_out_class);
		});
		$button.mouseout(function() {
			reserve_btn = false;
			if (now_loading) return;
			$button
				.addClass(options.btn_out_class)
				.removeClass(options.btn_on_class);
		});
		//æœ€åˆ�ã�¯mouseoutã�®çŠ¶æ…‹
		$button.mouseout();

		//**********************************************
		//ãƒ†ã‚­ã‚¹ãƒˆå…¥åŠ›ã‚¨ãƒªã‚¢
		//**********************************************
		//å‰�å‡¦ç�†(ã‚¯ãƒ­ã‚¹ãƒ–ãƒ©ã‚¦ã‚¶ç”¨)
		if(window.opera){
			//Operaç”¨
			$(combo_input).keypress(processKey);
		}else{
			//ã��ã�®ä»–ç”¨
			$(combo_input).keydown(processKey);
		}
		
		$(combo_input).focus(function() {
			show_hide = true;
			checkValChange();
		});
		$(combo_input).blur(function(ev) {
			
			//å…¥åŠ›å€¤ã�®ç›£è¦–ã‚’ä¸­æ­¢
			clearTimeout(timer_val_change);

			//å€™è£œæ¶ˆåŽ»ã‚’äºˆç´„
			show_hide = false;

			//æ¶ˆåŽ»äºˆç´„ã‚¿ã‚¤ãƒžãƒ¼ã‚’ã‚»ãƒƒãƒˆ
			checkShowHide();

			//ã‚»ãƒ¬ã‚¯ãƒˆçŠ¶æ…‹ã‚’ç¢ºèª�
			btnAttrDefault();
		});
		$(combo_input).mousedown(function(ev) {
			reserve_click = true;

			//æ¶ˆåŽ»äºˆç´„ã‚¿ã‚¤ãƒžãƒ¼ã‚’ä¸­æ­¢
			clearTimeout(timer_show_hide);

			ev.stopPropagation();
		});
		$(combo_input).mouseup(function(ev) {
			$(combo_input).focus();
			reserve_click = false;
			ev.stopPropagation();
		});

		//**********************************************
		//ãƒšãƒ¼ã‚¸ãƒŠãƒ“
		//**********************************************
		$navi.mousedown(function(ev) {
			reserve_click = true;

			//æ¶ˆåŽ»äºˆç´„ã‚¿ã‚¤ãƒžãƒ¼ã‚’ä¸­æ­¢
			clearTimeout(timer_show_hide);

			ev.stopPropagation();
		});
		$navi.mouseup(function(ev) {
			$(combo_input).focus();
			reserve_click = false;
			ev.stopPropagation();
		});

		//**********************************************
		//ã‚µãƒ–æƒ…å ±
		//**********************************************
		$attached_dl_set.mousedown(function(ev) {
			reserve_click = true;

			//æ¶ˆåŽ»äºˆç´„ã‚¿ã‚¤ãƒžãƒ¼ã‚’ä¸­æ­¢
			clearTimeout(timer_show_hide);
			ev.stopPropagation();
		});
		$attached_dl_set.mouseup(function(ev) {
			$(combo_input).focus();
			reserve_click = false;
			ev.stopPropagation();
		});

		//**********************************************
		//bodyå…¨ä½“
		//**********************************************
		$('body').mouseup(function() {
			//æ¶ˆåŽ»äºˆç´„ã‚¿ã‚¤ãƒžãƒ¼ã‚’ä¸­æ­¢
			clearTimeout(timer_show_hide);

			//å€™è£œã‚’æ¶ˆåŽ»ã�™ã‚‹
			show_hide = false;
			hideResult();
		});

		//================================================================================
		//03.åˆ�æœŸå€¤
		//--------------------------------------------------------------------------------
		//**********************************************
		//ComboBoxã�«åˆ�æœŸå€¤ã‚’æŒ¿å…¥
		//**********************************************
		function setInitVal(){
			if(options.init_val === false) return;

			if(options.select_only){
				//------------------------------------------
				//ã‚»ãƒ¬ã‚¯ãƒˆå°‚ç”¨ã�¸ã�®å€¤æŒ¿å…¥
				//------------------------------------------
				//hiddenã�¸å€¤ã‚’æŒ¿å…¥
				var q_word = options.init_val;
				$hidden.val(q_word);

				//ãƒ†ã‚­ã‚¹ãƒˆãƒœãƒƒã‚¯ã‚¹ã�¸å€¤ã‚’æŒ¿å…¥
				var init_val_data = '';
				if(typeof options.source == 'object'){
					//sourceã�Œãƒ‡ãƒ¼ã‚¿ã‚»ãƒƒãƒˆã�®å ´å�ˆ
					initInsteadOfDB(q_word);
				}else{
					var $xhr2 = $.get(
						options.init_src,
						{
							'q_word'      : q_word,
							'field'       : options.field,
							'primary_key' : options.primary_key,
							'db_table'    : options.db_table
						},
						function(data){ afterInit(data) }
					);
				}
			} else {
				//------------------------------------------
				//é€šå¸¸ã�®ã€�ãƒ†ã‚­ã‚¹ãƒˆãƒœãƒƒã‚¯ã‚¹ã�¸ã�®å€¤æŒ¿å…¥
				//------------------------------------------
				prev_value = options.init_val;
				$(combo_input).val(options.init_val);
			}
		}
		//**********************************************
		//ãƒ‡ãƒ¼ã‚¿ãƒ™ãƒ¼ã‚¹ã�§ã�¯ã�ªã��ã€�JSONã�‹ã‚‰åˆ�æœŸå€¤ã‚’å¾—ã‚‹
		//**********************************************
		function initInsteadOfDB(q_word){
			for(var i=0; i<options.source.length; i++){
				if(options.source[i][options.primary_key] == q_word){
					var data = options.source[i][options.field];
					break;
				}
			}
			afterInit(data);
		}
		//**********************************************
		//åˆ�æœŸåŒ–ç”¨Ajaxå¾Œã�®å‡¦ç�†
		//**********************************************
		function afterInit(data){
			$(combo_input).val(data);
			prev_value = data;

			//é�¸æŠžçŠ¶æ…‹
			$(combo_input)
				.attr('title',msg['select_ok'])
				.removeClass(options.select_ng_class)
				.addClass(options.select_ok_class);
		}
		
		//================================================================================
		//04.ãƒœã‚¿ãƒ³
		//--------------------------------------------------------------------------------
		//**********************************************
		//ãƒœã‚¿ãƒ³ã�®titleå±žæ€§ åˆ�æœŸ
		//**********************************************
		function btnAttrDefault() {

			if(options.select_only){

				if($(combo_input).val() != ''){
					if($hidden.val() != ''){

						//é�¸æŠžçŠ¶æ…‹
						$(combo_input)
							.attr('title',msg['select_ok'])
							.removeClass(options.select_ng_class)
							.addClass(options.select_ok_class);
					} else {

						//å…¥åŠ›é€”ä¸­
						$(combo_input)
							.attr('title',msg['select_ng'])
							.removeClass(options.select_ok_class)
							.addClass(options.select_ng_class);
					}
				} else {
					//å®Œå…¨ã�ªåˆ�æœŸçŠ¶æ…‹ã�¸æˆ»ã�™
					$hidden.val('');
				}
			}
			//åˆ�æœŸçŠ¶æ…‹
			$button.attr('title', msg['get_all_btn']);
			$img.attr('src', options.button_img);
			btnPositionAdjust();
		}
		//**********************************************
		//ãƒœã‚¿ãƒ³ã�®titleå±žæ€§ ãƒªã‚¹ãƒˆå±•é–‹ä¸­
		//**********************************************
		function btnAttrClose() {
			$button.attr('title',msg['close_btn']);
			$img.attr('src', options.load_img);
			btnPositionAdjust();
		}
		//**********************************************
		//ãƒœã‚¿ãƒ³ã�®titleå±žæ€§ ãƒ­ãƒ¼ãƒ‰ä¸­
		//**********************************************
		function btnAttrLoad() {
			$button.attr('title',msg['loading']);
			$img.attr('src', options.load_img);
			btnPositionAdjust();
		}
		//**********************************************
		//ãƒœã‚¿ãƒ³ã�®ç”»åƒ�ã�®ä½�ç½®ã‚’èª¿æ•´ã�™ã‚‹
		//**********************************************
		function btnPositionAdjust(){
			var width_btn = $button.innerWidth();
/* &&& 2012å¹´3æœˆ9æ—¥ rz3005ã�•ã‚“ä¿®æ­£ã€‚å•�é¡Œã�Œã�ªã�‘ã‚Œã�°ã�„ã�šã‚Œå‰Šé™¤ã€‚
			var width_btn = $button.width() + 
			parseInt($button.css('padding-left'), 10) +
			parseInt($button.css('padding-right'), 10);
*/
			var height_btn = $button.innerHeight();
/* &&& 2012å¹´3æœˆ9æ—¥ rz3005ã�•ã‚“ä¿®æ­£ã€‚å•�é¡Œã�Œã�ªã�‘ã‚Œã�°ã�„ã�šã‚Œå‰Šé™¤ã€‚
			var height_btn = $button.height() + 
			parseInt($button.css('padding-top'), 10) +
			parseInt($button.css('padding-bottom'), 10);
*/
			var width_img = $img.width();
			var height_img = $img.height();
			
			var left = width_btn / 2 - (width_img / 2);
			var top = height_btn / 2 - (height_img / 2);
			
			$img.css({
				'top':top,
				'left':left
			});
		}
		//**********************************************
		//ãƒ­ãƒ¼ãƒ‰ç”»åƒ�ã�®è¡¨ç¤ºãƒ»è§£é™¤
		//**********************************************
		function setLoadImg() {
			now_loading = true;
			btnAttrLoad();
		}
		function clearLoadImg() {
			$img.attr('src' , options.button_img);
			now_loading = false;
			if(reserve_btn) $button.mouseover(); else $button.mouseout();
		}

		//================================================================================
		//05.æœªåˆ†é¡ž
		//--------------------------------------------------------------------------------
		//**********************************************
		//é�¸æŠžå€™è£œã‚’è¿½ã�„ã�‹ã�‘ã�¦ç”»é�¢ã‚’ã‚¹ã‚¯ãƒ­ãƒ¼ãƒ«
		//**********************************************
		//ã‚­ãƒ¼æ“�ä½œã�«ã‚ˆã‚‹å€™è£œç§»å‹•ã€�ãƒšãƒ¼ã‚¸ç§»å‹•ã�®ã�¿ã�«é�©ç”¨
		//
		// @param boolean enforce ç§»å‹•å…ˆã‚’ãƒ†ã‚­ã‚¹ãƒˆãƒœãƒƒã‚¯ã‚¹ã�«å¼·åˆ¶ã�™ã‚‹ã�‹ï¼Ÿ
		function scrollWindow(enforce) {

			//------------------------------------------
			//ä½¿ç”¨ã�™ã‚‹å¤‰æ•°ã‚’å®šç¾©
			//------------------------------------------
			var $current_result = getCurrentResult();

			var target_top = ($current_result && !enforce)
				? $current_result.offset().top
				: $container.offset().top;

			var target_size;
			if(options.sub_info){
				target_size =
					$attached_dl_set.height() +
					parseInt($attached_dl_set.css('border-top-width'), 10) +
					parseInt($attached_dl_set.css('border-bottom-width'), 10);

			} else {
				setSizeLi();
				target_size = size_li;
			}

			var client_height = document.documentElement.clientHeight;

			var scroll_top = (document.documentElement.scrollTop > 0)
				? document.documentElement.scrollTop
				: document.body.scrollTop;

			var scroll_bottom = scroll_top + client_height - target_size;

			//------------------------------------------
			//ã‚¹ã‚¯ãƒ­ãƒ¼ãƒ«å‡¦ç�†
			//------------------------------------------
			var gap;
			if ($current_result.length) {
				if(target_top < scroll_top || target_size > client_height) {
					//ä¸Šã�¸ã‚¹ã‚¯ãƒ­ãƒ¼ãƒ«
					//â€»ãƒ–ãƒ©ã‚¦ã‚¶ã�®é«˜ã�•ã�Œã‚¿ãƒ¼ã‚²ãƒƒãƒˆã‚ˆã‚Šã‚‚ä½Žã�„å ´å�ˆã‚‚ã�“ã�¡ã‚‰ã�¸åˆ†å²�ã�™ã‚‹ã€‚
					gap = target_top - scroll_top;

				} else if (target_top > scroll_bottom) {
					//ä¸‹ã�¸ã‚¹ã‚¯ãƒ­ãƒ¼ãƒ«
					gap = target_top - scroll_bottom;

				} else {
					//ã‚¹ã‚¯ãƒ­ãƒ¼ãƒ«ã�¯è¡Œã‚�ã‚Œã�ªã�„
					return;
				}

			} else if (target_top < scroll_top) {
				gap = target_top - scroll_top;
			}
			window.scrollBy(0, gap);
		}

		//**********************************************
		//ã‚¿ã‚¤ãƒžãƒ¼ã�«ã‚ˆã‚‹å…¥åŠ›å€¤å¤‰åŒ–ç›£è¦–
		//**********************************************
		function checkValChange() {
			timer_val_change = setTimeout(isChange,500);

			function isChange() {
				now_value = $(combo_input).val();

				if(now_value != prev_value) {
					//sub_infoå±žæ€§ã‚’å‰Šé™¤
					$(combo_input).removeAttr('sub_info');

					//ã‚»ãƒ¬ã‚¯ãƒˆå°‚ç”¨æ™‚
					if(options.select_only){
						$hidden.val('');
						btnAttrDefault();
					}
					//ãƒšãƒ¼ã‚¸æ•°ã‚’ãƒªã‚»ãƒƒãƒˆ
					page_num_suggest = 1;
					
					type_suggest = true;
					suggest(true);
				}
				prev_value = now_value;

				//ä¸€å®šæ™‚é–“ã�”ã�¨ã�®ç›£è¦–ã‚’å†�é–‹
				checkValChange();
			}
		}

		//**********************************************
		//ã‚­ãƒ¼å…¥åŠ›ã�¸ã�®å¯¾å¿œ
		//**********************************************
		function processKey(e) {
			if (
				(/27$|38$|40$|^9$/.test(e.keyCode) && $result_area.is(':visible')) ||
				(/^37$|39$|13$|^9$/.test(e.keyCode) && getCurrentResult()) ||
				/40$/.test(e.keyCode)
			) {
				if (e.preventDefault)  e.preventDefault();
				if (e.stopPropagation) e.stopPropagation();

				e.cancelBubble = true;
				e.returnValue  = false;

				switch(e.keyCode) {
					case 37: // left
						if (e.shiftKey) firstPage();
						else            prevPage();
						break;

					case 38: // up
						key_select = true;
						prevResult();
						break;

					case 39: // right
						if (e.shiftKey) lastPage();
						else            nextPage();
						break;

					case 40: // down
						if (!$result_area.is(':visible') && !getCurrentResult()){
							type_suggest = false;
							suggest();
						} else {
							key_select = true;
							nextResult();
						}
						break;

					case 9:  // tab
						key_paging = true;
						hideResult();
						break;

					case 13: // return
						selectCurrentResult(true);
						break;

					case 27: //	escape
						key_paging = true;
						hideResult();
						break;
				}

			} else {
				checkValChange();
			}
		}

		//================================================================================
		//06.Ajax
		//--------------------------------------------------------------------------------
		//**********************************************
		//Ajaxã�®ä¸­æ–­
		//**********************************************
		function abortAjax() {
			if ($xhr){
				$xhr.abort();
				$xhr = false;
				clearLoadImg();
			}
		}

		//**********************************************
		//ãƒ‡ãƒ¼ã‚¿ãƒ™ãƒ¼ã‚¹ã�¸ã�®å•�ã�„å�ˆã‚�ã�›
		//**********************************************
		function suggest(){
			//å€™è£œãƒªã‚¹ãƒˆå�–å¾—å¾Œã€�ç¬¬ï¼‘å€™è£œã‚’é�¸æŠžçŠ¶æ…‹ã�«ã�™ã‚‹ã�‹? ãƒ†ã‚­ã‚¹ãƒˆå…¥åŠ›ä»¥å¤–ã�ªã‚‰ã€�ã��ã‚Œã‚’è¡Œã�†ã€‚
			var select_first   = (arguments[0] == undefined) ? false : true;
			
			var q_word         = (type_suggest) ? $.trim($(combo_input).val()) : '';
			var which_page_num = (type_suggest) ? page_num_suggest : page_num_all;

			if (type_suggest && q_word.length < options.minchars){ 
				hideResult();
				
			} else {
				//Ajaxé€šä¿¡ã‚’ã‚­ãƒ£ãƒ³ã‚»ãƒ«
				abortAjax();

				//ã‚µãƒ–æƒ…å ±æ¶ˆåŽ»
			$attached_dl_set.children('dl').hide();

				setLoadImg();

				if(typeof options.source == 'object'){
					//sourceã�Œãƒ‡ãƒ¼ã‚¿ã‚»ãƒƒãƒˆã�®å ´å�ˆ
					searchInsteadOfDB(q_word, which_page_num, select_first);
				}else{
					//ã�“ã�“ã�§Ajaxé€šä¿¡ã‚’è¡Œã�£ã�¦ã�„ã‚‹
					$xhr = $.getJSON(
						options.source,
						{
							'q_word'       : q_word,
							'page_num'     : which_page_num,
							'per_page'     : options.per_page,
							'field'        : options.field,
							'search_field' : options.search_field,
							'and_or'       : options.and_or,
							'show_field'   : options.show_field,
							'hide_field'   : options.hide_field,
							'select_field' : select_field,
							'order_field'  : options.order_field,
							'order_by'     : options.order_by,
							'primary_key'  : primary_key,
							'db_table'     : options.db_table
						},
						function(json_data){ afterAjax(json_data, q_word, which_page_num, select_first) }
					);
				}
			}
		}
		//**********************************************
		//ãƒ‡ãƒ¼ã‚¿ãƒ™ãƒ¼ã‚¹ã�§ã�¯ã�ªã��ã€�JSONã‚’æ¤œç´¢
		//**********************************************
		function searchInsteadOfDB(q_word, which_page_num, select_first){
			//æ­£è¦�è¡¨ç�¾ã�®ãƒ¡ã‚¿æ–‡å­—ã‚’ã‚¨ã‚¹ã‚±ãƒ¼ãƒ—
			var escaped_q = q_word.replace(/\W/g,'\\$&');
			escaped_q = escaped_q.toString();
		
			//SELECT * FROM source WHERE field LIKE q_word;
			var matched = [];
			var reg = new RegExp(escaped_q, 'gi');

/* &&& 2012å¹´3æœˆ9æ—¥ rz3005ã�•ã‚“ä¿®æ­£ã€‚å•�é¡Œã�Œã�ªã�‘ã‚Œã�°ã�„ã�šã‚Œå‰Šé™¤ã€‚
			for(var i = 0; i < options.source.length; i++){
				if(options.source[i][options.field].match(reg)){
					matched[matched.length] = options.source[i];
				}
			}
*/
			for (var k in options.source) {
				if (options.source[k][options.field].match(reg)) matched.push(options.source[k]);
			}
			var json_data = {};
			json_data['cnt'] = matched.length;
			if(!json_data['cnt']){
				json_data['candidate'] = false;

			}else{

				//ORDER BY (CASE WHEN ...), order_field ASC (or DESC)
				var matched1 = [];
				var matched2 = [];
				var matched3 = [];
				var reg1 = new RegExp('^' + escaped_q + '$', 'gi');
				var reg2 = new RegExp('^' + escaped_q, 'gi');

/* &&& 2012å¹´3æœˆ9æ—¥ rz3005ã�•ã‚“ä¿®æ­£ã€‚å•�é¡Œã�Œã�ªã�‘ã‚Œã�°ã�„ã�šã‚Œå‰Šé™¤ã€‚
				for(var i = 0; i < matched.length; i++){
					if(matched[i][options.order_field].match(reg1)){
						matched1.push(matched[i]);
					}else if(matched[i][options.order_field].match(reg2)){
						matched2.push(matched[i]);
					}else{
						matched3.push(matched[i]);
					}
				}
*/
				for (var k in matched) {
					if(matched[k][options.order_field].match(reg1)){
						matched1.push(matched[k]);
					}else if(matched[k][options.order_field].match(reg2)){
						matched2.push(matched[k]);
					}else{
						matched3.push(matched[k]);
					}
				}			
				if(options.order_by == 'ASC'){
					matched1.sort(compareASC);
					matched2.sort(compareASC);
					matched3.sort(compareASC);
				}else{
					matched1.sort(compareDESC);
					matched2.sort(compareDESC);
					matched3.sort(compareDESC);
				}
				var sorted = matched1.concat(matched2);
				sorted = sorted.concat(matched3);
				
				//LIMIT xx OFFSET xx
				var start = (which_page_num - 1) * options.per_page;
				var end   = start + options.per_page;
				
				//----------------------------------------------
				//æœ€çµ‚çš„ã�«è¿”ã‚‹ã‚ªãƒ–ã‚¸ã‚§ã‚¯ãƒˆã‚’ä½œæˆ�
				//----------------------------------------------
				var show_field = options.show_field.split(',');
				var hide_field = options.hide_field.split(',');
				for(var i = start, sub = 0; i < end; i++, sub++){
					if(sorted[i] == undefined) break;
				
					for(var key in sorted[i]){
						//ã‚»ãƒ¬ã‚¯ãƒˆå°‚ç”¨
						if(key == primary_key){
							if(json_data['primary_key'] == undefined){
								json_data['primary_key'] = [];
							}
							json_data['primary_key'].push(sorted[i][key]);
						}
					
						if(key == options.field){
							//å¤‰æ�›å€™è£œã‚’å�–å¾—
							if(json_data['candidate'] == undefined){
								json_data['candidate'] = [];
							}
							json_data['candidate'].push(sorted[i][key]);
						} else {
							//ã‚µãƒ–æƒ…å ±
							if($.inArray(key, hide_field) == -1){
								if(
									show_field !== false
									&& !$.inArray('*', show_field) > -1
									&& !$.inArray(key, show_field)
								){
									continue;
								}
								if(json_data['attached'] == undefined){
									json_data['attached'] = [];
								}
								if(json_data['attached'][sub] == undefined){
									json_data['attached'][sub] = [];
								}
								json_data['attached'][sub].push([key, sorted[i][key]]);
							}
						}
					}
				}
				json_data['cnt_page'] = json_data['candidate'].length;
			}
			afterAjax(json_data, q_word, which_page_num, select_first);
		}
		//**********************************************
		//searchInsteadOfDBå†…ã�®sortç”¨ã�®æ¯”è¼ƒé–¢æ•°
		//**********************************************
		function compareASC(a, b){
			return a[options.order_field].localeCompare(b[options.order_field]);
		}
		function compareDESC(a, b){
			return b[options.order_field].localeCompare(a[options.order_field]);
		}
		//**********************************************
		//å•�ã�„å�ˆã‚�ã�›å¾Œã�®å‡¦ç�†
		//**********************************************
		function afterAjax(json_data, q_word, which_page_num, select_first){
		
			if(!json_data.candidate){
				//ä¸€è‡´ã�™ã‚‹ãƒ‡ãƒ¼ã‚¿è¦‹ã�¤ã�‹ã‚‰ã�ªã�‹ã�£ã�Ÿ
				hideResult();
			} else {
				//å…¨ä»¶æ•°ã�Œ1ãƒšãƒ¼ã‚¸æœ€å¤§æ•°ã‚’è¶…ã�ˆã�ªã�„å ´å�ˆã€�ãƒšãƒ¼ã‚¸ãƒŠãƒ“ã�¯é�žè¡¨ç¤º
				if(json_data.cnt > json_data.cnt_page){
					setNavi(json_data.cnt, json_data.cnt_page, which_page_num);
				} else {
					$navi.css('display','none');
				}

				//å€™è£œãƒªã‚¹ãƒˆ(arr_candidate)
				var arr_candidate = json_data.candidate;
				/*
				ãƒ’ãƒƒãƒˆæ–‡å­—ã�¸ã�®ä¸‹ç·šã�®ä»˜åŠ ã‚’ã€�ä¸­æ­¢ã�—ã�¾ã�—ã�Ÿã€‚ 2012/01/11
				
				var arr_candidate = [];
				//æ­£è¦�è¡¨ç�¾ã�®ãƒ¡ã‚¿æ–‡å­—ã‚’ã‚¨ã‚¹ã‚±ãƒ¼ãƒ—
				var escaped_q = q_word.replace(/\W/g,'\\$&');
				$.each(json_data.candidate, function(i,obj){
					arr_candidate[i] = obj.replace(
						new RegExp(escaped_q, 'ig'),
						function(hit) {
							return '<span class="' + options.match_class + '">' + hit + '</span>';
						}
					);
				});
				*/
				
				//ã‚µãƒ–æƒ…å ±(arr_attached)
				var arr_attached = [];
				if(json_data.attached  && options.sub_info){
					$.each(json_data.attached,function(i,obj){
						arr_attached[i] = obj;
					});
				} else {
					arr_attached = false;
				}

				//ã‚»ãƒ¬ã‚¯ãƒˆå°‚ç”¨(arr_primary_key)
				var arr_primary_key = [];
				if(json_data.primary_key){
					$.each(json_data.primary_key,function(i,obj){
						arr_primary_key[i] = obj;
					});
				} else {
					arr_primary_key = false;
				}
				displayItems(arr_candidate, arr_attached, arr_primary_key);
			}
			clearLoadImg();
			if(!select_first) selectFirstResult(); //ãƒ†ã‚­ã‚¹ãƒˆå…¥åŠ›ä»¥å¤–ã�ªã‚‰ã€�ç¬¬ï¼‘å€™è£œã‚’é�¸æŠžçŠ¶æ…‹ã�«ã�™ã‚‹
		}
		//================================================================================
		//07.ãƒšãƒ¼ã‚¸ãƒŠãƒ“
		//--------------------------------------------------------------------------------
		//**********************************************
		//ãƒŠãƒ“éƒ¨åˆ†ã‚’ä½œæˆ�
		//**********************************************
		// @param integer cnt         DBã�‹ã‚‰å�–å¾—ã�—ã�Ÿå€™è£œã�®æ•°
		// @param integer page_num    å…¨ä»¶ã€�ã�¾ã�Ÿã�¯äºˆæ¸¬å€™è£œã�®ä¸€è¦§ã�®ãƒšãƒ¼ã‚¸æ•°
		function setNavi(cnt, cnt_page, page_num) {

			var num_page_top = options.per_page * (page_num - 1) + 1;
			var num_page_end = num_page_top + cnt_page - 1;

			var cnt_result = msg['page_info']
				.replace('cnt'          , cnt)
				.replace('num_page_top' , num_page_top)
				.replace('num_page_end' , num_page_end);

			$navi.text(cnt_result);

			var navi_p = $('<p></p>'); //ãƒšãƒ¼ã‚¸ãƒ³ã‚°éƒ¨åˆ†ã�®ã‚ªãƒ–ã‚¸ã‚§ã‚¯ãƒˆ
			var max    = Math.ceil(cnt / options.per_page); //å…¨ãƒšãƒ¼ã‚¸æ•°

			//ãƒšãƒ¼ã‚¸æ•°
			if (type_suggest) {
				max_suggest = max;
			}else{
				max_all = max;
			}

			//è¡¨ç¤ºã�™ã‚‹ä¸€é€£ã�®ãƒšãƒ¼ã‚¸ç•ªå�·ã�®å·¦å�³ç«¯
			var left  = page_num - Math.ceil ((options.navi_num - 1) / 2);
			var right = page_num + Math.floor((options.navi_num - 1) / 2);

			//ç�¾ãƒšãƒ¼ã‚¸ã�Œç«¯è¿‘ã��ã�®å ´å�ˆã�®left,rightã�®èª¿æ•´
			while(left < 1){ left ++;right++; }
			while(right > max){ right--; }
			while((right-left < options.navi_num - 1) && left > 1){ left--; }

			//----------------------------------------------
			//ãƒšãƒ¼ã‚¸ãƒ³ã‚°éƒ¨åˆ†ã‚’ä½œæˆ�

			//ã€Ž<< å‰�ã�¸ã€�ã�®è¡¨ç¤º
			if(page_num == 1) {
				if(!options.navi_simple){
					$('<span></span>')
						.text('<< 1')
						.addClass('page_end')
						.appendTo(navi_p);
				}
				$('<span></span>')
					.text(msg['prev'])
					.addClass('page_end')
					.appendTo(navi_p);
			} else {
				if(!options.navi_simple){
					$('<a></a>')
						.attr({'href':'javascript:void(0)','class':'navi_first'})
						.text('<< 1')
						.attr('title', msg['first_title'])
						.appendTo(navi_p);
				}
				$('<a></a>')
					.attr({'href':'javascript:void(0)','class':'navi_prev'})
					.text(msg['prev'])
					.attr('title', msg['prev_title'])
					.appendTo(navi_p);
			}

			//å�„ãƒšãƒ¼ã‚¸ã�¸ã�®ãƒªãƒ³ã‚¯ã�®è¡¨ç¤º
			for (i = left; i <= right; i++)
			{
				//ç�¾åœ¨ã�®ãƒšãƒ¼ã‚¸ç•ªå�·ã�¯<span>ã�§å›²ã‚€(å¼·èª¿è¡¨ç¤ºç”¨)
				var num_link = (i == page_num) ? '<span class="current">'+i+'</span>' : i;

				$('<a></a>')
					.attr({'href':'javascript:void(0)','class':'navi_page'})
					.html(num_link)
					.appendTo(navi_p);
			}

			//ã€Žæ¬¡ã�®Xä»¶ >>ã€�ã�®è¡¨ç¤º
			if(page_num == max) {
				$('<span></span>')
					.text(msg['next'])
					.addClass('page_end')
					.appendTo(navi_p);
				if(!options.navi_simple){
					$('<span></span>')
						.text(max + ' >>')
						.addClass('page_end')
						.appendTo(navi_p);
				}
			} else {
				$('<a></a>')
					.attr({'href':'javascript:void(0)','class':'navi_next'})
					.text(msg['next'])
					.attr('title', msg['next_title'])
					.appendTo(navi_p);
				if(!options.navi_simple){
					$('<a></a>')
						.attr({'href':'javascript:void(0)','class':'navi_last'})
						.text(max + ' >>')
						.attr('title', msg['last_title'])
						.appendTo(navi_p);
				}
			}

			//ãƒšãƒ¼ã‚¸ãƒŠãƒ“ã�®è¡¨ç¤ºã€�ã‚¤ãƒ™ãƒ³ãƒˆãƒ�ãƒ³ãƒ‰ãƒ©ã�®è¨­å®šã�¯å¿…è¦�ã�ªå ´å�ˆã�®ã�¿è¡Œã�†
			if (max > 1) {
				$navi.append(navi_p).show();

				//----------------------------------------------
				//ãƒšãƒ¼ã‚¸ãƒ³ã‚°éƒ¨åˆ†ã�®ã‚¤ãƒ™ãƒ³ãƒˆãƒ�ãƒ³ãƒ‰ãƒ©

				//ã€Ž<< 1ã€�ã‚’ã‚¯ãƒªãƒƒã‚¯
				$('.navi_first').mouseup(function(ev) {
					$(combo_input).focus();
					ev.preventDefault();
					firstPage();
				});

				//ã€Ž< å‰�ã�¸ã€�ã‚’ã‚¯ãƒªãƒƒã‚¯
				$('.navi_prev').mouseup(function(ev) {
					$(combo_input).focus();
					ev.preventDefault();
					prevPage();
				});

				//å�„ãƒšãƒ¼ã‚¸ã�¸ã�®ãƒªãƒ³ã‚¯ã‚’ã‚¯ãƒªãƒƒã‚¯
				$('.navi_page').mouseup(function(ev) {
					$(combo_input).focus();
					ev.preventDefault();

					if(!type_suggest){
						page_num_all = parseInt($(this).text(), 10);
					}else{
						page_num_suggest = parseInt($(this).text(), 10);
					}
					suggest();
				});

				//ã€Žæ¬¡ã�¸ >ã€�ã‚’ã‚¯ãƒªãƒƒã‚¯
				$('.navi_next').mouseup(function(ev) {
					$(combo_input).focus();
					ev.preventDefault();
					nextPage();
				});

				//ã€Žmax >>ã€�ã‚’ã‚¯ãƒªãƒƒã‚¯
				$('.navi_last').mouseup(function(ev) {
					$(combo_input).focus();
					ev.preventDefault();
					lastPage();
				});
			}
		}

		//**********************************************
		//1ãƒšãƒ¼ã‚¸ç›®ã�¸
		//**********************************************
		function firstPage() {
			if(!type_suggest) {
				if (page_num_all > 1) {
					page_num_all = 1;
					suggest();
				}
			}else{
				if (page_num_suggest > 1) {
					page_num_suggest = 1;
					suggest();
				}
			}
		}
		//**********************************************
		//å‰�ã�®ãƒšãƒ¼ã‚¸ã�¸
		//**********************************************
		function prevPage() {
			if(!type_suggest){
				if (page_num_all > 1) {
					page_num_all--;
					suggest();
				}
			}else{
				if (page_num_suggest > 1) {
					page_num_suggest--;
					suggest();
				}
			}
		}
		//**********************************************
		//æ¬¡ã�®ãƒšãƒ¼ã‚¸ã�¸
		//**********************************************
		function nextPage() {
			if(!type_suggest){
				if (page_num_all < max_all) {
					page_num_all++;
					suggest();
				}
			} else {
				if (page_num_suggest < max_suggest) {
					page_num_suggest++;
					suggest();
				}
			}
		}
		//**********************************************
		//æœ€å¾Œã�®ãƒšãƒ¼ã‚¸ã�¸
		//**********************************************
		function lastPage() {
			if(!type_suggest){
				if (page_num_all < max_all) {
					page_num_all = max_all;
					suggest();
				}
			}else{
				if (page_num_suggest < max_suggest) {
					page_num_suggest = max_suggest;
					suggest();
				}
			}
		}

		//================================================================================
		//08.å€™è£œãƒªã‚¹ãƒˆ
		//--------------------------------------------------------------------------------
		//**********************************************
		//å€™è£œä¸€è¦§ã�®<ul>æˆ�å½¢ã€�è¡¨ç¤º
		//**********************************************
		// @params array arr_candidate   DBã�‹ã‚‰æ¤œç´¢ãƒ»å�–å¾—ã�—ã�Ÿå€¤ã�®é…�åˆ—
		// @params array arr_attached    ã‚µãƒ–æƒ…å ±ã�®é…�åˆ—
		// @params array arr_primary_key ä¸»ã‚­ãƒ¼ã�®é…�åˆ—
		//
		//arr_candidateã��ã‚Œã�žã‚Œã�®å€¤ã‚’<li>ã�§å›²ã‚“ã�§è¡¨ç¤ºã€‚
		//å�Œæ™‚ã�«ã€�ã‚¤ãƒ™ãƒ³ãƒˆãƒ�ãƒ³ãƒ‰ãƒ©ã‚’è¨˜è¿°ã€‚
		function displayItems(arr_candidate, arr_attached, arr_primary_key) {

			if (arr_candidate.length == 0) {
				hideResult();
				return;
			}

			//å€™è£œãƒªã‚¹ãƒˆã‚’ã€�ä¸€æ—¦ãƒªã‚»ãƒƒãƒˆ
			$results.empty();
			$attached_dl_set.empty();
			for (var i = 0; i < arr_candidate.length; i++) {

				//å€™è£œãƒªã‚¹ãƒˆ
				var $li = $('<li>').text(arr_candidate[i]); //!!! against XSS !!!
				
				//ã‚»ãƒ¬ã‚¯ãƒˆå°‚ç”¨
				if(options.select_only){
					$li.attr('id', arr_primary_key[i]);
				}

				$results.append($li);

				//ã‚µãƒ–æƒ…å ±ã�®dlã‚’ç”Ÿæˆ�
				if(arr_attached){
					//sub_infoå±žæ€§ã�«JSONæ–‡å­—åˆ—ã��ã�®ã�¾ã�¾ã‚’æ ¼ç´�
					var json_subinfo = '{';
					var $dl = $('<dl>');
					//ãƒ†ãƒ¼ãƒ–ãƒ«ã�®å�„è¡Œã‚’ç”Ÿæˆ�
					for (var j=0; j < arr_attached[i].length; j++) {
						//sub_infoå±žæ€§ã�®å€¤ã‚’æ•´ã�ˆã‚‹
						var json_key = arr_attached[i][j][0].replace('\'', '\\\'');
						var json_val = arr_attached[i][j][1].replace('\'', '\\\'');
						json_subinfo += "'" + json_key + "':" + "'" + json_val + "'";
						if((j+1) < arr_attached[i].length) json_subinfo += ',';

						//thã�®åˆ¥å��ã‚’æ¤œç´¢ã�™ã‚‹
						if(options.sub_as[arr_attached[i][j][0]] != null){
							var dt = options.sub_as[arr_attached[i][j][0]];
						} else {
							var dt =  arr_attached[i][j][0];
						}
						dt = $('<dt>').text(dt); //!!! against XSS !!!
						$dl.append(dt);
						
						var dd = $('<dd>').text(arr_attached[i][j][1]);	//!!! against XSS !!!
						$dl.append(dd);
					}
					//sub_infoå±žæ€§ã‚’å€™è£œãƒªã‚¹ãƒˆã�®liã�«è¿½åŠ 
					json_subinfo += '}';
					$li.attr('sub_info', json_subinfo);
					$attached_dl_set.append($dl);
					$attached_dl_set.children('dl').hide();
				}
			}
			//ç”»é�¢ã�«è¡¨ç¤º
			if(arr_attached) $attached_dl_set.insertAfter($results);

			//ã‚µã‚¸ã‚§ã‚¹ãƒˆçµ�æžœè¡¨ç¤º
			var offset = $container.offset();
			$result_area
				.show()
				.width(
					$container.width() -
					($container.outerWidth() - $container.innerWidth())
/* &&& 2012å¹´3æœˆ9æ—¥ rz3005ã�•ã‚“ä¿®æ­£ã€‚å•�é¡Œã�Œã�ªã�‘ã‚Œã�°ã�„ã�šã‚Œå‰Šé™¤ã€‚
					parseInt($result_area.css('border-left-width'), 10) -
					parseInt($result_area.css('border-right-width'), 10)
*/
				)/*
				.css({
					'top':$container.outerHeight() + offset.top
				})*/;
			$container.addClass(options.container_open_class);

			$results
				.children('li')
				.mouseover(function() {

					//Firefoxã�§ã�¯ã€�å€™è£œä¸€è¦§ã�®ä¸Šã�«ãƒžã‚¦ã‚¹ã‚«ãƒ¼ã‚½ãƒ«ã�Œä¹—ã�£ã�¦ã�„ã‚‹ã�¨
					//ã�†ã�¾ã��ã‚¹ã‚¯ãƒ­ãƒ¼ãƒ«ã�—ã�ªã�„ã€‚ã��ã�®ã�Ÿã‚�ã�®å¯¾ç­–ã€‚ã‚¤ãƒ™ãƒ³ãƒˆä¸­æ–­ã€‚
					if (key_select) {
						key_select = false;
						return;
					}

					//ã‚µãƒ–æƒ…å ±ã‚’è¡¨ç¤º
					setSubInfo(this);

					$results.children('li').removeClass(options.select_class);
					$(this).addClass(options.select_class);
				})
				.mousedown(function(e) {
					reserve_click = true;

					//æ¶ˆåŽ»äºˆç´„ã‚¿ã‚¤ãƒžãƒ¼ã‚’ä¸­æ­¢
					clearTimeout(timer_show_hide);
					//ev.stopPropagation();
				})
				.mouseup(function(e) {
					reserve_click = false;

					//Firefoxã�§ã�¯ã€�å€™è£œä¸€è¦§ã�®ä¸Šã�«ãƒžã‚¦ã‚¹ã‚«ãƒ¼ã‚½ãƒ«ã�Œä¹—ã�£ã�¦ã�„ã‚‹ã�¨
					//ã�†ã�¾ã��ã‚¹ã‚¯ãƒ­ãƒ¼ãƒ«ã�—ã�ªã�„ã€‚ã��ã�®ã�Ÿã‚�ã�®å¯¾ç­–ã€‚ã‚¤ãƒ™ãƒ³ãƒˆä¸­æ–­ã€‚
					if (key_select) {
						key_select = false;
						return;
					}
					e.preventDefault();
					e.stopPropagation();
					selectCurrentResult(false);
				});

			//ãƒœã‚¿ãƒ³ã�®titleå±žæ€§å¤‰æ›´(é–‰ã�˜ã‚‹)
			btnAttrClose();
		}

		//**********************************************
		//ç�¾åœ¨é�¸æŠžä¸­ã�®å€™è£œã�®æƒ…å ±ã‚’å�–å¾—
		//**********************************************
		// @return object current_result ç�¾åœ¨é�¸æŠžä¸­ã�®å€™è£œã�®ã‚ªãƒ–ã‚¸ã‚§ã‚¯ãƒˆ(<li>è¦�ç´ )
		function getCurrentResult() {

			if (!$result_area.is(':visible')) return false;

			var $current_result = $results.children('li.' + options.select_class);

			if (!$current_result.length) $current_result = false;

			return $current_result;
		}
		//**********************************************
		//ç�¾åœ¨é�¸æŠžä¸­ã�®å€™è£œã�«æ±ºå®šã�™ã‚‹
		//**********************************************
		function selectCurrentResult(is_enter_key) {

			//é�¸æŠžå€™è£œã‚’è¿½ã�„ã�‹ã�‘ã�¦ã‚¹ã‚¯ãƒ­ãƒ¼ãƒ«
			scrollWindow(true);

			var $current_result = getCurrentResult();

			if ($current_result) {
				$(combo_input).val($current_result.text());
				//ã‚µãƒ–æƒ…å ±ã�Œã�‚ã‚‹ã�ªã‚‰sub_infoå±žæ€§ã‚’è¿½åŠ ãƒ»æ›¸ã��æ�›ã�ˆ
				if(options.sub_info) $(combo_input).attr('sub_info', $current_result.attr('sub_info'));
				hideResult();

				//added
				prev_value = $(combo_input).val();

				//ã‚»ãƒ¬ã‚¯ãƒˆå°‚ç”¨
				if(options.select_only){
					$hidden.val($current_result.attr('id'));
					btnAttrDefault();
				}
			}
			if(options.bind_to){
			 	//å€™è£œé�¸æŠžã‚’å¼•ã��é‡‘ã�«ã€�ã‚¤ãƒ™ãƒ³ãƒˆã‚’ç™ºç�«ã�™ã‚‹
				$(combo_input).trigger(options.bind_to, is_enter_key);
			}
			$(combo_input).focus();  //ãƒ†ã‚­ã‚¹ãƒˆãƒœãƒƒã‚¯ã‚¹ã�«ãƒ•ã‚©ãƒ¼ã‚«ã‚¹ã‚’ç§»ã�™
			$(combo_input).change(); //ãƒ†ã‚­ã‚¹ãƒˆãƒœãƒƒã‚¯ã‚¹ã�®å€¤ã�Œå¤‰ã‚�ã�£ã�Ÿã�“ã�¨ã‚’é€šçŸ¥
		}
		//**********************************************
		//é�¸æŠžå€™è£œã‚’æ¬¡ã�«ç§»ã�™
		//**********************************************
		function nextResult() {
			var $current_result = getCurrentResult();

			if ($current_result) {

				//ã‚µãƒ–æƒ…å ±ã‚’è¡¨ç¤º
				setSubInfo($current_result.next());

				$current_result
					.removeClass(options.select_class)
					.next()
						.addClass(options.select_class);
			}else{
				//ã‚µãƒ–æƒ…å ±ã‚’è¡¨ç¤º
				setSubInfo($results.children('li:first-child'), 0);

				$results.children('li:first-child').addClass(options.select_class);
			}
			//é�¸æŠžå€™è£œã‚’è¿½ã�„ã�‹ã�‘ã�¦ã‚¹ã‚¯ãƒ­ãƒ¼ãƒ«
			scrollWindow();
		}
		//**********************************************
		//é�¸æŠžå€™è£œã‚’å‰�ã�«ç§»ã�™
		//**********************************************
		function prevResult() {
			var $current_result = getCurrentResult();

			if ($current_result) {

				//ã‚µãƒ–æƒ…å ±ã‚’è¡¨ç¤º
				setSubInfo($current_result.prev());

				$current_result
					.removeClass(options.select_class)
					.prev()
						.addClass(options.select_class);
			}else{
				//ã‚µãƒ–æƒ…å ±ã‚’è¡¨ç¤º
				setSubInfo(
					$results.children('li:last-child'),
					($results.children('li').length - 1)
				);

				$results.children('li:last-child').addClass(options.select_class);
			}
			//é�¸æŠžå€™è£œã‚’è¿½ã�„ã�‹ã�‘ã�¦ã‚¹ã‚¯ãƒ­ãƒ¼ãƒ«
			scrollWindow();
		}
		//**********************************************
		//å€™è£œã�®æ¶ˆåŽ»ã‚’æœ¬å½“ã�«å®Ÿè¡Œã�™ã‚‹ã�‹åˆ¤æ–­
		//**********************************************
		function checkShowHide() {
			timer_show_hide = setTimeout(function() {
				if (show_hide == false && reserve_click == false){
					hideResult();
				}
			},500);
		}
		//**********************************************
		//å€™è£œã‚¨ãƒªã‚¢ã‚’æ¶ˆåŽ»
		//**********************************************
		function hideResult() {

			if (key_paging) {
				//é�¸æŠžå€™è£œã‚’è¿½ã�„ã�‹ã�‘ã�¦ã‚¹ã‚¯ãƒ­ãƒ¼ãƒ«
				scrollWindow(true);
				key_paging = false;
			}

			$result_area.hide();
			$container.removeClass(options.container_open_class);

			//ã‚µãƒ–æƒ…å ±æ¶ˆåŽ»
			$attached_dl_set.children('dl').hide();

			//Ajaxé€šä¿¡ã‚’ã‚­ãƒ£ãƒ³ã‚»ãƒ«
			abortAjax();

			//ãƒœã‚¿ãƒ³ã�®titleå±žæ€§åˆ�æœŸåŒ–
			btnAttrDefault();
		}
		//**********************************************
		//å€™è£œä¸€è¦§ã�®1ç•ªç›®ã�®é …ç›®ã‚’ã€�é�¸æŠžçŠ¶æ…‹ã�«ã�™ã‚‹
		//**********************************************
		function selectFirstResult(){
			$results.children('li:first-child').addClass(options.select_class);

			//ã‚µãƒ–æƒ…å ±ã‚’è¡¨ç¤º
			setSubInfo($results.children('li:first-child'));
		}
		//================================================================================
		//09.ã‚µãƒ–æƒ…å ±
		//--------------------------------------------------------------------------------
		//**********************************************
		//ã‚µãƒ–æƒ…å ±ã�§é »ç¹�ã�«ä½¿ç”¨ã�™ã‚‹è¦�ç´ ã�®ã‚µã‚¤ã‚ºã‚’ç®—å‡º
		//**********************************************
		function setSizeResults(){
/* &&& 2012å¹´3æœˆ9æ—¥ rz3005ã�•ã‚“ä¿®æ­£ã€‚å•�é¡Œã�Œã�ªã�‘ã‚Œã�°ã�„ã�šã‚Œå‰Šé™¤ã€‚
			if(size_navi == null){
				size_navi =
					$navi.height() +
					parseInt($navi.css('border-top-width'), 10) +
					parseInt($navi.css('border-bottom-width'), 10) +
					parseInt($navi.css('padding-top'), 10) +
					parseInt($navi.css('padding-bottom'), 10);
			}
*/
			if (size_results == null) {
				size_results = ($results.outerHeight() - $results.height()) / 2;
			}
		}
		function setSizeNavi(){
/* &&& 2012å¹´3æœˆ9æ—¥ rz3005ã�•ã‚“ä¿®æ­£ã€‚å•�é¡Œã�Œã�ªã�‘ã‚Œã�°ã�„ã�šã‚Œå‰Šé™¤ã€‚
			if(size_results == null){
				size_results = parseInt($results.css('border-top-width'), 10);
			}
*/
			if (size_navi == null) size_navi = $navi.outerHeight();
		}
		function setSizeLi(){
/* &&& 2012å¹´3æœˆ9æ—¥ rz3005ã�•ã‚“ä¿®æ­£ã€‚å•�é¡Œã�Œã�ªã�‘ã‚Œã�°ã�„ã�šã‚Œå‰Šé™¤ã€‚
			if(size_li == null){
				$obj = $results.children('li:first');
				size_li =
					$obj.height() +
					parseInt($obj.css('border-top-width'), 10) +
					parseInt($obj.css('border-bottom-width'), 10) +
					parseInt($obj.css('padding-top'), 10) +
					parseInt($obj.css('padding-bottom'), 10);
			}
*/
			if (size_li == null) size_li = $results.children('li:first').outerHeight();
		}
		function setSizeLeft(){
/* &&& 2012å¹´3æœˆ9æ—¥ rz3005ã�•ã‚“ä¿®æ­£ã€‚å•�é¡Œã�Œã�ªã�‘ã‚Œã�°ã�„ã�šã‚Œå‰Šé™¤ã€‚
			if(size_left == null){
				size_left =
					$results.width() +
					parseInt($results.css('padding-left'), 10) +
					parseInt($results.css('padding-right'), 10) +
					parseInt($results.css('border-left-width'), 10) +
					parseInt($results.css('border-right-width'), 10);
			}
*/
			if (size_left == null) size_left = $results.outerWidth();
		}

		//**********************************************
		//ã‚µãƒ–æƒ…å ±ã‚’è¡¨ç¤ºã�™ã‚‹
		//**********************************************
		// @paramas object  obj   ã‚µãƒ–æƒ…å ±ã‚’å�³éš£ã�«è¡¨ç¤ºã�•ã�›ã‚‹<li>è¦�ç´ 
		// @paramas integer n_idx é�¸æŠžä¸­ã�®<li>ã�®ç•ªå�·(0ï½ž)
		function setSubInfo(obj, n_idx){

			//ã‚µãƒ–æƒ…å ±ã‚’è¡¨ç¤ºã�—ã�ªã�„è¨­å®šã�ªã‚‰ã€�ã�“ã�“ã�§çµ‚äº†
			if(!options.sub_info) return;

			//ã‚µãƒ–æƒ…å ±ã�®åº§æ¨™è¨­å®šç”¨ã�®åŸºæœ¬æƒ…å ±
			//åˆ�å›žã�®è¨­å®šã� ã�‘ã�§ã€�å¾Œã�¯å‘¼ã�³å‡ºã�•ã‚Œã�ªã�„ã€‚
			setSizeNavi();
			setSizeResults();
			setSizeLi();
			setSizeLeft();

			//ç�¾åœ¨ã�®<li>ã�®ç•ªå�·ã�¯ï¼Ÿ
			if(n_idx == null){
				n_idx = $results.children('li').index(obj);
			}

			//ä¸€æ—¦ã€�ã‚µãƒ–æƒ…å ±å…¨æ¶ˆåŽ»
			$attached_dl_set.children('dl').hide();

			//ãƒªã‚¹ãƒˆå†…ã�®å€™è£œã‚’é�¸æŠžã�™ã‚‹å ´å�ˆã�®ã�¿ã€�ä»¥ä¸‹ã‚’å®Ÿè¡Œ
			if(n_idx > -1){

				var t_top = 0;
				if($navi.css('display') != 'none') t_top += size_navi;
				t_top += (size_results + size_li * n_idx);
				var t_left = size_left;

				t_top  += 'px';
				t_left += 'px';

				$attached_dl_set.children('dl').eq(n_idx).css({
					'position': 'absolute',
					'top'     : t_top,
					'left'    : t_left,
					'display' : 'block'
				});
			}
		}
	};

	//================================================================================
	//10.å‡¦ç�†ã�®å§‹ã�¾ã‚Š
	//--------------------------------------------------------------------------------
	$.fn.ajaxComboBox = function(source, options) {
		if (!source) return;

		//************************************************************
		//ã‚ªãƒ—ã‚·ãƒ§ãƒ³
		//************************************************************
		//----------------------------------------
		//åˆ�å›ž
		//----------------------------------------
		options = $.extend({
			//åŸºæœ¬è¨­å®š
			source         : source,
			db_table       : 'tbl',                    //æŽ¥ç¶šã�™ã‚‹DBã�®ãƒ†ãƒ¼ãƒ–ãƒ«å��
			img_dir        : 'acbox/img/',             //ãƒœã‚¿ãƒ³ç”»åƒ�ã�¸ã�®ãƒ‘ã‚¹
			field          : 'name',                   //å€™è£œã�¨ã�—ã�¦è¡¨ç¤ºã�™ã‚‹ã‚«ãƒ©ãƒ å��
			and_or         : 'AND',                    //è¤‡æ•°ã�®æ¤œç´¢å¾Œã�«å¯¾å¿œã�™ã‚‹ã�Ÿã‚�
			minchars       : 1,                        //å€™è£œäºˆæ¸¬å‡¦ç�†ã‚’å§‹ã‚�ã‚‹ã�®ã�«å¿…è¦�ã�ªæœ€ä½Žã�®æ–‡å­—æ•°
			per_page       : 10,                       //å€™è£œä¸€è¦§1ãƒšãƒ¼ã‚¸ã�«è¡¨ç¤ºã�™ã‚‹ä»¶æ•°
			navi_num       : 5,                        //ãƒšãƒ¼ã‚¸ãƒŠãƒ“ã�§è¡¨ç¤ºã�™ã‚‹ãƒšãƒ¼ã‚¸ç•ªå�·ã�®æ•°
			navi_simple    : false,                    //å…ˆé ­ã€�æœ«å°¾ã�®ãƒšãƒ¼ã‚¸ã�¸ã�®ãƒªãƒ³ã‚¯ã‚’è¡¨ç¤ºã�™ã‚‹ã�‹ï¼Ÿ
			init_val       : false,                    //ComboBoxã�®åˆ�æœŸå€¤(é…�åˆ—å½¢å¼�ã�§æ¸¡ã�™)
			init_src       : 'acbox/php/initval.php',  //åˆ�æœŸå€¤è¨­å®šã�§ã€�ã‚»ãƒ¬ã‚¯ãƒˆå°‚ç”¨ã�®å ´å�ˆã�«å¿…è¦�
			lang           : 'ja',                     //è¨€èªžã‚’é�¸æŠž(ãƒ‡ãƒ•ã‚©ãƒ«ãƒˆã�¯æ—¥æœ¬èªž)
			bind_to        : false,                    //å€™è£œé�¸æŠžå¾Œã�«å®Ÿè¡Œã�•ã‚Œã‚‹ã‚¤ãƒ™ãƒ³ãƒˆã�®å��å‰�
			
			//ã‚µãƒ–æƒ…å ±
			sub_info       : false, //ã‚µãƒ–æƒ…å ±ã‚’è¡¨ç¤ºã�™ã‚‹ã�‹ã�©ã�†ã�‹ï¼Ÿ
			sub_as         : {},    //ã‚µãƒ–æƒ…å ±ã�§ã�®ã€�ã‚«ãƒ©ãƒ å��ã�®åˆ¥å��
			show_field     : '',    //ã‚µãƒ–æƒ…å ±ã�§è¡¨ç¤ºã�™ã‚‹ã‚«ãƒ©ãƒ (è¤‡æ•°æŒ‡å®šã�¯ã‚«ãƒ³ãƒžåŒºåˆ‡ã‚Š)
			hide_field     : '',    //ã‚µãƒ–æƒ…å ±ã�§é�žè¡¨ç¤ºã�«ã�™ã‚‹ã‚«ãƒ©ãƒ (è¤‡æ•°æŒ‡å®šã�¯ã‚«ãƒ³ãƒžåŒºåˆ‡ã‚Š)

			//ã‚»ãƒ¬ã‚¯ãƒˆå°‚ç”¨
			select_only    : false, //ã‚»ãƒ¬ã‚¯ãƒˆå°‚ç”¨ã�«ã�™ã‚‹ã�‹ã�©ã�†ã�‹ï¼Ÿ
			primary_key    : 'id',  //ã‚»ãƒ¬ã‚¯ãƒˆå°‚ç”¨æ™‚ã€�hiddenã�®å€¤ã�¨ã�ªã‚‹ã‚«ãƒ©ãƒ 
			
			//ComboBoxé–¢é€£
			container_class: 'ac_container', //ComboBoxã�®<table>
			input_class    : 'ac_input', //ãƒ†ã‚­ã‚¹ãƒˆãƒœãƒƒã‚¯ã‚¹
			button_class   : 'ac_button', //ãƒœã‚¿ãƒ³ã�®CSSã‚¯ãƒ©ã‚¹
			btn_on_class   : 'ac_btn_on', //ãƒœã‚¿ãƒ³(moveræ™‚)
			btn_out_class  : 'ac_btn_out', //ãƒœã‚¿ãƒ³(moutæ™‚)
			re_area_class  : 'ac_result_area', //çµ�æžœãƒªã‚¹ãƒˆã�®<div>
			navi_class     : 'ac_navi', //ãƒšãƒ¼ã‚¸ãƒŠãƒ“ã‚’å›²ã‚€<div>
			results_class  : 'ac_results', //å€™è£œä¸€è¦§ã‚’å›²ã‚€<ul>
			select_class   : 'ac_over', //é�¸æŠžä¸­ã�®<li>
			match_class    : 'ac_match', //ãƒ’ãƒƒãƒˆæ–‡å­—ã�®<span>
			sub_info_class : 'ac_attached', //ã‚µãƒ–æƒ…å ±
			select_ok_class: 'ac_select_ok',
			select_ng_class: 'ac_select_ng',
			container_open_class:'ac_container_open'
		}, options);
		
		//----------------------------------------
		//2å›žç›®ã�®è¨­å®š(ä»–ã�®ã‚ªãƒ—ã‚·ãƒ§ãƒ³ã�®å€¤ã‚’å¼•ç”¨ã�™ã‚‹ã�Ÿã‚�)
		//----------------------------------------
		options = $.extend({
			search_field : options.field, //æ¤œç´¢ã�™ã‚‹ãƒ•ã‚£ãƒ¼ãƒ«ãƒ‰(ã‚«ãƒ³ãƒžåŒºåˆ‡ã‚Šã�§è¤‡æ•°æŒ‡å®šå�¯èƒ½)
			order_field  : options.field, //ORDER BY(SQL) ã�®åŸºæº–ã�¨ã�ªã‚‹ã‚«ãƒ©ãƒ å��(ã‚«ãƒ³ãƒžåŒºåˆ‡ã‚Šã�§è¤‡æ•°æŒ‡å®šå�¯èƒ½)
			order_by     : 'ASC',         //ORDER BY(SQL) ã�§ã€�ä¸¦ãƒ™æ›¿ã�ˆã‚‹ã�®ã�¯æ˜‡é †ã�‹é™�é †ã�‹

			//ç”»åƒ�
			button_img   : options.img_dir + 'combobox_button' + '.png',
			load_img     : options.img_dir + 'ajax-loader'     + '.gif'
		}, options);

		//************************************************************
		//ãƒ¡ãƒƒã‚»ãƒ¼ã‚¸ã‚’è¨€èªžåˆ¥ã�«ç”¨æ„�
		//************************************************************
		switch (options.lang){
		
			//æ—¥æœ¬èªž
			case 'ja':
				var msg = {
					'add_btn'     : 'è¿½åŠ ãƒœã‚¿ãƒ³',
					'add_title'   : 'å…¥åŠ›ãƒœãƒƒã‚¯ã‚¹ã‚’è¿½åŠ ã�—ã�¾ã�™',
					'del_btn'     : 'å‰Šé™¤ãƒœã‚¿ãƒ³',
					'del_title'   : 'å…¥åŠ›ãƒœãƒƒã‚¯ã‚¹ã‚’å‰Šé™¤ã�—ã�¾ã�™',
					'next'        : 'æ¬¡ã�¸',
					'next_title'  : 'æ¬¡ã�®'+options.per_page+'ä»¶ (å�³ã‚­ãƒ¼)',
					'prev'        : 'å‰�ã�¸',
					'prev_title'  : 'å‰�ã�®'+options.per_page+'ä»¶ (å·¦ã‚­ãƒ¼)',
					'first_title' : 'æœ€åˆ�ã�®ãƒšãƒ¼ã‚¸ã�¸ (Shift + å·¦ã‚­ãƒ¼)',
					'last_title'  : 'æœ€å¾Œã�®ãƒšãƒ¼ã‚¸ã�¸ (Shift + å�³ã‚­ãƒ¼)',
					'get_all_btn' : 'å…¨ä»¶å�–å¾— (ä¸‹ã‚­ãƒ¼)',
					'get_all_alt' : 'ç”»åƒ�:ãƒœã‚¿ãƒ³',
					'close_btn'   : 'é–‰ã�˜ã‚‹ (Tabã‚­ãƒ¼)',
					'close_alt'   : 'ç”»åƒ�:ãƒœã‚¿ãƒ³',
					'loading'     : 'ãƒ­ãƒ¼ãƒ‰ä¸­...',
					'loading_alt' : 'ç”»åƒ�:ãƒ­ãƒ¼ãƒ‰ä¸­...',
					'page_info'   : 'num_page_top - num_page_end ä»¶ (å…¨ cnt ä»¶)',
					'select_ng'   : 'æ³¨æ„� : ãƒªã‚¹ãƒˆã�®ä¸­ã�‹ã‚‰é�¸æŠžã�—ã�¦ã��ã� ã�•ã�„',
					'select_ok'   : 'OK : æ­£ã�—ã��é�¸æŠžã�•ã‚Œã�¾ã�—ã�Ÿã€‚'
				};
				break;

			//è‹±èªž
			case 'en':
				var msg = {
					'add_btn'     : 'Add button',
					'add_title'   : 'add a box',
					'del_btn'     : 'Del button',
					'del_title'   : 'delete a box',
					'next'        : 'Next',
					'next_title'  : 'Next'+options.per_page+' (Right key)',
					'prev'        : 'Prev',
					'prev_title'  : 'Prev'+options.per_page+' (Left key)',
					'first_title' : 'First (Shift + Left key)',
					'last_title'  : 'Last (Shift + Right key)',
					'get_all_btn' : 'Get All (Down key)',
					'get_all_alt' : '(button)',
					'close_btn'   : 'Close (Tab key)',
					'close_alt'   : '(button)',
					'loading'     : 'loading...',
					'loading_alt' : '(loading)',
					'page_info'   : 'num_page_top - num_page_end of cnt',
					'select_ng'   : 'Attention : Please choose from among the list.',
					'select_ok'   : 'OK : Correctly selected.'
				};
				break;

			case 'it':
				var msg = {
					'add_btn'     : 'Aggiungu',
					'add_title'   : 'Aggiungi',
					'del_btn'     : 'Togli',
					'del_title'   : 'Togli',
					'next'        : '>',
					'next_title'  : 'Prossimi '+options.per_page+' (Tasto destra)',
					'prev'        : '<',
					'prev_title'  : 'Precedenti '+options.per_page+' (Tasto sinista)',
					'first_title' : 'Primo (Shift + Tasto sinistra)',
					'last_title'  : 'Ultimo (Shift + Tasto destra)',
					'get_all_btn' : 'Tutti (Tasto giù)',
					'get_all_alt' : '(giù)',
					'close_btn'   : 'Chiudi (Tab)',
					'close_alt'   : '(chiudi)',
					'loading'     : 'caricamento...',
					'loading_alt' : '(caricamento)',
					'page_info'   : 'num_page_top - num_page_end of cnt',
					'select_ng'   : 'Attenzione : Scegliere un elemento dalla lista',
					'select_ok'   : 'OK : Selezione corretta.'
				};
				break;

			//ã‚¹ãƒšã‚¤ãƒ³èªž (Joaquin G. de la Zerdaæ°�ã�‹ã‚‰ã�®æ��ä¾›)
			case 'es':
				var msg = {
					'add_btn'     : 'Agregar boton',
					'add_title'   : 'Agregar una opcion',
					'del_btn'     : 'Borrar boton',
					'del_title'   : 'Borrar una opcion',
					'next'        : 'Siguiente',
					'next_title'  : 'Proximas '+options.per_page+' (tecla derecha)',
					'prev'        : 'Anterior',
					'prev_title'  : 'Anteriores '+options.per_page+' (tecla izquierda)',
					'first_title' : 'Primera (Shift + Left)',
					'last_title'  : 'Ultima (Shift + Right)',
					'get_all_btn' : 'Ver todos (tecla abajo)',
					'get_all_alt' : '(boton)',
					'close_btn'   : 'Cerrar (tecla TAB)',
					'close_alt'   : '(boton)',
					'loading'     : 'Cargando...',
					'loading_alt' : '(Cargando)',
					'page_info'   : 'num_page_top - num_page_end de cnt',
					'select_ng'   : 'Atencion: Elija una opcion de la lista.',
					'select_ok'   : 'OK: Correctamente seleccionado.'
				};
				break;

			default:
		}
		this.each(function() {
			new $.ajaxComboBox(this, source, options, msg);
		});
		return this;
	};
})(jQuery);
