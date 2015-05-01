var sent = document.getElementById("sent");
var rcvd = document.getElementById("rcvd");
var cpu = document.getElementById("cpu");
var txt = document.getElementById("txtbox");

swampdragon.onChannelMessage(function (channels, message) {
	console.log(channels);
	console.log(message);

	if (channels.indexOf('sysinfo_sent') > -1 && message.data.kb_sent) {
	    sent.innerText = message.data.kb_sent;
	}
	if (channels.indexOf('sysinfo_rec') > -1 && message.data.kb_received) {
		rcvd.innerText = message.data.kb_received;
	}
	if (channels.indexOf('sysinfo_cpu') > -1 && message.data.cpu) {
		cpu.innerText = message.data.cpu + '%';
	}
});

swampdragon.open(function() {
    swampdragon.subscribe('sys', 'sysinfo_sent', null);
    swampdragon.subscribe('sys', 'sysinfo_rec', null);
    swampdragon.subscribe('sys', 'sysinfo_cpu', null);
});