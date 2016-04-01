localStorage.food="naseberry";
obj = {"age":4,"name":"John"};
localStorage.user = JSON.stringify(obj);

if(typeof(localStorage)!=="undefined")
	  {
	  	
	  	function listAllItems(){
			for (i=0; i<=localStorage.length-1; i++)
			{
				key = localStorage.key(i);
				val = localStorage.getItem(key);
		          console.log(key,val);
			}
		}
		listAllItems();
		console.log("Hello World")
		console.log(obj)
	  }
	else
	  {
	  	console.log("Sorry! No Web Storage support..")
	  }