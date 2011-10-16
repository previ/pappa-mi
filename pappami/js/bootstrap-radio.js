/* Radio and toggle buttons */
              
!function( $ ) {

    function activate( element, container ) {
        container.find( '.active' ).removeClass( 'active' )
        element.addClass('active')
    }

    jQuery.fn.radioGroup = function() {
        
        return this.each( function() {
            var $this = $(this)
            $this.click( function() {
                activate( $this, $this.parent() )
            })
        })
    }
    
    jQuery.fn.toggleBtn = function() {
        return this.each( function() {
            var $this = $(this)
            $this.click( function(ev) {
                var target = ev.originalEvent.target;
                
                // because the event bubble and is also triggered by the LABEL element
                if (target.tagName != "INPUT") return;
                
                $this.toggleClass('active')
            })
        })
    }
    
    jQuery.fn.updateRadioState = function() {
        this.find( "[type='radio']" ).each( function() {            
            if(this.checked) {
                var $this = $(this).parent();
                activate($this,$this.parent());
            }
        });
    }
    
}( window.jQuery || window.ender );
