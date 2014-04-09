
(function ($) {
    $(document).ready(function () {
        /* overlays */
        $('a.rubriclink').prepOverlay({
             subtype: 'ajax',
             filter: 'div#content-core'
        });
    });

}(jQuery));

