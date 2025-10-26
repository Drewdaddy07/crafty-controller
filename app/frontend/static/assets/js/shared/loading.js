function rotateImage(degree) {
    $('#logo-animate').animate({ transform: degree }, {
        step: function (now, fx) {
            $(this).css({
                '-webkit-transform': 'rotate(' + now + 'deg)',
                '-moz-transform': 'rotate(' + now + 'deg)',
                'transform': 'rotate(' + now + 'deg)'
            });
        }
    });
    setTimeout(function () {
        rotateImage(360);
    }, 2000);
}