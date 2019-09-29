window.onload = function() {
    $("#dropdown-applications").mouseenter(function(){
        document.getElementById("dropdown-applications-list").classList.add("show")
    });
    $("#dropdown-applications").mouseleave(function(){
        document.getElementById("dropdown-applications-list").classList.remove("show")
    });
};
