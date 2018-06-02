var myImage = document.querySelector('img');

myImage.onclick = function() {
    var mySrc = myImage.getAttribute('src');
    if(mySrc === 'images/1.jpg') {
      myImage.setAttribute ('src','images/2.jpg');
    } else {
      myImage.setAttribute ('src','images/1.jpg');
    }
}

var myButton = document.querySelector('button');
var myResults = document.getElementById('results');
//var myResults = document.querySelector('h1');
myButton.onclick = function() {
  myResults.textContent = 'None'
}