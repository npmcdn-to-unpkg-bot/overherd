function search_data() {
	var search_val = $("#search-bar").val();
	console.log(search_val);
	$.ajax({
		type: "GET",
		url: "/samsara",
		data: { 'series_id': search_code },
		success: function(data) {
		    last_search_json = jQuery.parseJSON(data);
		    if ("observations" in last_search_json) {
		    	var new_node = add_new_node(
					search_val, 
					{"x": 0, "y": 0}, 
					new NodeData(search_code + ".FRED", "", {"data": last_search_json['observations']})
				)
				update();	
		    }
		}
	});
}