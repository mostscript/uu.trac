/*jshint browser: true, nomen: false, eqnull: true, es5:true, trailing:true */

(function ($) {

    "use strict";

    var origBgColor = null;

    function bgcolor(el) {
        var style = document.defaultView.getComputedStyle;
        if (el instanceof $) {
            el = el[0];  // bare DOM element
        }
        console.log(style(el, null));
        return style(el, null).backgroundColor;
    }

    function addInputHighlight(evt) {
        var _input = $(evt.currentTarget),
            cell = $(_input.parents('td')[0]),
            li = $(_input.parents('li')[0]);
        origBgColor = bgcolor(li);  // breadcrumb
        li.css({
            'background-color':'#ffe',
            'border-left':'5px solid red'
        });
        cell.css({
            'background-color':'#063'
        });
    }


    function removeInputHighlight(evt) {
        var _input = $(evt.currentTarget),
            cell = $(_input.parents('td')[0]),
            li = $(_input.parents('li')[0]);
        li.css({
            'background-color': origBgColor,
            'border-left': '1px solid rgb(0, 0, 255)'
        });
        cell.css({
            'background-color':'#fff'
        });
    }

    function hookupInputs() {
        $('.priorities-form .priority-grid input').each(function () {
            var input = $(this);
            input.focus(addInputHighlight);
            input.blur(removeInputHighlight);
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

