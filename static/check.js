function required(inputtx) 
   {
     if (inputtx.value.length == 0)
      { 
         alert("Please insert all fields");  	
         return false; 
      }  	
      return true; 
    } 

    function required()
{
var empt = document.forms["form"]["username"].value;
if (empt == "")
{
alert("Please input a Value");
return false;
}
else 
{
alert('Code has accepted : you can try another');
return true; 
}
}