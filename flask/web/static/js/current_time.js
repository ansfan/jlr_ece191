function startTime(time_id) {
    var today = new Date();
    // add a zero in front of numbers<10
    document.getElementById(time_id).innerHTML = today.toUTCString();
    t = setTimeout(function () {
        startTime(time_id)
    }, 500);
}
