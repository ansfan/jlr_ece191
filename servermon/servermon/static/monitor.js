var sent = document.getElementById("sent");
var rcvd = document.getElementById("rcvd");
var cpu = document.getElementById("cpu");

swampdragon.onChannelMessage(function (channels, message) {
    sent.innerText = message.data.kb_sent;
    rcvd.innerText = message.data.kb_received;
    cpu.innerText = message.data.cpu + '%';
});


swampdragon.ready(function() {
    swampdragon.subscribe('sys', 'sysinfo', null);
});