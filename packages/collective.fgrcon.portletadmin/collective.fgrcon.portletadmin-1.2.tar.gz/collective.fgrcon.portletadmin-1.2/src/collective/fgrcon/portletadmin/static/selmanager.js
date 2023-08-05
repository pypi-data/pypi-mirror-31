//
function get_portletmanagers(tcont, sid, vhmprefix){
	console.log(vhmprefix + ' '+ tcont+' ' + sid);
	var val = $('#p-'+tcont+'-'+sid).val();
	tsel = '#sel-'+tcont+'-'+sid;
	$.ajax({url: "@@avail-portlet-managers?tcont=" + vhmprefix+val,async: false, success:
	   function(result){
            $(tsel).html(result);
                   },
       error: function() { 
                    alert("Sorry, but " + val + " is not a valid container");
                }                 
                    });
}
