localStorage.food="naseberry";
# storing a JSON object
obj = {"age":4,"name":"John"};
localStorage.user = JSON.stringify(obj);

function listAllItems(){
	for (i=0; i<=localStorage.length-1; i++)
	{
		key = localStorage.key(i);
		val = localStorage.getItem(key);
          console.log(key,val);
	}
}
listAllItems();