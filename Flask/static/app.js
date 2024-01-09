// Fetch data from the Flask backend and create a bar chart
d3.json("/fetch_data_for_d3").then(function(data) {
    var width = 500;
    var height = 300;

    var svg = d3.select("#chart")
                .append("svg")
                .attr("width", width)
                .attr("height", height);

    // Create a tooltip
    var tooltip = d3.select("body")
                    .append("div")
                    .style("position", "absolute")
                    .style("visibility", "hidden")
                    .style("background", "#f8f9fa")
                    .style("border", "1px solid #ccc")
                    .style("border-radius", "4px")
                    .style("padding", "5px");

    // Create bars and add tooltip events
    svg.selectAll("rect")
       .data(data)
       .enter()
       .append("rect")
       .attr("x", function(d, i) {
           return i * (width / data.length);
       })
       .attr("y", function(d) {
           return height - d.value * 10; 
       })
       .attr("width", width / data.length - 5)
       .attr("height", function(d) {
           return d.value * 10; 
       })
       .attr("fill", "blue")
       .on("mouseover", function(event, d) {
           tooltip.html(d.message + "<br>" + d.value)
                  .style("visibility", "visible");
       })
       .on("mousemove", function(event) {
           tooltip.style("top", (event.pageY - 10) + "px")
                  .style("left", (event.pageX + 10) + "px");
       })
       .on("mouseout", function() {
           tooltip.style("visibility", "hidden");
       });

    // Adding text labels
    svg.selectAll("text")
       .data(data)
       .enter()
       .append("text")
       .text(function(d) {
           return d.message; 
       })
       .attr("x", function(d, i) {
           return i * (width / data.length) + (width / data.length - 5) / 2;
       })
       .attr("y", function(d) {
           return height - d.value * 10 - 5; 
       })
       .attr("text-anchor", "middle")
       .attr("fill", "black");
}).catch(function(error) {
    console.log(error);
});
