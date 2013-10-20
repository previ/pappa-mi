function mycarousel_initCallback(carousel)
{
    // Disable autoscrolling if the user clicks the prev or next button.
    carousel.buttonNext.bind('click', function() {
        carousel.startAuto(0);
    });

    carousel.buttonPrev.bind('click', function() {
        carousel.startAuto(0);
    });

    // Pause autoscrolling if the user moves with the cursor over the clip.
    carousel.clip.hover(function() {
        carousel.stopAuto();
    }, function() {
        carousel.startAuto();
    });
};

jQuery(document).ready(function() {
    jQuery('#menu').jcarousel({
		vertical: true,
		scroll: 1,
        auto: 5,
        wrap: 'both',
		buttonNextHTML: '<div></div>',
		buttonPrevHTML: '<div></div>',
        initCallback: mycarousel_initCallback
    });
});
