var textbox1 = document.getElementById("text1");
var textbox2 = document.getElementById("text2");
var textbox3 = document.getElementById("text3");

swampdragon.onChannelMessage(function (channels, message) {
	console.log(channels);
	console.log(message);

	if (channels.indexOf('stream1') > -1 && message.data.stream1) {
	    textbox1.innerText = message.data.stream1;
	}
	if (channels.indexOf('stream2') > -1 && message.data.stream2) {
		textbox2.innerText = message.data.stream2;
	}
	if (channels.indexOf('stream3') > -1 && message.data.stream3) {
		textbox3.innerText = message.data.stream3 + '%';
	}
});

swampdragon.open(function() {
    swampdragon.subscribe('room', 'stream1', null);
    swampdragon.subscribe('room', 'stream2', null);
    swampdragon.subscribe('room', 'stream3', null);
});