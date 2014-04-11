/*jshint browser: true, nomen: false, eqnull: true, es5:true, trailing:true */

(function ($) {

    "use strict";

    function selectToggle(el) {
        $(el).toggleClass('selected');
    }


    function toggleInputHighlight(evt) {
        var _input = $(evt.currentTarget),
            cell = $(_input.parents('td')[0]),
            li = $(_input.parents('li')[0]);
        selectToggle(li);
        selectToggle(cell);
    }

    function markDirty(evt) {
        var _input = $(evt.currentTarget),
            cell = $(_input.parents('td')[0]),
            li = $(_input.parents('li')[0]);
        li.addClass('dirty');
    }

    function hookupInputs() {
        $('.priorities-form .priority-grid input').each(function () {
            var input = $(this);
            input.focus(toggleInputHighlight);
            input.blur(toggleInputHighlight);
            input.change(markDirty);
        });
    }

    $(document).ready(function () {
        /* overlays */
        $('a.rubriclink').prepOverlay({
             subtype: 'ajax',
             filter: 'div#content-core'
        });
        /* highlights */
        hookupInputs();
    });

}(jQuery));

