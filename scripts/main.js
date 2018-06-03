function TFromDate() {
    var fromDate = document.getElementById("fromDate").value;
    var toDate = document.getElementById("toDate").value;
    var TodayDate = new Date();
    var fromErr = document.getElementById("fromErr");

    if (new Date(fromDate).getTime() > TodayDate.getTime()) {
          fromErr.innerHTML = "The Date must be Smaller or Equal to today date";
          return false;
     }
    if(new Date(toDate).getTime() < new Date(fromDate).getTime()) {        
          fromErr.innerHTML = "The Date must be Smaller or Equal to the to Date";
          return false;
    }
    fromErr.innerHTML = "";
    return true;
}

function TToDate() {
    var fromDate = document.getElementById("fromDate").value;
    var toDate = document.getElementById("toDate").value;
    var TodayDate = new Date();
    var toErr = document.getElementById("toErr");

    if (new Date(toDate).getTime() > TodayDate.getTime()) {
          toErr.innerHTML = "The Date must be Smaller or Equal to today date";
          return false;
     }    
    if(new Date(toDate).getTime() < new Date(fromDate).getTime()) {        
          toErr.innerHTML = "The Date must be Bigger or Equal to the from Date";
          return false;
    }
    toErr.innerHTML = ""        

    return true;
}