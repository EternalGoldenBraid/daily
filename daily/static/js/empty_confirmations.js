$(function() {
    $('#eventclear').bind('click'), function() {
        event.preventDefault();
        $.post($SCRIPT_ROOT + '/empty')
    };
});
