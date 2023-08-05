/*
    Attaches an onClick event on all links in class ext-link which opens this
    link in a new window.

    Copyright (c) 2008 Martin Scharrer <martin@scharrer-online.de>
    $Id: extlinks.js 15265 2016-02-11 04:29:08Z rjollos $
    $HeadURL: https://trac-hacks.org/svn/externallinksnewwindowplugin/0.11/tracextlinksnewwindow/htdocs/extlinks.js $

    This is Free Software under the GPL v3!
*/

$(document).ready( function() {
    $('a.ext-link').click ( function () {
        window.open( $(this).attr('href') );
        return false;
    });
});

