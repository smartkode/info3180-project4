var http = new XMLHttpRequest();
http.open("POST",url,true);
var url = "/profiles/";
http.open("POST",url,true);
http.send();
http.responseText;

var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
xmlhttp.open("POST", "/json-handler");
xmlhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
xmlhttp.send(JSON.stringify({name:"John Rambo", time:"2pm"}));